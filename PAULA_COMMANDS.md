# 🎲 Paula's Poker Commands

## Current Game: `poker_2a9d62ad`

### 🔍 **Check Your Hand**
```
get_my_hand(game_id="poker_2a9d62ad", player="Paula Stolk")
```

### 🎯 **Your Current Hand**
- **2♣️** (2 of Clubs - Black)
- **10♦️** (10 of Diamonds - Red)
- **4♥️** (4 of Hearts - Red)
- **7♠️** (7 of Spades - Black)
- **10♣️** (10 of Clubs - Black)

**You have a Pair of 10s!** 🎯
**Red suits: ♥️♦️ | Black suits: ♣️♠️**

### 🎮 **Available Actions**

#### **When it's your turn:**

**Bet 10 chips:**
```
place_bet(game_id="poker_2a9d62ad", player="Paula Stolk", action="bet", amount=10)
```

**Call (match Ruben's bet):**
```
place_bet(game_id="poker_2a9d62ad", player="Paula Stolk", action="call")
```

**Raise to 20 chips:**
```
place_bet(game_id="poker_2a9d62ad", player="Paula Stolk", action="raise", amount=20)
```

**Fold (give up):**
```
place_bet(game_id="poker_2a9d62ad", player="Paula Stolk", action="fold")
```

#### **During draw phase:**

**Discard cards 1 and 3 (replace them):**
```
discard_cards(game_id="poker_2a9d62ad", player="Paula Stolk", indices=[1, 3])
```

### 📊 **Check Game Status**
```
get_game_status(game_id="poker_2a9d62ad")
```

### 🎯 **Strategy Tips**

- **You have a pair of 10s** - this is a decent hand!
- **Ruben has a pair of 5s** - you're currently winning!
- **Consider betting** to build the pot
- **Don't fold** unless Ruben raises significantly

### 🎲 **Quick Start**

1. **Check your hand**: `get_my_hand(game_id="poker_2a9d62ad", player="Paula Stolk")`
2. **Make your move**: `place_bet(game_id="poker_2a9d62ad", player="Paula Stolk", action="bet", amount=10)`
3. **Wait for Ruben's turn**

---

**Ready to play? You're currently winning with your pair of 10s!** 🎲✨
