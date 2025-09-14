#!/usr/bin/env python3
import os
import json
import random
import uuid
import datetime
import requests
from typing import List, Dict, Optional
from fastmcp import FastMCP
import redis

# Initialize FastMCP server
mcp = FastMCP("Poke-R Poker Server")

# Redis client setup (following quizup pattern)
_redis_client: Optional[redis.Redis] = None

def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    redis_url = os.environ.get("REDIS_URL") or os.environ.get("REDIS_CONNECTION_STRING")
    if redis_url:
        _redis_client = redis.from_url(redis_url, decode_responses=True)
    else:
        _redis_client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            db=int(os.environ.get("REDIS_DB", "0")),
            decode_responses=True,
        )
    return _redis_client

# Deck: 52 cards (e.g., "2H" = 2 of Hearts, "TJ" = 10 of Jacks)
DECK = [f"{rank}{suit}" for rank in "23456789TJQKA" for suit in "HDCS"]

# Card ranking for hand evaluation
CARD_RANKS = {rank: i for i, rank in enumerate("23456789TJQKA")}

# Colorful emoji card representations
CARD_EMOJIS = {
    # Hearts (Red)
    '2H': '2♥️', '3H': '3♥️', '4H': '4♥️', '5H': '5♥️', '6H': '6♥️', '7H': '7♥️', '8H': '8♥️', '9H': '9♥️', 'TH': '10♥️', 'JH': 'J♥️', 'QH': 'Q♥️', 'KH': 'K♥️', 'AH': 'A♥️',
    # Diamonds (Red)
    '2D': '2♦️', '3D': '3♦️', '4D': '4♦️', '5D': '5♦️', '6D': '6♦️', '7D': '7♦️', '8D': '8♦️', '9D': '9♦️', 'TD': '10♦️', 'JD': 'J♦️', 'QD': 'Q♦️', 'KD': 'K♦️', 'AD': 'A♦️',
    # Clubs (Black)
    '2C': '2♣️', '3C': '3♣️', '4C': '4♣️', '5C': '5♣️', '6C': '6♣️', '7C': '7♣️', '8C': '8♣️', '9C': '9♣️', 'TC': '10♣️', 'JC': 'J♣️', 'QC': 'Q♣️', 'KC': 'K♣️', 'AC': 'A♣️',
    # Spades (Black)
    '2S': '2♠️', '3S': '3♠️', '4S': '4♠️', '5S': '5♠️', '6S': '6♠️', '7S': '7♠️', '8S': '8♠️', '9S': '9♠️', 'TS': '10♠️', 'JS': 'J♠️', 'QS': 'Q♠️', 'KS': 'K♠️', 'AS': 'A♠️'
}

def format_cards(cards: List[str]) -> List[str]:
    """Convert card codes to colorful emoji representations."""
    return [CARD_EMOJIS.get(card, card) for card in cards]

