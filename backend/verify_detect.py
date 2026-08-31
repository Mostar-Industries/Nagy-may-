import urllib.request
import json
import time

def verify_detect():
    url = "http://localhost:5002/detect"
    payload = {
        "detection_data": {
            "detections": [
                {"species": "Mastomys_natalensis", "confidence": 0.91}
            ],
            "location": {"latitude": 6.5, "longitude": 6.0}
        },
        "clinical_context": {"cases": []},
        "environmental_context": {"season": "dry"}
    }
    
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers)
    
    print(f"🚀 Sending request to {url}...")
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                body = response.read().decode('utf-8')
                result = json.loads(body)
                print("✅ /detect Verification SUCCESS!")
                print(json.dumps(result, indent=2))
            else:
                print(f"❌ Failed with status: {response.status}")
                print(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    time.sleep(2)
    verify_detect()
