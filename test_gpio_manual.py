#!/usr/bin/env python3
"""
Simple test to manually test the GPIO server communication
"""

import json
import subprocess
import time
import sys

def test_gpio_server():
    """Test the GPIO server manually"""
    print("Starting GPIO server...")
    
    # Start server
    process = subprocess.Popen(
        ["python3", "mcp_gpio_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit for server to start
    time.sleep(2)
    
    # Check if server is running
    if process.poll() is not None:
        print("Server failed to start")
        stderr_output = process.stderr.read()
        print(f"Server stderr: {stderr_output}")
        return
    
    try:
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
        
        request_str = json.dumps(init_request) + "\n"
        print(f"Sending: {request_str.strip()}")
        
        process.stdin.write(request_str)
        process.stdin.flush()
        
        # Try to read response with timeout
        import select
        import os
        
        # Set stdout to non-blocking
        flags = os.fcntl.fcntl(process.stdout.fileno(), os.fcntl.F_GETFL)
        os.fcntl.fcntl(process.stdout.fileno(), os.fcntl.F_SETFL, flags | os.O_NONBLOCK)
        
        # Wait for response
        timeout = 5.0
        start_time = time.time()
        response = ""
        
        while time.time() - start_time < timeout:
            try:
                chunk = process.stdout.read()
                if chunk:
                    response += chunk
                    if "\n" in response:
                        break
            except BlockingIOError:
                time.sleep(0.1)
                continue
        
        if response.strip():
            print(f"Received: {response.strip()}")
            try:
                parsed = json.loads(response.strip())
                print(f"Parsed response: {parsed}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")
        else:
            print("No response received")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_gpio_server()
