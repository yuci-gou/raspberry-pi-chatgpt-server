#!/usr/bin/env python3
"""
GPIO Client for Raspberry Pi GPIO Control
Communicates with JSON-RPC GPIO server to control GPIO pins
Updated to use the fixed client implementation
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

# Load MCP GPIO client (Model Context Protocol implementation)
try:
    from mcp_client_fixed import FixedGPIOClient
    GPIO_AVAILABLE = True
    print("✅ Fixed MCP GPIO client loaded successfully!")
except ImportError as e:
    GPIO_AVAILABLE = False
    print(f"❌ Fixed MCP GPIO client not available: {e}")
    print("   Please ensure the MCP GPIO server and client are properly installed.")
except Exception as e:
    GPIO_AVAILABLE = False
    print(f"❌ Unexpected error loading Fixed MCP GPIO client: {e}")

# Synchronous wrapper for Flask integration
class SyncGPIOClient:
    """Synchronous wrapper for Fixed GPIO Client"""
    
    def __init__(self):
        if GPIO_AVAILABLE:
            self.client = FixedGPIOClient()
        else:
            self.client = None
        logger.info("🔄 Sync GPIO Client initialized")
    
    def _execute_with_client(self, operation):
        """Execute operation with GPIO client connection"""
        if not self.client:
            raise RuntimeError("GPIO client not available")
        
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
    logger.info("🧪 Testing Fixed GPIO Client...")
    
    if not GPIO_AVAILABLE:
        logger.error("❌ GPIO client not available")
        return
    
    client = FixedGPIOClient()
    
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
