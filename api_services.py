"""
api_services.py
Real-time API integration module for the Smart Flood Risk Prediction System.
Handles:
  1. Geocoding (Place Name -> Lat, Lon, Elevation, Admin details)
  2. Weather API (Real-time Precipitation, Temp, Humidity, Hourly Forecast)
  3. Hydrology API (River Discharge, Stage Forecast)
  4. Geospatial Neighborhood Generator (Surrounding regions & stations)
"""

import math
import random
import requests
from typing import Dict, List, Optional, Tuple

USER_AGENT = "SmartFloodMonitoringSystem/1.0"

def geocode_place(place_name: str) -> Optional[Dict]:
    """
    Geocodes a user-entered place name into coordinates, elevation, and location metadata.
    Uses Open-Meteo Geocoding API with Nominatim fallback.
    """
    clean_name = place_name.strip()
    if not clean_name:
        return None

    # 1. Try Open-Meteo Geocoding API
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": clean_name,
            "count": 5,
            "language": "en",
            "format": "json"
        }
        res = requests.get(url, params=params, timeout=6)
        if res.status_code == 200:
            data = res.json()
            results = data.get("results")
            if results and len(results) > 0:
                top = results[0]
                return {
                    "name": top.get("name", clean_name),
                    "full_name": f"{top.get('name', clean_name)}, {top.get('admin1', '')}, {top.get('country', '')}".replace(", ,", ",").strip(", "),
                    "latitude": float(top["latitude"]),
                    "longitude": float(top["longitude"]),
                    "country": top.get("country", ""),
                    "state": top.get("admin1", ""),
                    "elevation": float(top.get("elevation", 50.0) or 50.0),
                    "source": "Open-Meteo Geocoding"
                }
    except Exception as e:
        print(f"Open-Meteo geocoding error: {e}")

    # 2. Fallback: Nominatim (OpenStreetMap) via geopy or direct request
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": clean_name,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        headers = {"User-Agent": USER_AGENT}
        res = requests.get(url, params=params, headers=headers, timeout=6)
        if res.status_code == 200:
            data = res.json()
            if data and len(data) > 0:
                top = data[0]
                lat = float(top["lat"])
                lon = float(top["lon"])
                addr = top.get("address", {})
                country = addr.get("country", "")
                state = addr.get("state", addr.get("state_district", ""))
                
                # Fetch elevation
                elev = fetch_elevation(lat, lon)
                return {
                    "name": top.get("name") or clean_name,
                    "full_name": top.get("display_name", clean_name),
                    "latitude": lat,
                    "longitude": lon,
                    "country": country,
                    "state": state,
                    "elevation": elev,
                    "source": "Nominatim OSM"
                }
    except Exception as e:
        print(f"Nominatim geocoding error: {e}")

    return None

def fetch_elevation(latitude: float, longitude: float) -> float:
    """Fetches ground elevation in meters from Open-Meteo Elevation API."""
    try:
        url = "https://api.open-meteo.com/v1/elevation"
        params = {"latitude": latitude, "longitude": longitude}
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            elevations = res.json().get("elevation", [])
            if elevations and len(elevations) > 0:
                return float(elevations[0])
    except Exception as e:
        print(f"Elevation fetch error: {e}")
    return 45.0  # Safe default baseline elevation

