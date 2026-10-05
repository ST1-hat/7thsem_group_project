"""
flood_engine.py
Core Machine Learning and Hydrological Risk Assessment Engine.
Integrates trained XGBoost/Random Forest models with physical hydrometeorological
thresholds to deliver robust, explainable flood risk assessments.
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

MODEL_FILE = os.path.join(os.path.dirname(__file__), 'flood_model.pkl')

class FloodRiskEngine:
    def __init__(self, model_path: str = MODEL_FILE):
        self.model_path = model_path
        self.xgb_model = None
        self.rf_model = None
        self.le_land = None
        self.le_soil = None
        self.feature_cols = []
        self.feature_importance = {}
        self.load_or_train_model()

    def load_or_train_model(self):
        """Loads serialized model artifacts, or initiates training if not present."""
        if not os.path.exists(self.model_path):
            print("Model artifacts not found, training new model...")
            from train_model import train_and_export
            train_and_export()

        with open(self.model_path, 'rb') as f:
            artifacts = pickle.load(f)

        self.xgb_model = artifacts['xgb_model']
        self.rf_model = artifacts['rf_model']
        self.le_land = artifacts['le_land']
        self.le_soil = artifacts['le_soil']
        self.feature_cols = artifacts['feature_cols']
        self.feature_importance = artifacts.get('feature_importance', {})
        print("Flood Risk Engine initialized successfully.")

    def predict_flood_risk(
        self,
        latitude: float,
        longitude: float,
        rainfall_mm: float,
        temperature_c: float,
        humidity_pct: float,
        river_discharge_m3s: float,
        water_level_m: float,
        elevation_m: float,
        land_cover: str = "Urban",
        soil_type: str = "Clay",
        population_density: float = 4500.0,
        infrastructure: int = 1,
        historical_floods: int = 1
    ) -> Dict[str, Any]:
        """
        Runs ML inference and hydrological risk synthesis on real-time inputs.
        Returns risk probability, risk category, alert color, and factor breakdown.
        """
        # Encode categorical variables safely
        try:
            land_enc = int(self.le_land.transform([land_cover])[0])
        except Exception:
            land_enc = int(self.le_land.transform([self.le_land.classes_[0]])[0])

        try:
            soil_enc = int(self.le_soil.transform([soil_type])[0])
        except Exception:
            soil_enc = int(self.le_soil.transform([self.le_soil.classes_[0]])[0])

        input_data = pd.DataFrame([{
            'latitude': latitude,
            'longitude': longitude,
            'rainfall': rainfall_mm,
            'temperature': temperature_c,
            'humidity': humidity_pct,
            'river_discharge': river_discharge_m3s,
            'water_level': water_level_m,
            'elevation': elevation_m,
            'population_density': population_density,
            'infrastructure': infrastructure,
            'historical_floods': historical_floods,
            'land_cover_encoded': land_enc,
            'soil_type_encoded': soil_enc
        }])[self.feature_cols]

        # 1. Machine Learning Probability
        prob_xgb = float(self.xgb_model.predict_proba(input_data)[0, 1])
        prob_rf = float(self.rf_model.predict_proba(input_data)[0, 1])
        ml_probability = (prob_xgb * 0.7) + (prob_rf * 0.3)

        # 2. Domain Hydrological Risk Calibration (IMD/CWC Flood Matrix)
        # High rainfall (>64.5mm) and low elevation drastically amplify physical inundation
        rain_factor = min(1.0, rainfall_mm / 180.0)
        discharge_factor = min(1.0, river_discharge_m3s / 3000.0)
        water_level_factor = min(1.0, water_level_m / 8.0)
        
        # Inversion for elevation: Lower elevation = higher vulnerability
        elevation_factor = max(0.0, 1.0 - (min(elevation_m, 2000.0) / 2000.0))
        
        hydro_index = (
            rain_factor * 0.35 +
            water_level_factor * 0.25 +
            discharge_factor * 0.20 +
            elevation_factor * 0.15 +
            (0.05 if historical_floods == 1 else 0.0)
        )

        # 3. Hybrid Blended Risk Score (0% to 100%)
        # Weighted combination of ML pattern and physical hydro dynamics
        blended_score = round(((ml_probability * 0.6) + (hydro_index * 0.4)) * 100, 1)
        blended_score = max(2.0, min(99.5, blended_score))

        # 4. Classification & Alerts
        if blended_score < 30.0:
            category = "LOW RISK"
            alert_level = "GREEN ALERT"
            status_text = "Safe / Normal Conditions"
            color_hex = "#22c55e"  # Emerald green
            description = "Rainfall and hydrologic indicators are well within safe absorption limits. No immediate threat."
        elif blended_score < 60.0:
            category = "MODERATE RISK"
            alert_level = "YELLOW ALERT"
            status_text = "Flood Watch / Advisory"
            color_hex = "#eab308"  # Amber yellow
            description = "Elevated moisture and moderate river discharge. Localized waterlogging possible in low-lying sectors."
        elif blended_score < 80.0:
            category = "HIGH RISK"
            alert_level = "ORANGE ALERT"
            status_text = "Severe Flood Warning"
            color_hex = "#f97316"  # Orange
            description = "Significant water accumulation and heavy rainfall. High probability of river overtopping and inundation."
        else:
            category = "CRITICAL RISK"
            alert_level = "RED ALERT"
            status_text = "Catastrophic / Flash Flood Emergency"
            color_hex = "#ef4444"  # Red
            description = "Severe emergency. Critical water levels and torrential runoff exceeding drainage capacity. Evacuation advisory active."

        # 5. Explainable AI Feature Contribution Breakdown
        contributions = {
            "Rainfall Intensity": round(rain_factor * 100, 1),
            "Water Level": round(water_level_factor * 100, 1),
            "River Discharge": round(discharge_factor * 100, 1),
            "Terrain Vulnerability (Low Elevation)": round(elevation_factor * 100, 1),
            "Atmospheric Humidity": round(min(100.0, humidity_pct), 1),
            "Historical Flood Precedent": 100.0 if historical_floods == 1 else 10.0
        }

        return {
            "risk_score": blended_score,
            "category": category,
            "alert_level": alert_level,
            "status_text": status_text,
            "color_hex": color_hex,
            "description": description,
            "ml_probability": round(ml_probability * 100, 1),
            "hydro_index": round(hydro_index * 100, 1),
            "contributions": contributions,
            "inputs_used": {
                "rainfall_mm": rainfall_mm,
                "temperature_c": temperature_c,
                "humidity_pct": humidity_pct,
                "river_discharge_m3s": river_discharge_m3s,
                "water_level_m": water_level_m,
                "elevation_m": elevation_m,
                "population_density": population_density,
                "historical_floods": historical_floods
            }
        }

# Global engine singleton instance
_engine_instance = None

def get_engine() -> FloodRiskEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = FloodRiskEngine()
    return _engine_instance
