"""
Freenove Projects Board GPIO Control Module
Provides functions to control Raspberry Pi 400 GPIO pins
"""

try:
    import RPi.GPIO as GPIO
    print("✅ RPi.GPIO imported successfully in freenove_projects_board.py")
except ImportError as e:
    print(f"❌ Failed to import RPi.GPIO in freenove_projects_board.py: {e}")
    print("   This usually means:")
    print("   - RPi.GPIO is not installed in the current Python environment")
    print("   - You're not running on a Raspberry Pi")
    print("   - Permission issues with GPIO access")
    raise
except Exception as e:
    print(f"❌ Unexpected error importing RPi.GPIO: {e}")
    raise

import time
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPIOController:
    """GPIO Controller for Raspberry Pi 400"""
    
    def __init__(self):
        """Initialize GPIO controller"""
        self.initialized = False
        self.active_pins = set()
        
    def initialize_gpio(self):
        """Initialize GPIO settings"""
        try:
            GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
            GPIO.setwarnings(False)  # Disable warnings
            self.initialized = True
            logger.info("GPIO initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")
            raise
    
    def setup_pin(self, pin: int, mode: str = "output") -> bool:
        """Setup a GPIO pin as input or output
        
        Args:
            pin (int): GPIO pin number (BCM numbering)
            mode (str): 'output' or 'input'
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.initialized:
            self.initialize_gpio()
            
        try:
            if mode.lower() == "output":
                GPIO.setup(pin, GPIO.OUT)
                self.active_pins.add(pin)
                logger.info(f"Pin {pin} set up as OUTPUT")
            elif mode.lower() == "input":
                GPIO.setup(pin, GPIO.IN)
                self.active_pins.add(pin)
                logger.info(f"Pin {pin} set up as INPUT")
            else:
                logger.error(f"Invalid mode: {mode}. Use 'output' or 'input'")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to setup pin {pin}: {e}")
            return False
    
    def set_gpio_output(self, pin: int, state: str) -> Dict[str, Any]:
        """Set GPIO pin output high or low
        
        Args:
            pin (int): GPIO pin number (BCM numbering)
            state (str): 'high', 'low', 'on', 'off', '1', '0'
            
        Returns:
            Dict[str, Any]: Result with success status and message
        """
        # Validate pin number
        if not self._is_valid_pin(pin):
            return {
                "success": False,
                "message": f"Invalid pin number: {pin}. Valid pins are 2-27 (excluding 3, 5, 8, 10)",
                "pin": pin,
                "state": state
            }
        
        # Setup pin if not already done
        if pin not in self.active_pins:
            if not self.setup_pin(pin, "output"):
                return {
                    "success": False,
                    "message": f"Failed to setup pin {pin} as output",
                    "pin": pin,
                    "state": state
                }
        
        # Parse state
        try:
            gpio_state = self._parse_state(state)
            if gpio_state is None:
                return {
                    "success": False,
                    "message": f"Invalid state: {state}. Use 'high', 'low', 'on', 'off', '1', or '0'",
                    "pin": pin,
                    "state": state
                }
            
            # Set GPIO output
            GPIO.output(pin, gpio_state)
            state_name = "HIGH" if gpio_state else "LOW"
            
            logger.info(f"GPIO pin {pin} set to {state_name}")
            
            return {
                "success": True,
                "message": f"GPIO pin {pin} successfully set to {state_name}",
                "pin": pin,
                "state": state_name,
                "gpio_value": gpio_state
            }
            
        except Exception as e:
            logger.error(f"Failed to set GPIO pin {pin}: {e}")
            return {
                "success": False,
                "message": f"Error setting GPIO pin {pin}: {str(e)}",
                "pin": pin,
                "state": state
            }
    
    def read_gpio_input(self, pin: int) -> Dict[str, Any]:
        """Read GPIO pin input state
        
        Args:
            pin (int): GPIO pin number (BCM numbering)
            
        Returns:
            Dict[str, Any]: Result with pin state
        """
        if not self._is_valid_pin(pin):
            return {
                "success": False,
                "message": f"Invalid pin number: {pin}",
                "pin": pin
            }
        
        # Setup pin if not already done
        if pin not in self.active_pins:
            if not self.setup_pin(pin, "input"):
                return {
                    "success": False,
                    "message": f"Failed to setup pin {pin} as input",
                    "pin": pin
                }
        
        try:
            state = GPIO.input(pin)
            state_name = "HIGH" if state else "LOW"
            
            return {
                "success": True,
                "message": f"GPIO pin {pin} is {state_name}",
                "pin": pin,
                "state": state_name,
                "gpio_value": state
            }
            
        except Exception as e:
            logger.error(f"Failed to read GPIO pin {pin}: {e}")
            return {
                "success": False,
                "message": f"Error reading GPIO pin {pin}: {str(e)}",
                "pin": pin
            }
    
    def _is_valid_pin(self, pin: int) -> bool:
        """Check if pin number is valid for GPIO output
        
        Args:
            pin (int): Pin number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Valid GPIO pins on Raspberry Pi (BCM numbering)
        # Excluding pins used for I2C (2, 3), UART (14, 15), and SPI (7, 8, 9, 10, 11)
        valid_pins = [4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
        return pin in valid_pins
    
    def _parse_state(self, state: str) -> Optional[bool]:
        """Parse state string to boolean
        
        Args:
            state (str): State string
            
        Returns:
            Optional[bool]: True for high/on, False for low/off, None if invalid
        """
        state_lower = state.lower().strip()
        
        if state_lower in ['high', 'on', '1', 'true']:
            return True
        elif state_lower in ['low', 'off', '0', 'false']:
            return False
        else:
            return None
    
    def get_pin_status(self) -> Dict[str, Any]:
        """Get status of all active pins
        
        Returns:
            Dict[str, Any]: Status of all pins
        """
        status = {
            "initialized": self.initialized,
            "active_pins": list(self.active_pins),
            "pin_count": len(self.active_pins)
        }
        
        return status
    
    def cleanup(self):
        """Clean up GPIO resources"""
        try:
            GPIO.cleanup()
            self.active_pins.clear()
            self.initialized = False
            logger.info("GPIO cleanup completed")
        except Exception as e:
            logger.error(f"Error during GPIO cleanup: {e}")

# Global GPIO controller instance
gpio_controller = GPIOController()

# Convenience functions for external use
def set_gpio_high(pin: int) -> Dict[str, Any]:
    """Set GPIO pin to HIGH
    
    Args:
        pin (int): GPIO pin number
        
    Returns:
        Dict[str, Any]: Result dictionary
    """
    return gpio_controller.set_gpio_output(pin, "high")

def set_gpio_low(pin: int) -> Dict[str, Any]:
    """Set GPIO pin to LOW
    
    Args:
        pin (int): GPIO pin number
        
    Returns:
        Dict[str, Any]: Result dictionary
    """
    return gpio_controller.set_gpio_output(pin, "low")

def set_gpio(pin: int, state: str) -> Dict[str, Any]:
    """Set GPIO pin to specified state
    
    Args:
        pin (int): GPIO pin number
        state (str): 'high', 'low', 'on', 'off', '1', '0'
        
    Returns:
        Dict[str, Any]: Result dictionary
    """
    return gpio_controller.set_gpio_output(pin, state)

def read_gpio(pin: int) -> Dict[str, Any]:
    """Read GPIO pin state
    
    Args:
        pin (int): GPIO pin number
        
    Returns:
        Dict[str, Any]: Result dictionary
    """
    return gpio_controller.read_gpio_input(pin)

def cleanup_gpio():
    """Clean up all GPIO resources"""
    gpio_controller.cleanup()

# Example usage and testing
if __name__ == "__main__":
    # Test the GPIO functions
    print("Testing GPIO Controller...")
    
    # Test setting pin 18 high
    result = set_gpio_high(18)
    print(f"Set pin 18 high: {result}")
    
    time.sleep(1)
    
    # Test setting pin 18 low
    result = set_gpio_low(18)
    print(f"Set pin 18 low: {result}")
    
    # Test with different state formats
    result = set_gpio(18, "on")
    print(f"Set pin 18 on: {result}")
    
    time.sleep(1)
    
    result = set_gpio(18, "off")
    print(f"Set pin 18 off: {result}")
    
    # Get status
    status = gpio_controller.get_pin_status()
    print(f"GPIO Status: {status}")
    
    # Cleanup
    cleanup_gpio()
    print("GPIO cleanup completed")
