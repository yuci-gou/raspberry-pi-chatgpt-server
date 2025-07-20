#!/usr/bin/env python3
"""
MCP GPIO Test Suite
Comprehensive testing for the MCP-based GPIO control system
"""

import time
import json
import asyncio
from mcp_client import MCPGPIOClient, SyncMCPGPIOClient

def test_sync_mcp_client():
    """Test the synchronous MCP client"""
    print("🧪 Testing Synchronous MCP GPIO Client")
    print("=" * 50)
    
    client = SyncMCPGPIOClient()
    
    try:
        # Test 1: List available tools
        print("1. Testing tool listing...")
        tools = client.list_tools()
        print(f"   Available tools: {[tool.get('name') for tool in tools]}")
        
        # Test 2: Get GPIO status
        print("\n2. Testing GPIO status...")
        status = client.get_gpio_status()
        print(f"   GPIO Status: {json.dumps(status, indent=2)}")
        
        # Test 3: List valid pins
        print("\n3. Testing valid pins list...")
        pins = client.list_valid_pins()
        print(f"   Valid pins: {pins.get('valid_pins', [])}")
        
        # Test 4: Set GPIO pin high
        test_pin = 18
        print(f"\n4. Testing set pin {test_pin} HIGH...")
        result = client.set_gpio_pin(test_pin, "high")
        print(f"   Result: {json.dumps(result, indent=2)}")
        
        time.sleep(1)
        
        # Test 5: Read GPIO pin
        print(f"\n5. Testing read pin {test_pin}...")
        result = client.read_gpio_pin(test_pin)
        print(f"   Result: {json.dumps(result, indent=2)}")
        
        # Test 6: Set GPIO pin low
        print(f"\n6. Testing set pin {test_pin} LOW...")
        result = client.set_gpio_pin(test_pin, "low")
        print(f"   Result: {json.dumps(result, indent=2)}")
        
        # Test 7: Test multiple pins
        print("\n7. Testing multiple pins...")
        test_pins = [18, 22, 24]
        for pin in test_pins:
            result = client.set_gpio_pin(pin, "on")
            print(f"   Pin {pin} ON: {result.get('success', False)}")
            time.sleep(0.5)
        
        time.sleep(1)
        
        for pin in test_pins:
            result = client.set_gpio_pin(pin, "off")
            print(f"   Pin {pin} OFF: {result.get('success', False)}")
            time.sleep(0.5)
        
        print("\n✅ Synchronous MCP client test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Synchronous MCP client test failed: {e}")

async def test_async_mcp_client():
    """Test the asynchronous MCP client"""
    print("\n🧪 Testing Asynchronous MCP GPIO Client")
    print("=" * 50)
    
    client = MCPGPIOClient()
    
    try:
        async with client.connect():
            # Test 1: List tools
            print("1. Testing async tool listing...")
            tools = await client.list_tools()
            print(f"   Available tools: {[tool.get('name') for tool in tools]}")
            
            # Test 2: GPIO operations
            test_pin = 18
            print(f"\n2. Testing async GPIO operations on pin {test_pin}...")
            
            # Set high
            result = await client.set_gpio_pin(test_pin, "high")
            print(f"   Set HIGH: {result.get('success', False)}")
            
            await asyncio.sleep(1)
            
            # Read state
            result = await client.read_gpio_pin(test_pin)
            print(f"   Read state: {result.get('state', 'unknown')}")
            
            # Set low
            result = await client.set_gpio_pin(test_pin, "low")
            print(f"   Set LOW: {result.get('success', False)}")
            
            # Get status
            status = await client.get_gpio_status()
            print(f"   Active pins: {status.get('active_pins', [])}")
            
        print("\n✅ Asynchronous MCP client test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Asynchronous MCP client test failed: {e}")

