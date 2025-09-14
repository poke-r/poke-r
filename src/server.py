#!/usr/bin/env python3
import os
import sys
import json
import random
import uuid
import datetime
import logging
import traceback
import signal
import asyncio
from typing import List, Dict, Optional
from fastmcp import FastMCP
import redis

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('poke-r.log') if os.path.exists('.') else logging.NullHandler()
    ]
)
logger = logging.getLogger("Poke-R")

# Global error handler for uncaught exceptions
def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions globally"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow KeyboardInterrupt to be handled normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.error(f"💥 Uncaught exception: {exc_type.__name__}: {exc_value}")
    logger.debug(f"🔍 Traceback: {traceback.format_exception(exc_type, exc_value, exc_traceback)}")
    
    # In production, don't crash the server
    if os.environ.get("ENVIRONMENT") == "production":
        logger.error("🔄 Server continuing despite uncaught exception")
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

# Set the global exception handler
sys.excepthook = handle_uncaught_exception

# Custom error handler for MCP server
def mcp_error_handler(error):
    """Handle MCP server errors"""
    logger.error(f"💥 MCP Server Error: {error}")
    logger.debug(f"🔍 Error details: {traceback.format_exc()}")
    
    # Check if it's a connection-related error
    if "ClosedResourceError" in str(error) or "anyio" in str(error):
        logger.warning("⚠️ Streamable HTTP connection error detected")
        logger.info("🔄 This is a known issue with MCP streamable HTTP transport")
        logger.info("🛡️ Server will continue running with error handling")
        return True  # Indicate error was handled
    
    return False  # Error not handled

# Initialize FastMCP server with enhanced configuration
mcp = FastMCP("Poke-R Poker Server")
logger.info("🚀 Initializing Poke-R Poker Server")

# Initialize Redis connection
try:
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    logger.info(f"🔗 Attempting Redis connection to: {redis_url}")
    r = redis.from_url(redis_url, decode_responses=True)
    # Test connection
    r.ping()
    logger.info("✅ Redis connection successful")
except Exception as e:
    logger.warning(f"⚠️ Redis connection failed: {e}")
    logger.info("🔄 Falling back to in-memory storage")
    # Fallback to in-memory storage for development
    r = None

# Deck: 52 cards (e.g., "2H" = 2 of Hearts, "TJ" = 10 of Jacks)
DECK = [f"{rank}{suit}" for rank in "23456789TJQKA" for suit in "HDCS"]

# Card ranking for hand evaluation
CARD_RANKS = {rank: i for i, rank in enumerate("23456789TJQKA")}

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
    sorted_counts = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

    # Check for flush
    is_flush = len(set(suits)) == 1

    # Check for straight
    sorted_ranks = sorted(ranks)
    is_straight = (
        sorted_ranks == list(range(min(sorted_ranks), max(sorted_ranks) + 1)) or
        sorted_ranks == [0, 1, 2, 3, 12]  # A-2-3-4-5 straight
    )

    # Determine hand type
    counts = [count for _, count in sorted_counts]

    if is_straight and is_flush:
        if sorted_ranks == [8, 9, 10, 11, 12]:  # Royal flush
            return ("royal_flush", 13, [])
        else:
            return ("straight_flush", max(sorted_ranks), [])
    elif counts == [4, 1]:
        return ("four_of_a_kind", sorted_counts[0][0], [sorted_counts[1][0]])
    elif counts == [3, 2]:
        return ("full_house", sorted_counts[0][0], [sorted_counts[1][0]])
    elif is_flush:
        return ("flush", max(sorted_ranks), sorted(sorted_ranks, reverse=True))
    elif is_straight:
        return ("straight", max(sorted_ranks), [])
    elif counts == [3, 1, 1]:
        return ("three_of_a_kind", sorted_counts[0][0], [sorted_counts[1][0], sorted_counts[2][0]])
    elif counts == [2, 2, 1]:
        return ("two_pair", max(sorted_counts[0][0], sorted_counts[1][0]),
                [min(sorted_counts[0][0], sorted_counts[1][0]), sorted_counts[2][0]])
    elif counts == [2, 1, 1, 1]:
        return ("pair", sorted_counts[0][0], [sorted_counts[1][0], sorted_counts[2][0], sorted_counts[3][0]])
    else:
        return ("high_card", max(sorted_ranks), sorted(sorted_ranks, reverse=True))

