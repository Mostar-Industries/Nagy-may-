#!/usr/bin/env python3
"""
Create REAL Firestore collections for MNTRK Sovereign Grid
"""
import firebase_admin
from firebase_admin import credentials, firestore
import os

FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)
db = firestore.client()

collections = [
    "training_data",
    "prediction_logs",
    "model_registry"
]

for collection in collections:
    db.collection(collection).add({'initialized': True})

print("✅ Firestore sovereign collections initialized successfully.")
