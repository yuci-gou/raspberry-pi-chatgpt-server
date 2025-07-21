# ChatGPT Web Server for Raspberry Pi 400

A simple Python web server that provides a web interface to interact with OpenAI's ChatGPT API. Users can ask questions in plain English through a web browser, and the server forwards the questions to ChatGPT and returns the responses.

## Features

- 🤖 Simple web interface for ChatGPT interaction
- 🚀 Flask-based Python backend
- 🌐 RESTful API endpoint for chat requests
- 📱 Responsive design that works on mobile devices
- 🍓 Optimized for Raspberry Pi 400
- ⚡ **GPIO Control via Natural Language** - Control Raspberry Pi GPIO pins using plain English
- 🔧 Direct GPIO API endpoints for advanced control
- 📊 Real-time GPIO status monitoring
- ❌ No authentication required (as requested)

## How Everything Works Together

### Architecture Overview

This project uses a **Model Context Protocol (MCP)** architecture to enable seamless communication between ChatGPT and Raspberry Pi GPIO hardware. Here's how all the components work together:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Flask Server   │    │  OpenAI ChatGPT │
│                 │◄──►│     (app.py)     │◄──►│      API        │
│  - User Input   │    │  - Web Interface │    │  - NL Processing│
│  - GPIO Status  │    │  - GPIO Detection│    │  - GPIO Commands│
└─────────────────┘    └──────────┬───────┘    └─────────────────┘
                                  │
                         ┌────────▼────────┐
                         │   MCP Client    │
                         │ (mcp_client.py) │
                         │ - Request Mgmt  │
                         │ - Threading     │
                         └────────┬────────┘
                                  │ JSON-RPC
                         ┌────────▼────────┐
                         │  GPIO Server    │
                         │(mcp_gpio_server)│
                         │ - Pin Control   │
                         │ - State Mgmt    │
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │ Hardware Layer  │
                         │(freenove_board) │
                         │ - RPi.GPIO      │
                         │ - Pin Interface │
                         └─────────────────┘
```

### Component Interaction Flow

#### 1. **User Interaction**
```
User types: "Turn on LED on pin 18"
   ↓
Web Interface (index.html) sends POST to /api/chat
```

#### 2. **Natural Language Processing**
```
Flask App (app.py) receives request
   ↓
Detects GPIO keywords ("turn on", "pin", "LED")
   ↓
Sends to ChatGPT with specialized GPIO prompt
   ↓
ChatGPT returns structured JSON command:
{
  "gpio_command": true,
  "action": "set_output", 
  "pin": 18,
  "state": "high"
}
```

#### 3. **Command Execution**
```
Flask App parses JSON command
   ↓
Calls mcp_gpio_client.set_gpio_pin(18, "high")
   ↓
MCP Client (mcp_client_fixed.py) starts GPIO server
   ↓
Sends JSON-RPC request to GPIO server
   ↓
GPIO server processes command via freenove_projects_board.py
   ↓
RPi.GPIO sets physical pin 18 HIGH
```

#### 4. **Response Chain**
```
Hardware operation completes
   ↓
GPIO server returns success JSON
   ↓
MCP client receives response
   ↓
Flask app combines ChatGPT answer + GPIO result
   ↓
