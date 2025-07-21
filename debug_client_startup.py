#!/usr/bin/env python3
"""
Debug script to test GPIO client startup
"""

import logging
from mcp_client import SimpleGPIOClient

# Configure detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("debug")

def test_client_startup():
    """Test GPIO client startup with detailed logging"""
    logger.info("🐛 Starting GPIO client startup debug test...")
    
    client = SimpleGPIOClient()
    
    try:
        logger.info("Starting server...")
        client.start_server()
        logger.info("✅ Server started successfully!")
        
        # Try a simple operation
        status = client.get_gpio_status()
        logger.info(f"GPIO status: {status}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Stopping server...")
        client.stop_server()
        logger.info("✅ Debug test complete")

if __name__ == "__main__":
    test_client_startup()
