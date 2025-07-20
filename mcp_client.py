#!/usr/bin/env python3
"""
MCP Client for GPIO Control
Handles communication with the MCP GPIO Server
"""

import asyncio
import json
import logging
import subprocess
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-client")

class MCPGPIOClient:
    """MCP Client for communicating with GPIO MCP Server"""
    
    def __init__(self, server_command: List[str] = None):
        """Initialize MCP client
        
        Args:
            server_command: Command to start the MCP server
        """
        self.server_command = server_command or ["python3", "mcp_gpio_server.py"]
        self.server_process = None
        self.request_id = 0
        logger.info("🔌 MCP GPIO Client initialized")
    
    def _get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send JSON-RPC request to MCP server
        
        Args:
            method: JSON-RPC method name
            params: Method parameters
            
        Returns:
            Response from server
        """
        if not self.server_process:
            raise RuntimeError("MCP server not started")
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
            "params": params or {}
        }
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_json.encode())
            await self.server_process.stdin.drain()
            
            # Read response
            response_line = await self.server_process.stdout.readline()
            if not response_line:
                raise RuntimeError("No response from MCP server")
            
            response = json.loads(response_line.decode().strip())
            
            if "error" in response:
                raise RuntimeError(f"MCP server error: {response['error']}")
            
            return response.get("result", {})
            
        except Exception as e:
            logger.error(f"Error communicating with MCP server: {e}")
            raise
    
    @asynccontextmanager
    async def connect(self):
        """Context manager for MCP server connection"""
        try:
            logger.info("🚀 Starting MCP GPIO server...")
            
            # Start the MCP server process
            self.server_process = await asyncio.create_subprocess_exec(
                *self.server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Initialize the connection
            await self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "clientInfo": {
                    "name": "flask-gpio-client",
                    "version": "1.0.0"
                }
            })
            
            logger.info("✅ Connected to MCP GPIO server")
            yield self
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MCP server: {e}")
            raise
        finally:
            if self.server_process:
                logger.info("🧹 Shutting down MCP GPIO server...")
                self.server_process.terminate()
                await self.server_process.wait()
                logger.info("✅ MCP GPIO server shutdown complete")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from MCP server"""
        try:
            result = await self._send_request("tools/list")
            return result.get("tools", [])
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return []
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        try:
            result = await self._send_request("tools/call", {
                "name": name,
                "arguments": arguments
            })
            
            # Extract text content from MCP response
            content = result.get("content", [])
            if content and len(content) > 0:
                text_content = content[0].get("text", "{}")
                return json.loads(text_content)
            
            return {"error": "No content in response"}
            
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return {"error": str(e), "tool": name, "arguments": arguments}
    
    async def set_gpio_pin(self, pin: int, state: str) -> Dict[str, Any]:
        """Set GPIO pin state via MCP
        
        Args:
            pin: GPIO pin number
            state: Pin state ('high', 'low', 'on', 'off', '1', '0')
            
        Returns:
            Result dictionary
        """
        return await self.call_tool("set_gpio_pin", {"pin": pin, "state": state})
    
    async def read_gpio_pin(self, pin: int) -> Dict[str, Any]:
        """Read GPIO pin state via MCP
        
        Args:
            pin: GPIO pin number
            
        Returns:
            Result dictionary
        """
        return await self.call_tool("read_gpio_pin", {"pin": pin})
    
    async def get_gpio_status(self) -> Dict[str, Any]:
        """Get GPIO controller status via MCP
        
        Returns:
            Status dictionary
        """
        return await self.call_tool("get_gpio_status", {})
    
    async def list_valid_pins(self) -> Dict[str, Any]:
        """Get list of valid GPIO pins via MCP
        
        Returns:
            Pin information dictionary
        """
        return await self.call_tool("list_valid_gpio_pins", {})

# Synchronous wrapper for Flask integration
class SyncMCPGPIOClient:
    """Synchronous wrapper for MCP GPIO Client"""
    
    def __init__(self):
        self.client = MCPGPIOClient()
        logger.info("🔄 Sync MCP GPIO Client initialized")
    
    def _run_async(self, coro):
        """Run async coroutine in sync context"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    async def _execute_with_client(self, operation):
        """Execute operation with MCP client connection"""
        async with self.client.connect():
            return await operation(self.client)
    
    def set_gpio_pin(self, pin: int, state: str) -> Dict[str, Any]:
        """Set GPIO pin state (synchronous)"""
        async def operation(client):
            return await client.set_gpio_pin(pin, state)
        
        return self._run_async(self._execute_with_client(operation))
    
    def read_gpio_pin(self, pin: int) -> Dict[str, Any]:
        """Read GPIO pin state (synchronous)"""
        async def operation(client):
            return await client.read_gpio_pin(pin)
        
        return self._run_async(self._execute_with_client(operation))
    
    def get_gpio_status(self) -> Dict[str, Any]:
        """Get GPIO status (synchronous)"""
        async def operation(client):
            return await client.get_gpio_status()
        
        return self._run_async(self._execute_with_client(operation))
    
    def list_valid_pins(self) -> Dict[str, Any]:
        """List valid GPIO pins (synchronous)"""
        async def operation(client):
            return await client.list_valid_pins()
        
        return self._run_async(self._execute_with_client(operation))
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools (synchronous)"""
        async def operation(client):
            return await client.list_tools()
        
        return self._run_async(self._execute_with_client(operation))

# Global instance for Flask app
mcp_gpio_client = SyncMCPGPIOClient()

# Test function
def test_mcp_client():
    """Test the MCP client functionality"""
    print("🧪 Testing MCP GPIO Client...")
    
    try:
        # Test listing tools
        tools = mcp_gpio_client.list_tools()
        print(f"Available tools: {[tool.get('name') for tool in tools]}")
        
        # Test GPIO status
        status = mcp_gpio_client.get_gpio_status()
        print(f"GPIO Status: {status}")
        
        # Test setting a pin
        result = mcp_gpio_client.set_gpio_pin(18, "high")
        print(f"Set pin 18 high: {result}")
        
        # Test reading a pin
        result = mcp_gpio_client.read_gpio_pin(18)
        print(f"Read pin 18: {result}")
        
        print("✅ MCP client test completed successfully")
        
    except Exception as e:
        print(f"❌ MCP client test failed: {e}")

if __name__ == "__main__":
    test_mcp_client()
