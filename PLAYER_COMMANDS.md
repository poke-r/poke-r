# 🎲 Player Poker Commands

## Current Game: `poker_2a9d62ad`

### 🔍 **Check Your Hand**
```
get_my_hand(game_id="poker_2a9d62ad", player="Your Name")
```

### 🎯 **Example Hand**
- **2♣️** (2 of Clubs - Black)
- **10♦️** (10 of Diamonds - Red) 
- **4♥️** (4 of Hearts - Red)
- **7♠️** (7 of Spades - Black)
- **10♣️** (10 of Clubs - Black)

**This would be a Pair of 10s!** 🎯
**Red suits: ♥️♦️ | Black suits: ♣️♠️**

### 🎮 **Available Actions**

#### **When it's your turn:**

**Bet 10 chips:**
```
place_bet(game_id="poker_2a9d62ad", player="Your Name", action="bet", amount=10)
```

**Call (match opponent's bet):**
```
place_bet(game_id="poker_2a9d62ad", player="Your Name", action="call")
```

**Raise to 20 chips:**
```
place_bet(game_id="poker_2a9d62ad", player="Your Name", action="raise", amount=20)
```

**Fold (give up):**
```
place_bet(game_id="poker_2a9d62ad", player="Your Name", action="fold")
```

#### **During draw phase:**

**Discard cards 1 and 3 (replace them):**
```
discard_cards(game_id="poker_2a9d62ad", player="Your Name", indices=[1, 3])
```

### 📊 **Check Game Status**
```
get_game_status(game_id="poker_2a9d62ad")
```

### 🎯 **Strategy Tips**

- **Pairs are decent hands** - consider betting to build the pot
- **Watch your opponent's betting patterns** - are they aggressive or conservative?
- **Don't fold too easily** unless opponent raises significantly
- **Manage your chips** - don't bet more than you can afford to lose

### 🎲 **Quick Start**

1. **Check your hand**: `get_my_hand(game_id="poker_2a9d62ad", player="Your Name")`
2. **Make your move**: `place_bet(game_id="poker_2a9d62ad", player="Your Name", action="bet", amount=10)`
3. **Wait for opponent's turn**

---

**Ready to play? Check your hand and make your move!** 🎲✨