Web interface displays both text and GPIO status
```

### Key Components Explained

#### **Flask Web Server (`app.py`)**
- **Role**: Main coordinator and web interface
- **Functions**: 
  - Serves web interface at `/`
  - Handles chat requests at `/api/chat`
  - Detects GPIO commands in natural language
  - Manages OpenAI API communication
  - Processes GPIO responses and error handling

#### **MCP Client (`mcp_client.py` + `mcp_client_fixed.py`)**
- **Role**: Bridge between Flask and GPIO server
- **Functions**:
  - Starts/stops GPIO server subprocess
  - Manages JSON-RPC communication
  - Handles threading for non-blocking operations
  - Provides synchronous API for Flask integration
  - Parses complex MCP response structures

#### **GPIO Server (`mcp_gpio_server.py`)**
- **Role**: JSON-RPC server for GPIO operations
- **Functions**:
  - Receives structured GPIO commands
  - Validates pin numbers and states
  - Interfaces with hardware layer
  - Returns detailed operation results
  - Handles multiple concurrent requests

#### **Hardware Interface (`freenove_projects_board.py`)**
- **Role**: Direct hardware abstraction layer
- **Functions**:
  - Wraps RPi.GPIO library
  - Manages pin initialization and cleanup
  - Provides safe GPIO operations
  - Handles board-specific configurations

#### **Web Interface (`templates/index.html`)**
- **Role**: User interaction frontend
- **Functions**:
  - Responsive chat interface
  - Real-time GPIO status display
  - Error handling and user feedback
  - AJAX communication with Flask backend

### Communication Protocols

#### **HTTP/REST API**
```
Browser ←→ Flask Server
- POST /api/chat (user questions)
- GET /api/gpio/status (GPIO status)
- POST /api/gpio (direct GPIO control)
```

#### **JSON-RPC 2.0**
```
MCP Client ←→ GPIO Server
- initialize (server setup)
- tools/list (available operations)
- tools/call (GPIO commands)
```

#### **Subprocess Communication**
```
Flask App ←→ MCP Client ←→ GPIO Server
- stdin/stdout for JSON-RPC messages
- stderr for server status and logging
- Threading for non-blocking operations
```

### Data Flow Example

**Complete flow for "Turn off pin 17":**

1. **User Input**: Types command in web browser
2. **Detection**: Flask detects GPIO keywords
3. **AI Processing**: ChatGPT generates: `{"gpio_command": true, "action": "set_output", "pin": 17, "state": "low"}`
4. **Command Parsing**: Flask extracts pin=17, state="low"
5. **MCP Request**: Client sends JSON-RPC to server
6. **Hardware Control**: Server calls `set_gpio(17, False)`
7. **Response**: Server returns `{"success": true, "message": "GPIO pin 17 successfully set to LOW", "pin": 17, "state": "LOW", "gpio_value": false}`
8. **Result Processing**: Flask combines ChatGPT response + GPIO result
9. **User Feedback**: Browser displays both text explanation and GPIO status

### Error Handling & Recovery

- **Connection Issues**: MCP client automatically retries with timeouts
- **Invalid Pins**: GPIO server validates pin numbers before operations
- **Hardware Errors**: Safe cleanup and error reporting
- **Process Management**: Automatic server restart on failures
- **User Feedback**: Clear error messages in web interface

### Performance Optimizations

- **Threading**: Non-blocking GPIO operations don't freeze web interface
- **Connection Pooling**: MCP client reuses server connections
- **Caching**: GPIO status cached to reduce hardware queries
- **Lightweight Protocol**: JSON-RPC minimizes communication overhead

This architecture ensures reliable, fast, and user-friendly GPIO control through natural language, making hardware interaction as simple as having a conversation with ChatGPT!

## Prerequisites

- Raspberry Pi 400 with Raspberry Pi OS
- Python 3.7 or higher
- Internet connection
- OpenAI API key

## Installation & Setup

### 1. Clone or Download the Project

```bash
# If you have git installed
git clone <repository-url>
cd raspberry-pi-chatgpt-server

# Or download and extract the files to a folder
```

### 2. Install Python Dependencies

```bash
# Install pip if not already installed
sudo apt update
sudo apt install python3-pip

# Install required packages
pip3 install -r requirements.txt
```

### 3. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the API key

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file and add your OpenAI API key
nano .env
```

Replace `your_openai_api_key_here` with your actual OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Running the Application

### Method 1: Development Mode (Recommended for testing)

```bash
# Run the Flask development server
python3 app.py
```

The server will start on `http://0.0.0.0:5000` and will be accessible from any device on your local network.

### Method 2: Production Mode with Gunicorn

```bash
# Install gunicorn (already in requirements.txt)
pip3 install gunicorn

# Run with gunicorn for better performance
gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
```

## Accessing the Application

1. **On the Raspberry Pi itself:**
   - Open a web browser and go to `http://localhost:5000`