def compare_hands(hand1: List[str], hand2: List[str]) -> int:
    """Compare two hands. Returns 1 if hand1 wins, -1 if hand2 wins, 0 if tie."""
    eval1 = evaluate_hand(hand1)
    eval2 = evaluate_hand(hand2)

    hand_rankings = {
        "royal_flush": 9, "straight_flush": 8, "four_of_a_kind": 7,
        "full_house": 6, "flush": 5, "straight": 4, "three_of_a_kind": 3,
        "two_pair": 2, "pair": 1, "high_card": 0
    }

    rank1 = hand_rankings[eval1[0]]
    rank2 = hand_rankings[eval2[0]]

    if rank1 > rank2:
        return 1
    elif rank1 < rank2:
        return -1
    else:
        # Same hand type, compare rank values and kickers
        if eval1[1] > eval2[1]:
            return 1
        elif eval1[1] < eval2[1]:
            return -1
        else:
            # Compare kickers
            for k1, k2 in zip(eval1[2], eval2[2]):
                if k1 > k2:
                    return 1
                elif k1 < k2:
                    return -1
            return 0

def get_game_state(game_id: str) -> Optional[Dict]:
    """Get game state from Redis or return None if not found."""
    logger.debug(f"🔍 Getting game state for ID: {game_id}")
    if not r:
        logger.debug("📝 Redis not available, returning None")
        return None
    try:
        state_json = r.get(game_id)
        if state_json:
            state = json.loads(state_json)
            logger.debug(f"✅ Retrieved game state: {len(state.get('players', []))} players, phase: {state.get('phase', 'unknown')}")
            return state
        else:
            logger.debug(f"❌ No game state found for ID: {game_id}")
            return None
    except redis.ConnectionError as e:
        logger.warning(f"⚠️ Redis connection lost: {e}")
        return None
    except Exception as e:
        logger.error(f"💥 Error getting game state for {game_id}: {e}")
        logger.debug(f"🔍 Traceback: {traceback.format_exc()}")
        return None

def save_game_state(game_id: str, state: Dict) -> bool:
    """Save game state to Redis. Returns True if successful."""
    logger.debug(f"💾 Saving game state for ID: {game_id}")
    if not r:
        logger.debug("📝 Redis not available, cannot save state")
        return False
    try:
        state_json = json.dumps(state)
        r.set(game_id, state_json, ex=3600)  # Expire after 1 hour
        logger.debug(f"✅ Game state saved successfully: {len(state_json)} bytes, expires in 1 hour")
        return True
    except redis.ConnectionError as e:
        logger.warning(f"⚠️ Redis connection lost during save: {e}")
        return False
    except Exception as e:
        logger.error(f"💥 Error saving game state for {game_id}: {e}")
        logger.debug(f"🔍 Traceback: {traceback.format_exc()}")
        return False

def check_availability(phone: str) -> bool:
    """Check if user is available for Poke-R games."""
    logger.debug(f"🔍 Checking availability for user: {phone}")
    if not r:
        logger.debug("📝 Redis not available, defaulting to available")
        return True  # Default to available if no Redis

    # Check if availability is enabled
    availability_key = f"user_availability:{phone}"
    availability_status = r.get(availability_key)
    logger.debug(f"📋 Availability status: {availability_status}")

    if not availability_status:
        logger.info(f"❌ User {phone} has not enabled Poke-R availability")
        return False

    # Check schedule if set
    schedule_key = f"{phone}:schedule"
    schedule_json = r.get(schedule_key)
    if schedule_json:
        logger.debug(f"📅 Checking schedule for user: {phone}")
        try:
            schedule = json.loads(schedule_json)
            now = datetime.datetime.now()
            current_time = now.time()
            current_weekday = now.weekday() + 1  # Monday = 1

            logger.debug(f"🕐 Current time: {current_time}, weekday: {current_weekday}")

            for window in schedule.get("windows", []):
                logger.debug(f"🪟 Checking window: {window}")
                if current_weekday in window.get("days", []):
                    start_time = datetime.datetime.strptime(window["start"], "%H:%M").time()
                    end_time = datetime.datetime.strptime(window["end"], "%H:%M").time()
                    logger.debug(f"⏰ Window times: {start_time} - {end_time}")
                    if start_time <= current_time <= end_time:
                        logger.info(f"✅ User {phone} is available (within scheduled window)")
                        return True
            logger.info(f"❌ User {phone} is outside scheduled hours")
            return False
        except Exception as e:
            logger.error(f"💥 Error checking schedule for {phone}: {e}")
            logger.debug(f"🔍 Traceback: {traceback.format_exc()}")

    logger.info(f"✅ User {phone} is available (no schedule restrictions)")
    return True

