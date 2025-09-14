# Poke-R: MCP-Powered 2-Player Poker Game

**Poke-R** is a head-to-head poker duel where two players play Five-Card Draw in chat. Each gets 5 private cards (via Poke DMs), bets, discards/draws up to 3 cards, bets again, and reveals hands. Players start with 100 chips, bluffing and strategizing over 3-5 hands (5-10 minutes). Poke parses commands (e.g., "Poke, raise 20") and calls an MCP server to manage state and resolve hands (e.g., "Alice's flush beats Bob's pair!"). Human psychology drives thousands of outcomes per game, keeping AI at bay. Privacy toggles ensure opt-in play, making it spam-free.

**Key Value Proposition**: Intense, bluff-heavy poker duels in your chats—no apps, human-driven, spam-free.

**Target Users**: Casual gamers, buddies on iMessage/WhatsApp, Poke beta testers, HackMIT participants.

## Features

### Core Gameplay
- **2-Player Five-Card Draw**: Deal, bet, discard/draw, resolve hands
- **Virtual Chips**: Start with 100 chips each, bet strategically
- **Bluffing Mechanics**: Side bets, psychological gameplay
- **Async Play**: 2-minute turn timers for chat environments
- **Private Cards**: Cards sent via Poke DMs for privacy

### Privacy Controls
- **Availability Toggle**: Control when you can receive game invites
- **Scheduled Availability**: Set specific hours (e.g., "19:00-22:00, Mon-Fri")
- **Consent-Based Invites**: Explicit accept/decline for all invites
- **Mute/Block Options**: Temporary or permanent notification controls

### Game Commands
- `Poke, start Poke-R with [buddy]` - Start a new game
- `Poke, bet 10` / `call` / `raise 20` / `fold` - Betting actions
- `Poke, discard 1,3` - Discard cards (up to 3)
- `Poke, side bet 10 on pair+` - Optional side bets
- `Poke, toggle Poke-R availability` - Privacy controls

## Technical Architecture

- **Client**: Poke (parses commands, DMs cards, renders results)
- **Backend**: MCP Server (Python + FastMCP)
- **Storage**: Redis (game state, hands, chips, user settings)
- **Deployment**: Render (free tier)

## Local Development

### Setup

```bash
git clone <your-repo-url>
cd poke-r
conda create -n poke-r python=3.13
conda activate poke-r
pip install -r requirements.txt
```

### Test

```bash
python src/server.py
# then in another terminal run:
npx @modelcontextprotocol/inspector
```

Open http://localhost:3000 and connect to `http://localhost:8000/mcp` using "Streamable HTTP" transport.

## Deployment

### Option 1: One-Click Deploy
Click the "Deploy to Render" button above.

### Option 2: Manual Deployment
1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Web Service on Render
4. Connect your forked repository
5. Render will automatically detect the `render.yaml` configuration

Your server will be available at `https://your-service-name.onrender.com/mcp`

## Poke Integration

Connect your MCP server to Poke at [poke.com/settings/connections](https://poke.com/settings/connections).

To test the connection explicitly, ask Poke something like: `Tell the subagent to use the "Poke-R" integration's "start_poker" tool`.

If you run into persistent issues with Poke not calling the right MCP (e.g., after renaming the connection), you may send `clearhistory` to Poke to delete all message history and start fresh.

## Success Metrics

- Deployable MVP with core poker mechanics
- 100 concurrent games, <1s response time
- Zero spam complaints
- Privacy-first design with opt-in controls

## Implementation Status

- ✅ Core poker game logic
- ✅ MCP tools for game operations
- ✅ Privacy controls and availability management
- ✅ Redis state management
- ✅ Render deployment configuration
- 🔄 Poke integration testing
