# Product Requirements Document (PRD): Poke-R - MCP-Powered 2-Player Poker Game via Poke Automations

## Version History
- **Version**: 3.1
- **Date**: September 14, 2025
- **Author**: Grok 4 (xAI)
- **Status**: Final Draft for Implementation
- **Purpose**: This PRD defines **Poke-R**, a 2-player Five-Card Draw poker game integrated with Poke.com’s AI assistant via Model Context Protocol (MCP). Players duel in iMessage/WhatsApp, betting and bluffing with virtual chips, while Poke deals cards, manages turns, and resolves hands. Designed for HackMIT 2025 (due 11:15 AM EDT, September 14, 2025), Poke-R emphasizes human-driven strategy (bluffing, reading opponents) with branching outcomes, ensuring Poke facilitates without playing. Privacy controls prevent spam invites. Optimized for Cursor AI to generate and deploy code in ~11 hours.

## Executive Summary
Poke-R is a head-to-head poker duel where two players play Five-Card Draw in chat. Each gets 5 private cards (via Poke DMs), bets, discards/draws up to 3 cards, bets again, and reveals hands. Players start with 100 chips, bluffing and strategizing over 3-5 hands (5-10 minutes). Poke parses commands (e.g., “Poke, raise 20”) and calls an MCP server to manage state and resolve hands (e.g., “Alice’s flush beats Bob’s pair!”). Human psychology drives thousands of outcomes per game, keeping AI at bay. Privacy toggles ensure opt-in play, making it spam-free.

**Key Value Proposition**: Intense, bluff-heavy poker duels in your chats—no apps, human-driven, spam-free.

**Target Users**: Casual gamers, buddies on iMessage/WhatsApp, Poke beta testers, HackMIT participants.

**Success Metrics**:
- Deployable MVP by 11:15 AM EDT (~11 hours).
- 100 concurrent games, <1s response time.
- Demo video with >1,000 social media views.
- Zero spam complaints.

## Goals and Objectives
- **Primary Goal**: Build an MCP server for a 2-player Five-Card Draw game, integrated with Poke, emphasizing human strategy over AI.
- **Objectives**:
  - Implement core poker mechanics: Deal, bet, discard/draw, resolve hands.
  - Limit Poke to facilitation: Parse commands, DM cards, relay results.
  - Support async play (2-min turn timers) for chat environments.
  - Retain privacy controls: Availability toggles, schedules, consent-based invites.
  - Target HackMIT prizes: “Most Fun” (bluffing duels), “Most Technically Impressive” (MCP + Redis), “Most Practical” (quick buddy games).
- **Non-Goals**:
  - Multi-player (>2) or real-time play.
  - AI opponents or complex hand animations.
  - Monetization or persistent accounts.

## Scope
- **In Scope**:
  - MCP server with poker logic, Redis state management, simplified hand evaluation.
  - Poke integration via https://github.com/InteractionCo/mcp-server-template.
  - 2-player support with bets, discards, and results.
  - Privacy: Toggles, schedules, invites.
  - Deployment on Render (free tier).
  - Testing with MCP Inspector and Poke webhook.
- **Out of Scope**:
  - Custom UI beyond text/emojis.
  - Full poker hand ranking (use simplified logic for MVP).
  - Compliance audits (beta context).
- **Assumptions**:
  - Poke beta access (MCP form, API key).
  - Redis available (local or Render add-on).
  - Python 3.13/3.12 via Conda.
- **Dependencies**:
  - Poke.com account.
  - GitHub template.
  - Redis for state.
  - Render hosting.

## User Stories and Features
### Core Gameplay Features
1. **Game Creation**:
   - **User Story**: As a player, I text “Poke, start Poke-R with [buddy]” to launch a 2-player poker duel.
   - **Requirements**:
     - Parse 2 players (phone numbers/@mentions from chat context).
     - Generate `game_id` (UUID).
     - Deal 5 private cards each (via Poke DMs, e.g., “Your cards: 2H, 7D, JC, QS, AH”).
     - Initialize 100 chips each (stored in Redis).
     - Start first betting round (minimum bet 5 chips).
     - Check player availability (see Privacy Features) before starting.
     - Output: “🎲 Poke-R duel started! Cards sent via DM. [Player1], bet first (min 5): bet/call/raise/fold.”

