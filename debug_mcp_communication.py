#!/usr/bin/env python3
"""
Debug script to test MCP client-server communication step by step
"""

import json
import subprocess
import time
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("debug-mcp")

def test_server_startup():
    """Test if GPIO server starts correctly"""
    logger.info("🧪 Testing GPIO server startup...")
    
    try:
        # Start the GPIO server
        server_process = subprocess.Popen(
            ["python3", "mcp_gpio_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        logger.info("✅ Server process started")
        
        # Wait for server to start
        time.sleep(2.0)
        
        # Check if server is still running
        if server_process.poll() is not None:
            stderr_output = server_process.stderr.read()
            logger.error(f"❌ Server terminated early. stderr: {stderr_output}")
            return False
        
        logger.info("✅ Server is running")
        
        # Try to send a simple request
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
        logger.info(f"📤 Sending init request: {request_json.strip()}")
        
        # Send request
        server_process.stdin.write(request_json)
        server_process.stdin.flush()
        
        # Wait for response
        logger.info("⏳ Waiting for response...")
        
        # Try to read response with timeout
        import select
        if hasattr(select, 'select'):
            ready, _, _ = select.select([server_process.stdout], [], [], 5.0)  # 5 second timeout
            if ready:
                response_line = server_process.stdout.readline().strip()
                logger.info(f"📥 Received response: {response_line}")
                
                # Try to parse JSON
                try:
                    response = json.loads(response_line)
                    logger.info("✅ Valid JSON response received!")
                    logger.info(f"   Response: {json.dumps(response, indent=2)}")
                    return True
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON response: {e}")
                    return False
            else:
                logger.error("❌ No response received within timeout")
                
                # Check stderr for errors
                stderr_ready, _, _ = select.select([server_process.stderr], [], [], 0.1)
                if stderr_ready:
                    stderr_data = server_process.stderr.read()
                    logger.error(f"Server stderr: {stderr_data}")
                
                return False
        else:
            # Fallback for systems without select
            response_line = server_process.stdout.readline().strip()
            logger.info(f"📥 Received response: {response_line}")
            return bool(response_line)
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Clean up server process
        if 'server_process' in locals():
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()

def test_client_connection():
    """Test MCP client connection"""
    logger.info("🧪 Testing MCP client connection...")
    
    try:
        from mcp_client import SimpleGPIOClient
        
        client = SimpleGPIOClient()
        logger.info("✅ Client created")
        
        # Test with context manager
        with client:
            logger.info("✅ Client context manager entered")
            
            # Try to list tools
            tools = client.list_tools()
            logger.info(f"📋 Tools response: {tools}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all debug tests"""
    logger.info("🚀 Starting MCP Communication Debug Tests")
    
    # Test 1: Server startup
    logger.info("\n" + "="*50)
    logger.info("TEST 1: GPIO Server Startup")
    logger.info("="*50)
    server_ok = test_server_startup()
    
    # Test 2: Client connection
    logger.info("\n" + "="*50)
    logger.info("TEST 2: MCP Client Connection")
    logger.info("="*50)
    client_ok = test_client_connection()
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("SUMMARY")
    logger.info("="*50)
    logger.info(f"Server startup: {'✅ PASS' if server_ok else '❌ FAIL'}")
    logger.info(f"Client connection: {'✅ PASS' if client_ok else '❌ FAIL'}")
    
    if server_ok and client_ok:
        logger.info("🎉 All tests passed! MCP communication should work.")
    else:
        logger.info("💥 Some tests failed. Check the logs above for details.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
