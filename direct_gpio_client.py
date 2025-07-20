#!/usr/bin/env python3
"""
Direct GPIO client that doesn't use subprocess/HTTP
Much simpler and more reliable for Flask integration
"""

import logging
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("direct-gpio")

class DirectGPIOClient:
    """Direct GPIO client without subprocess complexity"""
    
    def __init__(self):
        self.gpio_available = False
        self.gpio_controller = None
        self._initialize_gpio()
        logger.info("🔌 Direct GPIO Client initialized")
    
    def _initialize_gpio(self):
        """Initialize GPIO functionality"""
        try:
            # Import GPIO controller directly
            from freenove_projects_board import gpio_controller, set_gpio, read_gpio
            self.gpio_controller = gpio_controller
            self.set_gpio = set_gpio
            self.read_gpio = read_gpio
            self.gpio_available = True
            logger.info("✅ GPIO functionality loaded successfully!")
        except ImportError as e:
            self.gpio_available = False
            logger.warning(f"❌ GPIO not available: {e}")
        except Exception as e:
            self.gpio_available = False
            logger.error(f"❌ Unexpected GPIO error: {e}")
    
    def set_gpio_pin(self, pin: int, state: str) -> Dict[str, Any]:
        """Set GPIO pin state"""
        if not self.gpio_available:
            return {"success": False, "message": "GPIO not available"}
        
        try:
            logger.info(f"🔧 Setting pin {pin} to {state}")
            result = self.set_gpio(pin, state)
            logger.info(f"✅ GPIO set result: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ GPIO set error: {e}")
            return {"success": False, "message": f"GPIO set error: {e}"}
    
    def read_gpio_pin(self, pin: int) -> Dict[str, Any]:
        """Read GPIO pin state"""
        if not self.gpio_available:
            return {"success": False, "message": "GPIO not available"}
        
        try:
            logger.info(f"📖 Reading pin {pin}")
            result = self.read_gpio(pin)
            logger.info(f"✅ GPIO read result: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ GPIO read error: {e}")
            return {"success": False, "message": f"GPIO read error: {e}"}
    
    def get_gpio_status(self) -> Dict[str, Any]:
        """Get GPIO status"""
        if not self.gpio_available:
            return {"gpio_available": False, "message": "GPIO not available"}
        
        try:
            logger.info("📊 Getting GPIO status")
            
            # Get status from controller
            if hasattr(self.gpio_controller, 'get_pin_status'):
                status = self.gpio_controller.get_pin_status()
            else:
                status = {"message": "Status method not available"}
            
            # Add system info
            status.update({
                "gpio_available": True,
                "system": "Raspberry Pi 400",
                "gpio_mode": "BCM",
                "client_type": "direct"
            })
            
            logger.info(f"✅ GPIO status: {status}")
            return status
            
        except Exception as e:
            logger.error(f"❌ GPIO status error: {e}")
            return {"success": False, "message": f"GPIO status error: {e}"}
    
    def list_valid_pins(self) -> Dict[str, Any]:
        """List valid GPIO pins"""
        return {
            "valid_pins": [4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
            "numbering_mode": "BCM",
            "total_pins": 17
        }
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        return {
            "tools": [
                {"name": "set_gpio_pin", "description": "Set GPIO pin state"},
                {"name": "read_gpio_pin", "description": "Read GPIO pin state"},
                {"name": "get_gpio_status", "description": "Get GPIO status"}
            ]
        }

# Global instance for Flask app (compatible with existing code)
direct_gpio_client = DirectGPIOClient()

# Test function
def test_direct_gpio_client():
    """Test the direct GPIO client"""
    logger.info("🧪 Testing Direct GPIO Client...")
    
    try:
        # Test tools listing
        tools = direct_gpio_client.list_tools()
        logger.info(f"Available tools: {tools}")
        
        # Test GPIO status
        status = direct_gpio_client.get_gpio_status()
        logger.info(f"GPIO status: {status}")
        
        # Test GPIO operations (if available)
        if direct_gpio_client.gpio_available:
            try:
                result = direct_gpio_client.set_gpio_pin(18, "high")
                logger.info(f"Set pin 18 high: {result}")
                
                state = direct_gpio_client.read_gpio_pin(18)
                logger.info(f"Read pin 18: {state}")
                
            except Exception as e:
                logger.warning(f"GPIO operations failed: {e}")
        else:
            logger.info("GPIO not available - skipping GPIO operations")
        
        logger.info("✅ Direct GPIO client test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Direct GPIO client test failed: {e}")
        return False

if __name__ == "__main__":
    test_direct_gpio_client()
