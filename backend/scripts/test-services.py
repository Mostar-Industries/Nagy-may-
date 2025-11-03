#!/usr/bin/env python3
"""
Integration test script for Skyhawk services
Tests all endpoints and validates connectivity
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, List

BASE_URLS = {
    "ml": "http://localhost:5001",
    "api": "http://localhost:5002",
    "agent": "http://localhost:5003",
}

TESTS: List[Dict] = [
    {
        "name": "ML Service Health",
        "method": "GET",
        "service": "ml",
        "endpoint": "/health",
        "expected_status": 200,
    },
    {
        "name": "API Service Health",
        "method": "GET",
        "service": "api",
        "endpoint": "/health",
        "expected_status": 200,
    },
    {
        "name": "Agent Service Health",
        "method": "GET",
        "service": "agent",
        "endpoint": "/health",
        "expected_status": 200,
    },
    {
        "name": "Get Detections",
        "method": "GET",
        "service": "api",
        "endpoint": "/detections",
        "expected_status": 200,
    },
]

async def run_test(session: aiohttp.ClientSession, test: Dict) -> bool:
    """Run a single test"""
    url = f"{BASE_URLS[test['service']]}{test['endpoint']}"
    
    try:
        async with session.request(test["method"], url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            if resp.status == test["expected_status"]:
                print(f"✓ {test['name']}: {resp.status}")
                return True
            else:
                print(f"✗ {test['name']}: Expected {test['expected_status']}, got {resp.status}")
                return False
    except Exception as e:
        print(f"✗ {test['name']}: {e}")
        return False

async def main():
    """Run all tests"""
    print("Testing Skyhawk Services\n")
    
    async with aiohttp.ClientSession() as session:
        results = []
        for test in TESTS:
            result = await run_test(session, test)
            results.append(result)
            await asyncio.sleep(0.5)
    
    print(f"\n{'='*40}")
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All services operational!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