@mcp.tool(description="Start a new 2-player Poke-R poker game")
def start_poker(players: List[str]) -> Dict:
    """Starts a 2-player Poke-R duel."""
    logger.info(f"🎮 Starting new poker game with players: {players}")

    if len(players) != 2:
        logger.error(f"❌ Invalid player count: {len(players)} (expected 2)")
        return {'error': 'Exactly 2 players required'}

    # Check player availability
    logger.info("🔍 Checking player availability...")
    for player in players:
        if not check_availability(player):
            logger.warning(f"❌ Player {player} is unavailable")
            return {'error': f"{player} is unavailable for Poke-R games—try later?"}
        logger.info(f"✅ Player {player} is available")

    # Generate game ID
    game_id = f"poker_{uuid.uuid4().hex[:8]}"
    logger.info(f"🆔 Generated game ID: {game_id}")

    # Create and shuffle deck
    deck = DECK.copy()
    random.shuffle(deck)
    logger.debug(f"🃏 Deck shuffled: {len(deck)} cards")

    # Deal initial hands
    hands = {
        players[0]: deck[0:5],
        players[1]: deck[5:10]
    }
    logger.info(f"🎯 Dealt hands: {players[0]}={hands[players[0]]}, {players[1]}={hands[players[1]]}")

    # Initialize game state
    state = {
        'game_id': game_id,
        'players': players,
        'chips': {players[0]: 100, players[1]: 100},
        'hands': hands,
        'current_hand': 1,
        'pot': 0,
        'bets': {players[0]: 0, players[1]: 0},
        'phase': 'bet1',  # bet1, draw, bet2, showdown
        'deck': deck[10:],
        'current_player': players[0],
        'side_bets': {},
        'created_at': datetime.datetime.now().isoformat()
    }
    logger.info(f"📊 Game state initialized: Phase={state['phase']}, Current Player={state['current_player']}")

    # Save to Redis
    if not save_game_state(game_id, state):
        logger.error(f"💥 Failed to save game state for {game_id}")
        return {'error': 'Failed to save game state'}

    # Send pending invites
    logger.info("📨 Setting up pending invites...")
    for player in players:
        invite_key = f"{game_id}:pending:{player}"
        if r:
            r.set(invite_key, "1", ex=600)  # 10-minute timeout
            logger.debug(f"📧 Invite set for {player}: {invite_key}")

    logger.info(f"🎉 Game {game_id} started successfully!")
    return {
        'game_id': game_id,
        'message': f"🎲 Poke-R duel started! Cards sent via DM. {players[0]}, bet first (min 5): bet/call/raise/fold.",
        'hands': hands,
        'chips': state['chips']
    }