2. **From other devices on the same network:**
   - Find your Raspberry Pi's IP address: `hostname -I`
   - Open a web browser and go to `http://[PI_IP_ADDRESS]:5000`
   - Example: `http://192.168.1.100:5000`

## API Endpoints

### Chat Endpoint
- **URL:** `/api/chat`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Body:**
  ```json
  {
    "question": "Your question here"
  }
  ```
- **Response:**
  ```json
  {
    "question": "Your question here",
    "answer": "ChatGPT's response",
    "success": true
  }
  ```

### Health Check
- **URL:** `/health`
- **Method:** `GET`
- **Response:**
  ```json
  {
    "status": "healthy",
    "message": "ChatGPT server is running",
    "gpio_available": true
  }
  ```

### GPIO Control Endpoint
- **URL:** `/api/gpio`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Body for setting output:**
  ```json
  {
    "action": "set_output",
    "pin": 18,
    "state": "high"
  }
  ```
- **Body for reading input:**
  ```json
  {
    "action": "read_input",
    "pin": 18
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "GPIO pin 18 successfully set to HIGH",
    "pin": 18,
    "state": "HIGH",
    "gpio_value": true
  }
  ```

### GPIO Status Endpoint
- **URL:** `/api/gpio/status`
- **Method:** `GET`
- **Response:**
  ```json
  {
    "initialized": true,
    "active_pins": [18, 22, 24],
    "pin_count": 3,
    "gpio_available": true
  }
  ```

## GPIO Control via Natural Language

### 🎯 **NEW FEATURE**: Control GPIO pins using plain English!

You can now control Raspberry Pi GPIO pins by asking ChatGPT in natural language. The system automatically detects GPIO commands and executes them.

#### Example Commands:
- "Turn on LED on pin 18"
- "Set pin 22 high"
- "Turn off the light on pin 24"
- "Switch pin 18 to low"
- "Activate pin 17"

#### How it Works:
1. **Detection**: The system detects GPIO-related keywords in your question
2. **ChatGPT Processing**: ChatGPT generates structured GPIO commands in JSON format
3. **Execution**: The backend parses the JSON and executes the GPIO command
4. **Feedback**: You get both ChatGPT's response and GPIO execution results

#### Valid GPIO Pins (BCM numbering):
`4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27`

## Project Structure

```
raspberry-pi-chatgpt-server/
├── app.py                      # 🚀 Main Flask web server
│                              #    - Handles web requests and ChatGPT integration
│                              #    - Detects GPIO commands in natural language
│                              #    - Coordinates between web interface and GPIO
│
├── mcp_client.py              # 🔌 GPIO Client Wrapper
│                              #    - Provides simple GPIO interface for Flask
│                              #    - Manages connection to GPIO server
│                              #    - Handles response parsing and error handling
│
├── mcp_client_fixed.py        # ⚡ Robust GPIO Client Implementation  
│                              #    - Threading-based subprocess communication
│                              #    - Non-blocking GPIO operations
│                              #    - Reliable JSON-RPC message handling
│
├── mcp_gpio_server.py         # 🖥️  GPIO Server (JSON-RPC)
│                              #    - Processes GPIO commands via Model Context Protocol
│                              #    - Validates pin operations and manages state
│                              #    - Interfaces with hardware abstraction layer
│
├── freenove_projects_board.py # 🔧 Hardware GPIO Interface
│                              #    - Direct RPi.GPIO hardware control
│                              #    - Pin setup, cleanup, and safe operations
│                              #    - Board-specific GPIO configurations
│
├── templates/
│   └── index.html             # 🌐 Web User Interface
│                              #    - Responsive chat interface with GPIO status
│                              #    - Real-time feedback and error handling
│                              #    - AJAX communication with Flask backend
│
├── requirements.txt           # 📦 Python Dependencies
├── .env.example              # 🔑 Environment Variables Template  
├── .env                      # 🔒 Your Actual Environment Variables (create this)
├── .gitignore               # 🚫 Git Ignore Rules
├── README.md                # 📖 This Documentation
├── PROJECT_STRUCTURE.md     # 📋 Detailed Project Overview
└── MCP_ARCHITECTURE.md      # 🏗️  Model Context Protocol Details
```

### File Relationships

