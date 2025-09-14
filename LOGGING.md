# Poke-R Comprehensive Logging System

## 🎯 Overview

The Poke-R server now includes a comprehensive logging system that provides detailed visibility into all operations, even in production mode. This logging system is designed for debugging, monitoring, and troubleshooting poker games and MCP operations.

## 🔧 Logging Configuration

### Log Levels
- **INFO**: General operations, game flow, player actions
- **DEBUG**: Detailed state information, validation steps
- **WARNING**: Non-critical issues, validation failures
- **ERROR**: Critical errors with full tracebacks

### Log Format
```
2025-09-14 11:00:02,889 - Poke-R - INFO - 🚀 Starting Poke-R MCP server...
```

### Output Destinations
- **Console**: Real-time output for development and production
- **File**: `poke-r.log` (when writable directory available)
- **Production**: All logs visible in Render deployment logs

## 🎮 Game Operation Logging

### Game Creation
```
🎮 Starting new poker game with players: ['Alice', 'Bob']
🔍 Checking player availability...
✅ Player Alice is available
✅ Player Bob is available
🆔 Generated game ID: poker_a1b2c3d4
🃏 Deck shuffled: 52 cards
🎯 Dealt hands: Alice=['2H', '7D', 'JC', 'QS', 'AH'], Bob=['3C', '8S', 'KD', 'TH', '9H']
📊 Game state initialized: Phase=bet1, Current Player=Alice
💾 Saving game state for ID: poker_a1b2c3d4
✅ Game state saved successfully: 1234 bytes, expires in 1 hour
📨 Setting up pending invites...
🎉 Game poker_a1b2c3d4 started successfully!
```

### Betting Actions
```
🎯 Betting action: Alice -> bet (amount: 10) in game poker_a1b2c3d4
🎲 Game state: Phase=bet1, Current bet=0, Pot=0, Player chips=100
💰 bet validation: amount=10, min_bet=5, player_chips=100
💰 Alice bets 10 chips. New pot: 10, Player chips: 90
🔄 Turn switched to: Bob
✅ Betting action complete. Next turn: Bob
```

### Hand Evaluation
```
🏁 Showdown time! Comparing hands...
🎯 Hand comparison: Alice=['2H', '7D', 'JC', 'QS', 'AH'] vs Bob=['3C', '8S', 'KD', 'TH', '9H']
🏆 Alice wins with pair: ['2H', '7D', 'JC', 'QS', 'AH']
📊 Hand 1 complete. New hand: 2
🎲 Starting new hand...
🎯 New hands dealt: Alice=['KH', '4D', '8C', '2S', '6H'], Bob=['9S', 'QC', '5D', 'AH', '3H']
```

### Card Discarding
```
🔄 Discard action: Alice discarding cards at indices [1, 3] in game poker_a1b2c3d4
🎯 Original hand: ['KH', '4D', '8C', '2S', '6H']
🔄 Alice discarded: ['4D', '2S'], drew: ['7C', 'JD']
🎯 New hand: ['KH', '8C', '6H', '7C', 'JD']
🎯 Moving to bet2 phase. Next player: Bob
```

## 🔒 Privacy Control Logging

### Availability Management
```
🔧 Toggling availability for user: +1234567890
✅ Availability enabled for +1234567890
```

### Schedule Management
```
📅 Setting schedule for +1234567890: 19:00-22:00, Mon-Fri
🕐 Parsing times: 19:00 - 22:00
📅 Added day: Mon -> 1
📅 Added day: Fri -> 5
📅 Schedule parsed: {'windows': [{'start': '19:00', 'end': '22:00', 'days': [1, 5]}]}
✅ Schedule saved for +1234567890
```

### Availability Checks
```
🔍 Checking availability for user: +1234567890
📋 Availability status: True
📅 Checking schedule for user: +1234567890
🕐 Current time: 20:30:00, weekday: 1
🪟 Checking window: {'start': '19:00', 'end': '22:00', 'days': [1, 5]}
⏰ Window times: 19:00:00 - 22:00:00
✅ User +1234567890 is available (within scheduled window)
```

## 🗄️ State Management Logging

### Redis Operations
```
🔗 Attempting Redis connection to: redis://localhost:6379
✅ Redis connection successful
💾 Saving game state for ID: poker_a1b2c3d4
✅ Game state saved successfully: 1234 bytes, expires in 1 hour
🔍 Getting game state for ID: poker_a1b2c3d4
✅ Retrieved game state: 2 players, phase: bet1
```

