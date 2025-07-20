# ChatGPT Web Server for Raspberry Pi 400

A simple Python web server that provides a web interface to interact with OpenAI's ChatGPT API. Users can ask questions in plain English through a web browser, and the server forwards the questions to ChatGPT and returns the responses.

## Features

- 🤖 Simple web interface for ChatGPT interaction
- 🚀 Flask-based Python backend
- 🌐 RESTful API endpoint for chat requests
- 📱 Responsive design that works on mobile devices
- 🍓 Optimized for Raspberry Pi 400
- ❌ No authentication required (as requested)

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
    "message": "ChatGPT server is running"
  }
  ```

## Project Structure

```
raspberry-pi-chatgpt-server/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your actual environment variables (create this)
└── README.md           # This file
```

## Troubleshooting

### Common Issues

1. **"OpenAI API key not configured" error:**
   - Make sure you created the `.env` file with your API key
   - Check that the API key is valid and has credits

2. **"Failed to connect to the server" error:**
   - Ensure the Flask server is running
   - Check if port 5000 is available
   - Verify firewall settings if accessing from other devices

3. **Import errors:**
   - Make sure all dependencies are installed: `pip3 install -r requirements.txt`
   - Check Python version: `python3 --version`

4. **Permission denied errors:**
   - Try running with `sudo` if needed
   - Or use a different port: `python3 app.py --port 8080`

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