```
Web Browser
    ↕️ HTTP/AJAX
📄 templates/index.html
    ↕️ Flask Routes  
🚀 app.py
    ↕️ Function Calls
🔌 mcp_client.py  
    ↕️ Import/Threading
⚡ mcp_client_fixed.py
    ↕️ JSON-RPC Subprocess
🖥️ mcp_gpio_server.py
    ↕️ Hardware Calls
🔧 freenove_projects_board.py
    ↕️ RPi.GPIO Library
🔗 Raspberry Pi Hardware
```

This clean, modular structure ensures:
- **Separation of Concerns**: Each file has a specific, well-defined role
- **Easy Maintenance**: Components can be updated independently  
- **Reliable Communication**: Robust inter-process communication protocols
- **Scalability**: New GPIO features can be added without affecting core chat functionality

## Testing GPIO Functionality

### Method 1: Using the Web Interface
1. Open the web interface in your browser
2. Check the GPIO status indicator (should show "Available" on Raspberry Pi)
3. Try these example commands:
   - "Turn on LED on pin 18"
   - "Set pin 22 high"
   - "Turn off pin 18"
   - "Switch pin 24 to low"

### Method 2: Using the Test Script
```bash
# Run the GPIO test script
python3 gpio_test.py
```

This script will:
- Test basic GPIO operations
- Test multiple pins
- Test error handling
- Show GPIO status
- Optional LED blink demo

### Method 3: Direct API Testing
```bash
# Set pin 18 high
curl -X POST http://localhost:5000/api/gpio \
  -H "Content-Type: application/json" \
  -d '{"action": "set_output", "pin": 18, "state": "high"}'

# Check GPIO status
curl http://localhost:5000/api/gpio/status
```

### Hardware Setup for Testing
1. **LED Test Circuit:**
   - Connect LED positive leg to GPIO pin (e.g., pin 18)
   - Connect LED negative leg to ground through a 220Ω resistor
   - Use physical pins: GPIO 18 = Pin 12, Ground = Pin 6

2. **GPIO Pin Mapping (BCM to Physical):**
   - GPIO 18 → Physical Pin 12
   - GPIO 22 → Physical Pin 15
   - GPIO 24 → Physical Pin 18
   - Ground → Physical Pins 6, 9, 14, 20, 25, 30, 34, 39

## Troubleshooting

### Common Issues

1. **"OpenAI API key not configured" error:**
   - Make sure you created the `.env` file with your API key
   - Check that the API key is valid and has credits

2. **"Failed to connect to the server" error:**
   - Ensure the Flask server is running
   - Check if port 5000 is available
   - Verify firewall settings if accessing from other devices

3. **"GPIO functionality not available" error:**
   - Make sure you're running on a Raspberry Pi
   - Install RPi.GPIO: `pip3 install RPi.GPIO`
   - Run with sudo if needed: `sudo python3 app.py`
   - Check that GPIO pins are not already in use

4. **Import errors:**
   - Make sure all dependencies are installed: `pip3 install -r requirements.txt`
   - Check Python version: `python3 --version`

5. **Permission denied errors:**
   - Try running with `sudo` if needed for GPIO access
   - Or use a different port: `python3 app.py --port 8080`

6. **GPIO pin not responding:**
   - Check your wiring connections
   - Verify you're using the correct pin numbers (BCM vs Physical)
   - Test with the `gpio_test.py` script first
   - Make sure the pin is not reserved for other functions

### Checking Logs

The Flask development server will show logs in the terminal. Look for error messages there if something isn't working.

## Security Notes

- This application has no authentication as requested
- Only run on trusted networks
- Consider adding authentication for production use
- Keep your OpenAI API key secure and never commit it to version control

## Customization

- Modify `templates/index.html` to change the web interface
- Adjust the ChatGPT model or parameters in `app.py`
- Add more API endpoints as needed

## Performance Tips for Raspberry Pi 400

- Use gunicorn for better performance in production
- Consider limiting the number of concurrent requests
- Monitor CPU and memory usage
- Use a lightweight browser for testing

## License

This project is open source. Feel free to modify and distribute as needed.
