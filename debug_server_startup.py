#!/usr/bin/env python3
"""
Debug script to test MCP GPIO server startup
"""

import subprocess
import sys
import time
import select

def test_server_startup():
    """Test if the server starts and sends ready signal"""
    print("🧪 Testing MCP GPIO server startup...")
    
    try:
        # Start the server
        proc = subprocess.Popen(
            ["python3", "mcp_gpio_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        print(f"✅ Server process started with PID: {proc.pid}")
        
        # Wait for server ready signal
        server_ready = False
        stderr_output = []
        
        for attempt in range(50):  # 5 seconds total
            # Check if process is still running
            if proc.poll() is not None:
                print(f"❌ Server process exited with code: {proc.returncode}")
                stdout_data = proc.stdout.read()
                stderr_data = proc.stderr.read()
                print(f"Stdout: {stdout_data}")
                print(f"Stderr: {stderr_data}")
                return False
            
            # Check for stderr data
            if hasattr(select, 'select'):
                ready, _, _ = select.select([proc.stderr], [], [], 0.1)
                if ready:
                    stderr_line = proc.stderr.readline()
                    if stderr_line:
                        stderr_output.append(stderr_line.strip())
                        print(f"📝 Server stderr: {stderr_line.strip()}")
                        if "GPIO_SERVER_READY" in stderr_line:
                            server_ready = True
                            print("✅ GPIO_SERVER_READY signal received!")
                            break
            
            time.sleep(0.1)
        
        if not server_ready:
            print("❌ Server did not send ready signal within timeout")
            print(f"All stderr output: {stderr_output}")
            
            # Try to get any remaining output
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except:
                proc.kill()
                
            return False
        
        # Test basic communication
        print("🔧 Testing basic JSON-RPC communication...")
        
        # Send initialize request
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
        
        request_json = json.dumps(init_request) + "\n"
        print(f"📤 Sending: {request_json.strip()}")
        
        proc.stdin.write(request_json)
        proc.stdin.flush()
        
        # Read response with timeout
        if hasattr(select, 'select'):
            ready, _, _ = select.select([proc.stdout], [], [], 5.0)
            if ready:
                response_line = proc.stdout.readline()
                print(f"📥 Received: {response_line.strip()}")
                
                try:
                    import json
                    response = json.loads(response_line)
                    if "result" in response:
                        print("✅ Server responded correctly to initialize!")
                        return True
                    else:
                        print(f"❌ Server response error: {response.get('error')}")
                        return False
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    return False
            else:
                print("❌ No response from server within timeout")
                return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        # Clean up
        try:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=2)
        except:
            try:
                proc.kill()
            except:
                pass

if __name__ == "__main__":
    import json
    success = test_server_startup()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Server startup test")
