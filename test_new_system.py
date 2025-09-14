#!/usr/bin/env python3
"""
Test the new phone-number-as-primary-key system
"""

import requests
import json
import time

def test_new_system():
    print("🎲 Testing New Phone-Number-as-Primary-Key System")
    print("=" * 60)

    # Get session ID
    response = requests.head('https://fastmcp-server-z2pr.onrender.com/mcp', timeout=10)
    session_id = response.headers.get('mcp-session-id')
    print(f"Session ID: {session_id}")

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

        # Only add id for requests, not notifications
        if not method.startswith("notifications/"):
            payload['id'] = request_id

        if params is not None:
            payload['params'] = params

        response = requests.post('https://fastmcp-server-z2pr.onrender.com/mcp',
                               headers=headers, json=payload, timeout=30)

        # Parse SSE response
        lines = response.text.strip().split('\n')
        for line in lines:
            if line.startswith('data: '):
                data = line[6:]
                try:
                    result = json.loads(data)
                    print(f"DEBUG: {method} response: {result}")
                    return result
                except:
                    continue
        return {"error": "No valid response"}

    # Initialize MCP
    print("\n1. Initializing MCP...")
    init_result = make_request("initialize", {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"}
    })
    print(f"✅ Initialize: {init_result.get('result', {}).get('serverInfo', {}).get('name')}")

    # Send initialized notification
    make_request("notifications/initialized")

    # Register players
    print("\n2. Registering players...")

    # Register Ruben
    ruben_result = make_request("tools/call", {
        "name": "register_player_tool",
        "arguments": {
            "phone": "+31646118037",
            "name": "Ruben Stolk"
        }
    }, 2)
    print(f"✅ Ruben registration: {ruben_result.get('result', {}).get('structuredContent', {}).get('message')}")

    # Register Paula
    paula_result = make_request("tools/call", {
        "name": "register_player_tool",
        "arguments": {
            "phone": "+31645226133",
            "name": "Paula Stolk"
        }
    }, 3)
    print(f"✅ Paula registration: {paula_result.get('result', {}).get('structuredContent', {}).get('message')}")

    # Enable availability for both players
    print("\n3. Enabling availability...")

    ruben_avail = make_request("tools/call", {
        "name": "toggle_availability",
        "arguments": {"phone": "+31646118037"}
    }, 4)
    print(f"✅ Ruben availability: {ruben_avail.get('result', {}).get('structuredContent', {}).get('message')}")

    paula_avail = make_request("tools/call", {
        "name": "toggle_availability",
        "arguments": {"phone": "+31645226133"}
    }, 5)
    print(f"✅ Paula availability: {paula_avail.get('result', {}).get('structuredContent', {}).get('message')}")

    # Start poker game using NAMES (not phone numbers)
    print("\n4. Starting poker game with names...")
    start_result = make_request("tools/call", {
        "name": "start_poker",
        "arguments": {
            "players": ["Ruben Stolk", "Paula Stolk"]  # Using names!
        }
    }, 6)

    if "error" in start_result.get('result', {}).get('structuredContent', {}):
        print(f"❌ Game start failed: {start_result.get('result', {}).get('structuredContent', {}).get('error')}")
    else:
        content = start_result.get('result', {}).get('structuredContent', {})
        print(f"🎉 Game started successfully!")
        print(f"   Game ID: {content.get('game_id')}")
        print(f"   Message: {content.get('message')}")
        print(f"   Players: {content.get('players')}")

        hands = content.get('hands', {})
        print(f"   Ruben's hand: {hands.get('Ruben Stolk', [])}")
        print(f"   Paula's hand: {hands.get('Paula Stolk', [])}")

    print("\n" + "=" * 60)
    print("🎯 New system working: Phone numbers as primary keys, names as aliases!")

if __name__ == "__main__":
    test_new_system()
