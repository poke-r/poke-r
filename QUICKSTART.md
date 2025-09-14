# Poke-R Quick Start Guide

Get started with Poke-R poker games in under 5 minutes!

## What is Poke-R?

Poke-R is a 2-player Five-Card Draw poker game that runs entirely in your chat apps (iMessage, WhatsApp, etc.) through Poke's AI assistant. No apps to download, no accounts to create - just pure poker fun with friends!

## How to Play

### 1. Start a Game
Send this message to Poke:
```
Poke, start Poke-R with @friend
```

### 2. Play Poker
- **Cards**: Sent privately via DM
- **Betting**: "Poke, bet 10" / "call" / "raise 20" / "fold"
- **Discard**: "Poke, discard 1,3" (up to 3 cards)
- **Side Bets**: "Poke, side bet 10 on pair+"

### 3. Win!
- Best hand wins the pot
- Play 3-5 hands per game
- Most chips wins overall

## Game Commands

| Command | Description | Example |
|---------|-------------|---------|
| `start Poke-R with @player` | Start new game | `Poke, start Poke-R with @alice` |
| `bet [amount]` | Place bet | `Poke, bet 15` |
| `call` | Match opponent's bet | `Poke, call` |
| `raise [amount]` | Raise the bet | `Poke, raise 25` |
| `fold` | Give up hand | `Poke, fold` |
| `discard [cards]` | Discard cards | `Poke, discard 1,3,5` |
| `side bet [amount] on [type]` | Place side bet | `Poke, side bet 10 on pair+` |

## Privacy Controls

### Availability Settings
```
Poke, toggle Poke-R availability
Poke, set Poke-R hours 19:00-22:00, Mon-Fri
```

### Invite Management
- All invites require explicit acceptance
- 10-minute timeout on invites
- Block/mute options available

## Hand Rankings

From strongest to weakest:
1. **Royal Flush** - A, K, Q, J, 10 (same suit)
2. **Straight Flush** - Five cards in sequence (same suit)
3. **Four of a Kind** - Four cards of same rank
4. **Full House** - Three of a kind + pair
5. **Flush** - Five cards of same suit
6. **Straight** - Five cards in sequence
7. **Three of a Kind** - Three cards of same rank
8. **Two Pair** - Two different pairs
9. **Pair** - Two cards of same rank
10. **High Card** - Highest card wins

## Tips for Success

### Betting Strategy
- **Bluffing**: Use raises to represent strong hands
- **Position**: Act after opponent to gain information
- **Pot Odds**: Consider pot size vs. bet amount
- **Side Bets**: Add extra excitement and chips

### Card Management
- **Discard Wisely**: Keep cards that work together
- **Draw Strategy**: Aim for straights, flushes, or pairs
- **Read Opponent**: Watch betting patterns

### Privacy
- **Set Hours**: Control when you can receive invites
- **Accept Selectively**: Only join games you want to play
- **Use Mute**: Temporarily disable notifications

## Troubleshooting

### Common Issues

**"Player unavailable"**
- Player hasn't enabled Poke-R availability
- Player is outside their scheduled hours
- Player has blocked Poke-R notifications

**"Game not found"**
- Game expired (1-hour timeout)
- Wrong game ID
- Server restart

**"Not your turn"**
- Wait for opponent's action
- Check current player in game status

### Getting Help

1. **Check Game Status**: Ask Poke for current game state
2. **Restart Game**: Start a new game if issues persist
3. **Clear History**: Send `clearhistory` to Poke if integration issues
4. **Contact Support**: Email hi@interaction.co for Poke integration help

## Advanced Features

### Side Bets
Place bets on hand outcomes:
- `pair+` - Win with pair or better
- `flush+` - Win with flush or better
- `straight+` - Win with straight or better

### Scheduling
Set specific availability windows:
- `19:00-22:00, Mon-Fri` - Weekday evenings
- `12:00-14:00, Sat-Sun` - Weekend lunch
- `20:00-23:00, Fri-Sun` - Weekend nights

### Game Management
- **Status Check**: Get current game information
- **Invite Acceptance**: Respond to game invites
- **Availability Toggle**: Enable/disable Poke-R

## Example Game Flow

```
Alice: "Poke, start Poke-R with @bob"
Poke: "🎲 Poke-R duel started! Cards sent via DM. Alice, bet first (min 5): bet/call/raise/fold."

Alice: "Poke, bet 10"
Poke: "Alice bets 10! Bob, your move: bet/call/raise/fold."

Bob: "Poke, call"
Poke: "Bets matched! Alice, discard up to 3 cards: 'Poke, discard [indices]'."

Alice: "Poke, discard 1,3"
Poke: "New cards dealt to Alice. Bob, bet (min 5): bet/call/raise/fold."

Bob: "Poke, bet 15"
Alice: "Poke, call"
Poke: "Showdown! Alice wins 25 chips with flush! Next hand starting..."
```

## Ready to Play?

1. **Enable Poke-R**: `Poke, toggle Poke-R availability`
2. **Find a Friend**: Someone else with Poke-R enabled
3. **Start Playing**: `Poke, start Poke-R with @friend`
4. **Have Fun**: Bluff, bet, and win!

---

**Need help?** Check the [Deployment Guide](DEPLOYMENT.md) for technical setup or contact support at hi@interaction.co
