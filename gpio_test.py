#!/usr/bin/env python3
"""
GPIO Test Script for Raspberry Pi 400
Test the GPIO control functionality without the web interface
"""

import time
import sys
from freenove_projects_board import set_gpio_high, set_gpio_low, set_gpio, read_gpio, cleanup_gpio, gpio_controller

def test_gpio_basic():
    """Test basic GPIO operations"""
    print("🔧 Testing Basic GPIO Operations")
    print("=" * 50)
    
    test_pin = 18  # GPIO pin 18 (physical pin 12)
    
    # Test setting pin high
    print(f"Setting GPIO pin {test_pin} HIGH...")
    result = set_gpio_high(test_pin)
    print(f"Result: {result}")
    time.sleep(2)
    
    # Test setting pin low
    print(f"\nSetting GPIO pin {test_pin} LOW...")
    result = set_gpio_low(test_pin)
    print(f"Result: {result}")
    time.sleep(2)
    
    # Test with different state formats
    print(f"\nTesting different state formats on pin {test_pin}:")
    
    states = ['on', 'high', '1', 'off', 'low', '0']
    for state in states:
        print(f"  Setting pin {test_pin} to '{state}'...")
        result = set_gpio(test_pin, state)
        print(f"  Result: {result['success']} - {result['message']}")
        time.sleep(1)

def test_multiple_pins():
    """Test controlling multiple GPIO pins"""
    print("\n🔧 Testing Multiple GPIO Pins")
    print("=" * 50)
    
    test_pins = [18, 22, 24]  # Multiple GPIO pins
    
    # Turn all pins on
    print("Turning all test pins ON...")
    for pin in test_pins:
        result = set_gpio_high(pin)
        print(f"Pin {pin}: {result['success']} - {result['message']}")
    
    time.sleep(2)
    
    # Turn all pins off
    print("\nTurning all test pins OFF...")
    for pin in test_pins:
        result = set_gpio_low(pin)
        print(f"Pin {pin}: {result['success']} - {result['message']}")

def test_invalid_operations():
    """Test error handling with invalid operations"""
    print("\n🔧 Testing Error Handling")
    print("=" * 50)
    
    # Test invalid pin
    print("Testing invalid pin number...")
    result = set_gpio(99, 'high')
    print(f"Invalid pin result: {result}")
    
    # Test invalid state
    print("\nTesting invalid state...")
    result = set_gpio(18, 'invalid_state')
    print(f"Invalid state result: {result}")

def test_gpio_status():
    """Test GPIO status reporting"""
    print("\n🔧 Testing GPIO Status")
    print("=" * 50)
    
    status = gpio_controller.get_pin_status()
    print(f"GPIO Controller Status: {status}")

def led_blink_demo(pin=18, blinks=5):
    """Demonstrate LED blinking"""
    print(f"\n💡 LED Blink Demo on Pin {pin}")
    print("=" * 50)
    print(f"Blinking LED {blinks} times (connect LED to GPIO pin {pin})")
    
    for i in range(blinks):
        print(f"Blink {i+1}/{blinks} - LED ON")
        set_gpio_high(pin)
        time.sleep(0.5)
        
        print(f"Blink {i+1}/{blinks} - LED OFF")
        set_gpio_low(pin)
        time.sleep(0.5)

def main():
    """Main test function"""
    print("🍓 Raspberry Pi 400 GPIO Test Suite")
    print("=" * 50)
    print("This script tests the GPIO control functionality.")
    print("Make sure you're running this on a Raspberry Pi with proper permissions.")
    print()
    
    try:
        # Run all tests
        test_gpio_basic()
        test_multiple_pins()
        test_invalid_operations()
        test_gpio_status()
        
        # Ask user if they want to run LED demo
        response = input("\n🤔 Do you want to run the LED blink demo? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            pin = input("Enter GPIO pin number for LED (default 18): ").strip()
            pin = int(pin) if pin.isdigit() else 18
            led_blink_demo(pin)
        
        print("\n✅ All tests completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    finally:
        # Always cleanup GPIO
        print("\n🧹 Cleaning up GPIO...")
        cleanup_gpio()
        print("GPIO cleanup completed.")

if __name__ == "__main__":
    main()