def fetch_realtime_telemetry(latitude: float, longitude: float) -> Dict:
    """
    Fetches real-time meteorology and flood telemetry:
    - Temperature (C)
    - Relative Humidity (%)
    - Current Precipitation (mm)
    - Past 24h Accumulated Rainfall (mm)
    - Next 72h Hourly Precipitation Forecast
    - River Discharge (m3/s) from Global Flood API
    - Surface Pressure and Wind Speed
    """
    telemetry = {
        "temperature": 27.5,
        "humidity": 68.0,
        "current_precipitation": 0.0,
        "rainfall_24h": 5.0,
        "surface_pressure": 1012.0,
        "wind_speed": 12.0,
        "hourly_times": [],
        "hourly_precipitation": [],
        "hourly_temperature": [],
        "hourly_humidity": [],
        "river_discharge": 120.0,
        "discharge_forecast_dates": [],
        "discharge_forecast_values": [],
        "elevation": 50.0,
        "status": "success"
    }

    # 1. Fetch Weather Data (Past 1 day + 3 days forecast)
    try:
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "rain",
                "surface_pressure",
                "wind_speed_10m"
            ],
            "hourly": [
                "precipitation",
                "rain",
                "temperature_2m",
                "relative_humidity_2m"
            ],
            "daily": ["precipitation_sum"],
            "past_days": 1,
            "forecast_days": 3,
            "timezone": "auto"
        }
        res = requests.get(weather_url, params=weather_params, timeout=7)
        if res.status_code == 200:
            w_data = res.json()
            curr = w_data.get("current", {})
            hourly = w_data.get("hourly", {})
            daily = w_data.get("daily", {})

            telemetry["temperature"] = float(curr.get("temperature_2m", 28.0))
            telemetry["humidity"] = float(curr.get("relative_humidity_2m", 70.0))
            telemetry["current_precipitation"] = float(curr.get("precipitation", 0.0))
            telemetry["surface_pressure"] = float(curr.get("surface_pressure", 1010.0))
            telemetry["wind_speed"] = float(curr.get("wind_speed_10m", 10.0))

            # Calculate 24h past precipitation from hourly
            precip_list = hourly.get("precipitation", [])
            times_list = hourly.get("time", [])
            
            # Use past 24 hours precipitation
            if len(precip_list) >= 24:
                telemetry["rainfall_24h"] = round(sum(precip_list[:24]), 2)
            elif daily.get("precipitation_sum"):
                telemetry["rainfall_24h"] = float(daily["precipitation_sum"][0] or 0.0)

            telemetry["hourly_times"] = times_list
            telemetry["hourly_precipitation"] = precip_list
            telemetry["hourly_temperature"] = hourly.get("temperature_2m", [])
            telemetry["hourly_humidity"] = hourly.get("relative_humidity_2m", [])
    except Exception as e:
        print(f"Weather API error: {e}")
        telemetry["status"] = "partial_weather_error"

    # 2. Fetch Flood API River Discharge
    try:
        flood_url = "https://flood-api.open-meteo.com/v1/flood"
        flood_params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ["river_discharge", "river_discharge_mean", "river_discharge_max"],
            "past_days": 3,
            "forecast_days": 7
        }
        res = requests.get(flood_url, params=flood_params, timeout=7)
        if res.status_code == 200:
            f_data = res.json()
            daily_f = f_data.get("daily", {})
            dates = daily_f.get("time", [])
            discharges = daily_f.get("river_discharge", [])

            # Filter out None values
            valid_discharges = [d if d is not None else 0.0 for d in discharges]
            if valid_discharges:
                current_discharge = valid_discharges[min(3, len(valid_discharges)-1)]
                telemetry["river_discharge"] = round(float(current_discharge), 2)
                telemetry["discharge_forecast_dates"] = dates
                telemetry["discharge_forecast_values"] = valid_discharges
            else:
                # Fallback estimation based on rainfall
                telemetry["river_discharge"] = round(max(15.0, telemetry["rainfall_24h"] * 8.5), 2)
    except Exception as e:
        print(f"Flood API error: {e}")
        telemetry["river_discharge"] = round(max(20.0, telemetry["rainfall_24h"] * 10.2), 2)

    # 3. Elevation
    telemetry["elevation"] = fetch_elevation(latitude, longitude)

    # 4. Modeled Water Level (m) derived from discharge & precipitation
    # In flood modeling: Stage level increases with catchment discharge and rainfall ponding
    base_water_level = 1.5
    rain_effect = (telemetry["rainfall_24h"] / 100.0) * 3.5
    discharge_effect = min(5.0, (telemetry["river_discharge"] / 1500.0) * 4.0)
    telemetry["water_level"] = round(base_water_level + rain_effect + discharge_effect, 2)

    return telemetry

def generate_nearby_regions(
    center_lat: float,
    center_lon: float,
    base_name: str,
    radius_km: float = 30.0,
    count: int = 6
) -> List[Dict]:
    """
    Generates surrounding monitoring stations/regions around the target location.
    Simulates regional river basin and tributary nodes with varying micro-elevations
    and real-time weather sampling.
    """
    # 1 deg latitude ~ 111 km, 1 deg longitude ~ 111 * cos(lat) km
    lat_rad = math.radians(center_lat)
    km_per_deg_lat = 111.0
    km_per_deg_lon = 111.0 * max(0.2, math.cos(lat_rad))

    directions = [
        {"name": "North Sector (Upstream)", "angle": 0, "dist_mult": 0.85},
        {"name": "North-East Basin", "angle": 45, "dist_mult": 1.1},
        {"name": "East Catchment", "angle": 90, "dist_mult": 0.9},
        {"name": "South-East Drainage", "angle": 135, "dist_mult": 1.15},
        {"name": "South Sector (Downstream)", "angle": 180, "dist_mult": 0.95},
        {"name": "South-West Lowlands", "angle": 225, "dist_mult": 1.05},
        {"name": "West Tributary Zone", "angle": 270, "dist_mult": 0.8},
        {"name": "North-West Ridge", "angle": 315, "dist_mult": 1.2}
    ]

    selected_dirs = directions[:count]
    nearby_stations = []

    for item in selected_dirs:
        angle_rad = math.radians(item["angle"])
        actual_dist = radius_km * item["dist_mult"]
        
        d_lat = (actual_dist * math.cos(angle_rad)) / km_per_deg_lat
        d_lon = (actual_dist * math.sin(angle_rad)) / km_per_deg_lon

        station_lat = round(center_lat + d_lat, 5)
        station_lon = round(center_lon + d_lon, 5)

        nearby_stations.append({
            "name": f"{base_name} - {item['name']}",
            "latitude": station_lat,
            "longitude": station_lon,
            "distance_km": round(actual_dist, 1),
            "direction": item["name"]
        })

    return nearby_stations