@mcp.tool(description="Place a bet, call, raise, or fold in the current poker game")
def place_bet(game_id: str, player: str, action: str, amount: int = 0) -> Dict:
    """Handles bet, call, raise, or fold actions."""
    logger.info(f"🎯 Betting action: {player} -> {action} (amount: {amount}) in game {game_id}")

    state = get_game_state(game_id)
    if not state:
        logger.error(f"❌ Game {game_id} not found or expired")
        return {'error': 'Game not found or expired'}

    if player != state['current_player']:
        logger.warning(f"❌ Wrong turn: {player} tried to act, but {state['current_player']} is current player")
        return {'error': 'Not your turn'}

    if action not in ['bet', 'call', 'raise', 'fold']:
        logger.error(f"❌ Invalid action: {action}")
        return {'error': 'Invalid action. Use: bet, call, raise, or fold'}

    opponent = state['players'][1 - state['players'].index(player)]
    current_bet = state['bets'].get(opponent, 0)
    logger.debug(f"🎲 Game state: Phase={state['phase']}, Current bet={current_bet}, Pot={state['pot']}, Player chips={state['chips'][player]}")

    if action == 'fold':
        logger.info(f"🃏 {player} folds! {opponent} wins pot of {state['pot']} chips")
        # Player folds, opponent wins pot
        state['chips'][opponent] += state['pot']
        state['pot'] = 0
        state['bets'] = {p: 0 for p in state['players']}
        state['current_hand'] += 1
        logger.info(f"📊 Hand {state['current_hand']-1} complete. New hand: {state['current_hand']}")

        if state['current_hand'] > 5:  # End after 5 hands
            winner = max(state['chips'], key=state['chips'].get)
            logger.info(f"🏆 Game over! Winner: {winner} with {state['chips'][winner]} chips")
            save_game_state(game_id, state)
            return {
                'message': f"{player} folds! {opponent} wins {state['pot']} chips. Game over! {winner} wins with {state['chips'][winner]} chips! 🥳",
                'game_over': True,
                'winner': winner,
                'final_chips': state['chips']
            }

        # Start next hand
        logger.info("🎲 Starting new hand...")
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
        logger.info(f"🎯 New hands dealt: {state['players'][0]}={state['hands'][state['players'][0]]}, {state['players'][1]}={state['hands'][state['players'][1]]}")

        save_game_state(game_id, state)
        return {
            'message': f"{player} folds! {opponent} wins {state['pot']} chips. Next hand starting...",
            'new_hand': True,
            'hands': state['hands']
        }

    elif action in ['bet', 'raise']:
        min_bet = current_bet + 5 if action == 'raise' else 5
        logger.debug(f"💰 {action} validation: amount={amount}, min_bet={min_bet}, player_chips={state['chips'][player]}")

        if amount < min_bet:
            logger.warning(f"❌ {player} bet too low: {amount} < {min_bet}")
            return {'error': f'Minimum bet is {min_bet} chips'}
        if state['chips'][player] < amount:
            logger.warning(f"❌ {player} insufficient chips: {state['chips'][player]} < {amount}")
            return {'error': 'Not enough chips'}

        state['bets'][player] = amount
        state['chips'][player] -= amount
        state['pot'] += amount
        logger.info(f"💰 {player} {action}s {amount} chips. New pot: {state['pot']}, Player chips: {state['chips'][player]}")

    elif action == 'call':
        logger.debug(f"📞 Call validation: current_bet={current_bet}, player_chips={state['chips'][player]}")

        if state['chips'][player] < current_bet:
            logger.warning(f"❌ {player} insufficient chips to call: {state['chips'][player]} < {current_bet}")
            return {'error': 'Not enough chips to call'}

        state['bets'][player] = current_bet
        state['chips'][player] -= current_bet
        state['pot'] += current_bet
        logger.info(f"📞 {player} calls {current_bet} chips. New pot: {state['pot']}, Player chips: {state['chips'][player]}")

    # Switch to opponent
    state['current_player'] = opponent
    logger.debug(f"🔄 Turn switched to: {opponent}")

    # Check if betting round is complete
    if state['bets'][player] == state['bets'][opponent] and state['bets'][player] > 0:
        logger.info(f"✅ Betting round complete! Both players bet {state['bets'][player]} chips")

        if state['phase'] == 'bet1':
            state['phase'] = 'draw'
            logger.info(f"🎯 Moving to draw phase. {player} can discard up to 3 cards")
            save_game_state(game_id, state)
            return {
                'message': f"Bets matched! {player}, discard up to 3 cards: 'Poke, discard [indices]'.",
                'phase': 'draw',
                'current_player': player
            }
        elif state['phase'] == 'bet2':
            state['phase'] = 'showdown'
            logger.info("🏁 Showdown time! Comparing hands...")

            # Resolve hand
            hand1 = state['hands'][state['players'][0]]
            hand2 = state['hands'][state['players'][1]]
            winner_idx = compare_hands(hand1, hand2)

            logger.info(f"🎯 Hand comparison: {state['players'][0]}={hand1} vs {state['players'][1]}={hand2}")

            if winner_idx == 1:
                winner = state['players'][0]
                winner_hand = hand1
            elif winner_idx == -1:
                winner = state['players'][1]
                winner_hand = hand2
            else:
                winner = None  # Tie
                winner_hand = None

            if winner:
                state['chips'][winner] += state['pot']
                winner_hand_type = evaluate_hand(winner_hand)[0]
                logger.info(f"🏆 {winner} wins with {winner_hand_type}: {winner_hand}")
                message = f"Showdown! {winner} wins {state['pot']} chips with {winner_hand_type}!"
            else:
                # Split pot on tie
                split_amount = state['pot'] // 2
                state['chips'][state['players'][0]] += split_amount
                state['chips'][state['players'][1]] += split_amount
                logger.info(f"🤝 Tie! Pot split: {split_amount} chips each")
                message = f"Showdown! It's a tie! Pot split equally."

            state['pot'] = 0
            state['bets'] = {p: 0 for p in state['players']}
            state['current_hand'] += 1
            logger.info(f"📊 Hand {state['current_hand']-1} complete. New hand: {state['current_hand']}")

            if state['current_hand'] > 5:  # End game
                final_winner = max(state['chips'], key=state['chips'].get)
                logger.info(f"🏆 Game over! Final winner: {final_winner} with {state['chips'][final_winner]} chips")
                save_game_state(game_id, state)
                return {
                    'message': f"{message} Game over! {final_winner} wins with {state['chips'][final_winner]} chips! 🥳",
                    'game_over': True,
                    'winner': final_winner,
                    'final_chips': state['chips']
                }

            # Start next hand
            logger.info("🎲 Starting new hand...")
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
            logger.info(f"🎯 New hands dealt: {state['players'][0]}={state['hands'][state['players'][0]]}, {state['players'][1]}={state['hands'][state['players'][1]]}")

            save_game_state(game_id, state)
            return {
                'message': f"{message} Next hand starting...",
                'new_hand': True,
                'hands': state['hands']
            }

    save_game_state(game_id, state)
    logger.info(f"✅ Betting action complete. Next turn: {opponent}")
    return {
        'message': f"{player} {action}s {amount or ''}! {opponent}, your move: bet/call/raise/fold.",
        'current_player': opponent,
        'pot': state['pot'],
        'chips': state['chips']
    }