2. **Betting Rounds**:
   - **User Story**: As a player, I bet, call, raise, or fold to outsmart my opponent in two betting rounds (pre- and post-draw).
   - **Requirements**:
     - Commands: “Poke, bet 10”, “call”, “raise 20”, “fold” (via group or private chat).
     - Validate: Sufficient chips; raise ≥ current bet + 5; call matches opponent’s bet.
     - Two rounds per hand: Pre-draw (after deal), post-draw (after discard).
     - 2-minute turn timer; auto-fold on timeout.
     - Output: “Bob raises to 20! Alice, call/raise/fold? (30s left)” or “Bob folds—Alice wins 10 chips!”

3. **Discard/Draw Phase**:
   - **User Story**: As a player, I discard up to 3 cards to improve my hand.
   - **Requirements**:
     - Command: “Poke, discard 1,3” (DM, indices of cards to discard, e.g., first and third).
     - Replace discarded cards with new ones from deck (tracked in Redis).
     - Limit: Max 3 discards per player.
     - Output: “New cards DM’d to [player]. Start final betting.”

4. **Hand Resolution and Results**:
   - **User Story**: At the end of a hand, I see who wins the pot; after 3-5 hands, I see the final winner.
   - **Requirements**:
     - Evaluate hands using simplified ranking (e.g., pair > high card; full logic optional for MVP).
     - Winner takes pot (sum of bets); ties split chips.
     - End after 3-5 hands or “Poke, end Poke-R”.
     - Output: “Alice’s pair beats Bob’s high card! Alice wins 30 chips. Next hand?”
     - Final: “Game over! Alice: 120 chips, Bob: 80. Alice wins! 🥳 Play again? Y/N.”
     - Optional: Leaderboard (top 10 by chips, Redis).

5. **Bluffing Enhancements**:
   - **User Story**: As a player, I use side bets to bluff or add risk.
   - **Requirements**:
     - Command: “Poke, side bet 10 on pair+” (costs 5 chips; pays 2x if player wins with pair or better).
     - Limit: 1 side bet per hand per player.
     - Output: “Bob’s side bet: 10 chips on pair+. Continue betting.”

### Privacy and Control Features
6. **Availability Toggle**:
   - **User Story**: I toggle Poke-R availability to avoid unwanted invites.
   - **Requirements**: Command “Poke, toggle Poke-R availability”; store in Redis (`user_availability:{phone}`, default off); prompt first use: “Enable Poke-R? Y/N.”

7. **Scheduled Availability**:
   - **User Story**: I set Poke-R hours (e.g., “19:00-22:00, Mon-Fri”).
   - **Requirements**: Command “Poke, set Poke-R hours [start-end, days]”; store in Redis (`{phone}:schedule`); check before invites.

8. **Consent-Based Invites**:
   - **User Story**: I explicitly accept invites to avoid spam.
   - **Requirements**: Notification “@buddy invited you to Poke-R—accept? Y/N”; 10-min timeout; store in Redis (`{game_id}:pending:{phone}`).

9. **Mute/Block Options**:
   - **User Story**: I mute or block Poke-R notifications.
   - **Requirements**: Commands “Poke, mute Poke-R 1 hour” or “block [buddy]”; store in Redis (`{phone}:blocked`).

### Non-Functional Requirements
- **Performance**: <1-second MCP response; support 100 concurrent games.
- **Security**: Validate inputs; use MCP auth; delete game data after 1 hour; GDPR-like consent.
- **Privacy**: Opt-in invites; max 3 notifications/day per user.
- **Scalability**: Redis for state; Render auto-scales.
- **Accessibility**: Text-only with emojis; no color reliance.
- **Logging**: Console logs for debugging; optional error tracking.
- **Reliability**: 99% uptime; handle Redis failures gracefully.

