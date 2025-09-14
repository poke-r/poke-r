# 🎲 Poke API Integration

## Overview

The Poke-R poker server now automatically notifies players via the Poke API when it's their turn to make a move. This creates a seamless gaming experience where players don't need to constantly check for updates.

## 🔧 Configuration

### Environment Variables

Set these environment variables in your deployment:

```bash
POKE_API_URL=https://poke.com/api  # Default Poke API endpoint
POKE_API_KEY=your_api_key_here     # Required for authentication
```

### Authentication

The server uses Bearer token authentication:
```
Authorization: Bearer {POKE_API_KEY}
```

## 📱 Notification Triggers

### 1. Game Start
When a poker game begins, the first player receives a notification:
```json
{
  "phone": "+31646118037",
  "message": "🎲 Poke-R game started! Your turn to bet first. Check your hand and make your move!",
  "game_id": "poker_2a9d62ad",
  "game_type": "poker",
  "action": "your_turn"
}
```

### 2. Turn Switches
After each player makes a move, the opponent is notified:
```json
{
  "phone": "+31645226133",
  "message": "🎲 Your turn in Poke-R! Ruben Stolk made their move. Check your hand and make your bet!",
  "game_id": "poker_2a9d62ad",
  "game_type": "poker",
  "action": "your_turn"
}
```

### 3. Second Betting Round
After the draw phase, the other player is notified:
```json
{
  "phone": "+31646118037",
  "message": "🎲 Second betting round! Paula Stolk drew cards. Your turn to bet!",
  "game_id": "poker_2a9d62ad",
  "game_type": "poker",
  "action": "your_turn"
}
```

## 🎯 Notification Flow

```
Game Start → Notify Player 1
    ↓
Player 1 Bet → Notify Player 2
    ↓
Player 2 Call → Notify Player 1
    ↓
Draw Phase → Notify Player 2
    ↓
Player 2 Bet → Notify Player 1
    ↓
Player 1 Call → Showdown
```

## 🛡️ Error Handling

- **Missing API Key**: Notifications are skipped with a warning
- **API Failures**: Game continues normally, errors are logged
- **Network Issues**: Timeout after 10 seconds, game continues
- **Invalid Responses**: Detailed error logging for debugging

## 📊 Monitoring

The server logs all notification attempts:
- ✅ Successful notifications
- ⚠️ Failed notifications with status codes
- ❌ Network/API errors

## 🧪 Testing

Use the test script to verify integration:
```bash
python test_poke_integration.py
```

This will:
1. Register players
2. Start a poker game
3. Make moves to trigger notifications
4. Verify notification flow

## 🔗 API Endpoint

**POST** `{POKE_API_URL}/notify`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {POKE_API_KEY}
```

**Payload:**
```json
{
  "phone": "string",
  "message": "string",
  "game_id": "string",
  "game_type": "poker",
  "action": "your_turn"
}
```

## 🎮 Player Experience

With Poke API integration, players can:
- ✅ Receive instant notifications when it's their turn
- ✅ Play without constantly checking the game status
- ✅ Get context about what happened (opponent's move)
- ✅ Know which phase of the game they're in

This creates a much more engaging and seamless poker experience! 🎲✨
