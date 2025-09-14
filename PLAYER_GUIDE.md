# 🎲 Poke-R Player Guide

## How to Play Poker on Poke-R

### 🎯 **Getting Started**

1. **Register Yourself** (if not already done):
   ```
   register_player_tool(phone="+31645226133", name="Paula Stolk")
   ```

2. **Enable Availability**:
   ```
   toggle_availability(phone="+31645226133")
   ```

### 🎮 **During a Game**

#### **Check Your Hand**
To see your cards, use:
```
get_my_hand(game_id="poker_2a9d62ad", player="Your Name")
```

**Response will show:**
- Your hand (your 5 cards with colorful emojis)
- Your current chips
- Who's turn it is
- Current game phase
- Pot size

**Card Colors:**
- ♥️♦️ = Red suits (Hearts & Diamonds)
- ♣️♠️ = Black suits (Clubs & Spades)

#### **Make Your Move**
When it's your turn, you can:

**Bet** (place initial bet):
```
place_bet(game_id="poker_2a9d62ad", player="Your Name", action="bet", amount=10)
```

**Call** (match opponent's bet):
```
place_bet(game_id="poker_2a9d62ad", player="Your Name", action="call")
```

**Raise** (increase the bet):
```
place_bet(game_id="poker_2a9d62ad", player="Your Name", action="raise", amount=20)
```

**Fold** (give up the hand):
```
place_bet(game_id="poker_2a9d62ad", player="Your Name", action="fold")
```

#### **Discard Cards** (during draw phase)
If you want to replace some cards:
```
discard_cards(game_id="poker_2a9d62ad", player="Your Name", indices=[1, 3])
```
*Note: indices are 1-5, representing card positions*

#### **Check Game Status**
To see current game state:
```
get_game_status(game_id="poker_2a9d62ad")
```

### 🎯 **Current Game Example**

**Game ID**: `poker_2a9d62ad`
**Players**: Ruben Stolk vs Paula Stolk
**Current Phase**: First betting round
**Current Player**: Ruben Stolk (his turn to bet)

**Paula's Hand**: `['2C', 'TD', '4H', '7S', 'TC']` (Pair of 10s)
**Ruben's Hand**: `['3C', '4D', '5S', 'AH', '5D']` (Pair of 5s)

### 🔒 **Privacy Notes**

- ✅ You can only see your own hand
- ✅ You cannot see opponent's cards
- ✅ Game status doesn't reveal hands
- ✅ This maintains poker strategy and bluffing

### 🎲 **Game Flow**

1. **First Betting Round**: Both players bet/call/raise/fold
2. **Draw Phase**: Players can discard up to 3 cards
3. **Second Betting Round**: Final betting round
4. **Showdown**: Compare hands, winner takes pot
5. **Next Hand**: Repeat until 5 hands completed

### 🏆 **Hand Rankings** (strongest to weakest)

1. **Royal Flush**: A, K, Q, J, 10 (same suit)
2. **Straight Flush**: 5 consecutive cards (same suit)
3. **Four of a Kind**: 4 cards of same rank
4. **Full House**: 3 of a kind + pair
5. **Flush**: 5 cards of same suit
6. **Straight**: 5 consecutive cards
7. **Three of a Kind**: 3 cards of same rank
8. **Two Pair**: 2 different pairs
9. **Pair**: 2 cards of same rank
10. **High Card**: Highest single card

---

**Ready to play? Use `get_my_hand` to see your cards and start betting!** 🎲✨
