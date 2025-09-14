#!/usr/bin/env python3
"""
Test Poke API integration for poker game notifications
"""
import requests
import json
import time

def test_poke_integration():
    """Test the Poke API integration with poker game notifications"""

    # Get session ID
    response = requests.head('https://fastmcp-server-z2pr.onrender.com/mcp', timeout=10)
    session_id = response.headers.get('mcp-session-id')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'mcp-session-id': session_id
    }

    def make_request(method, params=None, request_id=1):
        payload = {
            'jsonrpc': '2.0',
            'method': method
        }

        if not method.startswith('notifications/'):
            payload['id'] = request_id

        if params is not None:
            payload['params'] = params

        response = requests.post('https://fastmcp-server-z2pr.onrender.com/mcp',
                               headers=headers, json=payload, timeout=30)

        lines = response.text.strip().split('\n')
        for line in lines:
            if line.startswith('data: '):
                data = line[6:]
                try:
                    return json.loads(data)
                except:
                    continue
        return {'error': 'No valid response'}

    # Initialize MCP
    make_request('initialize', {
        'protocolVersion': '2025-06-18',
        'capabilities': {},
        'clientInfo': {'name': 'poke-integration-test', 'version': '1.0.0'}
    })
    make_request('notifications/initialized')

    print('🎲 TESTING POKE API INTEGRATION:')
    print('=' * 50)

    # Register players
    print('1. Registering players...')
    make_request('tools/call', {
        'name': 'register_player_tool',
        'arguments': {'phone': '+31646118037', 'name': 'Ruben Stolk'}
    }, 1)

    make_request('tools/call', {
        'name': 'register_player_tool',
        'arguments': {'phone': '+31645226133', 'name': 'Paula Stolk'}
    }, 2)

    # Enable availability
    print('2. Enabling availability...')
    make_request('tools/call', {
        'name': 'toggle_availability',
        'arguments': {'phone': '+31646118037'}
    }, 3)

    make_request('tools/call', {
        'name': 'toggle_availability',
        'arguments': {'phone': '+31645226133'}
    }, 4)

    # Start poker game (should trigger notification to Ruben)
    print('3. Starting poker game (should notify Ruben)...')
    result = make_request('tools/call', {
        'name': 'start_poker',
        'arguments': {'players': ['Ruben Stolk', 'Paula Stolk']}
    }, 5)

    content = result.get('result', {}).get('structuredContent', {})
    game_id = content.get('game_id')
    print(f'   Game ID: {game_id}')
    print(f'   Message: {content.get("message")}')
    print(f'   Current Player: {content.get("current_player")}')

    if game_id:
        # Ruben makes a bet (should trigger notification to Paula)
        print('\\n4. Ruben makes a bet (should notify Paula)...')
        result = make_request('tools/call', {
            'name': 'place_bet',
            'arguments': {
                'game_id': game_id,
                'player': 'Ruben Stolk',
                'action': 'bet',
                'amount': 10
            }
        }, 6)

        content = result.get('result', {}).get('structuredContent', {})
        print(f'   Message: {content.get("message")}')
        print(f'   Current Player: {content.get("current_player")}')

        # Paula makes a call (should trigger notification back to Ruben)
        print('\\n5. Paula makes a call (should notify Ruben)...')
        result = make_request('tools/call', {
            'name': 'place_bet',
            'arguments': {
                'game_id': game_id,
                'player': 'Paula Stolk',
                'action': 'call'
            }
        }, 7)

        content = result.get('result', {}).get('structuredContent', {})
        print(f'   Message: {content.get("message")}')
        print(f'   Phase: {content.get("phase")}')

    print('\\n' + '=' * 50)
    print('✅ Poke API integration test completed!')
    print('📱 Check Poke app for notifications:')
    print('   - Game start notification to Ruben')
    print('   - Turn notification to Paula after Ruben\'s bet')
    print('   - Turn notification to Ruben after Paula\'s call')

if __name__ == "__main__":
    test_poke_integration()
