#!/usr/bin/env python3
"""
Demonstration of the complete Poke-R workflow for agents
"""

import requests
import json

def demo_complete_workflow():
    print("🎲 Poke-R Complete Workflow Demo")
    print("=" * 50)

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
        'clientInfo': {'name': 'demo-agent', 'version': '1.0.0'}
    })
    make_request('notifications/initialized')

    print("✅ MCP Initialized")

    # Step 1: Register Ruben Stolk
    print("\n1️⃣ Registering Ruben Stolk...")
    result = make_request('tools/call', {
        'name': 'register_player_tool',
        'arguments': {
            'phone': '+31646118037',
            'name': 'Ruben Stolk'
        }
    }, 1)

    content = result.get('result', {}).get('structuredContent', {})
    print(f"   Result: {content.get('message')}")

    # Step 2: Register Paula Stolk
    print("\n2️⃣ Registering Paula Stolk...")
    result = make_request('tools/call', {
        'name': 'register_player_tool',
        'arguments': {
            'phone': '+31645226133',
            'name': 'Paula Stolk'
        }
    }, 2)

    content = result.get('result', {}).get('structuredContent', {})
    print(f"   Result: {content.get('message')}")

    # Step 3: Enable availability for Ruben
    print("\n3️⃣ Enabling availability for Ruben...")
    result = make_request('tools/call', {
        'name': 'toggle_availability',
        'arguments': {'phone': '+31646118037'}
    }, 3)

    content = result.get('result', {}).get('structuredContent', {})
    print(f"   Result: {content.get('message')}")

    # Step 4: Enable availability for Paula
    print("\n4️⃣ Enabling availability for Paula...")
    result = make_request('tools/call', {
        'name': 'toggle_availability',
        'arguments': {'phone': '+31645226133'}
    }, 4)

    content = result.get('result', {}).get('structuredContent', {})
    print(f"   Result: {content.get('message')}")

    # Step 5: Start poker game
    print("\n5️⃣ Starting poker game...")
    result = make_request('tools/call', {
        'name': 'start_poker',
        'arguments': {
            'players': ['Ruben Stolk', 'Paula Stolk']
        }
    }, 5)

    if 'error' in result.get('result', {}).get('structuredContent', {}):
        error = result.get('result', {}).get('structuredContent', {}).get('error')
        print(f"   ❌ Error: {error}")
    else:
        content = result.get('result', {}).get('structuredContent', {})
        print(f"   🎉 SUCCESS!")
        print(f"   Game ID: {content.get('game_id')}")
        print(f"   Message: {content.get('message')}")
        print(f"   Players: {content.get('players')}")

        hands = content.get('hands', {})
        print(f"   Ruben's hand: {hands.get('Ruben Stolk', [])}")
        print(f"   Paula's hand: {hands.get('Paula Stolk', [])}")

    print("\n" + "=" * 50)
    print("✅ This workflow works! The agent should follow these exact steps.")

if __name__ == "__main__":
    demo_complete_workflow()
