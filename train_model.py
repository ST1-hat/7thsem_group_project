"""
train_model.py
Trains and serializes the Machine Learning models (Random Forest and XGBoost)
for the Smart Flood Risk Prediction & Real-Time Monitoring System.
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def train_and_export():
    dataset_path = 'flood_risk_dataset_corrected.csv'
    if not os.path.exists(dataset_path):
        dataset_path = 'flood_risk_dataset_india.csv'
    
    print(f"Loading dataset from: {dataset_path}...")
    df = pd.read_csv(dataset_path)

    # Standardize column names to clean, ascii identifiers
    clean_cols = [
        'latitude', 'longitude', 'rainfall', 'temperature', 'humidity',
        'river_discharge', 'water_level', 'elevation', 'land_cover', 'soil_type',
        'population_density', 'infrastructure', 'historical_floods', 'flood_occurred'
    ]
    df.columns = clean_cols

    # Encode categorical variables
    le_land = LabelEncoder()
    df['land_cover_encoded'] = le_land.fit_transform(df['land_cover'].astype(str))
    
    le_soil = LabelEncoder()
    df['soil_type_encoded'] = le_soil.fit_transform(df['soil_type'].astype(str))

    feature_cols = [
        'latitude', 'longitude', 'rainfall', 'temperature', 'humidity',
        'river_discharge', 'water_level', 'elevation', 'population_density',
        'infrastructure', 'historical_floods', 'land_cover_encoded', 'soil_type_encoded'
    ]
    target_col = 'flood_occurred'

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set size: {len(X_train)}, Test set size: {len(X_test)}")
    print(f"Positive flood cases: {y.sum()} / {len(y)} ({y.mean()*100:.1f}%)")

    # 1. Train Random Forest Classifier
    print("Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(
        n_estimators=120,
        max_depth=9,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)

    y_pred_rf = rf_model.predict(X_test)
    y_prob_rf = rf_model.predict_proba(X_test)[:, 1]
    rf_metrics = {
        'accuracy': float(accuracy_score(y_test, y_pred_rf)),
        'precision': float(precision_score(y_test, y_pred_rf)),
        'recall': float(recall_score(y_test, y_pred_rf)),
        'f1': float(f1_score(y_test, y_pred_rf)),
        'roc_auc': float(roc_auc_score(y_test, y_prob_rf))
    }
    print("Random Forest Evaluation:", rf_metrics)

    # 2. Train XGBoost Classifier
    print("Training XGBoost Classifier...")
    xgb_model = XGBClassifier(
        n_estimators=120,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        eval_metric='logloss'
    )
    xgb_model.fit(X_train, y_train)

    y_pred_xgb = xgb_model.predict(X_test)
    y_prob_xgb = xgb_model.predict_proba(X_test)[:, 1]
    xgb_metrics = {
        'accuracy': float(accuracy_score(y_test, y_pred_xgb)),
        'precision': float(precision_score(y_test, y_pred_xgb)),
        'recall': float(recall_score(y_test, y_pred_xgb)),
        'f1': float(f1_score(y_test, y_pred_xgb)),
        'roc_auc': float(roc_auc_score(y_test, y_prob_xgb))
    }
    print("XGBoost Evaluation:", xgb_metrics)

    # Feature Importance
    feature_importance = dict(zip(feature_cols, [float(v) for v in xgb_model.feature_importances_]))
    sorted_fi = dict(sorted(feature_importance.items(), key=lambda item: item[1], reverse=True))

    # Save artifacts
    artifacts = {
        'xgb_model': xgb_model,
        'rf_model': rf_model,
        'le_land': le_land,
        'le_soil': le_soil,
        'feature_cols': feature_cols,
        'land_classes': list(le_land.classes_),
        'soil_classes': list(le_soil.classes_),
        'metrics': {
            'rf': rf_metrics,
            'xgb': xgb_metrics
        },
        'feature_importance': sorted_fi
    }

    model_file = 'flood_model.pkl'
    with open(model_file, 'wb') as f:
        pickle.dump(artifacts, f)
    print(f"Model saved successfully to {model_file}")

    metadata_file = 'model_metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump({
            'feature_cols': feature_cols,
            'land_classes': list(le_land.classes_),
            'soil_classes': list(le_soil.classes_),
            'metrics': {'rf': rf_metrics, 'xgb': xgb_metrics},
            'feature_importance': sorted_fi
        }, f, indent=4)
    print(f"Metadata saved to {metadata_file}")

if __name__ == '__main__':
    train_and_export()