@mcp.tool(description="Discard up to 3 cards and draw new ones")
def discard_cards(game_id: str, player: str, indices: List[int]) -> Dict:
    """Discards up to 3 cards and draws new ones."""
    logger.info(f"🔄 Discard action: {player} discarding cards at indices {indices} in game {game_id}")

    state = get_game_state(game_id)
    if not state:
        logger.error(f"❌ Game {game_id} not found or expired")
        return {'error': 'Game not found or expired'}

    if state['phase'] != 'draw':
        logger.warning(f"❌ Wrong phase: {state['phase']} (expected 'draw')")
        return {'error': 'Not in discard phase'}

    if player != state['current_player']:
        logger.warning(f"❌ Wrong turn: {player} tried to discard, but {state['current_player']} is current player")
        return {'error': 'Not your turn'}

    if len(indices) > 3:
        logger.warning(f"❌ Too many cards to discard: {len(indices)} > 3")
        return {'error': 'Maximum 3 cards can be discarded'}

    if any(i < 1 or i > 5 for i in indices):
        logger.warning(f"❌ Invalid card indices: {indices} (must be 1-5)")
        return {'error': 'Invalid card indices (use 1-5)'}

    # Discard and draw new cards
    hand = state['hands'][player]
    original_hand = hand.copy()
    discarded_cards = []
    new_cards = []

    logger.debug(f"🎯 Original hand: {original_hand}")

    for i in sorted(indices, reverse=True):
        discarded_card = hand.pop(i-1)  # Convert to 0-based index
        discarded_cards.append(discarded_card)
        if state['deck']:
            new_card = state['deck'].pop(0)
            hand.append(new_card)
            new_cards.append(new_card)

    logger.info(f"🔄 {player} discarded: {discarded_cards}, drew: {new_cards}")
    logger.info(f"🎯 New hand: {hand}")

    # Switch to second betting round
    state['phase'] = 'bet2'
    state['current_player'] = state['players'][1 - state['players'].index(player)]
    state['bets'] = {p: 0 for p in state['players']}
    logger.info(f"🎯 Moving to bet2 phase. Next player: {state['current_player']}")

    save_game_state(game_id, state)
    return {
        'message': f"New cards dealt to {player}. {state['current_player']}, bet (min 5): bet/call/raise/fold.",
        'phase': 'bet2',
        'current_player': state['current_player'],
        'hand': state['hands'][player]
    }

