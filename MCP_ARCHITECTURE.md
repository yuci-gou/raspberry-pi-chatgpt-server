# MCP-Based GPIO Architecture

## 🏗️ **Architecture Overview**

This project now implements a sophisticated **Model Context Protocol (MCP)** based architecture for GPIO control, providing a clean separation of concerns and enhanced modularity.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │◄──►│  Flask Backend   │◄──►│   ChatGPT API   │
│                 │    │   (MCP Client)   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼ MCP Protocol
                       ┌──────────────────┐
                       │ Raspberry Pi 400 │
                       │   MCP Server     │
                       │  (GPIO Control)  │
                       └──────────────────┘
```

## 🎯 **Components**

### 1. **MCP GPIO Server** (`mcp_gpio_server.py`)
- **Purpose**: Standalone MCP server that handles all GPIO operations
- **Protocol**: Model Context Protocol (MCP) via stdio
- **Tools Provided**:
  - `set_gpio_pin` - Set GPIO pin high/low
  - `read_gpio_pin` - Read GPIO pin state
  - `get_gpio_status` - Get GPIO controller status
  - `list_valid_gpio_pins` - List available GPIO pins
- **Resources**:
  - `gpio://status` - GPIO controller status
  - `gpio://pins` - Valid GPIO pins information
  - `gpio://hardware` - Raspberry Pi hardware info

### 2. **MCP Client** (`mcp_client.py`)
- **Purpose**: Client library for communicating with MCP GPIO server
- **Features**:
  - Asynchronous MCP client (`MCPGPIOClient`)
  - Synchronous wrapper for Flask integration (`SyncMCPGPIOClient`)
  - JSON-RPC communication over stdio
  - Automatic server process management

### 3. **Enhanced Flask Backend** (`app.py`)
- **Purpose**: Web server with dual-mode GPIO support
- **Modes**:
  - **MCP Mode**: Uses MCP client to communicate with GPIO server
  - **Direct Mode**: Falls back to direct GPIO control
  - **None Mode**: No GPIO functionality available
- **Features**:
  - Automatic mode detection and fallback
  - ChatGPT integration with structured GPIO commands
  - RESTful API endpoints for GPIO control

## 🚀 **Benefits of MCP Architecture**

### **1. Modularity**
- GPIO server can be reused by multiple applications
- Clean separation between GPIO hardware and business logic
- Easy to add new MCP servers for different hardware components

### **2. Scalability**
- Multiple MCP servers can run simultaneously
- Easy to distribute GPIO control across different processes
- Supports complex multi-component systems

### **3. Standardization**
- Uses industry-standard MCP protocol
- Structured tool calling with JSON schemas
- Consistent API across different hardware components

### **4. Flexibility**
- ChatGPT gets structured tools via MCP
- Easy to extend with new GPIO operations
- Support for both sync and async operations

### **5. Robustness**
- Automatic fallback to direct GPIO mode
- Process isolation for GPIO operations
- Better error handling and recovery

## 🛠️ **Usage Examples**

### **Starting the MCP GPIO Server**
```bash
# Run the standalone MCP GPIO server
python3 mcp_gpio_server.py
```

### **Using the MCP Client Directly**
```python
from mcp_client import SyncMCPGPIOClient

client = SyncMCPGPIOClient()

# Set GPIO pin 18 high
result = client.set_gpio_pin(18, "high")
print(result)

# Read GPIO pin state
result = client.read_gpio_pin(18)
print(result)

# Get GPIO status
status = client.get_gpio_status()
print(status)
```

### **Async MCP Client Usage**
```python
import asyncio
from mcp_client import MCPGPIOClient

async def gpio_operations():
    client = MCPGPIOClient()
    async with client.connect():
        result = await client.set_gpio_pin(18, "high")
        print(result)

asyncio.run(gpio_operations())
```

### **Flask Integration**
The Flask backend automatically detects and uses MCP mode when available:

```python
# The backend automatically chooses the best available mode:
# 1. MCP mode (preferred)
# 2. Direct GPIO mode (fallback)
# 3. No GPIO mode (error handling)
```

## 🧪 **Testing**

### **Comprehensive Test Suite**
```bash
# Run the complete MCP GPIO test suite
python3 test_mcp_gpio.py
```

### **Individual Component Tests**
```bash
# Test MCP client only
python3 mcp_client.py

# Test MCP server only
python3 mcp_gpio_server.py

# Test original GPIO functionality
python3 gpio_test.py
```

## 🔧 **Configuration**

### **MCP Server Configuration**
The MCP server can be configured by modifying `mcp_gpio_server.py`:

```python
# Valid GPIO pins (BCM numbering)
valid_pins = [4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]

# Server information
server_name = "raspberry-pi-gpio"
server_version = "1.0.0"
```

### **MCP Client Configuration**
The client can be configured with custom server commands:

```python
client = MCPGPIOClient(server_command=["python3", "mcp_gpio_server.py"])
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **MCP Server Not Starting**
   - Check if all dependencies are installed: `pip3 install -r requirements.txt`
   - Verify RPi.GPIO is available: `python3 -c "import RPi.GPIO"`
   - Run with sudo if needed: `sudo python3 mcp_gpio_server.py`

2. **MCP Client Connection Issues**
   - Ensure the server command path is correct
   - Check for port conflicts or permission issues
   - Verify JSON-RPC communication is working

3. **GPIO Operations Failing**
   - Check GPIO pin numbers (use BCM numbering)
   - Verify hardware connections
   - Ensure pins are not already in use

### **Debug Mode**
Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 **Future Enhancements**

### **Planned Features**
1. **Multiple Hardware Support**: Add MCP servers for sensors, motors, displays
2. **Network MCP**: Support MCP over TCP/IP for distributed systems
3. **GPIO Monitoring**: Real-time GPIO state monitoring and events
4. **Hardware Discovery**: Automatic detection of connected hardware
5. **Configuration Management**: Dynamic GPIO pin configuration
6. **Performance Optimization**: Batch GPIO operations and caching

### **Extension Points**
- Add new tools to the MCP server for advanced GPIO operations
- Implement custom MCP resources for hardware-specific data
- Create specialized MCP clients for different use cases
- Integrate with other MCP servers for complex automation

## 📚 **References**

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Raspberry Pi GPIO Documentation](https://www.raspberrypi.org/documentation/usage/gpio/)
- [RPi.GPIO Library Documentation](https://pypi.org/project/RPi.GPIO/)

This MCP-based architecture provides a solid foundation for building complex IoT and automation systems with your Raspberry Pi 400!