def notify_player_turn(game_id: str, player_phone: str, player_name: str, message: str) -> None:
    """Send notification to player via Poke API when it's their turn."""
    try:
        # Poke API endpoint for sending notifications
        poke_api_url = os.environ.get("POKE_API_URL", "https://poke.com/api")
        
        # Prepare notification payload
        payload = {
            "phone": player_phone,
            "message": message,
            "game_id": game_id,
            "game_type": "poker",
            "action": "your_turn"
        }
        
        # Send notification to Poke API
        response = requests.post(
            f"{poke_api_url}/notify",
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Notified {player_name} ({player_phone}) - {message}")
        else:
            print(f"⚠️ Failed to notify {player_name} ({player_phone}): {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error notifying {player_name} ({player_phone}): {e}")
        # Don't fail the game if notification fails

def evaluate_hand(cards: List[str]) -> tuple:
    """Evaluate poker hand strength. Returns (hand_type, rank_value, kickers)."""
    if len(cards) != 5:
        return ("invalid", 0, [])

    # Parse cards
    ranks = []
    suits = []
    for card in cards:
        rank = card[:-1]
        suit = card[-1]
        ranks.append(CARD_RANKS[rank])
        suits.append(suit)

    # Count rank frequencies
    rank_counts = {}
    for rank in ranks:
        rank_counts[rank] = rank_counts.get(rank, 0) + 1

    # Sort by frequency then by rank
    sorted_counts = sorted(rank_counts.items(), key=lambda x: (-x[1], -x[0]))

    # Check for hand types
    counts = [count for _, count in sorted_counts]
    rank_values = [rank for rank, _ in sorted_counts]

    # Flush check
    is_flush = len(set(suits)) == 1

    # Straight check
    is_straight = False
    if len(set(ranks)) == 5:
        sorted_ranks = sorted(ranks)
        if sorted_ranks[-1] - sorted_ranks[0] == 4:
            is_straight = True
        # Check for A-2-3-4-5 straight
        elif sorted_ranks == [0, 1, 2, 3, 12]:  # A-2-3-4-5
            is_straight = True

    # Determine hand type
    if is_straight and is_flush:
        if sorted_ranks[-1] == 12:  # Ace high straight flush
            return ("royal_flush", 0, [])
        else:
            return ("straight_flush", sorted_ranks[-1], [])
    elif counts == [4, 1]:
        return ("four_of_a_kind", rank_values[0], [rank_values[1]])
    elif counts == [3, 2]:
        return ("full_house", rank_values[0], [rank_values[1]])
    elif is_flush:
        return ("flush", sorted(ranks, reverse=True), [])
    elif is_straight:
        if sorted_ranks == [0, 1, 2, 3, 12]:  # A-2-3-4-5
            return ("straight", 3, [])  # 5 high straight
        else:
            return ("straight", sorted_ranks[-1], [])
    elif counts == [3, 1, 1]:
        kickers = sorted([rank_values[1], rank_values[2]], reverse=True)
        return ("three_of_a_kind", rank_values[0], kickers)
    elif counts == [2, 2, 1]:
        pair_ranks = sorted([rank_values[0], rank_values[1]], reverse=True)
        return ("two_pair", pair_ranks[0], [pair_ranks[1], rank_values[2]])
    elif counts == [2, 1, 1, 1]:
        kickers = sorted([rank_values[1], rank_values[2], rank_values[3]], reverse=True)
        return ("pair", rank_values[0], kickers)
    else:
        return ("high_card", sorted(ranks, reverse=True), [])

def compare_hands(hand1: List[str], hand2: List[str]) -> int:
    """Compare two poker hands. Returns 1 if hand1 wins, -1 if hand2 wins, 0 if tie."""
    hand_types = ["high_card", "pair", "two_pair", "three_of_a_kind", "straight",
                  "flush", "full_house", "four_of_a_kind", "straight_flush", "royal_flush"]

    type1, rank1, kickers1 = evaluate_hand(hand1)
    type2, rank2, kickers2 = evaluate_hand(hand2)

    # Compare hand types
    if hand_types.index(type1) > hand_types.index(type2):
        return 1
    elif hand_types.index(type1) < hand_types.index(type2):
        return -1

    # Same hand type, compare ranks
    if isinstance(rank1, list) and isinstance(rank2, list):
        for r1, r2 in zip(rank1, rank2):
            if r1 > r2:
                return 1
            elif r1 < r2:
                return -1
    else:
        if rank1 > rank2:
            return 1
        elif rank1 < rank2:
            return -1

    # Compare kickers
    for k1, k2 in zip(kickers1, kickers2):
        if k1 > k2:
            return 1
        elif k1 < k2:
            return -1

    return 0

def get_game_state(game_id: str) -> Optional[Dict]:
    """Get game state from Redis or return None if not found."""
    try:
        r = get_redis()
        state_json = r.get(game_id)
        return json.loads(state_json) if state_json else None
    except Exception:
        return None

def save_game_state(game_id: str, state: Dict) -> bool:
    """Save game state to Redis. Returns True if successful."""
    try:
        r = get_redis()
        r.set(game_id, json.dumps(state), ex=3600)  # Expire after 1 hour
        return True
    except Exception:
        return False

def register_player(phone: str, name: str) -> bool:
    """Register a player with phone number as primary key and name as alias."""
    try:
        r = get_redis()

        # Store phone -> name mapping
        r.set(f"player_name:{phone}", name)

        # Store name -> phone mapping for reverse lookup
        r.set(f"player_phone:{name}", phone)

        return True
    except Exception:
        return False

def get_player_phone(player_identifier: str) -> str:
    """Get phone number from player identifier (phone or name)."""
    try:
        r = get_redis()

        # If it looks like a phone number, return as-is
        if player_identifier.startswith('+') and len(player_identifier) > 5:
            return player_identifier

        # Otherwise, look up phone by name
        phone = r.get(f"player_phone:{player_identifier}")
        return phone if phone else player_identifier
    except Exception:
        return player_identifier

def get_player_name(phone: str) -> str:
    """Get player name from phone number."""
    try:
        r = get_redis()
        name = r.get(f"player_name:{phone}")
        return name if name else phone
    except Exception:
        return phone

def check_availability(phone: str) -> bool:
    """Check if user is available for Poke-R games."""
    try:
        r = get_redis()

        # Check if availability is enabled
        availability_key = f"user_availability:{phone}"
        availability_value = r.get(availability_key)
        if not availability_value or availability_value.lower() != 'true':
            return False

        # Check schedule if set
        schedule_key = f"{phone}:schedule"
        schedule_json = r.get(schedule_key)
        if schedule_json:
            try:
                schedule = json.loads(schedule_json)
                now = datetime.datetime.now()
                current_time = now.time()
                current_weekday = now.weekday() + 1  # Monday = 1

                for window in schedule.get("windows", []):
                    if current_weekday in window.get("days", []):
                        start_time = datetime.datetime.strptime(window["start"], "%H:%M").time()
                        end_time = datetime.datetime.strptime(window["end"], "%H:%M").time()
                        if start_time <= current_time <= end_time:
                            return True
                return False
            except Exception:
                pass

        return True
    except Exception:
        return True  # Default to available if Redis fails

@mcp.tool(description="Register a player with phone number and name")
def register_player_tool(phone: str, name: str) -> Dict:
    """Register a player with phone number as primary key and name as alias."""
    if not phone or not name:
        return {'error': 'Both phone number and name are required'}

    if not phone.startswith('+'):
        return {'error': 'Phone number must start with + (e.g., +31646118037)'}

    if register_player(phone, name):
        return {
            'message': f"Player registered: {name} ({phone})",
            'phone': phone,
            'name': name
        }
    else:
        return {'error': 'Failed to register player'}

@mcp.tool(description="Start a new 2-player Poke-R poker game")
def start_poker(players: List[str]) -> Dict:
    """Starts a 2-player Poke-R duel."""
    if len(players) != 2:
        return {'error': 'Exactly 2 players required'}

    # Convert player identifiers to phone numbers
    player_phones = []
    player_names = []

    for player in players:
        phone = get_player_phone(player)
        name = get_player_name(phone)

        # Check if player is registered (has phone->name mapping)
        if not get_redis().get(f"player_name:{phone}"):
            return {'error': f"Player '{player}' not registered. Use register_player_tool first with phone number and name."}

        player_phones.append(phone)
        player_names.append(name)

    # Check player availability by phone number
    for i, phone in enumerate(player_phones):
        if not check_availability(phone):
            return {'error': f"{player_names[i]} ({phone}) is unavailable for Poke-R games—try later?"}

    # Generate game ID
    game_id = f"poker_{uuid.uuid4().hex[:8]}"

    # Create and shuffle deck
    deck = DECK.copy()
    random.shuffle(deck)

    # Deal initial hands (use phone numbers as keys internally)
    hands = {
        player_phones[0]: deck[0:5],
        player_phones[1]: deck[5:10]
    }

    # Initialize game state (use phone numbers internally, display names externally)
    state = {
        'game_id': game_id,
        'players': player_phones,  # Store phone numbers internally
        'player_names': player_names,  # Store names for display
        'chips': {player_phones[0]: 100, player_phones[1]: 100},
        'hands': hands,
        'current_hand': 1,
        'pot': 0,
        'bets': {player_phones[0]: 0, player_phones[1]: 0},
        'phase': 'bet1',  # bet1, draw, bet2, showdown
        'deck': deck[10:],
        'current_player': player_phones[0],
        'side_bets': {},
        'created_at': datetime.datetime.now().isoformat()
    }

    # Save to Redis
    if not save_game_state(game_id, state):
        return {'error': 'Failed to save game state'}

    # Send pending invites
    try:
        r = get_redis()
        for phone in player_phones:
            invite_key = f"{game_id}:pending:{phone}"
            r.set(invite_key, "1", ex=600)  # 10-minute timeout
    except Exception:
        pass  # Invites are optional

    # Notify the first player it's their turn
    first_player_name = player_names[0]
    first_player_phone = player_phones[0]
    notify_message = f"🎲 Poke-R game started! Your turn to bet first. Check your hand and make your move!"
    notify_player_turn(game_id, first_player_phone, first_player_name, notify_message)

    # Return game info without revealing hands (hands should be sent via DM)
    return {
        'game_id': game_id,
        'message': f"🎲 Poke-R duel started! Cards sent via DM. {player_names[0]}, bet first (min 5): bet/call/raise/fold.",
        'chips': {player_names[0]: 100, player_names[1]: 100},
        'players': player_names,
        'current_player': player_names[0],
        'phase': 'bet1'
    }

@mcp.tool(description="Get your own hand for a poker game")
def get_my_hand(game_id: str, player: str) -> Dict:
    """Get a player's own hand without revealing opponent's cards."""
    state = get_game_state(game_id)
    if not state:
        return {'error': 'Game not found or expired'}

    # Convert player identifier to phone number
    player_phone = get_player_phone(player)

    # Check if player is in the game
    if player_phone not in state['players']:
        return {'error': 'Player not in this game'}

    # Get player's hand
    player_hand = state['hands'].get(player_phone, [])
    player_name = get_player_name(player_phone)

    return {
        'game_id': game_id,
        'player': player_name,
        'hand': format_cards(player_hand),
        'hand_codes': player_hand,  # Keep original codes for game logic
        'chips': state['chips'].get(player_phone, 0),
        'current_player': get_player_name(state['current_player']),
        'phase': state['phase'],
        'pot': state['pot']
    }

@mcp.tool(description="Place a bet, call, raise, or fold in the current poker game")
def place_bet(game_id: str, player: str, action: str, amount: int = 0) -> Dict:
    """Handles bet, call, raise, or fold actions."""
    state = get_game_state(game_id)
    if not state:
        return {'error': 'Game not found or expired'}

    if player != state['current_player']:
        return {'error': 'Not your turn'}

    if action not in ['bet', 'call', 'raise', 'fold']:
        return {'error': 'Invalid action. Use: bet, call, raise, or fold'}

    opponent = state['players'][1 - state['players'].index(player)]
    current_bet = state['bets'].get(opponent, 0)

    if action == 'fold':
        # Player folds, opponent wins pot
        state['chips'][opponent] += state['pot']
        state['pot'] = 0
        state['bets'] = {p: 0 for p in state['players']}
        state['current_hand'] += 1

        if state['current_hand'] > 5:  # End after 5 hands
            winner = max(state['chips'], key=state['chips'].get)
            save_game_state(game_id, state)
            return {
                'message': f"{player} folds! {opponent} wins {state['pot']} chips. Game over! {winner} wins with {state['chips'][winner]} chips! 🥳",
                'game_over': True,
                'winner': winner,
                'final_chips': state['chips']
            }

        # Start next hand
        deck = DECK.copy()
        random.shuffle(deck)
        state['hands'] = {
            state['players'][0]: deck[0:5],
            state['players'][1]: deck[5:10]
        }
        state['deck'] = deck[10:]
        state['phase'] = 'bet1'
        state['current_player'] = state['players'][0]
        state['side_bets'] = {}

        save_game_state(game_id, state)
        return {
            'message': f"{player} folds! {opponent} wins {state['pot']} chips. Next hand starting...",
            'new_hand': True,
            'hands': state['hands']
        }

    elif action in ['bet', 'raise']:
        min_bet = current_bet + 5 if action == 'raise' else 5
        if amount < min_bet:
            return {'error': f'Minimum bet is {min_bet} chips'}
        if state['chips'][player] < amount:
            return {'error': 'Not enough chips'}

        state['bets'][player] = amount
        state['chips'][player] -= amount
        state['pot'] += amount

    elif action == 'call':
        if state['chips'][player] < current_bet:
            return {'error': 'Not enough chips to call'}

        state['bets'][player] = current_bet
        state['chips'][player] -= current_bet
        state['pot'] += current_bet

    # Switch to opponent
    state['current_player'] = opponent
    
    # Notify the opponent it's their turn
    opponent_name = get_player_name(opponent)
    notify_message = f"🎲 Your turn in Poke-R! {player} made their move. Check your hand and make your bet!"
    notify_player_turn(game_id, opponent, opponent_name, notify_message)

    # Check if betting round is complete
    if state['bets'][player] == state['bets'][opponent] and state['bets'][player] > 0:
        if state['phase'] == 'bet1':
            state['phase'] = 'draw'
            save_game_state(game_id, state)
            return {
                'message': f"Bets matched! {player}, discard up to 3 cards: 'Poke, discard [indices]'.",
                'phase': 'draw',
                'current_player': player
            }
        elif state['phase'] == 'bet2':
            state['phase'] = 'showdown'
            # Resolve hand
            winner_idx = compare_hands(state['hands'][state['players'][0]], state['hands'][state['players'][1]])
            if winner_idx == 1:
                winner = state['players'][0]
            elif winner_idx == -1:
                winner = state['players'][1]
            else:
                winner = None  # Tie

            if winner:
                state['chips'][winner] += state['pot']
                winner_hand_type = evaluate_hand(state['hands'][winner])[0]
                winner_hand_emojis = format_cards(state['hands'][winner])
                winner_name = get_player_name(winner)
                message = f"Showdown! {winner_name} wins {state['pot']} chips with {winner_hand_type}! Hand: {' '.join(winner_hand_emojis)}"
            else:
                # Split pot on tie
                split_amount = state['pot'] // 2
                state['chips'][state['players'][0]] += split_amount
                state['chips'][state['players'][1]] += split_amount
                message = f"Showdown! It's a tie! Pot split equally."

            state['pot'] = 0
            state['bets'] = {p: 0 for p in state['players']}
            state['current_hand'] += 1

            if state['current_hand'] > 5:  # End game
                final_winner = max(state['chips'], key=state['chips'].get)
                save_game_state(game_id, state)
                return {
                    'message': f"{message} Game over! {final_winner} wins with {state['chips'][final_winner]} chips! 🥳",
                    'game_over': True,
                    'winner': final_winner,
                    'final_chips': state['chips']
                }

            # Start next hand
            deck = DECK.copy()
            random.shuffle(deck)
            state['hands'] = {
                state['players'][0]: deck[0:5],
                state['players'][1]: deck[5:10]
            }
            state['deck'] = deck[10:]
            state['phase'] = 'bet1'
            state['current_player'] = state['players'][0]
            state['side_bets'] = {}

            save_game_state(game_id, state)
            return {
                'message': f"{message} Next hand starting...",
                'new_hand': True,
                'hands': state['hands']
            }

    save_game_state(game_id, state)
    return {
        'message': f"{player} {action}s {amount or ''}! {opponent}, your move: bet/call/raise/fold.",
        'current_player': opponent,
        'pot': state['pot'],
        'chips': state['chips']
    }

@mcp.tool(description="Discard up to 3 cards and draw new ones")
def discard_cards(game_id: str, player: str, indices: List[int]) -> Dict:
    """Discards up to 3 cards and draws new ones."""
    state = get_game_state(game_id)
    if not state:
        return {'error': 'Game not found or expired'}

    if state['phase'] != 'draw':
        return {'error': 'Not in discard phase'}

    if player != state['current_player']:
        return {'error': 'Not your turn'}

    if len(indices) > 3:
        return {'error': 'Maximum 3 cards can be discarded'}

    if any(i < 1 or i > 5 for i in indices):
        return {'error': 'Invalid card indices (use 1-5)'}

    # Discard and draw new cards
    hand = state['hands'][player]
    for i in sorted(indices, reverse=True):
        hand.pop(i-1)  # Convert to 0-based index
        if state['deck']:
            hand.append(state['deck'].pop(0))

    # Switch to second betting round
    state['phase'] = 'bet2'
    state['current_player'] = state['players'][1 - state['players'].index(player)]
    state['bets'] = {p: 0 for p in state['players']}
    
    # Notify the other player it's their turn for second betting round
    other_player = state['current_player']
    other_player_name = get_player_name(other_player)
    notify_message = f"🎲 Second betting round! {player} drew cards. Your turn to bet!"
    notify_player_turn(game_id, other_player, other_player_name, notify_message)

    save_game_state(game_id, state)
    return {
        'message': f"New cards dealt to {player}. {state['current_player']}, bet (min 5): bet/call/raise/fold.",
        'phase': 'bet2',
        'current_player': state['current_player'],
        'hand': state['hands'][player]
    }

@mcp.tool(description="Toggle Poke-R availability for receiving game invites")
def toggle_availability(phone: str) -> Dict:
    """Toggles Poke-R availability for a user."""
    try:
        r = get_redis()
        key = f"user_availability:{phone}"
        current = r.get(key)
        new_state = False if current and current.lower() == 'true' else True
        r.set(key, str(new_state))

        return {
            'message': f"Poke-R availability {'enabled' if new_state else 'disabled'}.",
            'available': new_state
        }
    except Exception:
        return {'error': 'Redis not available'}

@mcp.tool(description="Set availability schedule (e.g., '19:00-22:00, Mon-Fri')")
def set_schedule(phone: str, schedule_str: str) -> Dict:
    """Sets availability schedule for Poke-R games."""
    try:
        r = get_redis()
        times, days_str = schedule_str.split(',')
        start, end = times.strip().split('-')
        days = []

        # Parse days
        day_mapping = {'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 7}
        for day_range in days_str.split('-'):
            day_range = day_range.strip()
            if day_range in day_mapping:
                days.append(day_mapping[day_range])

        schedule = {
            "windows": [{
                "start": start.strip(),
                "end": end.strip(),
                "days": days
            }]
        }

        r.set(f"{phone}:schedule", json.dumps(schedule))
        return {
            'message': f"Schedule set: {schedule_str}",
            'schedule': schedule
        }
    except Exception as e:
        return {'error': f'Invalid format—try "19:00-22:00, Mon-Fri". Error: {str(e)}'}

@mcp.tool(description="Accept a pending Poke-R game invite")
def accept_invite(game_id: str, phone: str) -> Dict:
    """Accepts a pending game invite."""
    try:
        r = get_redis()
        invite_key = f"{game_id}:pending:{phone}"
        if not r.get(invite_key):
            return {'error': 'No pending invite found'}

        # Remove invite
        r.delete(invite_key)

        return {
            'message': f"Joined Poke-R game {game_id}! Cards incoming. 🎲",
            'game_id': game_id
        }
    except Exception:
        return {'error': 'Redis not available'}

@mcp.tool(description="Get current game status and state")
def get_game_status(game_id: str) -> Dict:
    """Get current game status."""
    state = get_game_state(game_id)
    if not state:
        return {'error': 'Game not found or expired'}

    return {
        'game_id': game_id,
        'players': state['players'],
        'current_player': state['current_player'],
        'phase': state['phase'],
        'pot': state['pot'],
        'chips': state['chips'],
        'current_hand': state['current_hand'],
        'bets': state['bets']
    }

@mcp.tool(description="Get server information")
def get_server_info() -> Dict:
    """Get information about the Poke-R server."""
    return {
        "server_name": "Poke-R Poker Server",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": os.sys.version.split()[0],
        "redis_available": True  # We'll assume Redis is available
    }

# Add health check endpoint
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint for Render deployment"""
    return JSONResponse({
        "status": "healthy",
        "redis_available": True,
        "server": "Poke-R Poker Server",
        "version": "1.0.0"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    print(f"Starting Poke-R MCP server on {host}:{port}")
    mcp.run(transport="http", host=host, port=port)
