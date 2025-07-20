from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
import json
import re
from dotenv import load_dotenv
try:
    from freenove_projects_board import set_gpio, read_gpio, cleanup_gpio
    GPIO_AVAILABLE = True
    print("✅ GPIO functionality loaded successfully!")
except ImportError as e:
    GPIO_AVAILABLE = False
    print(f"❌ Warning: GPIO functionality not available. Import error: {e}")
    print("   Troubleshooting steps:")
    print("   1. Make sure you're running on a Raspberry Pi")
    print("   2. Install RPi.GPIO: pip3 install RPi.GPIO")
    print("   3. Try running with sudo: sudo python3 app.py")
    print("   4. Check if RPi.GPIO is in your virtual environment")
except Exception as e:
    GPIO_AVAILABLE = False
    print(f"❌ Unexpected error loading GPIO: {e}")

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint to handle chat requests"""
    try:
        # Get the question from the request
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'No question provided'}), 400
        
        question = data['question']
        
        # Check if API key is configured
        if not openai.api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Check if this is a GPIO-related question
        gpio_command = detect_gpio_command(question)
        
        if gpio_command:
            # Create a specialized prompt for GPIO commands
            system_prompt = create_gpio_system_prompt()
            user_prompt = f"User request: {question}\n\nPlease provide a response that includes GPIO command instructions."
        else:
            # Regular chat prompt
            system_prompt = "You are a helpful assistant for a Raspberry Pi 400 system."
            user_prompt = question
        
        # Make request to OpenAI ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.3 if gpio_command else 0.7
        )
        
        # Extract the response
        answer = response.choices[0].message.content.strip()
        
        # Process GPIO commands if detected
        gpio_result = None
        if gpio_command and GPIO_AVAILABLE:
            gpio_result = process_gpio_response(answer)
        
        response_data = {
            'question': question,
            'answer': answer,
            'success': True,
            'gpio_detected': bool(gpio_command),
            'gpio_available': GPIO_AVAILABLE
        }
        
        if gpio_result:
            response_data['gpio_result'] = gpio_result
        
        return jsonify(response_data)
        
    except openai.error.AuthenticationError:
        return jsonify({'error': 'Invalid OpenAI API key'}), 401
    except openai.error.RateLimitError:
        return jsonify({'error': 'OpenAI API rate limit exceeded'}), 429
    except openai.error.APIError as e:
        return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def detect_gpio_command(question: str) -> bool:
    """Detect if the question is asking for GPIO control
    
    Args:
        question (str): User's question
        
    Returns:
        bool: True if GPIO command detected
    """
    gpio_keywords = [
        'gpio', 'pin', 'led', 'light', 'turn on', 'turn off', 'set high', 'set low',
        'switch on', 'switch off', 'activate', 'deactivate', 'digital output',
        'output high', 'output low', 'pin high', 'pin low'
    ]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in gpio_keywords)

def create_gpio_system_prompt() -> str:
    """Create system prompt for GPIO commands
    
    Returns:
        str: System prompt for GPIO operations
    """
    return """You are a Raspberry Pi 400 GPIO assistant. When users ask to control GPIO pins, provide helpful responses and include structured GPIO commands.

For GPIO control requests, always include a JSON command block in your response using this format:
```json
{
    "gpio_command": true,
    "action": "set_output",
    "pin": [pin_number],
    "state": "[high/low/on/off]"
}
```

Valid GPIO pins (BCM numbering): 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27

Examples:
- "Turn on LED on pin 18" → Include: {"gpio_command": true, "action": "set_output", "pin": 18, "state": "high"}
- "Set pin 22 low" → Include: {"gpio_command": true, "action": "set_output", "pin": 22, "state": "low"}

Always explain what you're doing and include the JSON command block."""

def process_gpio_response(response: str) -> dict:
    """Process ChatGPT response for GPIO commands
    
    Args:
        response (str): ChatGPT response text
        
    Returns:
        dict: GPIO execution result
    """
    try:
        # Look for JSON command blocks in the response
        json_pattern = r'```json\s*({.*?})\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if not matches:
            return {"success": False, "message": "No GPIO command found in response"}
        
        # Parse the first JSON command found
        command_json = json.loads(matches[0])
        
        if not command_json.get('gpio_command'):
            return {"success": False, "message": "Not a GPIO command"}
        
        action = command_json.get('action')
        pin = command_json.get('pin')
        state = command_json.get('state')
        
        if action == 'set_output' and pin is not None and state is not None:
            # Execute the GPIO command
            result = set_gpio(int(pin), str(state))
            return result
        else:
            return {
                "success": False, 
                "message": "Invalid GPIO command format",
                "parsed_command": command_json
            }
            
    except json.JSONDecodeError as e:
        return {"success": False, "message": f"Failed to parse GPIO command: {e}"}
    except Exception as e:
        return {"success": False, "message": f"Error processing GPIO command: {e}"}

@app.route('/api/gpio', methods=['POST'])
def gpio_control():
    """Direct GPIO control endpoint"""
    if not GPIO_AVAILABLE:
        return jsonify({'error': 'GPIO functionality not available'}), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        action = data.get('action')
        pin = data.get('pin')
        state = data.get('state')
        
        if action == 'set_output':
            if pin is None or state is None:
                return jsonify({'error': 'Pin and state required for set_output'}), 400
            
            result = set_gpio(int(pin), str(state))
            return jsonify(result)
        
        elif action == 'read_input':
            if pin is None:
                return jsonify({'error': 'Pin required for read_input'}), 400
            
            result = read_gpio(int(pin))
            return jsonify(result)
        
        else:
            return jsonify({'error': 'Invalid action. Use set_output or read_input'}), 400
            
    except Exception as e:
        return jsonify({'error': f'GPIO control error: {str(e)}'}), 500

@app.route('/api/gpio/status', methods=['GET'])
def gpio_status():
    """Get GPIO system status"""
    try:
        if GPIO_AVAILABLE:
            from freenove_projects_board import gpio_controller
            status = gpio_controller.get_pin_status()
            status['gpio_available'] = True
        else:
            status = {
                'gpio_available': False,
                'message': 'GPIO functionality not available'
            }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': f'Status error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'message': 'ChatGPT server is running',
        'gpio_available': GPIO_AVAILABLE
    })

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
