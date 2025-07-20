#!/usr/bin/env python3
"""
Simplified GPIO Client for Raspberry Pi GPIO Control
Communicates with JSON-RPC GPIO server to control GPIO pins
"""

import json
import logging
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gpio-client")

class SimpleGPIOClient:
    """Simple JSON-RPC GPIO Client"""
    
    def __init__(self, server_script: str = "mcp_gpio_server.py"):
        """Initialize GPIO client
        
        Args:
            server_script: Path to the GPIO server script
        """
        self.server_script = server_script
        self.server_process = None
        self.request_id = 0
        logger.info("🔌 Simple GPIO Client initialized")
    
    def _get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send JSON-RPC request to GPIO server
        
        Args:
            method: JSON-RPC method name
            params: Method parameters
            
        Returns:
            Response from server
        """
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
            self.server_process.stdin.write(request_json)  # Write string directly, not bytes
            self.server_process.stdin.flush()
        except BrokenPipeError:
            raise RuntimeError("GPIO server connection broken")
        except Exception as e:
            raise RuntimeError(f"Failed to send request to GPIO server: {e}")
        
        # Read response with timeout using select
        try:
            import select
            
            # Use select for timeout on reading response
            if hasattr(select, 'select'):
                ready, _, _ = select.select([self.server_process.stdout], [], [], 10.0)  # 10 second timeout
                if not ready:
                    raise TimeoutError("GPIO server response timeout (10 seconds)")
                
                response_line = self.server_process.stdout.readline().strip()
            else:
                # Fallback for systems without select
                response_line = self.server_process.stdout.readline().strip()
            
            logger.info(f"Received response: {response_line}")
            
            if not response_line:
                # Check if server process is still running
                if self.server_process.poll() is not None:
                    stderr_output = self.server_process.stderr.read()
                    raise RuntimeError(f"GPIO server terminated unexpectedly. stderr: {stderr_output}")
                else:
                    raise RuntimeError("Empty response from GPIO server (server still running)")
            
            response = json.loads(response_line)
            
            if "error" in response:
                raise RuntimeError(f"GPIO server error: {response['error']}")
            
            return response.get("result", {})
            
        except json.JSONDecodeError as e:
            # Check server stderr for more info
            stderr_info = ""
            try:
                import select
                if hasattr(select, 'select'):
                    ready, _, _ = select.select([self.server_process.stderr], [], [], 0.1)
                    if ready:
                        stderr_info = f" Server stderr: {self.server_process.stderr.read()}"
            except:
                pass
            
            raise RuntimeError(f"Invalid JSON response from GPIO server: {e}. Response was: '{response_line}'{stderr_info}")
        except Exception as e:
            raise RuntimeError(f"Communication error with GPIO server: {e}")
    
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
            
            # Wait for server ready signal
            server_ready = False
            for attempt in range(50):  # 5 seconds total
                if self.server_process.poll() is not None:
                    stderr_output = self.server_process.stderr.read()
                    stdout_output = self.server_process.stdout.read()
                    raise RuntimeError(f"GPIO server failed to start. stderr: {stderr_output}, stdout: {stdout_output}")
                
                # Check for server ready signal in stderr
                import select
                if hasattr(select, 'select'):
                    ready, _, _ = select.select([self.server_process.stderr], [], [], 0.1)
                    if ready:
                        stderr_data = self.server_process.stderr.readline()
                        if stderr_data:
                            logger.info(f"Server stderr: {stderr_data.strip()}")
                            if "GPIO_SERVER_READY" in stderr_data:
                                server_ready = True
                                logger.info("✅ GPIO server ready signal received")
                                break
                
                time.sleep(0.1)
            
            if not server_ready:
                raise RuntimeError("GPIO server did not send ready signal within timeout")
            
            # Check for any startup errors in stderr (non-blocking)
            import select
            if hasattr(select, 'select'):
                ready, _, _ = select.select([self.server_process.stderr], [], [], 0.1)
                if ready:
                    stderr_data = self.server_process.stderr.read()
                    if stderr_data and "ERROR" in stderr_data:
                        logger.warning(f"Server stderr: {stderr_data}")
            
            # Initialize the server with timeout
            logger.info("Sending initialization request...")
            try:
                init_response = self._send_request("initialize", {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "gpio-client", "version": "1.0.0"}
                })
                
                logger.info(f"Initialization response: {init_response}")
                logger.info("✅ GPIO server started and initialized successfully")
            except TimeoutError as e:
                logger.error(f"⏰ GPIO server initialization timeout: {e}")
                raise RuntimeError(f"GPIO server initialization timeout: {e}")
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
        """Set GPIO pin state
        
        Args:
            pin: GPIO pin number
            state: Pin state ('high', 'low', 'on', 'off', '1', '0')
            
        Returns:
            Result from GPIO operation
        """
        return self._send_request("tools/call", {
            "name": "set_gpio_pin",
            "arguments": {"pin": pin, "state": state}
        })
    
    def read_gpio_pin(self, pin: int) -> Dict[str, Any]:
        """Read GPIO pin state
        
        Args:
            pin: GPIO pin number
            
        Returns:
            Current pin state
        """
        return self._send_request("tools/call", {
            "name": "read_gpio_pin",
            "arguments": {"pin": pin}
        })
    
    def get_gpio_status(self) -> Dict[str, Any]:
        """Get GPIO controller status
        
        Returns:
            GPIO controller status
        """
        return self._send_request("tools/call", {
            "name": "get_gpio_status",
            "arguments": {}
        })
    
    def list_valid_pins(self) -> Dict[str, Any]:
        """List valid GPIO pins
        
        Returns:
            List of valid GPIO pins
        """
        return self._send_request("tools/call", {
            "name": "list_valid_gpio_pins",
            "arguments": {}
        })
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools
        
        Returns:
            List of available tools
        """
        return self._send_request("tools/list")

