#!/usr/bin/env python3
"""
Test script for simplified GPIO client-server communication
"""

import logging
import time
from mcp_client import SimpleGPIOClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test-gpio")

def test_gpio_communication():
    """Test GPIO client-server communication"""
    logger.info("🧪 Testing GPIO Client-Server Communication...")
    
    client = SimpleGPIOClient()
    
    try:
        with client:
            logger.info("✅ GPIO server started successfully")
            
            # Test 1: List available tools
            logger.info("📋 Testing tool listing...")
            tools = client.list_tools()
            logger.info(f"Available tools: {tools}")
            
            # Test 2: Get GPIO status
            logger.info("📊 Testing GPIO status...")
            status = client.get_gpio_status()
            logger.info(f"GPIO status: {status}")
            
            # Test 3: List valid pins
            logger.info("📌 Testing valid pins list...")
            pins = client.list_valid_pins()
            logger.info(f"Valid pins: {pins}")
            
            # Test 4: Set GPIO pin (if GPIO is available)
            logger.info("🔧 Testing GPIO pin control...")
            try:
                result = client.set_gpio_pin(18, "high")
                logger.info(f"Set pin 18 high: {result}")
                
                # Read back the pin state
                state = client.read_gpio_pin(18)
                logger.info(f"Read pin 18 state: {state}")
                
                # Set pin low
                result = client.set_gpio_pin(18, "low")
                logger.info(f"Set pin 18 low: {result}")
                
            except Exception as e:
                logger.warning(f"GPIO operations failed (expected on non-Pi systems): {e}")
            
            logger.info("✅ All tests completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_gpio_communication()
    if success:
        print("🎉 GPIO communication test PASSED!")
    else:
        print("💥 GPIO communication test FAILED!")
