#!/usr/bin/env python3
"""
Simple test runner for Poke-R integration tests
"""

import subprocess
import sys
import os

def install_test_dependencies():
    """Install test dependencies"""
    print("📦 Installing test dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_integration_tests():
    """Run the integration tests"""
    print("🧪 Running Poke-R integration tests...")
    try:
        result = subprocess.run([sys.executable, "test_integration.py"],
                              capture_output=True, text=True, timeout=300)

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def main():
    """Main test runner"""
    print("🎲 Poke-R Test Runner")
    print("=" * 30)

    # Install dependencies
    if not install_test_dependencies():
        sys.exit(1)

    # Run tests
    if not run_integration_tests():
        print("\n❌ Tests failed!")
        sys.exit(1)

    print("\n🎉 All tests completed successfully!")

if __name__ == "__main__":
    main()
