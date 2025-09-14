# 🎨 Colorful Emoji Card Guide

## 🃏 **Card Suit Colors**

### **Red Suits** (Hearts & Diamonds)
- ♥️ = Hearts
- ♦️ = Diamonds

### **Black Suits** (Clubs & Spades)
- ♣️ = Clubs
- ♠️ = Spades

## 🎯 **Paula's Current Hand**

**Original Codes**: `['2C', 'TD', '4H', '7S', 'TC']`

**With Colorful Emojis**:
1. **2♣️** - 2 of Clubs (Black)
2. **10♦️** - 10 of Diamonds (Red)
3. **4♥️** - 4 of Hearts (Red)
4. **7♠️** - 7 of Spades (Black)
5. **10♣️** - 10 of Clubs (Black)

## 🎲 **How to Read Cards**

### **Rank** (Number/Letter)
- **2-9**: Number cards
- **T**: Ten (10)
- **J**: Jack
- **Q**: Queen
- **K**: King
- **A**: Ace

### **Suit** (Color)
- **Red**: ♥️♦️ (Hearts & Diamonds)
- **Black**: ♣️♠️ (Clubs & Spades)

## 🎯 **Paula's Hand Analysis**

**Hand**: `['2C', 'TD', '4H', '7S', 'TC']`
- **Pair of 10s**: Two 10s (TD, TC)
- **Suits**: 2♣️, 10♦️, 4♥️, 7♠️, 10♣️
- **Colors**: Black, Red, Red, Black, Black
- **Strength**: Medium hand (pair)

## 🎮 **Commands for Paula**

### **Check Hand** (with emojis when server updates):
```
get_my_hand(game_id="poker_2a9d62ad", player="Paula Stolk")
```

### **Make Move**:
```
place_bet(game_id="poker_2a9d62ad", player="Paula Stolk", action="bet", amount=10)
```

---

**Note**: The server is currently showing card codes (`2C`, `TD`, etc.) but will soon display colorful emojis (`2♣️`, `10♦️`, etc.) for better visual distinction! 🎨✨
