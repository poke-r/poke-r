# 🎯 Agent Instructions: How to Start Poke-R Games

## ✅ CONFIRMED: `register_player_tool` IS AVAILABLE

The agent **DOES** have access to `register_player_tool`. Here's the proof:

### Current Available Tools:
1. **register_player_tool** ← **THIS IS THE KEY TOOL!**
2. start_poker
3. place_bet
4. discard_cards
5. toggle_availability
6. set_schedule
7. accept_invite
8. get_game_status
9. get_server_info

## 🎲 Required Workflow for Starting Games

### Step 1: Register Players (REQUIRED FIRST!)
```json
{
  "name": "register_player_tool",
  "arguments": {
    "phone": "+31646118037",
    "name": "Ruben Stolk"
  }
}
```

```json
{
  "name": "register_player_tool",
  "arguments": {
    "phone": "+31645226133",
    "name": "Paula Stolk"
  }
}
```

### Step 2: Enable Availability
```json
{
  "name": "toggle_availability",
  "arguments": {
    "phone": "+31646118037"
  }
}
```

```json
{
  "name": "toggle_availability",
  "arguments": {
    "phone": "+31645226133"
  }
}
```

### Step 3: Start Poker Game
```json
{
  "name": "start_poker",
  "arguments": {
    "players": ["Ruben Stolk", "Paula Stolk"]
  }
}
```

## 🔧 Key Points

1. **Registration is MANDATORY** - Players must be registered before starting games
2. **Phone numbers are primary keys** - Use phone numbers for registration and availability
3. **Names are aliases** - Use names in game creation after registration
4. **Availability must be enabled** - Toggle availability after registration

## ❌ Common Mistakes

- ❌ Trying to start games without registration
- ❌ Using phone numbers in `start_poker` (use names after registration)
- ❌ Forgetting to enable availability after registration

## ✅ Success Pattern

1. Register both players with `register_player_tool`
2. Enable availability for both players with `toggle_availability`
3. Start game with `start_poker` using names
4. Game will start successfully!

---

**The agent should refresh its tools list and look for `register_player_tool` - it's definitely there!**