## Technical Architecture
- **Client**: Poke (parses commands, DMs cards, renders results).
- **Backend**: MCP Server (Python + FastMCP).
  - Endpoint: `/mcp` (Streamable HTTP transport).
  - Tools: `@mcp.tool` for `start_poker`, `place_bet`, `discard_cards`, etc.
- **Storage**: Redis (game state, hands, chips, user settings).
- **External Services**: None (static deck logic).
- **Integration Flow**:
  1. User texts Poke (e.g., “start Poke-R”).
  2. Poke calls MCP tool (e.g., `start_poker`).
  3. Server processes (Redis), streams JSON response.
  4. Poke displays in chat (group or DM).
- **Tech Stack**:
  - Python 3.13 (or 3.12 fallback).
  - FastMCP (from template).
  - Libraries: `redis`, `uuid`, `datetime`.
  - Deployment: Render (free tier).
  - Testing: MCP Inspector (`npx @modelcontextprotocol/inspector`).

## Implementation Plan
Given the ~11-hour HackMIT deadline, prioritize an MVP with core poker logic and privacy features.

### Phase 1: Setup (30 Minutes)
- Fork https://github.com/InteractionCo/mcp-server-template.
- Install dependencies:
  ```
  conda create -n mcp-server python=3.13 -c conda-forge
  conda activate mcp-server
  pip install fastmcp redis
  ```
- Run locally: `python src/server.py`.

### Phase 2: Core Logic (1-1.5 Hours)
- Implement MCP tools in `src/server.py` (see below).
- Use Redis for game state (hands, chips, bets).
- Simplify hand evaluation (e.g., pair vs. high card for MVP).

### Phase 3: Integration and Testing (30 Minutes)
- Deploy to Render → Get MCP URL (e.g., `https://poker-mcp.onrender.com/mcp`).
- Add to Poke: https://poke.com/settings/connections/integrations/new.
- Test via Poke API key:
  ```
  curl -X POST 'https://poke.com/api/v1/inbound-sms/webhook' \
       -H "Authorization: Bearer YOUR_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{"message": "Start Poke-R with +1234567890"}'
  ```
- Simulate with MCP Inspector; test edge cases (invalid bets, timeouts, declines).

### Phase 4: Polish and Submission (15 Minutes)
- Add emojis (🎲 for deal, 🥳 for win).
- Record 30-second WhatsApp demo (2-player duel, bluffing).
- Submit to https://interaction.co/HackMIT with repo, video, README.
- Pitch: “Poke-R: Bluff-heavy 2-player poker duels in chats, MCP-powered, with privacy controls for spam-free fun.”

## Sample MCP Server Code
This extends the template with Five-Card Draw logic, simplified for MVP. For HackMIT, focus on `start_poker`, `place_bet`, and basic hand resolution. Add `discard_cards` and privacy tools if time allows.

