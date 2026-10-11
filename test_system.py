"""
test_system.py
Comprehensive end-to-end test suite for the Smart Flood Risk Prediction & Monitoring System.
Tests:
  1. Geocoding Service (Open-Meteo & Nominatim)
  2. Real-Time Telemetry Retrieval (Precipitation, GloFAS Discharge, Elevation)
  3. Machine Learning & Hydrological Engine (XGBoost, RF, IMD Matrix)
  4. Nearby Peripheral Stations Generation
  5. Folium Geospatial Map with Evacuation Corridors & Relief Shelters
  6. Plotly Analytics & Gauge Visualizations
  7. AI Evacuation Routing Engine (Dijkstra Pathfinding with Hydrological Impedance)
  8. Historical Disaster Time-Travel Replay (Patna 2019, Kerala 2018, Delhi 2023)
"""

import sys
from api_services import geocode_place, fetch_realtime_telemetry, generate_nearby_regions
from flood_engine import get_engine
from map_view import create_flood_map
from evacuation_engine import compute_evacuation_plan, generate_relief_shelters, build_evacuation_graph, solve_dijkstra_route
from historical_scenarios import get_available_scenarios, get_scenario, get_stage_telemetry
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

    print("\n5. Testing AI Evacuation Routing Engine (Dijkstra Graph Pathfinding)...")
    shelters = generate_relief_shelters(place["latitude"], place["longitude"], place["name"], telemetry["elevation"])
    assert len(shelters) >= 3, "Expected at least 3 candidate shelters"
    assert all("elevation_m" in s and "capacity" in s for s in shelters), "Malformed shelter data"
    print(f"   [PASS] Generated {len(shelters)} designated relief shelters.")

    evac_plan = compute_evacuation_plan(
        origin_lat=place["latitude"],
        origin_lon=place["longitude"],
        city_name=place["name"],
        base_elevation=telemetry["elevation"],
        flood_risk_score=85.0  # Simulate peak danger score
    )
    assert evac_plan["direct_route"]["found"] is True, "Direct route not found"
    assert evac_plan["safe_route"]["found"] is True, "Safe route not found"
    assert evac_plan["safe_route"]["is_safe"] is True, "Safe route should be marked safe"
    print(f"   [PASS] Evacuation Plan computed:")
    print(f"          - Destination: {evac_plan['target_shelter']['name']}")
    print(f"          - Direct Route: {evac_plan['direct_route']['total_distance_km']} km (Max water: {evac_plan['direct_route']['max_water_depth_m']}m - SUBMERGED)")
    print(f"          - AI Safe Corridor: {evac_plan['safe_route']['total_distance_km']} km (Max water: {evac_plan['safe_route']['max_water_depth_m']}m - CLEAR, ETA: {evac_plan['safe_route']['transit_time_mins']} min)")

    print("\n6. Testing Historical Disaster Time-Travel Archive...")
    scenarios = get_available_scenarios()
    assert len(scenarios) >= 3, "Expected at least 3 historical disaster scenarios"
    print(f"   [PASS] Found {len(scenarios)} historical disaster scenarios: {[s['id'] for s in scenarios]}")

    for sc in scenarios:
        sc_full = get_scenario(sc["id"])
        stage_0 = get_stage_telemetry(sc["id"], 0)
        stage_peak = get_stage_telemetry(sc["id"], 2)
        assert stage_0["rainfall_24h"] >= 0, "Invalid rainfall"
        assert stage_peak["rainfall_24h"] > stage_0["rainfall_24h"], "Peak rainfall should exceed stage 0"
        print(f"   [PASS] Scenario '{sc['title']}': Verified Stage 0 ({stage_0['rainfall_24h']}mm) vs Peak ({stage_peak['rainfall_24h']}mm, {stage_peak['river_discharge']} m3/s)")

    print("\n7. Testing Enhanced Folium Geospatial Map with Evacuation Corridors...")
    m = create_flood_map(place, pred, nearby, evacuation_plan=evac_plan)
    assert m is not None, "Map generation returned None"
    map_html = m._repr_html_()
    assert len(map_html) > 500, "Map HTML seems empty"
    print("   [PASS] Interactive Folium map with shelters and AI evacuation paths created successfully.")

    print("\n8. Testing Plotly Analytics & Visualizations...")
    g_fig = create_risk_gauge(pred["risk_score"], pred["category"], pred["color_hex"])
    r_fig = create_precipitation_forecast_chart(telemetry["hourly_times"], telemetry["hourly_precipitation"])
    d_fig = create_river_discharge_chart(telemetry["discharge_forecast_dates"], telemetry["discharge_forecast_values"])
    x_fig = create_factor_radar_chart(pred["contributions"])
    c_fig = create_nearby_comparison_chart(nearby)
    assert all([g_fig, r_fig, d_fig, x_fig, c_fig]), "Plotly chart creation failed"
    print("   [PASS] All Plotly forecast charts generated without errors.")

    print("\n==================================================")
    print("ALL 8 END-TO-END SYSTEM TEST MODULES PASSED WITH 100% SUCCESS!")
    print("==================================================")

if __name__ == '__main__':
    run_tests()
