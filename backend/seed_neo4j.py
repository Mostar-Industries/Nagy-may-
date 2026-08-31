import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))
sys.path.append(os.path.join(os.getcwd(), "backend", "ai_services"))
sys.path.append(os.path.join(os.getcwd(), "backend", "ai_services", "consciousness"))

from ai_services.consciousness.grid_manager import grid_manager
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def seed_test_data():
    print(f"🌍 Connecting to: {grid_manager.neo4j_uri}")
    print(f"👤 User: {grid_manager.neo4j_user}")
    print(f"🗄️ Database: {grid_manager.neo4j_db}")
    print("🧠 Seeding Mostar Grid with test detections...")
    
    test_detections = [
        {
            "species": "Mastomys_natalensis",
            "confidence": 0.95,
            "latitude": 6.5,
            "longitude": 7.3,
            "odu": "Eji_Ogbe",
            "risk": 0.945
        },
        {
            "species": "Mastomys_erythroleucus",
            "confidence": 0.88,
            "latitude": 7.2,
            "longitude": 3.9,
            "odu": "Iwori_Meji",
            "risk": 0.504
        }
    ]

    for det in test_detections:
        detection_data = {
            "detections": [{"species": det["species"], "confidence": det["confidence"]}],
            "location": {"latitude": det["latitude"], "longitude": det["longitude"]}
        }
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "odu_pattern": det["odu"],
            "risk_assessment": {"score": det["risk"]},
            "ubuntu_guidance": "Community vigilance is key."
        }
        
        print(f"-> Persisting {det['species']} at ({det['latitude']}, {det['longitude']})")
        grid_manager.persist_detection(detection_data, analysis)

    print("✅ Seeding complete.")
    
    # Verify records
    with grid_manager.neo4j_driver.session(database=grid_manager.neo4j_db) as session:
        count_res = session.run("MATCH (d:DetectionNode) RETURN count(d) as count")
        count = count_res.single()["count"]
        print(f"📊 Verification: Found {count} DetectionNodes in '{grid_manager.neo4j_db}' database.")

        result = session.run("MATCH (d:DetectionNode) RETURN d.id as id, d.species as species, d.timestamp as ts LIMIT 5")
        records = list(result)
        print(f"📊 Verification: Found samples:")
        for r in records:
            print(f"  - ID: {r['id']}, Species: {r['species']}, Time: {r['ts']}")
        
        rel_result = session.run("MATCH (d:DetectionNode)-[r:DETECTED_IN]->(h:Habitat) RETURN count(r) as count, h.id as habitat_id LIMIT 1")
        rel_data = rel_result.single()
        if rel_data:
            print(f"📊 Verification: Confirmed 'DETECTED_IN' relationship to habitat '{rel_data['habitat_id']}'.")
        else:
            print("❌ Verification: No 'DETECTED_IN' relationships found!")

if __name__ == "__main__":
    seed_test_data()