```python
import mcp
import redis
import uuid
import json
import random
import datetime
from typing import List, Dict

mcp_server = mcp.fastmcp("PokeRMCP")
r = redis.Redis(host='localhost', port=6379, db=0)  # Update for Render

# Deck: 52 cards (e.g., "2H" = 2 of Hearts)
DECK = [f"{rank}{suit}" for rank in "23456789TJQKA" for suit in "HDCS"]

def evaluate_hand(cards: List[str]) -> tuple:
    """Simplified hand evaluation for MVP: pair, high card."""
    ranks = [card[:-1] for card in cards]
    counts = {r: ranks.count(r) for r in ranks}
    if 2 in counts.values():
        return ("pair", max(r for r, c in counts.items() if c == 2))
    return ("high_card", max(ranks, key=lambda r: "23456789TJQKA".index(r)))

@mcp_server.tool
def start_poker(players: List[str]) -> Dict:
    """Starts a 2-player Poke-R duel."""
    if len(players) != 2:
        return {'error': 'Exactly 2 players required'}
    for p in players:
        if not check_availability(p):
            return {'error': f"{p} is unavailable—try later?"}
        r.set(f"game_{game_id}:pending:{p}", "1", ex=600)  # 10-min invite timeout
    game_id = f"poker_{uuid.uuid4().hex[:8]}"
    deck = DECK.copy()
    random.shuffle(deck)
    hands = {p: deck[i*5:(i+1)*5] for i, p in enumerate(players)}
    state = {
        'players': players,
        'chips': {p: 100 for p in players},
        'hands': hands,
        'current_hand': 1,
        'pot': 0,
        'bets': {p: 0 for p in players},
        'phase': 'bet1',
        'deck': deck[10:],
        'current_player': players[0]
    }
    r.set(game_id, json.dumps(state))
    return {
        'game_id': game_id,
        'message': f"🎲 Poke-R duel started! Cards DM’d. {players[0]}, bet first (min 5): bet/call/raise/fold."
    }

@mcp_server.tool
def place_bet(game_id: str, player: str, action: str, amount: int = 0) -> Dict:
    """Handles bet, call, raise, or fold."""
    state = json.loads(r.get(game_id))
    if not state or player != state['current_player']:
        return {'error': 'Invalid action or turn'}
    opponent = state['players'][1 - state['players'].index(player)]
    if action not in ['bet', 'call', 'raise', 'fold']:
        return {'error': 'Invalid action'}
    if action in ['bet', 'raise']:
        if amount < state['bets'].get(opponent, 0) + 5 or state['chips'][player] < amount:
            return {'error': 'Invalid amount'}
        state['bets'][player] = amount
        state['pot'] += amount - state['bets'][player]
    elif action == 'call':
        amount = state['bets'].get(opponent, 0)
        if state['chips'][player] < amount:
            return {'error': 'Not enough chips'}
        state['bets'][player] = amount
        state['pot'] += amount
    elif action == 'fold':
        state['chips'][opponent] += state['pot']
        state['pot'] = 0
        state['current_hand'] += 1
        r.set(game_id, json.dumps(state))
        if state['current_hand'] > 3:  # End after 3 hands
            r.delete(game_id)
            winner = max(state['chips'], key=state['chips'].get)
            return {'message': f"Game over! {winner} wins with {state['chips'][winner]} chips! 🥳 Play again? Y/N"}
        return {'message': f"{player} folds! {opponent} wins {state['pot']} chips. Next hand soon."}
    state['current_player'] = opponent
    if state['bets'][player] == state['bets'].get(opponent, 0) and state['bets'][player] > 0:
        state['phase'] = 'draw' if state['phase'] == 'bet1' else 'showdown'
    r.set(game_id, json.dumps(state))
    if state['phase'] == 'draw':
        return {'message': f"Bets matched! {player}, discard up to 3 cards: ‘Poke, discard [indices]’."}
    elif state['phase'] == 'showdown':
        winner = max(state['players'], key=lambda p: evaluate_hand(state['hands'][p]))
        state['chips'][winner] += state['pot']
        state['pot'] = 0
        state['current_hand'] += 1
        r.set(game_id, json.dumps(state))
        if state['current_hand'] > 3:
            r.delete(game_id)
            final_winner = max(state['chips'], key=state['chips'].get)
            return {'message': f"Showdown! {winner} wins with {evaluate_hand(state['hands'][winner])[0]}. Game over! {final_winner} wins with {state['chips'][final_winner]} chips! 🥳"}
        return {'message': f"Showdown! {winner} wins {state['pot']} chips with {evaluate_hand(state['hands'][winner])[0]}. Next hand soon."}
    return {'message': f"{player} {action}s {amount or ''}! {opponent}, your move: bet/call/raise/fold."}

@mcp_server.tool
def discard_cards(game_id: str, player: str, indices: List[int]) -> Dict:
    """Discards up to 3 cards and draws new ones."""
    state = json.loads(r.get(game_id))
    if not state or state['phase'] != 'draw' or player != state['current_player']:
        return {'error': 'Invalid discard phase or turn'}
    if len(indices) > 3 or any(i < 1 or i > 5 for i in indices):
        return {'error': 'Invalid indices (1-5, max 3)'}
    hand = state['hands'][player]
    for i in sorted(indices, reverse=True):
        hand.pop(i-1)
        hand.append(state['deck'].pop(0))
    state['current_player'] = state['players'][1 - state['players'].index(player)]
    state['bets'] = {p: 0 for p in state['players']}
    if state['current_player'] == state['players'][0]:
        state['phase'] = 'bet2'
    r.set(game_id, json.dumps(state))
    return {'message': f"New cards DM’d to {player}. {state['current_player']}, bet (min 5): bet/call/raise/fold."}

@mcp_server.tool
def toggle_availability(phone: str) -> Dict:
    """Toggles Poke-R availability."""
    key = f"user_availability:{phone}"
    current = r.get(key)
    new_state = not bool(current) if current else True
    r.set(key, str(new_state))
    return {'message': f"Poke-R availability {'enabled' if new_state else 'disabled'}."}

@mcp_server.tool
def set_schedule(phone: str, schedule_str: str) -> Dict:
    """Sets availability schedule (e.g., '19:00-22:00, Mon-Fri')."""
    try:
        times, days_str = schedule_str.split(',')
        start, end = times.strip().split('-')
        days = [datetime.datetime.strptime(d.strip(), '%a').weekday() + 1 for d in days_str.split('-')]
        schedule = {"windows": [{"start": start, "end": end, "days": days}]}
        r.set(f"{phone}:schedule", json.dumps(schedule))
        return {'message': f"Schedule set: {schedule_str}."}
    except:
        return {'error': 'Invalid format—try "19:00-22:00, Mon-Fri".'}

@mcp_server.tool
def check_availability(phone: str) -> bool:
    """Checks if user is available."""
    if not bool(r.get(f"user_availability:{phone}")):
        return False
    schedule = r.get(f"{phone}:schedule")
    if schedule:
        now = datetime.datetime.now()
        for window in json.loads(schedule)['windows']:
            if now.weekday() + 1 in window['days']:
                start_time = datetime.datetime.strptime(window['start'], '%H:%M').time()
                end_time = datetime.datetime.strptime(window['end'], '%H:%M').time()
                if start_time <= now.time() <= end_time:
                    return True
        return False
    return True

@mcp_server.tool
def accept_invite(game_id: str, phone: str) -> Dict:
    """Accepts pending invite."""
    if r.get(f"{game_id}:pending:{phone}"):
        state = json.loads(r.get(game_id))
        state['players'].append(phone)
        r.set(game_id, json.dumps(state))
        r.delete(f"{game_id}:pending:{phone}")
        return {'message': "Joined Poke-R! Cards incoming. 🎲"}
    return {'error': 'No pending invite.'}

if __name__ == "__main__":
    mcp_server.run(transport=mcp.transports.StreamableHTTP(), host="0.0.0.0", port=8000)
```

