# Raspberry Pi ChatGPT Server - Project Structure

## Core Files

### Main Application
- `app.py` - Flask web server with ChatGPT integration and GPIO control
- `templates/index.html` - Web interface for the ChatGPT server

### GPIO Control System
- `mcp_client.py` - GPIO client wrapper for Flask integration
- `mcp_client_fixed.py` - Robust GPIO client implementation (threading-based)
- `mcp_gpio_server.py` - JSON-RPC GPIO server using MCP protocol
- `freenove_projects_board.py` - Hardware GPIO interface for Raspberry Pi

### Configuration
- `requirements.txt` - Python package dependencies
- `.env.example` - Environment variables template
- `.env` - Your actual environment variables (not in git)
- `.gitignore` - Git ignore rules

### Documentation
- `README.md` - Project documentation
- `MCP_ARCHITECTURE.md` - Model Context Protocol architecture details
- `PROJECT_STRUCTURE.md` - This file

## How It Works

1. **Flask App** (`app.py`) serves a web interface and handles chat requests
2. **ChatGPT Integration** processes user questions via OpenAI API
3. **GPIO Detection** identifies GPIO-related commands in user input
4. **MCP Client** (`mcp_client.py`) provides a simple interface for GPIO operations
5. **Fixed Client** (`mcp_client_fixed.py`) implements robust subprocess communication
6. **GPIO Server** (`mcp_gpio_server.py`) handles actual GPIO pin control
7. **Hardware Interface** (`freenove_projects_board.py`) interfaces with RPi.GPIO

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Run the server
python3 app.py

# Access web interface
# Open browser to http://localhost:5000
```

## GPIO Commands

The system responds to natural language GPIO commands like:
- "Turn on pin 18"
- "Set pin 17 low" 
- "Turn off LED on pin 22"

Valid GPIO pins: 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27
