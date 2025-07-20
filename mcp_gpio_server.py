#!/usr/bin/env python3
"""
MCP GPIO Server for Raspberry Pi 400
Provides GPIO control capabilities via Model Context Protocol (MCP)
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from pydantic import BaseModel, Field

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource,
    CallToolRequest,
    CallToolResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    ReadResourceRequest,
    ReadResourceResult,
)

# Import our GPIO controller
from freenove_projects_board import gpio_controller, set_gpio, read_gpio, cleanup_gpio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-gpio-server")

# Pydantic models for tool arguments
class SetGpioPinArgs(BaseModel):
    pin: int = Field(description="GPIO pin number (BCM numbering)")
    state: str = Field(description="Pin state: 'high', 'low', 'on', 'off', '1', '0'")

class ReadGpioPinArgs(BaseModel):
    pin: int = Field(description="GPIO pin number (BCM numbering)")

class GetGpioStatusArgs(BaseModel):
    pass  # No arguments needed

class MCPGPIOServer:
    """MCP Server for Raspberry Pi GPIO Control"""
    
    def __init__(self):
        self.server = Server("raspberry-pi-gpio")
        self.setup_handlers()
        logger.info("🍓 MCP GPIO Server initialized")
    
    def setup_handlers(self):
        """Set up MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available GPIO tools"""
            return [
                Tool(
                    name="set_gpio_pin",
                    description="Set a GPIO pin to high or low state",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pin": {
                                "type": "integer",
                                "description": "GPIO pin number (BCM numbering)",
                                "minimum": 1,
                                "maximum": 27
                            },
                            "state": {
                                "type": "string",
                                "description": "Pin state to set",
                                "enum": ["high", "low", "on", "off", "1", "0"]
                            }
                        },
                        "required": ["pin", "state"]
                    }
                ),
                Tool(
                    name="read_gpio_pin",
                    description="Read the current state of a GPIO pin",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pin": {
                                "type": "integer",
                                "description": "GPIO pin number (BCM numbering)",
                                "minimum": 1,
                                "maximum": 27
                            }
                        },
                        "required": ["pin"]
                    }
                ),
                Tool(
                    name="get_gpio_status",
                    description="Get the status of all GPIO pins and the GPIO controller",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="list_valid_gpio_pins",
                    description="Get a list of all valid GPIO pins for this Raspberry Pi",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "set_gpio_pin":
                    args = SetGpioPinArgs(**arguments)
                    result = set_gpio(args.pin, args.state)
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                elif name == "read_gpio_pin":
                    args = ReadGpioPinArgs(**arguments)
                    result = read_gpio(args.pin)
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                elif name == "get_gpio_status":
                    status = gpio_controller.get_pin_status()
                    # Add additional system information
                    status.update({
                        "system": "Raspberry Pi 400",
                        "gpio_mode": "BCM",
                        "server_status": "running"
                    })
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(status, indent=2)
                    )]
                
                elif name == "list_valid_gpio_pins":
                    valid_pins = [4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
                    pin_info = {
                        "valid_pins": valid_pins,
                        "numbering_mode": "BCM",
                        "total_pins": len(valid_pins),
                        "pin_mapping": {
                            "GPIO 18": "Physical Pin 12",
                            "GPIO 22": "Physical Pin 15", 
                            "GPIO 24": "Physical Pin 18",
                            "GPIO 17": "Physical Pin 11",
                            "GPIO 27": "Physical Pin 13"
                        },
                        "excluded_pins": {
                            "2, 3": "I2C (SDA, SCL)",
                            "14, 15": "UART (TXD, RXD)",
                            "7, 8, 9, 10, 11": "SPI interface"
                        }
                    }
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(pin_info, indent=2)
                    )]
                
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                logger.error(f"Error in tool call {name}: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": str(e),
                        "tool": name,
                        "arguments": arguments
                    }, indent=2)
                )]
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="gpio://status",
                    name="GPIO Controller Status",
                    description="Current status of the GPIO controller and active pins",
                    mimeType="application/json"
                ),
                Resource(
                    uri="gpio://pins",
                    name="Valid GPIO Pins",
                    description="List of valid GPIO pins and their mappings",
                    mimeType="application/json"
                ),
                Resource(
                    uri="gpio://hardware",
                    name="Hardware Information",
                    description="Raspberry Pi hardware and GPIO information",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read resource content"""
            try:
                if uri == "gpio://status":
                    status = gpio_controller.get_pin_status()
                    status.update({
                        "timestamp": asyncio.get_event_loop().time(),
                        "server": "MCP GPIO Server",
                        "system": "Raspberry Pi 400"
                    })
                    return json.dumps(status, indent=2)
                
                elif uri == "gpio://pins":
                    pin_info = {
                        "valid_pins": [4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
                        "numbering_mode": "BCM",
                        "physical_mapping": {
                            "GPIO 4": "Pin 7", "GPIO 5": "Pin 29", "GPIO 6": "Pin 31",
                            "GPIO 12": "Pin 32", "GPIO 13": "Pin 33", "GPIO 16": "Pin 36",
                            "GPIO 17": "Pin 11", "GPIO 18": "Pin 12", "GPIO 19": "Pin 35",
                            "GPIO 20": "Pin 38", "GPIO 21": "Pin 40", "GPIO 22": "Pin 15",
                            "GPIO 23": "Pin 16", "GPIO 24": "Pin 18", "GPIO 25": "Pin 22",
                            "GPIO 26": "Pin 37", "GPIO 27": "Pin 13"
                        }
                    }
                    return json.dumps(pin_info, indent=2)
                
                elif uri == "gpio://hardware":
                    hardware_info = {
                        "model": "Raspberry Pi 400",
                        "gpio_pins": 40,
                        "available_gpio": 27,
                        "usable_gpio": 17,
                        "voltage": "3.3V",
                        "max_current_per_pin": "16mA",
                        "total_max_current": "50mA"
                    }
                    return json.dumps(hardware_info, indent=2)
                
                else:
                    return json.dumps({"error": f"Unknown resource: {uri}"})
                    
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return json.dumps({"error": str(e), "resource": uri})
    
    async def run(self):
        """Run the MCP server"""
        logger.info("🚀 Starting MCP GPIO Server...")
        
        # Initialize the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="raspberry-pi-gpio",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities()
                )
            )

async def main():
    """Main function to run the MCP GPIO server"""
    try:
        logger.info("🍓 Initializing Raspberry Pi 400 MCP GPIO Server")
        server = MCPGPIOServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("⚠️ Server interrupted by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
    finally:
        logger.info("🧹 Cleaning up GPIO resources...")
        cleanup_gpio()
        logger.info("✅ MCP GPIO Server shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
