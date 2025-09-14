#!/usr/bin/env python3
"""
Poke-R Integration Test Suite
Tests all major functionality of the Poke-R poker server
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class PokeRIntegrationTest:
    def __init__(self, base_url: str = "https://fastmcp-server-z2pr.onrender.com"):
        self.base_url = base_url
        self.mcp_url = f"{base_url}/mcp"
        self.session_id = None
        self.test_results = []

    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })

    def make_mcp_request(self, method: str, params: Dict = None, request_id: int = 1) -> Dict:
        """Make an MCP request to the server"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        if self.session_id:
            headers["mcp-session-id"] = self.session_id

        payload = {
            "jsonrpc": "2.0",
            "method": method
        }

        # Only add id for requests, not notifications
        if not method.startswith("notifications/"):
            payload["id"] = request_id

        if params is not None:
            payload["params"] = params

        try:
            response = requests.post(self.mcp_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            # Parse SSE response
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError:
                        continue

            return {"error": "No valid JSON data found in response"}

        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def test_server_health(self) -> bool:
        """Test if server is responding"""
        try:
            response = requests.get(self.base_url, timeout=10)
            return response.status_code in [200, 404, 405]  # Any response means server is up
        except:
            return False

    def test_mcp_initialization(self) -> bool:
        """Test MCP protocol initialization"""
        # Get session ID first
        try:
            response = requests.head(self.mcp_url, timeout=10)
            self.session_id = response.headers.get('mcp-session-id')
            if not self.session_id:
                print(f"DEBUG: No session ID in headers: {dict(response.headers)}")
                return False
        except Exception as e:
            print(f"DEBUG: Failed to get session ID: {e}")
            return False

        # Initialize MCP
        result = self.make_mcp_request("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {
                "name": "integration-test",
                "version": "1.0.0"
            }
        })

        if "error" in result:
            print(f"DEBUG: Initialize failed: {result}")
            return False

        # Send initialized notification
        initialized_result = self.make_mcp_request("notifications/initialized", None)

        # Notifications don't return data, so we just check for connection errors
        if "error" in initialized_result and "No valid JSON data found" not in initialized_result["error"]:
            print(f"DEBUG: Initialized notification failed: {initialized_result}")
            return False

        return True

    def test_tools_list(self) -> bool:
        """Test that all poker tools are available"""
        result = self.make_mcp_request("tools/list", {})

        if "error" in result:
            return False

        tools = result.get("result", {}).get("tools", [])
        expected_tools = [
            "start_poker", "place_bet", "discard_cards",
            "toggle_availability", "set_schedule", "accept_invite",
            "get_game_status", "get_server_info"
        ]

        tool_names = [tool["name"] for tool in tools]
        return all(tool in tool_names for tool in expected_tools)

    def test_server_info(self) -> bool:
        """Test get_server_info tool"""
        result = self.make_mcp_request("tools/call", {
            "name": "get_server_info",
            "arguments": {}
        })

        if "error" in result:
            return False

        content = result.get("result", {}).get("structuredContent", {})
        return content.get("server_name") == "Poke-R Poker Server"

    def test_availability_toggle(self) -> bool:
        """Test availability toggle functionality"""
        test_phone = "+31646118037"

        # Test enabling availability
        result = self.make_mcp_request("tools/call", {
            "name": "toggle_availability",
            "arguments": {"phone": test_phone}
        })

        if "error" in result:
            print(f"DEBUG: Toggle 1 failed: {result}")
            return False

        content = result.get("result", {}).get("structuredContent", {})
        print(f"DEBUG: Toggle 1 result: {content}")
        if not content.get("available"):
            return False

        # Test disabling availability
        result = self.make_mcp_request("tools/call", {
            "name": "toggle_availability",
            "arguments": {"phone": test_phone}
        })

        if "error" in result:
            print(f"DEBUG: Toggle 2 failed: {result}")
            return False

        content = result.get("result", {}).get("structuredContent", {})
        print(f"DEBUG: Toggle 2 result: {content}")
        if content.get("available"):
            return False

        # Test enabling again
        result = self.make_mcp_request("tools/call", {
            "name": "toggle_availability",
            "arguments": {"phone": test_phone}
        })

        if "error" in result:
            print(f"DEBUG: Toggle 3 failed: {result}")
            return False

        content = result.get("result", {}).get("structuredContent", {})
        print(f"DEBUG: Toggle 3 result: {content}")
        return content.get("available")

    def test_poker_game_flow(self) -> bool:
        """Test complete poker game flow"""
        test_players = ["Alice", "Bob"]

        # Enable availability for both players
        for player in test_players:
            result = self.make_mcp_request("tools/call", {
                "name": "toggle_availability",
                "arguments": {"phone": player}
            })
            if "error" in result:
                return False

        # Start poker game
        result = self.make_mcp_request("tools/call", {
            "name": "start_poker",
            "arguments": {"players": test_players}
        })

        if "error" in result:
            return False

        content = result.get("result", {}).get("structuredContent", {})
        game_id = content.get("game_id")

        if not game_id:
            return False

        # Test placing a bet
        result = self.make_mcp_request("tools/call", {
            "name": "place_bet",
            "arguments": {
                "game_id": game_id,
                "player": "Alice",
                "action": "bet",
                "amount": 10
            }
        })

        if "error" in result:
            return False

        # Test getting game status
        result = self.make_mcp_request("tools/call", {
            "name": "get_game_status",
            "arguments": {"game_id": game_id}
        })

        if "error" in result:
            return False

        content = result.get("result", {}).get("structuredContent", {})
        return content.get("game_id") == game_id

    def test_schedule_functionality(self) -> bool:
        """Test schedule setting functionality"""
        test_phone = "+31646118037"

        result = self.make_mcp_request("tools/call", {
            "name": "set_schedule",
            "arguments": {
                "phone": test_phone,
                "schedule_str": "19:00-22:00, Mon-Fri"
            }
        })

        if "error" in result:
            return False

        content = result.get("result", {}).get("structuredContent", {})
        return "Schedule set" in content.get("message", "")

    def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print("🎲 Poke-R Integration Test Suite")
        print("=" * 50)

        # Test 1: Server Health
        success = self.test_server_health()
        self.log_test("Server Health Check", success,
                     "Server responding" if success else "Server not responding")
        if not success:
            return False

        # Test 2: MCP Initialization
        success = self.test_mcp_initialization()
        self.log_test("MCP Initialization", success,
                     f"Session ID: {self.session_id}" if success else "Failed to initialize")
        if not success:
            return False

        # Test 3: Tools List
        success = self.test_tools_list()
        self.log_test("Tools List", success,
                     "All 8 poker tools available" if success else "Missing tools")
        if not success:
            return False

        # Test 4: Server Info
        success = self.test_server_info()
        self.log_test("Server Info", success,
                     "Server info retrieved" if success else "Failed to get server info")
        if not success:
            return False

        # Test 5: Availability Toggle
        success = self.test_availability_toggle()
        self.log_test("Availability Toggle", success,
                     "Toggle functionality working" if success else "Toggle not working")
        if not success:
            return False

        # Test 6: Schedule Functionality
        success = self.test_schedule_functionality()
        self.log_test("Schedule Setting", success,
                     "Schedule functionality working" if success else "Schedule not working")
        if not success:
            return False

        # Test 7: Poker Game Flow
        success = self.test_poker_game_flow()
        self.log_test("Poker Game Flow", success,
                     "Complete game flow working" if success else "Game flow failed")
        if not success:
            return False

        # Summary
        print("\n" + "=" * 50)
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)

        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Poke-R server is fully functional!")
            return True
        else:
            print("❌ Some tests failed. Check the details above.")
            return False

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "https://fastmcp-server-z2pr.onrender.com"

    print(f"Testing Poke-R server at: {base_url}")
    print("This may take a few minutes...\n")

    tester = PokeRIntegrationTest(base_url)
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
