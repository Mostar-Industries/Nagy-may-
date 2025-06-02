import pandas as pd
import joblib
import asyncio
import logging
import psycopg2
from sqlalchemy.future import select
from sqlalchemy import text
from shared import firebase_config, database
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, log_loss
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sovereign-Orchestrator")

MODEL_PATH = "model/model.joblib"

def fetch_firestore_data(collection="training_data"):
    logger.info("Fetching live Firestore data...")
    docs = firebase_config.db.collection(collection).stream()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data)

async def fetch_neon_data():
    logger.info("Fetching historical Neon data...")
    query = text("SELECT temperature, humidity, rainfall, vegetation_index, soil_moisture, outbreak_risk FROM ecological_training_data")
    async for session in database.get_session():
        result = await session.execute(query)
        rows = result.fetchall()
    columns = ['temperature', 'humidity', 'rainfall', 'vegetation_index', 'soil_moisture', 'outbreak_risk']
    return pd.DataFrame(rows, columns=columns)

def merge_datasets(df_live, df_historical):
    logger.info("Merging datasets...")
    combined = pd.concat([df_live, df_historical], ignore_index=True)
    combined.drop_duplicates(inplace=True)
    combined.fillna(0, inplace=True)
    return combined

def train_hybrid_model(df):
    logger.info("Training fusion model...")
    features = ['temperature', 'humidity', 'rainfall', 'vegetation_index', 'soil_moisture']
    label = 'outbreak_risk'
    X = df[features]
    y = df[label]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=200, max_depth=8)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
        'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
        'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0),
        'loss': log_loss(y_test, y_proba)
    }
    logger.info(f"Model trained successfully: {metrics}")
    joblib.dump(model, MODEL_PATH)
    return metrics

async def execute_training():
    df_live = fetch_firestore_data()
    df_historical = await fetch_neon_data()
    merged = merge_datasets(df_live, df_historical)
    metrics = train_hybrid_model(merged)
    return metrics