# Synchronous wrapper for Flask integration
class SyncGPIOClient:
    """Synchronous wrapper for Simple GPIO Client"""
    
    def __init__(self):
        self.client = SimpleGPIOClient()
        logger.info("🔄 Sync GPIO Client initialized")
    
    def _execute_with_client(self, operation):
        """Execute operation with GPIO client connection"""
        with self.client:
            return operation(self.client)
    
    def set_gpio_pin(self, pin: int, state: str) -> Dict[str, Any]:
        """Set GPIO pin state (synchronous)"""
        def operation(client):
            return client.set_gpio_pin(pin, state)
        
        return self._execute_with_client(operation)
    
    def read_gpio_pin(self, pin: int) -> Dict[str, Any]:
        """Read GPIO pin state (synchronous)"""
        def operation(client):
            return client.read_gpio_pin(pin)
        
        return self._execute_with_client(operation)
    
    def get_gpio_status(self) -> Dict[str, Any]:
        """Get GPIO status (synchronous)"""
        def operation(client):
            return client.get_gpio_status()
        
        return self._execute_with_client(operation)
    
    def list_valid_pins(self) -> Dict[str, Any]:
        """List valid GPIO pins (synchronous)"""
        def operation(client):
            return client.list_valid_pins()
        
        return self._execute_with_client(operation)
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools (synchronous)"""
        def operation(client):
            return client.list_tools()
        
        return self._execute_with_client(operation)

# Global instance for Flask app
mcp_gpio_client = SyncGPIOClient()

# Test function
def test_gpio_client():
    """Test the GPIO client functionality"""
    logger.info("🧪 Testing Simple GPIO Client...")
    
    client = SimpleGPIOClient()
    
    try:
        with client:
            # Test listing tools
            tools = client.list_tools()
            logger.info(f"Available tools: {tools}")
            
            # Test GPIO operations
            logger.info("Testing GPIO pin 18...")
            
            # Set pin high
            result = client.set_gpio_pin(18, "high")
            logger.info(f"Set pin 18 high: {result}")
            
            # Read pin state
            state = client.read_gpio_pin(18)
            logger.info(f"Pin 18 state: {state}")
            
            # Get status
            status = client.get_gpio_status()
            logger.info(f"GPIO status: {status}")
            
    except Exception as e:
        logger.error(f"❌ GPIO client test failed: {e}")

if __name__ == "__main__":
    test_gpio_client()
