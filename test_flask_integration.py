#!/usr/bin/env python3
"""
Test Flask integration with GPIO client
"""

import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("flask-integration-test")

def test_gpio_client_in_flask_context():
    """Test GPIO client when imported in Flask context"""
    logger.info("🧪 Testing GPIO client in Flask-like context...")
    
    try:
        # Import Flask first (like in app.py)
        from flask import Flask
        app = Flask(__name__)
        
        # Now import GPIO client (like in app.py)
        from simple_gpio_client import http_gpio_client
        
        logger.info("✅ GPIO client imported successfully in Flask context")
        
        # Test a simple GPIO operation
        logger.info("🔧 Testing GPIO operation...")
        
        try:
            # This should trigger service startup
            result = http_gpio_client.set_gpio_pin(17, "high")
            logger.info(f"GPIO result: {result}")
            
            if result.get("success"):
                logger.info("✅ GPIO operation successful!")
                return True
            else:
                logger.error(f"❌ GPIO operation failed: {result.get('message')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ GPIO operation exception: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Flask integration test failed: {e}")
        return False

def test_direct_client():
    """Test GPIO client directly (not in Flask context)"""
    logger.info("🧪 Testing GPIO client directly...")
    
    try:
        from simple_gpio_client import SimpleHTTPGPIOClient
        
        with SimpleHTTPGPIOClient() as client:
            result = client.set_gpio_pin(17, "high")
            logger.info(f"Direct client result: {result}")
            
            if result.get("success"):
                logger.info("✅ Direct client successful!")
                return True
            else:
                logger.error(f"❌ Direct client failed: {result.get('message')}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Direct client test failed: {e}")
        return False

def check_port_conflicts():
    """Check for port conflicts"""
    logger.info("🔍 Checking for port conflicts...")
    
    import socket
    
    # Check if common ports are in use
    ports_to_check = [5000, 5001, 5002, 5003, 5004, 5005]
    
    for port in ports_to_check:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                logger.info(f"✅ Port {port} is available")
        except OSError as e:
            logger.warning(f"⚠️ Port {port} is in use: {e}")

if __name__ == "__main__":
    logger.info("🚀 Starting Flask integration tests...")
    
    # Test 1: Check port conflicts
    logger.info("\n" + "="*50)
    logger.info("TEST 1: Port Conflicts")
    logger.info("="*50)
    check_port_conflicts()
    
    # Test 2: Direct client
    logger.info("\n" + "="*50)
    logger.info("TEST 2: Direct GPIO Client")
    logger.info("="*50)
    direct_works = test_direct_client()
    
    # Test 3: Flask context
    logger.info("\n" + "="*50)
    logger.info("TEST 3: Flask Integration")
    logger.info("="*50)
    flask_works = test_gpio_client_in_flask_context()
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("SUMMARY")
    logger.info("="*50)
    logger.info(f"Direct client works: {direct_works}")
    logger.info(f"Flask integration works: {flask_works}")
    
    if direct_works and not flask_works:
        logger.info("💡 Direct client works but Flask integration fails - Flask context issue")
    elif not direct_works:
        logger.info("💡 Direct client fails - GPIO client/service issue")
    elif flask_works:
        logger.info("✅ Everything works - issue might be elsewhere")
