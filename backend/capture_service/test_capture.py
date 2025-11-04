#!/usr/bin/env python3
"""
Test script for capture service
Validates configuration and connectivity without starting full service
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capture_service.config import CaptureConfig
from capture_service.inference_client import InferenceClient
import asyncio

def test_config():
    """Test configuration validity"""
    print("=" * 60)
    print("Testing Configuration...")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. Environment Variables:")
    env_vars = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "YOLO_API_URL": CaptureConfig.YOLO_API_URL,
        "SUPABASE_URL": CaptureConfig.SUPABASE_URL,
        "INFERENCE_INTERVAL": CaptureConfig.INFERENCE_INTERVAL,
        "MIN_CONFIDENCE": CaptureConfig.MIN_CONFIDENCE,
    }
    
    for key, value in env_vars.items():
        status = "✅" if value else "❌"
        print(f"   {status} {key}: {value or 'NOT SET'}")
    
    # Check RTSP streams
    print("\n2. RTSP Streams:")
    streams = CaptureConfig.get_enabled_streams()
    print(f"   Found {len(streams)} enabled stream(s)")
    
    for i, stream in enumerate(streams, 1):
        print(f"\n   Stream {i}:")
        print(f"      Name: {stream['name']}")
        print(f"      URL: {stream['url']}")
        print(f"      Location: {stream['location']}")
        print(f"      Region: {stream['region']}")
    
    # Validate config
    print("\n3. Configuration Validation:")
    is_valid = CaptureConfig.validate()
    if is_valid:
        print("   ✅ Configuration is valid")
    else:
        print("   ❌ Configuration has issues")
    
    return is_valid

async def test_ml_service():
    """Test ML service connectivity"""
    print("\n" + "=" * 60)
    print("Testing ML Service Connectivity...")
    print("=" * 60)
    
    client = InferenceClient(
        api_url=CaptureConfig.YOLO_API_URL,
        timeout=CaptureConfig.API_TIMEOUT
    )
    
    print(f"\n1. Testing connection to: {CaptureConfig.YOLO_API_URL}")
    
    try:
        # Test health endpoint
        import aiohttp
        async with aiohttp.ClientSession() as session:
            health_url = f"{CaptureConfig.YOLO_API_URL}/health"
            async with session.get(health_url, timeout=5) as response:
                if response.status == 200:
                    print("   ✅ ML service is healthy")
                    data = await response.json()
                    print(f"   Response: {data}")
                    return True
                else:
                    print(f"   ❌ ML service returned status {response.status}")
                    return False
    except Exception as e:
        print(f"   ❌ Failed to connect: {e}")
        print("\n   Make sure ML service is running:")
        print("   cd backend/ml_service && python app.py")
        print("   OR")
        print("   docker-compose up ml-service")
        return False

def test_rtsp_format():
    """Test RTSP URL format"""
    print("\n" + "=" * 60)
    print("Testing RTSP URL Formats...")
    print("=" * 60)
    
    streams = CaptureConfig.get_enabled_streams()
    
    for i, stream in enumerate(streams, 1):
        url = stream['url']
        print(f"\n{i}. {stream['name']}")
        
        if url.startswith('rtsp://'):
            print("   ✅ Valid RTSP protocol")
            
            # Check for credentials
            if '@' in url:
                print("   ✅ Credentials included")
            else:
                print("   ⚠️  No credentials (may be required)")
            
            # Check for port
            if ':554' in url or url.count(':') > 2:
                print("   ✅ Port specified")
            else:
                print("   ⚠️  No port specified (will use default)")
                
        else:
            print("   ❌ Invalid protocol (must start with rtsp://)")
            print(f"   Current: {url}")
            print("   Example: rtsp://username:password@192.168.1.100:554/stream1")

def main():
    """Run all tests"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  SKYHAWK CAPTURE SERVICE - CONFIGURATION TEST           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # Test configuration
    config_valid = test_config()
    
    # Test RTSP format
    test_rtsp_format()
    
    # Test ML service
    ml_valid = asyncio.run(test_ml_service())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if config_valid:
        print("✅ Configuration: PASS")
    else:
        print("❌ Configuration: FAIL")
    
    if ml_valid:
        print("✅ ML Service: PASS")
    else:
        print("❌ ML Service: FAIL")
    
    print("\n" + "=" * 60)
    
    if config_valid and ml_valid:
        print("🎉 ALL TESTS PASSED!")
        print("\nYou can now start the capture service:")
        print("   python capture_loop.py")
        print("\nOr with Docker:")
        print("   docker-compose up capture-service")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nPlease fix the issues above before starting the service.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
