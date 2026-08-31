import requests
import json
import time

API_URL = "http://localhost:5002"
ML_URL = "http://localhost:5001"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "mostar123"

def test_detect():
    print("\n🚀 Testing /detect (Consciousness + Persistence)...")
    payload = {
        "detection_data": {
            "detections": [{"species": "Mastomys_natalensis", "confidence": 0.95}],
            "location": {"latitude": 6.5, "longitude": 7.3}
        },
        "environmental_context": {"season": "dry"},
        "clinical_context": {}
    }
    try:
        response = requests.post(f"{API_URL}/detect", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Odu: {result.get('odu_pattern')}")
            print(f"✅ Risk: {result.get('risk_assessment', {}).get('score')}")
            print(f"✅ Ubuntu: {result.get('ubuntu_guidance')}")
        else:
            print(f"❌ Response: {response.text}")
    except Exception as e:
        print(f"❌ /detect failed: {e}")

def test_risk_analysis_regional():
    print("\n🚀 Testing /risk-analysis (Regional - Mostar Grid)...")
    payload = {
        "latitude": 6.5,
        "longitude": 7.3
    }
    try:
        response = requests.post(f"{API_URL}/risk-analysis", json=payload)
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ /risk-analysis (regional) failed: {e}")

def test_risk_analysis_cluster():
    print("\n🚀 Testing /risk-analysis (Cluster Analysis)...")
    payload = {
        "detections": [
            {"species": "Mastomys_natalensis", "confidence": 0.95},
            {"species": "Mastomys_erythroleucus", "confidence": 0.88}
        ],
        "environmental_context": {"season": "dry"},
        "location": {"latitude": 6.5, "longitude": 7.3}
    }
    try:
        response = requests.post(f"{API_URL}/risk-analysis", json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"✅ Cluster Risk: {result.get('cluster_risk')}")
        print(f"✅ Analysis Count: {len(result.get('analyses', []))}")
    except Exception as e:
        print(f"❌ /risk-analysis (cluster) failed: {e}")

def test_rag_query():
    print("\n🚀 Testing /rag-query (LangChain + Mostar Grid)...")
    payload = {
        "question": "What is the current risk level in habitat at lat 6.5, lon 7.3?"
    }
    try:
        response = requests.post(f"{API_URL}/rag-query", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"⚠️  RAG endpoint may need Ollama to be ready: {response.text}")
    except Exception as e:
        print(f"❌ /rag-query failed: {e}")

def test_health_checks():
    print("\n🚀 Testing Service Health...")
    services = {
        "Core API": "http://localhost:5002/health",
        "ML Service": "http://localhost:5001/health"
    }
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=2)
            status = "✅ Healthy" if response.status_code == 200 else f"⚠️  {response.status_code}"
            print(f"{name}: {status}")
        except Exception as e:
            print(f"{name}: ❌ Unreachable - {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("   MOSTAR AI - PHASE 6 VERIFICATION SUITE")
    print("=" * 60)
    
    test_health_checks()
    time.sleep(1)
    
    test_detect()
    time.sleep(1)
    
    test_risk_analysis_cluster()
    time.sleep(1)
    
    test_risk_analysis_regional()
    time.sleep(1)
    
    # Wait a bit for Neo4j and Ollama to be ready if they are still booting
    print("\n⏳ Waiting for DCX0 (Ollama) and Neo4j to fully boot...")
    time.sleep(5)
    test_rag_query()
    
    print("\n" + "=" * 60)
    print("   VERIFICATION COMPLETE")
    print("=" * 60)
