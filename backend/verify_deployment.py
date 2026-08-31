import requests
import json
import time
import sys

# Configuration
BASE_URL_CORE = "http://localhost:5002"
BASE_URL_AGENT = "http://localhost:5003"

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_result(name, passed, details=""):
    if passed:
        status = f"{Colors.OKGREEN}✅ PASS{Colors.ENDC}"
    else:
        status = f"{Colors.FAIL}❌ FAIL{Colors.ENDC}"
        
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")

def test_core_detection():
    print(f"\n{Colors.HEADER}--- Test 1: Core API Detection Flow (REMOSTAR) ---{Colors.ENDC}")
    url = f"{BASE_URL_CORE}/ai/detections"
    # Using a reliable test image
    payload = {
        "image_url": "https://raw.githubusercontent.com/ultralytics/yolov5/master/data/images/zidane.jpg",
        "location": {"latitude": 6.5, "longitude": 6.0}
    }
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for Consciousness Integration
            has_mostar = "mostar_intelligence" in data
            consciousness = data.get("mostar_intelligence", {})
            has_odu = "odu_pattern" in consciousness
            risk_score = consciousness.get("risk_assessment", {}).get("score")
            
            print_result("Core API Service Reachable", True)
            print_result("Mostar Intelligence Key Present", has_mostar)
            print_result("Ifá Odu Pattern Generated", has_odu, f"Pattern: {consciousness.get('odu_pattern')}")
            print_result("Risk Assessment Calculated", risk_score is not None, f"Score: {risk_score}")
            
            if has_mostar and has_odu:
                return True
        else:
            print_result("Core API Request", False, f"Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print_result("Core API Connection", False, "Is the service running on port 5002?")
        return False
    except Exception as e:
        print_result("Core API Error", False, str(e))
        return False

def test_dcx0_reasoning():
    print(f"\n{Colors.HEADER}--- Test 2: DCX0 Symbolic Reasoning (Agent API) ---{Colors.ENDC}")
    url = f"{BASE_URL_AGENT}/generate_lang_chain_insights"
    payload = {
        "query": "How should communities respond to increased Mastomys detection?",
        "chain_type": "consciousness_analysis"
    }
    
    try:
        print(f"Sending request to {url} (May take time for LLM)...")
        response = requests.post(url, json=payload, timeout=120) 
        
        if response.status_code == 200:
            data = response.json()
            
            dcx0_analysis = data.get("dcx0_analysis", {})
            ubuntu_integration = data.get("ubuntu_integration", {})
            
            has_reasoning = "symbolic_reasoning" in dcx0_analysis
            has_ubuntu = bool(ubuntu_integration)
            
            print_result("Agent API Service Reachable", True)
            print_result("DCX0 Symbolic Reasoning", has_reasoning)
            print_result("Ubuntu Framework Integrated", has_ubuntu)
            
            if has_reasoning:
                return True
        else:
            print_result("Agent API Request", False, f"Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print_result("Agent API Connection", False, "Is the service running on port 5003?")
        return False
    except Exception as e:
        print_result("Agent API Error", False, str(e))
        return False

def test_enhanced_vision():
    print(f"\n{Colors.HEADER}--- Test 3: Enhanced Vision Analysis (Chained) ---{Colors.ENDC}")
    url = f"{BASE_URL_AGENT}/analyze_vision"
    payload = {
        "image_url": "https://raw.githubusercontent.com/ultralytics/yolov5/master/data/images/bus.jpg",
        "parameters": {"analysis_depth": "comprehensive"}
    }
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            core_detection = data.get("core_detection", {})
            dcx0_analysis = data.get("dcx0_enhanced_analysis", {})
            
            is_chained = bool(core_detection)
            is_enhanced = "symbolic_interpretation" in dcx0_analysis
            
            print_result("Service Chaining (Agent->Core)", is_chained, "Core API results present")
            print_result("Vision Consciousness Enhanced", is_enhanced)
            
            if is_chained and is_enhanced:
                return True
        else:
            print_result("Enhanced Vision Request", False, f"Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print_result("Enhanced Vision Connection", False, "Is the service running?")
        return False
    except Exception as e:
        print_result("Enhanced Vision Error", False, str(e))
        return False

if __name__ == "__main__":
    print(f"{Colors.BOLD}Mastomys AI Architecture Verification{Colors.ENDC}")
    print("=====================================")
    
    success_count = 0
    total_tests = 3
    
    if test_core_detection(): success_count += 1
    if test_dcx0_reasoning(): success_count += 1
    if test_enhanced_vision(): success_count += 1
    
    print(f"\n{Colors.BOLD}Summary: {success_count}/{total_tests} Tests Passed{Colors.ENDC}")
    if success_count == total_tests:
        print(f"{Colors.OKGREEN}All Systems Operational. Architecture Verified.{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}Some systems checks failed. Ensure Docker stack is running.{Colors.ENDC}")
