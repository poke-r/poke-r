# 📊 Comprehensive Logging Guide

## Overview

The Poke-R server now includes detailed logging throughout the application to help debug issues and monitor Poke API integration. All logs are written to both console and file (`poke-r-server.log`).

## 🔧 Logging Configuration

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),      # Console output
        logging.FileHandler('poke-r-server.log')  # File output
    ]
)
```

## 📋 Log Categories

### 🚀 Server Startup
```
🚀 Starting Poke-R MCP server on 0.0.0.0:8000
🔧 Environment variables - POKE_API_URL=https://poke.com/api, POKE_API_KEY=***
📊 Logging configured - level=INFO, handlers=console+file
```

### 🎲 Game Functions

#### Start Poker Game
```
🎲 START_POKER called - players=['Ruben Stolk', 'Paula Stolk']
📢 About to notify first player - player=Ruben Stolk (+31646118037), message='🎲 Poke-R game started! Your turn to bet first. Check your hand and make your move!'
```

#### Place Bet
```
🎲 PLACE_BET called - game_id=poker_12345678, player=Ruben Stolk, action=bet, amount=10
🎮 Game state - current_player=Ruben Stolk, phase=bet1, pot=0
🎯 Betting details - opponent=+31645226133, current_bet=0, player_bet=0
🔄 Switching turns - from Ruben Stolk to +31645226133
📢 About to notify opponent - opponent=Paula Stolk (+31645226133), message='🎲 Your turn in Poke-R! Ruben Stolk made their move. Check your hand and make your bet!'
```

#### Discard Cards
```
🎲 DISCARD_CARDS called - game_id=poker_12345678, player=Paula Stolk, indices=[1, 3]
🎮 Game state - phase=draw, current_player=Paula Stolk
📢 About to notify other player for second betting round - player=Ruben Stolk (+31646118037), message='🎲 Second betting round! Paula Stolk drew cards. Your turn to bet!'
```

### 🔔 Poke API Notifications

#### Successful Notification
```
🔔 NOTIFY_PLAYER_TURN called - game_id=poker_12345678, player=Paula Stolk (+31645226133), message='🎲 Your turn in Poke-R! Ruben Stolk made their move. Check your hand and make your bet!'
🔧 Poke API config - URL=https://poke.com/api, API_KEY=***
📤 Sending Poke API notification - URL=https://poke.com/api/notify, payload={"phone": "+31645226133", "message": "🎲 Your turn in Poke-R! Ruben Stolk made their move. Check your hand and make your bet!", "game_id": "poker_12345678", "game_type": "poker", "action": "your_turn"}
📥 Poke API response - status_code=200, headers={'content-type': 'application/json', 'content-length': '25'}
✅ Successfully notified Paula Stolk (+31645226133) - 🎲 Your turn in Poke-R! Ruben Stolk made their move. Check your hand and make your bet!
📱 Response body: {"status": "sent"}
```

#### Missing API Key
```
🔔 NOTIFY_PLAYER_TURN called - game_id=poker_12345678, player=Paula Stolk (+31645226133), message='🎲 Your turn in Poke-R! Ruben Stolk made their move. Check your hand and make your bet!'
🔧 Poke API config - URL=https://poke.com/api, API_KEY=NOT_SET
⚠️ POKE_API_KEY not set - skipping notification to Paula Stolk
```

#### API Error
```
🔔 NOTIFY_PLAYER_TURN called - game_id=poker_12345678, player=Paula Stolk (+31645226133), message='🎲 Your turn in Poke-R! Ruben Stolk made their move. Check your hand and make your bet!'
🔧 Poke API config - URL=https://poke.com/api, API_KEY=***
📤 Sending Poke API notification - URL=https://poke.com/api/notify, payload={"phone": "+31645226133", "message": "🎲 Your turn in Poke-R! Ruben Stolk made their move. Check your hand and make your bet!", "game_id": "poker_12345678", "game_type": "poker", "action": "your_turn"}
📥 Poke API response - status_code=401, headers={'content-type': 'application/json'}
⚠️ Failed to notify Paula Stolk (+31645226133): 401 - {"error": "Invalid API key"}
```

### ❌ Error Logging

#### Function Errors
```
❌ Game not found or expired - game_id=poker_12345678
⚠️ Not player's turn - player=Paula Stolk, current_player=Ruben Stolk
❌ Invalid action - action=invalid_action
```

#### Exception Logging
```
❌ Error notifying Paula Stolk (+31645226133): Connection timeout
❌ Traceback: Traceback (most recent call last):
  File "server.py", line 96, in notify_player_turn
    response = requests.post(...)
  requests.exceptions.Timeout: Connection timeout
```

## 🔍 Debugging Checklist

### 1. Check Server Startup
Look for:
- ✅ `🚀 Starting Poke-R MCP server`
- ✅ `🔧 Environment variables - POKE_API_KEY=***` (not NOT_SET)

### 2. Check Game Flow
Look for:
- ✅ `🎲 START_POKER called`
- ✅ `📢 About to notify first player`
- ✅ `🎲 PLACE_BET called`
- ✅ `🔄 Switching turns`

### 3. Check Poke API Calls
Look for:
- ✅ `🔔 NOTIFY_PLAYER_TURN called`
- ✅ `📤 Sending Poke API notification`
- ✅ `📥 Poke API response - status_code=200`

### 4. Common Issues

#### No Poke API Calls
- Check: `⚠️ POKE_API_KEY not set`
- Solution: Set `POKE_API_KEY` environment variable

#### API Calls Failing
- Check: `⚠️ Failed to notify` with error details
- Check: `📥 Poke API response - status_code=XXX`
- Solution: Verify API key and endpoint

#### Game Flow Issues
- Check: `⚠️ Not player's turn`
- Check: `❌ Game not found or expired`
- Solution: Verify game state and player registration

## 📁 Log Files

- **Console**: Real-time output in terminal
- **File**: `poke-r-server.log` in server directory
- **Format**: `YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message`

## 🎯 Key Log Messages to Watch

1. **Game Start**: `🎲 START_POKER called`
2. **Turn Switch**: `🔄 Switching turns`
3. **Notification**: `🔔 NOTIFY_PLAYER_TURN called`
4. **API Call**: `📤 Sending Poke API notification`
5. **API Response**: `📥 Poke API response - status_code=200`

With this comprehensive logging, you can now see exactly what's happening in the server and debug any issues with the Poke API integration! 🔍✨
