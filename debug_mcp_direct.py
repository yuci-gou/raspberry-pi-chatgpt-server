#!/usr/bin/env python3
"""
Debug script to test MCP GPIO communication directly
"""

import json
import subprocess
import sys
import time
import select

def test_direct_communication():
    """Test direct communication with GPIO server"""
    print("🧪 Testing direct communication with GPIO server...")
    
    # Start the server
    server_process = subprocess.Popen(
        ["python3", "mcp_gpio_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Wait for ready signal
        print("Waiting for server ready signal...")
        start_time = time.time()
        while time.time() - start_time < 10:
            if hasattr(select, 'select'):
                ready, _, _ = select.select([server_process.stderr], [], [], 0.1)
                if ready:
                    stderr_line = server_process.stderr.readline()
                    print(f"Server stderr: {stderr_line.strip()}")
                    if "GPIO_SERVER_READY" in stderr_line:
                        print("✅ Server ready!")
                        break
            time.sleep(0.1)
        else:
            print("❌ Server not ready within timeout")
            return
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "debug-client", "version": "1.0.0"}
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        print(f"Sending request: {request_json.strip()}")
        
        server_process.stdin.write(request_json)
        server_process.stdin.flush()
        
        # Read response with timeout
        print("Waiting for response...")
        if hasattr(select, 'select'):
            ready, _, _ = select.select([server_process.stdout], [], [], 5.0)
            if ready:
                response_line = server_process.stdout.readline().strip()
                print(f"Received response: {response_line}")
                
                if response_line:
                    response = json.loads(response_line)
                    print(f"Parsed response: {response}")
                else:
                    print("❌ Empty response")
            else:
                print("❌ Response timeout")
        
        # Test a simple GPIO command
        gpio_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "set_gpio_pin",
                "arguments": {"pin": 17, "state": "low"}
            }
        }
        
        request_json = json.dumps(gpio_request) + "\n"
        print(f"Sending GPIO request: {request_json.strip()}")
        
        server_process.stdin.write(request_json)
        server_process.stdin.flush()
        
        # Read GPIO response
        if hasattr(select, 'select'):
            ready, _, _ = select.select([server_process.stdout], [], [], 5.0)
            if ready:
                response_line = server_process.stdout.readline().strip()
                print(f"Received GPIO response: {response_line}")
            else:
                print("❌ GPIO response timeout")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    finally:
        print("🛑 Terminating server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("✅ Test complete")

if __name__ == "__main__":
    test_direct_communication()
