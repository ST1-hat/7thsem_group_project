"""
test_system.py
Comprehensive end-to-end test suite for the Smart Flood Risk Prediction & Monitoring System.
"""

import sys
from api_services import geocode_place, fetch_realtime_telemetry, generate_nearby_regions
from flood_engine import get_engine
from map_view import create_flood_map
from utils import (
    create_risk_gauge,
    create_precipitation_forecast_chart,
    create_river_discharge_chart,
    create_factor_radar_chart,
    create_nearby_comparison_chart
)

def run_tests():
    print("==================================================")
    print("1. Testing Geocoding Service...")
    place = geocode_place("Patna")
    assert place is not None, "Geocoding returned None"
    assert "latitude" in place and "longitude" in place, "Missing coordinates in geocoding"
    print(f"   [PASS] Geocoded '{place['name']}': Lat={place['latitude']}, Lon={place['longitude']}, Elev={place['elevation']}m")

    print("\n2. Testing Real-Time Telemetry Retrieval...")
    telemetry = fetch_realtime_telemetry(place["latitude"], place["longitude"])
    assert "rainfall_24h" in telemetry, "Missing rainfall_24h"
    assert "river_discharge" in telemetry, "Missing river_discharge"
    print(f"   [PASS] Telemetry: Temp={telemetry['temperature']}C, Humidity={telemetry['humidity']}%, 24h Rain={telemetry['rainfall_24h']}mm, River Discharge={telemetry['river_discharge']} m3/s")

    print("\n3. Testing Machine Learning & Hydrological Engine...")
    engine = get_engine()
    pred = engine.predict_flood_risk(
        latitude=place["latitude"],
        longitude=place["longitude"],
        rainfall_mm=telemetry["rainfall_24h"],
        temperature_c=telemetry["temperature"],
        humidity_pct=telemetry["humidity"],
        river_discharge_m3s=telemetry["river_discharge"],
        water_level_m=telemetry["water_level"],
        elevation_m=telemetry["elevation"],
        land_cover="Urban",
        soil_type="Clay",
        population_density=5200.0,
        historical_floods=1
    )
    assert "risk_score" in pred, "Missing risk_score"
    assert "alert_level" in pred, "Missing alert_level"
    print(f"   [PASS] Prediction: Risk Score={pred['risk_score']}%, Alert={pred['alert_level']}, Category={pred['category']}")

    print("\n4. Testing Nearby Peripheral Stations Generation...")
    nearby = generate_nearby_regions(place["latitude"], place["longitude"], place["name"], radius_km=25.0, count=6)
    assert len(nearby) == 6, f"Expected 6 stations, got {len(nearby)}"
    for s in nearby:
        s["risk"] = engine.predict_flood_risk(
            latitude=s["latitude"],
            longitude=s["longitude"],
            rainfall_mm=telemetry["rainfall_24h"],
            temperature_c=telemetry["temperature"],
            humidity_pct=telemetry["humidity"],
            river_discharge_m3s=telemetry["river_discharge"],
            water_level_m=telemetry["water_level"],
            elevation_m=telemetry["elevation"],
            land_cover="Agricultural",
            soil_type="Clay"
        )
    print(f"   [PASS] Generated & evaluated {len(nearby)} peripheral stations.")

    print("\n5. Testing Folium Geospatial Map Creation...")
    m = create_flood_map(place, pred, nearby)
    assert m is not None, "Map generation returned None"
    map_html = m._repr_html_()
    assert len(map_html) > 500, "Map HTML seems empty"
    print("   [PASS] Interactive Folium map created successfully.")

    print("\n6. Testing Plotly Analytics & Visualizations...")
    g_fig = create_risk_gauge(pred["risk_score"], pred["category"], pred["color_hex"])
    r_fig = create_precipitation_forecast_chart(telemetry["hourly_times"], telemetry["hourly_precipitation"])
    d_fig = create_river_discharge_chart(telemetry["discharge_forecast_dates"], telemetry["discharge_forecast_values"])
    x_fig = create_factor_radar_chart(pred["contributions"])
    c_fig = create_nearby_comparison_chart(nearby)
    assert all([g_fig, r_fig, d_fig, x_fig, c_fig]), "Plotly chart creation failed"
    print("   [PASS] All Plotly forecast charts generated without errors.")

    print("\n==================================================")
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("==================================================")

if __name__ == '__main__':
    run_tests()
