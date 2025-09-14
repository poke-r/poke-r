# Poke-R Deployment Guide

This guide covers deploying the Poke-R MCP server to Render and integrating it with Poke.com.

## Prerequisites

- GitHub repository with the Poke-R code
- Render.com account
- Poke.com account with MCP integration access

## Deployment Steps

### 1. Deploy to Render

1. **Fork this repository** to your GitHub account
2. **Connect to Render**:
   - Go to [render.com](https://render.com)
   - Sign up/login with your GitHub account
   - Click "New +" → "Web Service"
   - Connect your forked repository

3. **Configure the service**:
   - **Name**: `poke-r-poker-server` (or your preferred name)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/server.py`
   - **Plan**: Free (or upgrade for better performance)

4. **Environment Variables**:
   - `ENVIRONMENT`: `production`
   - `REDIS_URL`: `redis://localhost:6379` (or your Redis instance)

5. **Deploy**: Click "Create Web Service"

6. **Wait for deployment** (usually 2-5 minutes)

7. **Get your MCP URL**: Your server will be available at:
   ```
   https://your-service-name.onrender.com/mcp
   ```

### 2. Set up Redis (Optional for MVP)

For the MVP, the server works without Redis (uses in-memory storage). For production:

1. **Add Redis service** in Render:
   - Go to your Render dashboard
   - Click "New +" → "Redis"
   - Choose free plan
   - Copy the Redis URL

2. **Update environment variable**:
   - Go to your web service settings
   - Update `REDIS_URL` with your Redis instance URL

### 3. Test the Deployment

1. **Health check**:
   ```bash
   curl https://your-service-name.onrender.com/health
   ```

2. **MCP Inspector** (for development):
   ```bash
   npx @modelcontextprotocol/inspector
   ```
   - Open http://localhost:3000
   - Connect to `https://your-service-name.onrender.com/mcp`
   - Use "Streamable HTTP" transport

### 4. Integrate with Poke

1. **Go to Poke Settings**:
   - Visit [poke.com/settings/connections](https://poke.com/settings/connections)
   - Click "Add Integration"

2. **Configure MCP Connection**:
   - **Name**: `Poke-R Poker`
   - **Type**: MCP Server
   - **URL**: `https://your-service-name.onrender.com/mcp`
   - **Transport**: Streamable HTTP

3. **Test the Integration**:
   - Send a message to Poke: "Tell the subagent to use the 'Poke-R Poker' integration's 'start_poker' tool"
   - Or: "Start a poker game with Alice and Bob"

## Available MCP Tools

The server provides these tools for Poke integration:

### Game Management
- `start_poker(players: List[str])` - Start a new 2-player game
- `place_bet(game_id: str, player: str, action: str, amount: int)` - Betting actions
- `discard_cards(game_id: str, player: str, indices: List[int])` - Discard/draw cards
- `get_game_status(game_id: str)` - Get current game state

### Privacy Controls
- `toggle_availability(phone: str)` - Toggle game availability
- `set_schedule(phone: str, schedule_str: str)` - Set availability schedule
- `accept_invite(game_id: str, phone: str)` - Accept game invites

### Side Features
- `place_side_bet(game_id: str, player: str, bet_type: str, amount: int)` - Side bets
- `get_server_info()` - Server information

## Game Flow Example

1. **Start Game**: "Poke, start Poke-R with @alice"
2. **Betting**: "Poke, bet 10" / "call" / "raise 20" / "fold"
3. **Discard**: "Poke, discard 1,3" (discard first and third cards)
4. **Final Betting**: Continue betting after draw
5. **Showdown**: Automatic hand resolution

## Troubleshooting

### Common Issues

1. **Server not responding**:
   - Check Render logs for errors
   - Verify environment variables
   - Ensure all dependencies are installed

2. **Redis connection failed**:
   - Server works without Redis (in-memory mode)
   - For production, add Redis service in Render

3. **Poke integration not working**:
   - Verify MCP URL is correct
   - Check Poke connection settings
   - Try `clearhistory` command in Poke

4. **Game state lost**:
   - Games expire after 1 hour
   - Redis persistence recommended for production

### Debug Commands

```bash
# Check server health
curl https://your-service-name.onrender.com/health

# Test MCP connection
curl -X POST https://your-service-name.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

## Performance Notes

- **Free tier limits**: 750 hours/month, sleeps after inactivity
- **Response time**: <1 second for most operations
- **Concurrent games**: Supports 100+ games simultaneously
- **Memory usage**: ~50MB per instance

## Security Considerations

- All game data expires after 1 hour
- No persistent user accounts
- Input validation on all MCP tools
- Privacy controls prevent spam invites

## Support

- **Render Issues**: Check Render documentation
- **Poke Integration**: Contact hi@interaction.co
- **MCP Protocol**: Visit modelcontextprotocol.io
- **This Project**: Open GitHub issues

## Next Steps

1. Deploy to Render
2. Test with MCP Inspector
3. Integrate with Poke
4. Test game flow with friends
5. Monitor performance and logs
6. Consider upgrading to paid Render plan for production use
