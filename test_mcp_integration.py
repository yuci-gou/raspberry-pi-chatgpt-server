#!/usr/bin/env python3
"""
Test MCP client-server integration directly
"""

import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("mcp-integration-test")

def test_mcp_client_server():
    """Test MCP client-server communication"""
    logger.info("🧪 Testing MCP client-server integration...")
    
    try:
        # Import MCP client
        from mcp_client import SimpleGPIOClient
        
        logger.info("✅ MCP client imported successfully")
        
        # Test MCP client with server
        with SimpleGPIOClient() as client:
            logger.info("🔧 Testing MCP GPIO operations...")
            
            # Test tools listing
            try:
                tools = client.list_tools()
                logger.info(f"Available tools: {tools}")
            except Exception as e:
                logger.error(f"❌ List tools failed: {e}")
                return False
            
            # Test GPIO status
            try:
                status = client.get_gpio_status()
                logger.info(f"GPIO status: {status}")
            except Exception as e:
                logger.error(f"❌ GPIO status failed: {e}")
                return False
            
            # Test GPIO set operation
            try:
                result = client.set_gpio_pin(17, "high")
                logger.info(f"Set pin 17 high: {result}")
                
                if result.get("success"):
                    logger.info("✅ MCP GPIO operation successful!")
                    return True
                else:
                    logger.error(f"❌ MCP GPIO operation failed: {result.get('message')}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ MCP GPIO operation exception: {e}")
                return False
                
    except Exception as e:
        logger.error(f"❌ MCP integration test failed: {e}")
        return False

def test_mcp_sync_client():
    """Test MCP synchronous client (used by Flask)"""
    logger.info("🧪 Testing MCP sync client (Flask integration)...")
    
    try:
        # Import the sync client used by Flask
        from mcp_client import mcp_gpio_client
        
        logger.info("✅ MCP sync client imported successfully")
        
        # Test GPIO operations
        try:
            # Test GPIO status
            status = mcp_gpio_client.get_gpio_status()
            logger.info(f"Sync client GPIO status: {status}")
            
            # Test GPIO set operation
            result = mcp_gpio_client.set_gpio_pin(17, "high")
            logger.info(f"Sync client set pin 17 high: {result}")
            
            if result.get("success"):
                logger.info("✅ MCP sync client successful!")
                return True
            else:
                logger.error(f"❌ MCP sync client failed: {result.get('message')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ MCP sync client exception: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ MCP sync client test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting MCP integration tests...")
    
    # Test 1: Direct MCP client
    logger.info("\n" + "="*50)
    logger.info("TEST 1: Direct MCP Client")
    logger.info("="*50)
    direct_works = test_mcp_client_server()
    
    # Test 2: Sync MCP client (Flask integration)
    logger.info("\n" + "="*50)
    logger.info("TEST 2: MCP Sync Client (Flask Integration)")
    logger.info("="*50)
    sync_works = test_mcp_sync_client()
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("SUMMARY")
    logger.info("="*50)
    logger.info(f"Direct MCP client works: {direct_works}")
    logger.info(f"Sync MCP client works: {sync_works}")
    
    if direct_works and sync_works:
        logger.info("✅ All MCP tests passed - MCP implementation is working!")
    elif direct_works and not sync_works:
        logger.info("💡 Direct MCP works but sync client fails - Flask integration issue")
    elif not direct_works:
        logger.info("💡 Direct MCP fails - Core MCP client/server issue")
    else:
        logger.info("❌ All MCP tests failed - Need to debug MCP implementation")
