#!/usr/bin/env python3
"""
Simple HTTP-based GPIO service for Raspberry Pi 400
Much more reliable than JSON-RPC over stdio
"""

from flask import Flask, request, jsonify
import logging
import sys
import threading
import time

# Import GPIO controller
try:
    from freenove_projects_board import gpio_controller, set_gpio, read_gpio, cleanup_gpio
    GPIO_AVAILABLE = True
    print("✅ GPIO functionality loaded successfully!", file=sys.stderr)
except ImportError as e:
    GPIO_AVAILABLE = False
    print(f"❌ GPIO not available: {e}", file=sys.stderr)

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("gpio-service")

# Create Flask app
app = Flask(__name__)

@app.route('/gpio/set', methods=['POST'])
def set_gpio_pin():
    """Set GPIO pin state"""
    if not GPIO_AVAILABLE:
        return jsonify({"success": False, "message": "GPIO not available"}), 500
    
    try:
        data = request.get_json()
        pin = data.get('pin')
        state = data.get('state')
        
        if pin is None or state is None:
            return jsonify({"success": False, "message": "Pin and state required"}), 400
        
        result = set_gpio(int(pin), str(state))
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error setting GPIO pin: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/gpio/read', methods=['POST'])
def read_gpio_pin():
    """Read GPIO pin state"""
    if not GPIO_AVAILABLE:
        return jsonify({"success": False, "message": "GPIO not available"}), 500
    
    try:
        data = request.get_json()
        pin = data.get('pin')
        
        if pin is None:
            return jsonify({"success": False, "message": "Pin required"}), 400
        
        result = read_gpio(int(pin))
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error reading GPIO pin: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/gpio/status', methods=['GET'])
def get_gpio_status():
    """Get GPIO status"""
    if not GPIO_AVAILABLE:
        return jsonify({"gpio_available": False, "message": "GPIO not available"})
    
    try:
        status = gpio_controller.get_pin_status()
        status.update({
            "gpio_available": True,
            "system": "Raspberry Pi 400",
            "gpio_mode": "BCM",
            "service_status": "running"
        })
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting GPIO status: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "gpio_available": GPIO_AVAILABLE,
        "service": "GPIO Service"
    })

def run_service():
    """Run the GPIO service"""
    logger.info("🚀 Starting Simple GPIO Service on port 5001...")
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)

if __name__ == "__main__":
    run_service()