@mcp.tool(description="Place a side bet on hand outcome")
def place_side_bet(game_id: str, player: str, bet_type: str, amount: int) -> Dict:
    """Place a side bet (e.g., 'pair+' for pair or better)."""
    state = get_game_state(game_id)
    if not state:
        return {'error': 'Game not found or expired'}

    if player not in state['players']:
        return {'error': 'Not a player in this game'}

    if state['chips'][player] < amount:
        return {'error': 'Not enough chips'}

    if player in state.get('side_bets', {}):
        return {'error': 'Already placed a side bet this hand'}

    # Initialize side bets if not exists
    if 'side_bets' not in state:
        state['side_bets'] = {}

    state['side_bets'][player] = {
        'type': bet_type,
        'amount': amount
    }
    state['chips'][player] -= amount

    save_game_state(game_id, state)
    return {
        'message': f"{player} placed side bet: {amount} chips on {bet_type}",
        'side_bet': state['side_bets'][player]
    }

@mcp.tool(description="Toggle Poke-R availability for receiving game invites")
def toggle_availability(phone: str) -> Dict:
    """Toggles Poke-R availability for a user."""
    logger.info(f"🔧 Toggling availability for user: {phone}")

    if not r:
        logger.error("❌ Redis not available for availability toggle")
        return {'error': 'Redis not available'}

    key = f"user_availability:{phone}"
    current = r.get(key)
    new_state = not bool(current) if current else True
    r.set(key, str(new_state))

    logger.info(f"✅ Availability {'enabled' if new_state else 'disabled'} for {phone}")
    return {
        'message': f"Poke-R availability {'enabled' if new_state else 'disabled'}.",
        'available': new_state
    }