## Risks and Mitigations
- **Risk**: HackMIT deadline (~11 hours). **Mitigation**: Focus on MVP (`start_poker`, `place_bet`, simplified hand evaluation); skip `discard_cards` if needed.
- **Risk**: Poke integration issues. **Mitigation**: Test with webhook (https://poke.com/api/v1/inbound-sms/webhook); email hi@interaction.co for bouncer issues.
- **Risk**: Notification spam. **Mitigation**: Enforce opt-in, 3/day limit, clear decline messages.
- **Risk**: Redis setup. **Mitigation**: Use local Redis for dev; Render add-on for prod.
- **Risk**: Hand evaluation complexity. **Mitigation**: Use simplified ranking (pair vs. high card); add full logic post-submission.

## Appendix
- **Resources**:
  - Poke Integration: https://poke.com/settings/connections/integrations/new
  - MCP Template: https://github.com/InteractionCo/mcp-server-template
  - Submission: https://interaction.co/HackMIT
  - MCP Docs: modelcontextprotocol.io
- **Next Steps**:
  - Paste into Cursor AI: “Implement this MCP server code for Poke-R.”
  - Fork template, deploy to Render, test with Poke API.
  - Test edge cases (invalid bets, timeouts).
  - Record 30-second WhatsApp demo (2-player bluffing duel).
  - Submit before 11:15 AM EDT with repo, video, README.
- **Contact**: Email hi@interaction.co for Poke issues or visit HackMIT booth.