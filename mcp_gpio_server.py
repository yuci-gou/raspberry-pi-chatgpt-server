#!/usr/bin/env python3
"""
Simplified JSON-RPC GPIO Server for Raspberry Pi 400
Provides GPIO control capabilities via JSON-RPC over stdio
"""

import json
import sys
import logging
from typing import Any, Dict, List, Optional

# Import our GPIO controller
try:
    from freenove_projects_board import gpio_controller, set_gpio, read_gpio, cleanup_gpio
    GPIO_AVAILABLE = True
except ImportError as e:
    GPIO_AVAILABLE = False
    print(f"GPIO not available: {e}", file=sys.stderr)

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("gpio-server")

class SimpleGPIOServer:
    """Simple JSON-RPC GPIO Server"""
    
    def __init__(self):
        self.request_id = 0
        logger.info("🍓 Simple GPIO Server initialized")
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC request"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "tools/list":
                result = self.list_tools()
            elif method == "tools/call":
                result = self.call_tool(params)
            elif method == "initialize":
                result = self.initialize(params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": str(e)}
            }
    
    def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the server"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "serverInfo": {
                "name": "raspberry-pi-gpio",
                "version": "1.0.0"
            }
        }
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        tools = [
            {
                "name": "set_gpio_pin",
                "description": "Set a GPIO pin to high or low state",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pin": {"type": "integer", "minimum": 1, "maximum": 27},
                        "state": {"type": "string", "enum": ["high", "low", "on", "off", "1", "0"]}
                    },
                    "required": ["pin", "state"]
                }
            },
            {
                "name": "read_gpio_pin",
                "description": "Read the current state of a GPIO pin",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pin": {"type": "integer", "minimum": 1, "maximum": 27}
                    },
                    "required": ["pin"]
                }
            },
            {
                "name": "get_gpio_status",
                "description": "Get the status of all GPIO pins and the GPIO controller",
                "inputSchema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "list_valid_gpio_pins",
                "description": "Get a list of all valid GPIO pins for this Raspberry Pi",
                "inputSchema": {"type": "object", "properties": {}, "required": []}
            }
        ]
        return {"tools": tools}
    
    def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool"""
        if not GPIO_AVAILABLE:
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({"error": "GPIO functionality not available"})
                }]
            }
        
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "set_gpio_pin":
                pin = arguments.get("pin")
                state = arguments.get("state")
                result = set_gpio(pin, state)
                
            elif tool_name == "read_gpio_pin":
                pin = arguments.get("pin")
                result = read_gpio(pin)
                
            elif tool_name == "get_gpio_status":
                result = gpio_controller.get_pin_status()
                result.update({
                    "system": "Raspberry Pi 400",
                    "gpio_mode": "BCM",
                    "server_status": "running"
                })
                
            elif tool_name == "list_valid_gpio_pins":
                result = {
                    "valid_pins": [4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
                    "numbering_mode": "BCM",
                    "total_pins": 17
                }
                
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }]
            }
            
        except Exception as e:
            logger.error(f"Error in tool call {tool_name}: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({"error": str(e), "tool": tool_name})
                }]
            }
    
    def run(self):
        """Run the server (blocking)"""
        logger.info("🚀 Starting Simple GPIO Server...")
        
        # Send server ready signal to stderr (so client can see it)
        print("GPIO_SERVER_READY", file=sys.stderr, flush=True)
        
        # Ensure stdout is ready for JSON-RPC communication
        sys.stdout.flush()
        
        try:
            # Use a more robust input reading approach
            while True:
                try:
                    # Read line from stdin
                    line = sys.stdin.readline()
                    if not line:  # EOF
                        logger.info("EOF received, shutting down server")
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    logger.info(f"Received request: {line}")
                    
                    try:
                        request = json.loads(line)
                        response = self.handle_request(request)
                        response_json = json.dumps(response)
                        logger.info(f"Sending response: {response_json}")
                        print(response_json, flush=True)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON: {e}")
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {"code": -32700, "message": "Parse error"}
                        }
                        print(json.dumps(error_response), flush=True)
                        
                except EOFError:
                    logger.info("EOFError received, shutting down server")
                    break
                except KeyboardInterrupt:
                    logger.info("⚠️ Server interrupted by user")
                    break
                    
        except KeyboardInterrupt:
            logger.info("⚠️ Server interrupted by user")
        except Exception as e:
            logger.error(f"❌ Server error: {e}")
        finally:
            logger.info("🧹 Cleaning up GPIO resources...")
            if GPIO_AVAILABLE:
                cleanup_gpio()
            logger.info("✅ GPIO Server shutdown complete")

def main():
    """Main function to run the GPIO server"""
    server = SimpleGPIOServer()
    server.run()

if __name__ == "__main__":
    main()