@mcp.tool(description="Set availability schedule (e.g., '19:00-22:00, Mon-Fri')")
def set_schedule(phone: str, schedule_str: str) -> Dict:
    """Sets availability schedule for Poke-R games."""
    logger.info(f"📅 Setting schedule for {phone}: {schedule_str}")

    if not r:
        logger.error("❌ Redis not available for schedule setting")
        return {'error': 'Redis not available'}

    try:
        times, days_str = schedule_str.split(',')
        start, end = times.strip().split('-')
        days = []

        logger.debug(f"🕐 Parsing times: {start} - {end}")

        # Parse days
        day_mapping = {'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 7}
        for day_range in days_str.split('-'):
            day_range = day_range.strip()
            if day_range in day_mapping:
                days.append(day_mapping[day_range])
                logger.debug(f"📅 Added day: {day_range} -> {day_mapping[day_range]}")

        schedule = {
            "windows": [{
                "start": start.strip(),
                "end": end.strip(),
                "days": days
            }]
        }

        logger.info(f"📅 Schedule parsed: {schedule}")
        r.set(f"{phone}:schedule", json.dumps(schedule))
        logger.info(f"✅ Schedule saved for {phone}")

        return {
            'message': f"Schedule set: {schedule_str}",
            'schedule': schedule
        }
    except Exception as e:
        logger.error(f"💥 Error parsing schedule '{schedule_str}': {e}")
        logger.debug(f"🔍 Traceback: {traceback.format_exc()}")
        return {'error': f'Invalid format—try "19:00-22:00, Mon-Fri". Error: {str(e)}'}

@mcp.tool(description="Accept a pending Poke-R game invite")
def accept_invite(game_id: str, phone: str) -> Dict:
    """Accepts a pending game invite."""
    logger.info(f"📧 Accepting invite: {phone} -> {game_id}")

    if not r:
        logger.error("❌ Redis not available for invite acceptance")
        return {'error': 'Redis not available'}

    invite_key = f"{game_id}:pending:{phone}"
    if not r.get(invite_key):
        logger.warning(f"❌ No pending invite found for {phone} in game {game_id}")
        return {'error': 'No pending invite found'}

    # Remove invite
    r.delete(invite_key)
    logger.info(f"✅ Invite accepted and removed for {phone}")

    return {
        'message': f"Joined Poke-R game {game_id}! Cards incoming. 🎲",
        'game_id': game_id
    }

@mcp.tool(description="Get current game status and state")
def get_game_status(game_id: str) -> Dict:
    """Get current game status."""
    logger.info(f"📊 Getting game status for: {game_id}")

    state = get_game_state(game_id)
    if not state:
        logger.warning(f"❌ Game {game_id} not found or expired")
        return {'error': 'Game not found or expired'}

    logger.info(f"📊 Game status: Phase={state['phase']}, Hand={state['current_hand']}, Pot={state['pot']}, Current Player={state['current_player']}")
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
    logger.info("ℹ️ Server info requested")

    info = {
        "server_name": "Poke-R Poker Server",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": os.sys.version.split()[0],
        "redis_available": r is not None
    }

    logger.info(f"ℹ️ Server info: {info}")
    return info

# Add health check endpoint
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint for Render deployment"""
    logger.info("🏥 Health check requested")

    health_status = {
        "status": "healthy",
        "redis_available": r is not None,
        "server": "Poke-R Poker Server",
        "version": "1.0.0"
    }

    logger.info(f"🏥 Health check response: {health_status}")
    return JSONResponse(health_status)

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True

def run_server_with_retry():
    """Run the server with retry logic for connection errors"""
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries and not shutdown_requested:
        try:
            logger.info(f"🎮 Starting MCP server (attempt {retry_count + 1}/{max_retries})...")
            
            # Wrap the MCP run in a try-catch to handle streamable HTTP errors
            try:
                mcp.run(
                    transport="http",
                    host=host,
                    port=port,
                    stateless_http=True
                )
            except Exception as mcp_error:
                # Check if it's the specific streamable HTTP error
                if "ClosedResourceError" in str(mcp_error) or "anyio" in str(mcp_error):
                    logger.warning("⚠️ Streamable HTTP connection error caught")
                    logger.info("🛡️ This is a known MCP transport issue, continuing...")
                    # Don't treat this as a fatal error
                    return
                else:
                    # Re-raise other errors
                    raise
            
            break  # If we get here, the server ran successfully
        except Exception as e:
            retry_count += 1
            logger.error(f"💥 Server attempt {retry_count} failed: {e}")
            logger.debug(f"🔍 Traceback: {traceback.format_exc()}")
            
            if retry_count < max_retries:
                logger.info(f"🔄 Retrying in 5 seconds... (attempt {retry_count + 1}/{max_retries})")
                import time
                time.sleep(5)
            else:
                logger.error("💥 Max retries reached, server failed to start")
                if os.environ.get("ENVIRONMENT") == "production":
                    logger.error("🔄 Server will attempt restart in 30 seconds...")
                    time.sleep(30)
                    retry_count = 0  # Reset retry count for production restart
                else:
                    raise

if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info("🚀 Starting Poke-R MCP server...")
    logger.info(f"🌐 Server configuration: {host}:{port}")
    logger.info(f"🔗 Redis available: {r is not None}")
    logger.info(f"🌍 Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    logger.info(f"🐍 Python version: {os.sys.version.split()[0]}")
    
    print(f"Starting Poke-R MCP server on {host}:{port}")
    print(f"Redis available: {r is not None}")
    
    try:
        run_server_with_retry()
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"💥 Fatal server error: {e}")
        logger.debug(f"🔍 Traceback: {traceback.format_exc()}")
        # In production, try to restart
        if os.environ.get("ENVIRONMENT") == "production":
            logger.error("🔄 Attempting server restart...")
            import time
            time.sleep(10)
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            raise