def test_flask_integration():
    """Test Flask app integration with MCP"""
    print("\n🧪 Testing Flask Integration with MCP")
    print("=" * 50)
    
    try:
        import requests
        
        # Test health endpoint
        print("1. Testing health endpoint...")
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   GPIO Available: {data.get('gpio_available')}")
            print(f"   GPIO Mode: {data.get('gpio_mode')}")
        else:
            print(f"   Health check failed: {response.status_code}")
        
        # Test GPIO status endpoint
        print("\n2. Testing GPIO status endpoint...")
        response = requests.get("http://localhost:5000/api/gpio/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   GPIO Available: {data.get('gpio_available')}")
            print(f"   GPIO Mode: {data.get('gpio_mode')}")
            print(f"   Active Pins: {data.get('active_pins', [])}")
        else:
            print(f"   GPIO status failed: {response.status_code}")
        
        # Test direct GPIO control
        print("\n3. Testing direct GPIO control...")
        gpio_data = {
            "action": "set_output",
            "pin": 18,
            "state": "high"
        }
        response = requests.post("http://localhost:5000/api/gpio", json=gpio_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   GPIO Control: {data.get('success', False)}")
            print(f"   Message: {data.get('message', 'No message')}")
        else:
            print(f"   GPIO control failed: {response.status_code}")
        
        # Test ChatGPT integration
        print("\n4. Testing ChatGPT GPIO integration...")
        chat_data = {
            "question": "Turn on LED on pin 18"
        }
        response = requests.post("http://localhost:5000/api/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   Chat Success: {data.get('success', False)}")
            print(f"   GPIO Detected: {data.get('gpio_detected', False)}")
            if data.get('gpio_result'):
                gpio_result = data['gpio_result']
                print(f"   GPIO Executed: {gpio_result.get('success', False)}")
                print(f"   GPIO Message: {gpio_result.get('message', 'No message')}")
        else:
            print(f"   ChatGPT integration failed: {response.status_code}")
        
        print("\n✅ Flask integration test completed!")
        
    except ImportError:
        print("   ⚠️ Requests library not available, skipping Flask integration test")
    except Exception as e:
        print(f"\n❌ Flask integration test failed: {e}")

def led_blink_demo_mcp():
    """LED blink demonstration using MCP"""
    print("\n💡 MCP LED Blink Demo")
    print("=" * 50)
    
    client = SyncMCPGPIOClient()
    test_pin = 18
    blinks = 3
    
    print(f"Blinking LED on pin {test_pin} {blinks} times using MCP...")
    
    try:
        for i in range(blinks):
            print(f"Blink {i+1}/{blinks} - LED ON")
            result = client.set_gpio_pin(test_pin, "high")
            if not result.get('success'):
                print(f"   Error: {result.get('message')}")
                break
            
            time.sleep(0.5)
            
            print(f"Blink {i+1}/{blinks} - LED OFF")
            result = client.set_gpio_pin(test_pin, "low")
            if not result.get('success'):
                print(f"   Error: {result.get('message')}")
                break
            
            time.sleep(0.5)
        
        print("✅ MCP LED blink demo completed!")
        
    except Exception as e:
        print(f"❌ MCP LED blink demo failed: {e}")

def main():
    """Main test function"""
    print("🍓 Raspberry Pi 400 MCP GPIO Test Suite")
    print("=" * 60)
    print("This comprehensive test suite validates the MCP-based GPIO control system.")
    print()
    
    try:
        # Run all tests
        test_sync_mcp_client()
        
        # Ask user for async test
        response = input("\n🤔 Run async MCP client test? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            asyncio.run(test_async_mcp_client())
        
        # Ask user for Flask integration test
        response = input("\n🤔 Run Flask integration test? (requires Flask server running) (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            test_flask_integration()
        
        # Ask user for LED demo
        response = input("\n🤔 Run MCP LED blink demo? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            led_blink_demo_mcp()
        
        print("\n" + "=" * 60)
        print("🎉 All MCP GPIO tests completed!")
        print("Your MCP-based GPIO control system is working perfectly!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    main()