### Fallback Operations
```
⚠️ Redis connection failed: Error 61 connecting to localhost:6379. Connection refused.
🔄 Falling back to in-memory storage
📝 Redis not available, returning None
📝 Redis not available, cannot save state
```

## 🚀 Server Lifecycle Logging

### Startup
```
🚀 Initializing Poke-R Poker Server
🔗 Attempting Redis connection to: redis://localhost:6379
⚠️ Redis connection failed: Error 61 connecting to localhost:6379. Connection refused.
🔄 Falling back to in-memory storage
🚀 Starting Poke-R MCP server...
🌐 Server configuration: 0.0.0.0:8000
🔗 Redis available: False
🌍 Environment: development
🐍 Python version: 3.13.5
🎮 Starting MCP server...
```

### Health Checks
```
🏥 Health check requested
🏥 Health check response: {'status': 'healthy', 'redis_available': False, 'server': 'Poke-R Poker Server', 'version': '1.0.0'}
```

### Server Info
```
ℹ️ Server info requested
ℹ️ Server info: {'server_name': 'Poke-R Poker Server', 'version': '1.0.0', 'environment': 'development', 'python_version': '3.13.5', 'redis_available': False}
```

## 🚨 Error Logging

### Validation Errors
```
❌ Invalid player count: 3 (expected 2)
❌ Wrong turn: Bob tried to act, but Alice is current player
❌ Invalid action: invalid_action
❌ Player Alice bet too low: 2 < 5
❌ Player Bob insufficient chips: 5 < 10
❌ Too many cards to discard: 4 > 3
❌ Invalid card indices: [0, 6] (must be 1-5)
```

### System Errors
```
💥 Error getting game state for poker_a1b2c3d4: Connection timeout
🔍 Traceback: Traceback (most recent call...)
💥 Error saving game state for poker_a1b2c3d4: Redis connection lost
💥 Server startup failed: Port 8000 already in use
```

## 📊 Log Analysis Examples

### Game Flow Tracking
```bash
# Track a complete game
grep "poker_a1b2c3d4" poke-r.log

# Track player actions
grep "Alice" poke-r.log | grep "🎯\|💰\|🔄"

# Track betting rounds
grep "Betting round complete" poke-r.log
```

### Error Monitoring
```bash
# Find all errors
grep "💥\|❌" poke-r.log

# Track Redis issues
grep "Redis" poke-r.log

# Monitor availability issues
grep "availability" poke-r.log
```

### Performance Monitoring
```bash
# Track game creation time
grep "🎮 Starting new poker game" poke-r.log

# Monitor state save operations
grep "💾 Saving game state" poke-r.log

# Track hand evaluations
grep "🏁 Showdown time" poke-r.log
```

## 🎯 Production Benefits

### Debugging
- **Complete game flow visibility** from start to finish
- **Player action tracking** with validation details
- **State management monitoring** with Redis operations
- **Error context** with full tracebacks

### Monitoring
- **Real-time game status** for all active games
- **Performance metrics** for betting and hand evaluation
- **Availability tracking** for privacy controls
- **System health** monitoring with Redis status

### Troubleshooting
- **Player issue diagnosis** with detailed action logs
- **Game state recovery** with complete state information
- **Integration debugging** with MCP tool call tracking
- **Performance optimization** with timing information

## 🔧 Log Customization

### Environment Variables
- `LOG_LEVEL`: Set minimum log level (DEBUG, INFO, WARNING, ERROR)
- `LOG_FILE`: Custom log file path
- `ENVIRONMENT`: Environment name for log context

### Production Considerations
- **Log rotation**: Implement log rotation for long-running servers
- **Log aggregation**: Use centralized logging for multiple instances
- **Alerting**: Set up alerts for ERROR level logs
- **Retention**: Configure log retention policies

## 📈 Monitoring Integration

### Render Deployment
- Logs automatically appear in Render dashboard
- Real-time log streaming available
- Log search and filtering capabilities
- Error alerting and notifications

### External Monitoring
- **Structured logging**: JSON format available for parsing
- **Metrics extraction**: Log parsing for performance metrics
- **Alert integration**: Error logs can trigger alerts
- **Dashboard integration**: Log data for monitoring dashboards

---

## 🎉 Summary

The comprehensive logging system provides complete visibility into Poke-R operations, making it easy to:

- **Debug issues** with detailed context and tracebacks
- **Monitor performance** with timing and state information
- **Track user behavior** with privacy and availability logging
- **Troubleshoot problems** with complete game flow visibility
- **Optimize performance** with detailed operation metrics

All logs are visible in production mode, ensuring full observability for deployed instances.
