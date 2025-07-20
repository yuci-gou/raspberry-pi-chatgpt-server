#!/usr/bin/env python3
"""
Simple HTTP-based GPIO client
Much more reliable than JSON-RPC over stdio
"""

import requests
import subprocess
import time
import logging
import atexit
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple-gpio-client")

class SimpleHTTPGPIOClient:
    """Simple HTTP-based GPIO client"""
    
    def __init__(self, service_port=None):
        self.service_port = service_port  # Will be determined dynamically
        self.base_url = None  # Will be set after service starts
        self.service_process = None
        logger.info("🔌 Simple HTTP GPIO Client initialized")
    
    def start_service(self):
        """Start the GPIO service"""
        if self.service_process:
            logger.warning("GPIO service already running")
            return
        
        try:
            logger.info("🚀 Starting GPIO service...")
            self.service_process = subprocess.Popen(
                ["python3", "simple_gpio_service.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Read the service port from stdout
            port_found = False
            error_found = False
            
            for _ in range(50):  # Try for 5 seconds
                if self.service_process.poll() is not None:
                    # Process has terminated
                    stderr_output = self.service_process.stderr.read()
                    stdout_output = self.service_process.stdout.read()
                    raise RuntimeError(f"GPIO service failed to start. stderr: {stderr_output}, stdout: {stdout_output}")
                
                # Try to read a line from stdout
                try:
                    line = self.service_process.stdout.readline()
                    if line:
                        line = line.strip()
                        if line.startswith("SERVICE_PORT:"):
                            self.service_port = int(line.split(":")[1])
                            self.base_url = f"http://127.0.0.1:{self.service_port}"
                            port_found = True
                            logger.info(f"✅ GPIO service started on port {self.service_port}")
                            break
                        elif line.startswith("SERVICE_ERROR:"):
                            error_msg = line.split(":", 1)[1]
                            error_found = True
                            raise RuntimeError(f"GPIO service error: {error_msg}")
                except:
                    pass
                
                time.sleep(0.1)
            
            if not port_found and not error_found:
                raise RuntimeError("GPIO service did not report its port within timeout")
            
            # Test service health
            if port_found:
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=5)
                    if response.status_code == 200:
                        logger.info("✅ GPIO service health check passed")
                    else:
                        raise RuntimeError(f"Service health check failed: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    raise RuntimeError(f"Service not responding: {e}")
                
        except Exception as e:
            logger.error(f"❌ Failed to start GPIO service: {e}")
            if self.service_process:
                self.service_process.terminate()
                self.service_process = None
            raise
    
    def stop_service(self):
        """Stop the GPIO service"""
        if not self.service_process:
            return
        
        logger.info("🛑 Stopping GPIO service...")
        try:
            self.service_process.terminate()
            self.service_process.wait(timeout=5)
            logger.info("✅ GPIO service stopped")
        except subprocess.TimeoutExpired:
            logger.warning("Service didn't stop gracefully, killing...")
            self.service_process.kill()
            self.service_process.wait()
        finally:
            self.service_process = None
    
    def __enter__(self):
        """Context manager entry"""
        self.start_service()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_service()
    
    def set_gpio_pin(self, pin: int, state: str) -> Dict[str, Any]:
        """Set GPIO pin state"""
        try:
            response = requests.post(
                f"{self.base_url}/gpio/set",
                json={"pin": pin, "state": state},
                timeout=10
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"HTTP request failed: {e}"}
    
    def read_gpio_pin(self, pin: int) -> Dict[str, Any]:
        """Read GPIO pin state"""
        try:
            response = requests.post(
                f"{self.base_url}/gpio/read",
                json={"pin": pin},
                timeout=10
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"HTTP request failed: {e}"}
    
    def get_gpio_status(self) -> Dict[str, Any]:
        """Get GPIO status"""
        try:
            response = requests.get(f"{self.base_url}/gpio/status", timeout=10)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"HTTP request failed: {e}"}
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools (for compatibility)"""
        return {
            "tools": [
                {"name": "set_gpio_pin", "description": "Set GPIO pin state"},
                {"name": "read_gpio_pin", "description": "Read GPIO pin state"},
                {"name": "get_gpio_status", "description": "Get GPIO status"}
            ]
        }

# Synchronous wrapper for Flask integration
class SyncHTTPGPIOClient:
    """Synchronous wrapper for HTTP GPIO Client"""
    
    def __init__(self):
        self.client = SimpleHTTPGPIOClient()
        logger.info("🔄 Sync HTTP GPIO Client initialized")
    
    def _execute_with_client(self, operation):
        """Execute operation with GPIO client"""
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
        return {
            "valid_pins": [4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
            "numbering_mode": "BCM",
            "total_pins": 17
        }
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools (synchronous)"""
        def operation(client):
            return client.list_tools()
        return self._execute_with_client(operation)

# Global instance for Flask app (compatible with existing code)
http_gpio_client = SyncHTTPGPIOClient()

# Test function
def test_http_gpio_client():
    """Test the HTTP GPIO client"""
    logger.info("🧪 Testing HTTP GPIO Client...")
    
    client = SimpleHTTPGPIOClient()
    
    try:
        with client:
            # Test tools listing
            tools = client.list_tools()
            logger.info(f"Available tools: {tools}")
            
            # Test GPIO status
            status = client.get_gpio_status()
            logger.info(f"GPIO status: {status}")
            
            # Test GPIO operations (if available)
            try:
                result = client.set_gpio_pin(18, "high")
                logger.info(f"Set pin 18 high: {result}")
                
                state = client.read_gpio_pin(18)
                logger.info(f"Read pin 18: {state}")
                
            except Exception as e:
                logger.warning(f"GPIO operations failed (expected on non-Pi): {e}")
            
            logger.info("✅ HTTP GPIO client test completed!")
            
    except Exception as e:
        logger.error(f"❌ HTTP GPIO client test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_http_gpio_client()
