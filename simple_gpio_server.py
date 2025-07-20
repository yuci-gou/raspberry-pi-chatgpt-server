#!/usr/bin/env python3
"""
Ultra-simple GPIO server for debugging
Just echoes back what it receives to test communication
"""

import json
import sys
import logging

# Configure logging to stderr
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("simple-gpio")

def main():
    """Simple echo server for testing"""
    logger.info("🚀 Starting Simple Echo GPIO Server...")
    
    # Send ready signal
    print("READY", flush=True)
    
    try:
        while True:
            # Read line from stdin
            line = sys.stdin.readline()
            if not line:  # EOF
                break
                
            line = line.strip()
            if not line:
                continue
            
            logger.info(f"📥 Received: {line}")
            
            try:
                # Try to parse as JSON
                request = json.loads(line)
                
                # Create a simple response
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id", 1),
                    "result": {
                        "status": "ok",
                        "method": request.get("method", "unknown"),
                        "echo": request
                    }
                }
                
                response_json = json.dumps(response)
                logger.info(f"📤 Sending: {response_json}")
                print(response_json, flush=True)
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {e}"}
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        logger.info("⚠️ Server interrupted")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
    finally:
        logger.info("✅ Server shutdown")

if __name__ == "__main__":
    main()
