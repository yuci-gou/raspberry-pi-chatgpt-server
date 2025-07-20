#!/usr/bin/env python3
"""
Test script to verify GPIO server returns proper JSON responses
"""

import json
import subprocess
import time
import sys

def test_gpio_server_json():
    """Test that GPIO server returns proper JSON responses"""
    print("🧪 Testing GPIO Server JSON Response...")
    
    # Start the GPIO server
    server_process = subprocess.Popen(
        ["python3", "mcp_gpio_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Wait for server to start
        time.sleep(1.0)
        
        # Check if server is still running
        if server_process.poll() is not None:
            stderr_output = server_process.stderr.read()
            print(f"❌ Server failed to start: {stderr_output}")
            return False
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        print(f"📤 Sending: {json.dumps(init_request)}")
        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response_line = server_process.stdout.readline().strip()
        print(f"📥 Received: {response_line}")
        
        # Verify it's valid JSON
        try:
            response = json.loads(response_line)
            print("✅ Valid JSON response received!")
            print(f"   Response: {json.dumps(response, indent=2)}")
            
            # Test a GPIO command
            gpio_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "set_gpio_pin",
                    "arguments": {"pin": 18, "state": "high"}
                }
            }
            
            print(f"📤 Sending GPIO command: {json.dumps(gpio_request)}")
            server_process.stdin.write(json.dumps(gpio_request) + "\n")
            server_process.stdin.flush()
            
            # Read GPIO response
            gpio_response_line = server_process.stdout.readline().strip()
            print(f"📥 Received GPIO response: {gpio_response_line}")
            
            # Verify GPIO response is valid JSON
            gpio_response = json.loads(gpio_response_line)
            print("✅ Valid JSON GPIO response received!")
            print(f"   GPIO Response: {json.dumps(gpio_response, indent=2)}")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            print(f"   Raw response: '{response_line}'")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Clean up server process
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait()

if __name__ == "__main__":
    success = test_gpio_server_json()
    if success:
        print("🎉 GPIO Server JSON Response Test PASSED!")
    else:
        print("💥 GPIO Server JSON Response Test FAILED!")
        sys.exit(1)
