#!/usr/bin/env python3
"""
Debug script to test GPIO service startup directly
"""

import subprocess
import time
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug-gpio")

def test_gpio_service_directly():
    """Test starting the GPIO service directly"""
    logger.info("🧪 Testing GPIO service startup directly...")
    
    try:
        # Start the service process
        logger.info("Starting GPIO service process...")
        process = subprocess.Popen(
            ["python3", "simple_gpio_service.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output for 10 seconds
        port = None
        for i in range(100):  # 10 seconds
            if process.poll() is not None:
                # Process terminated
                stdout_output = process.stdout.read()
                stderr_output = process.stderr.read()
                logger.error(f"❌ Process terminated early!")
                logger.error(f"stdout: {stdout_output}")
                logger.error(f"stderr: {stderr_output}")
                return False
            
            # Try to read a line
            try:
                line = process.stdout.readline()
                if line:
                    line = line.strip()
                    logger.info(f"📥 Service output: {line}")
                    if line.startswith("SERVICE_PORT:"):
                        port = int(line.split(":")[1])
                        logger.info(f"✅ Found port: {port}")
                        break
                    elif line.startswith("SERVICE_ERROR:"):
                        error_msg = line.split(":", 1)[1]
                        logger.error(f"❌ Service error: {error_msg}")
                        return False
            except:
                pass
            
            time.sleep(0.1)
        
        if not port:
            logger.error("❌ No port found within timeout")
            process.terminate()
            return False
        
        # Test health check
        logger.info(f"🔍 Testing health check on port {port}...")
        time.sleep(2.0)  # Give Flask more time
        
        for attempt in range(10):
            try:
                response = requests.get(f"http://127.0.0.1:{port}/health", timeout=3)
                if response.status_code == 200:
                    logger.info(f"✅ Health check passed on attempt {attempt + 1}")
                    logger.info(f"Response: {response.json()}")
                    
                    # Test GPIO status
                    try:
                        status_response = requests.get(f"http://127.0.0.1:{port}/gpio/status", timeout=3)
                        logger.info(f"GPIO Status: {status_response.json()}")
                    except Exception as e:
                        logger.warning(f"GPIO status failed: {e}")
                    
                    process.terminate()
                    return True
                else:
                    logger.warning(f"Health check attempt {attempt + 1} failed: {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Health check attempt {attempt + 1} failed: {e}")
            
            time.sleep(1.0)
        
        logger.error("❌ All health check attempts failed")
        process.terminate()
        return False
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def test_simple_flask():
    """Test a minimal Flask app to see if Flask works at all"""
    logger.info("🧪 Testing minimal Flask app...")
    
    # Create a minimal Flask test script
    test_script = '''
import sys
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/test')
def test():
    return jsonify({"status": "ok", "message": "Flask is working"})

if __name__ == "__main__":
    print("FLASK_PORT:5002", flush=True)
    app.run(host='127.0.0.1', port=5002, debug=False, use_reloader=False)
'''
    
    # Write test script
    with open("test_flask_minimal.py", "w") as f:
        f.write(test_script)
    
    try:
        # Start the test Flask app
        process = subprocess.Popen(
            ["python3", "test_flask_minimal.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Wait for port
        port_found = False
        for i in range(50):
            if process.poll() is not None:
                stdout_output = process.stdout.read()
                stderr_output = process.stderr.read()
                logger.error(f"❌ Flask test process terminated early!")
                logger.error(f"stdout: {stdout_output}")
                logger.error(f"stderr: {stderr_output}")
                return False
            
            try:
                line = process.stdout.readline()
                if line and line.strip().startswith("FLASK_PORT:"):
                    port_found = True
                    logger.info("✅ Flask test app started")
                    break
            except:
                pass
            
            time.sleep(0.1)
        
        if not port_found:
            logger.error("❌ Flask test app did not start")
            process.terminate()
            return False
        
        # Test the Flask app
        time.sleep(2.0)
        try:
            response = requests.get("http://127.0.0.1:5002/test", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Flask test successful: {response.json()}")
                process.terminate()
                return True
            else:
                logger.error(f"❌ Flask test failed: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Flask test request failed: {e}")
        
        process.terminate()
        return False
        
    except Exception as e:
        logger.error(f"❌ Flask test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting GPIO service debug tests...")
    
    # Test 1: Minimal Flask
    logger.info("\n" + "="*50)
    logger.info("TEST 1: Minimal Flask App")
    logger.info("="*50)
    flask_works = test_simple_flask()
    
    # Test 2: GPIO Service
    logger.info("\n" + "="*50)
    logger.info("TEST 2: GPIO Service")
    logger.info("="*50)
    gpio_works = test_gpio_service_directly()
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("SUMMARY")
    logger.info("="*50)
    logger.info(f"Flask works: {flask_works}")
    logger.info(f"GPIO service works: {gpio_works}")
    
    if flask_works and not gpio_works:
        logger.info("💡 Flask works but GPIO service doesn't - check GPIO service code")
    elif not flask_works:
        logger.info("💡 Flask itself has issues - check Python/Flask installation")
    elif gpio_works:
        logger.info("✅ Everything works - issue might be in client timing/logic")
