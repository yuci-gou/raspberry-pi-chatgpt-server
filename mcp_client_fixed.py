#!/usr/bin/env python3
"""
Fixed GPIO Client for Raspberry Pi GPIO Control
Uses more robust subprocess communication
"""

import json
import logging
import subprocess
import sys
import time
import threading
import queue
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gpio-client-fixed")

class FixedGPIOClient:
    """Fixed GPIO Client with robust communication"""
    
    def __init__(self, server_script: str = "mcp_gpio_server.py"):
        """Initialize GPIO client"""
        self.server_script = server_script
        self.server_process = None
        self.request_id = 0
        self.response_queue = queue.Queue()
        self.stdout_thread = None
        self.stderr_thread = None
        logger.info("🔌 Fixed GPIO Client initialized")
    
    def _get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    def _read_stdout(self):
        """Read stdout in a separate thread"""
        try:
            while self.server_process and self.server_process.poll() is None:
                line = self.server_process.stdout.readline()
                if line:
                    line = line.strip()
                    logger.info(f"Server stdout: {line}")
                    self.response_queue.put(('stdout', line))
                else:
                    time.sleep(0.01)
        except Exception as e:
            logger.error(f"Error reading stdout: {e}")
            self.response_queue.put(('error', str(e)))
    
    def _read_stderr(self):
        """Read stderr in a separate thread"""
        try:
            while self.server_process and self.server_process.poll() is None:
                line = self.server_process.stderr.readline()
                if line:
                    line = line.strip()
                    logger.info(f"Server stderr: {line}")
                    self.response_queue.put(('stderr', line))
                else:
                    time.sleep(0.01)
        except Exception as e:
            logger.error(f"Error reading stderr: {e}")
    
    def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send JSON-RPC request to GPIO server"""
        if not self.server_process:
            raise RuntimeError("GPIO server not started")
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method
        }
        
        if params:
            request["params"] = params
        
        # Send request to server
        request_json = json.dumps(request) + "\n"
        logger.info(f"Sending request: {request_json.strip()}")
        
        try:
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
        except Exception as e:
            raise RuntimeError(f"Failed to send request to GPIO server: {e}")
        
        # Wait for response with timeout
        timeout = 10.0
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                msg_type, data = self.response_queue.get(timeout=0.1)
                if msg_type == 'stdout':
                    # This should be our JSON response
                    try:
                        response = json.loads(data)
                        if response.get("id") == request["id"]:
                            if "error" in response:
                                raise RuntimeError(f"GPIO server error: {response['error']}")
                            return response.get("result", {})
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from server: {data}")
                        continue
                elif msg_type == 'error':
                    raise RuntimeError(f"Server communication error: {data}")
            except queue.Empty:
                continue
        
        raise TimeoutError("GPIO server response timeout")
    
    def start_server(self):
        """Start the GPIO server"""
        if self.server_process:
            logger.warning("GPIO server already running")
            return
        
        try:
            logger.info(f"🚀 Starting GPIO server: python3 {self.server_script}")
            self.server_process = subprocess.Popen(
                ["python3", self.server_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            # Start reader threads
            self.stdout_thread = threading.Thread(target=self._read_stdout, daemon=True)
            self.stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
            self.stdout_thread.start()
            self.stderr_thread.start()
            
            # Wait for server ready signal
            server_ready = False
            start_time = time.time()
            timeout = 10.0
            
            while time.time() - start_time < timeout:
                try:
                    msg_type, data = self.response_queue.get(timeout=0.1)
                    if msg_type == 'stderr' and "GPIO_SERVER_READY" in data:
                        server_ready = True
                        logger.info("✅ GPIO server ready signal received")
                        break
                except queue.Empty:
                    continue
            
            if not server_ready:
                raise RuntimeError("GPIO server did not send ready signal within timeout")
            
            # Initialize the server
            logger.info("Sending initialization request...")
            try:
                init_response = self._send_request("initialize", {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "gpio-client", "version": "1.0.0"}
                })
                
                logger.info(f"Initialization response: {init_response}")
                logger.info("✅ GPIO server started and initialized successfully")
            except Exception as e:
                logger.error(f"❌ GPIO server initialization failed: {e}")
                raise RuntimeError(f"GPIO server initialization failed: {e}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start GPIO server: {e}")
            if self.server_process:
                self.server_process.terminate()
                self.server_process = None
            raise
    
    def stop_server(self):
        """Stop the GPIO server"""
        if not self.server_process:
            return
        
        logger.info("🛑 Stopping GPIO server...")
        try:
            self.server_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.server_process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                logger.warning("GPIO server didn't shut down gracefully, killing...")
                self.server_process.kill()
                self.server_process.wait()
            
            logger.info("✅ GPIO server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping GPIO server: {e}")
        finally:
            self.server_process = None
    
    def __enter__(self):
        """Context manager entry"""
        self.start_server()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_server()
    
    def set_gpio_pin(self, pin: int, state: str) -> Dict[str, Any]:
        """Set GPIO pin state"""
        return self._send_request("tools/call", {
            "name": "set_gpio_pin",
            "arguments": {"pin": pin, "state": state}
        })
    
    def read_gpio_pin(self, pin: int) -> Dict[str, Any]:
        """Read GPIO pin state"""
        return self._send_request("tools/call", {
            "name": "read_gpio_pin",
            "arguments": {"pin": pin}
        })
    
    def get_gpio_status(self) -> Dict[str, Any]:
        """Get GPIO controller status"""
        return self._send_request("tools/call", {
            "name": "get_gpio_status",
            "arguments": {}
        })
    
    def list_valid_pins(self) -> Dict[str, Any]:
        """List valid GPIO pins"""
        return self._send_request("tools/call", {
            "name": "list_valid_gpio_pins",
            "arguments": {}
        })
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        return self._send_request("tools/list")

# Test function
def test_fixed_gpio_client():
    """Test the fixed GPIO client"""
    logger.info("🧪 Testing Fixed GPIO Client...")
    
    client = FixedGPIOClient()
    
    try:
        with client:
            # Test listing tools
            tools = client.list_tools()
            logger.info(f"Available tools: {tools}")
            
            # Test GPIO operations
            logger.info("Testing GPIO pin 17...")
            
            # Set pin low
            result = client.set_gpio_pin(17, "low")
            logger.info(f"Set pin 17 low: {result}")
            
            # Read pin state
            state = client.read_gpio_pin(17)
            logger.info(f"Pin 17 state: {state}")
            
    except Exception as e:
        logger.error(f"❌ Fixed GPIO client test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_gpio_client()
