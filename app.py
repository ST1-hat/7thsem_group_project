"""
app.py
Smart Flood Risk Prediction & Real-Time Monitoring System
A comprehensive AI-driven geospatial and hydrometeorological dashboard.
Takes user input as a place name, fetches real-time API telemetry, predicts flood risk,
renders an interactive highlighted map with nearby regional stations, and displays
an executive dashboard with forecast hydrographs and emergency advisories.
"""

import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import json
import time

# Local modular imports
from api_services import geocode_place, fetch_realtime_telemetry, generate_nearby_regions
from flood_engine import get_engine
from map_view import create_flood_map
from utils import (
    EMERGENCY_ADVISORIES,
    create_risk_gauge,
    create_precipitation_forecast_chart,
    create_river_discharge_chart,
    create_factor_radar_chart,
    create_nearby_comparison_chart
)

# ---------------------------------------------------------
# Page Configuration & Custom CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Smart Flood Risk Prediction & Monitoring System",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Impact Dashboard Styling
st.markdown("""
<style>
    /* Main Layout */
    .main {
        background-color: #f8fafc;
    }
    
    /* Header Container */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0369a1 100%);
        padding: 24px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15);
    }
    .main-header h1 {
        color: white !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #94a3b8 !important;
        font-size: 14px !important;
        margin-top: 6px !important;
        margin-bottom: 0 !important;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    .metric-label {
        font-size: 12px;
        text-transform: uppercase;
        font-weight: 700;
        color: #64748b;
        letter-spacing: 0.5px;
    }
    .metric-val {
        font-size: 24px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 2px;
    }

    /* Alert Banner */
    .alert-banner {
        border-radius: 10px;
        padding: 16px 22px;
        color: white;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Section Headers */
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 10px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Tag badge */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# State Initialization
# ---------------------------------------------------------
if 'current_place' not in st.session_state:
    st.session_state.current_place = "Patna"
if 'place_info' not in st.session_state:
    st.session_state.place_info = None
if 'telemetry' not in st.session_state:
    st.session_state.telemetry = None
if 'risk_result' not in st.session_state:
    st.session_state.risk_result = None
if 'nearby_stations' not in st.session_state:
    st.session_state.nearby_stations = []
if 'sim_rain' not in st.session_state:
    st.session_state.sim_rain = 0.0
if 'sim_discharge' not in st.session_state:
    st.session_state.sim_discharge = 0.0

engine = get_engine()

# ---------------------------------------------------------
# Core Evaluation Function
# ---------------------------------------------------------
def analyze_location(place_query: str, sim_rain_add: float = 0.0, sim_discharge_add: float = 0.0):
    with st.spinner(f"🔍 Geocoding '{place_query}' & querying real-time satellites and flood sensors..."):
        # 1. Geocode
        place_data = geocode_place(place_query)
        if not place_data:
            st.error(f"Could not locate '{place_query}'. Please check the spelling or try another city.")
            return False

        lat = place_data["latitude"]
        lon = place_data["longitude"]

        # 2. Fetch Real-time Telemetry
        telemetry_data = fetch_realtime_telemetry(lat, lon)
        
        # Apply any active simulation offsets
        eff_rain = max(0.0, telemetry_data["rainfall_24h"] + sim_rain_add)
        eff_discharge = max(0.0, telemetry_data["river_discharge"] + sim_discharge_add)
        eff_water_level = max(0.5, telemetry_data["water_level"] + (sim_rain_add / 40.0) + (sim_discharge_add / 800.0))

        # Check historical flood zones in India
        known_flood_regions = ["bihar", "assam", "kerala", "mumbai", "odisha", "cuttack", "patna", "guwahati", "bengal", "ganga", "brahmaputra"]
        is_historical = 1 if any(k in place_data["full_name"].lower() for k in known_flood_regions) else 0

        # 3. Predict Risk for Primary Target
        primary_risk = engine.predict_flood_risk(
            latitude=lat,
            longitude=lon,
            rainfall_mm=round(eff_rain, 1),
            temperature_c=telemetry_data["temperature"],
            humidity_pct=telemetry_data["humidity"],
            river_discharge_m3s=round(eff_discharge, 1),
            water_level_m=round(eff_water_level, 2),
            elevation_m=telemetry_data["elevation"],
            land_cover="Urban",
            soil_type="Clay" if is_historical else "Loam",
            population_density=5200.0,
            infrastructure=1,
            historical_floods=is_historical
        )

        # 4. Generate & Predict Nearby Stations
        nearby = generate_nearby_regions(lat, lon, place_data["name"], radius_km=28.0, count=6)
        for station in nearby:
            # Micro-variations around regional node
            st_lat = station["latitude"]
            st_lon = station["longitude"]
            st_elev = max(5.0, telemetry_data["elevation"] + np.random.uniform(-12, 18))
            st_rain = max(0.0, eff_rain * np.random.uniform(0.85, 1.25))
            st_discharge = max(5.0, eff_discharge * np.random.uniform(0.8, 1.2))
            st_wl = max(0.5, eff_water_level * np.random.uniform(0.9, 1.15))

            st_risk = engine.predict_flood_risk(
                latitude=st_lat,
                longitude=st_lon,
                rainfall_mm=round(st_rain, 1),
                temperature_c=telemetry_data["temperature"],
                humidity_pct=telemetry_data["humidity"],
                river_discharge_m3s=round(st_discharge, 1),
                water_level_m=round(st_wl, 2),
                elevation_m=round(st_elev, 1),
                land_cover="Agricultural",
                soil_type="Clay",
                population_density=3400.0,
                infrastructure=0,
                historical_floods=is_historical
            )
            station["risk"] = st_risk
            station["elevation"] = round(st_elev, 1)

        # Save to session
        st.session_state.current_place = place_query
        st.session_state.place_info = place_data
        st.session_state.telemetry = telemetry_data
        st.session_state.risk_result = primary_risk
        st.session_state.nearby_stations = nearby
        return True

# Run initial analysis if not already run
if st.session_state.place_info is None:
    analyze_location("Patna")

# ---------------------------------------------------------
# Sidebar: Controls & Place Search
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌐 Location Input")
    search_input = st.text_input(
        "Enter City, Town, or District Name:",
        value=st.session_state.current_place,
        placeholder="e.g., Guwahati, Mumbai, Patna, Kochi"
    )

    if st.button("🔎 Fetch Telemetry & Assess Risk", use_container_width=True, type="primary"):
        if search_input.strip():
            analyze_location(search_input.strip(), st.session_state.sim_rain, st.session_state.sim_discharge)

    st.markdown("---")
    st.markdown("##### ⚡ Quick Select Flood Hotspots:")
    quick_cols1 = st.columns(2)
    with quick_cols1[0]:
        if st.button("🌊 Patna", use_container_width=True):
            analyze_location("Patna", st.session_state.sim_rain, st.session_state.sim_discharge)
        if st.button("🌊 Mumbai", use_container_width=True):
            analyze_location("Mumbai", st.session_state.sim_rain, st.session_state.sim_discharge)
        if st.button("🌊 Cuttack", use_container_width=True):
            analyze_location("Cuttack", st.session_state.sim_rain, st.session_state.sim_discharge)
    with quick_cols1[1]:
        if st.button("🌊 Guwahati", use_container_width=True):
            analyze_location("Guwahati", st.session_state.sim_rain, st.session_state.sim_discharge)
        if st.button("🌊 Kochi", use_container_width=True):
            analyze_location("Kochi", st.session_state.sim_rain, st.session_state.sim_discharge)
        if st.button("🌊 Varanasi", use_container_width=True):
            analyze_location("Varanasi", st.session_state.sim_rain, st.session_state.sim_discharge)

    st.markdown("---")
    st.markdown("### 🧪 What-If Simulation Sandbox")
    st.caption("Simulate environmental surges to test model sensitivity:")

    sim_rain_slider = st.slider(
        "Simulate Rainfall Surge (+ mm):",
        min_value=0,
        max_value=250,
        value=int(st.session_state.sim_rain),
        step=10,
        help="Simulate heavy monsoon or cloudburst rainfall over 24 hours."
    )
    sim_discharge_slider = st.slider(
        "Simulate Upstream Dam Release (+ m³/s):",
        min_value=0,
        max_value=4000,
        value=int(st.session_state.sim_discharge),
        step=100,
        help="Simulate sudden water release from upstream reservoirs/barrages."
    )

    if (sim_rain_slider != st.session_state.sim_rain) or (sim_discharge_slider != st.session_state.sim_discharge):
        st.session_state.sim_rain = float(sim_rain_slider)
        st.session_state.sim_discharge = float(sim_discharge_slider)
        analyze_location(st.session_state.current_place, st.session_state.sim_rain, st.session_state.sim_discharge)

    if st.session_state.sim_rain > 0 or st.session_state.sim_discharge > 0:
        if st.button("↺ Reset Simulation to Live API Values", use_container_width=True):
            st.session_state.sim_rain = 0.0
            st.session_state.sim_discharge = 0.0
            analyze_location(st.session_state.current_place, 0.0, 0.0)

    st.markdown("---")
    st.markdown("##### 📌 System Telemetry Source:")
    st.caption("• **Geocoding:** Open-Meteo & Nominatim\n• **Weather:** Open-Meteo High-Res\n• **Discharge:** Open-Meteo Global Flood API\n• **AI Model:** XGBoost & Random Forest Ensemble")

# ---------------------------------------------------------
# Main Dashboard Header
# ---------------------------------------------------------
st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1>🌊 Smart Flood Risk Prediction & Real-Time Monitoring System</h1>
            <p>Automated AI Hydrometeorological Telemetry, Early Warning Classification & Geospatial Inundation Mapping</p>
        </div>
        <div style="text-align: right;">
            <span class="badge" style="background: rgba(255,255,255,0.2); color: white;">7th Sem Capstone Project</span>
            <div style="font-size: 11px; color: #cbd5e1; margin-top: 4px;">Live Auto-Refresh Active</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Section 1: Executive Alert Banner & Key Metrics
# ---------------------------------------------------------
place = st.session_state.place_info
risk = st.session_state.risk_result
tele = st.session_state.telemetry

if place and risk and tele:
    # Alert Banner
    alert_bg = risk["color_hex"]
    st.markdown(f"""
    <div class="alert-banner" style="background: {alert_bg};">
        <div>
            <div style="font-size: 12px; letter-spacing: 1px; font-weight: 800; text-transform: uppercase;">
                CURRENT ADVISORY STATUS
            </div>
            <div style="font-size: 26px; font-weight: 900; margin-top: 2px;">
                {risk['alert_level']} — {risk['category']} ({risk['risk_score']}%)
            </div>
            <div style="font-size: 13px; opacity: 0.95; margin-top: 4px;">
                📍 <b>{place['full_name']}</b> | Lat: {place['latitude']:.4f}, Lon: {place['longitude']:.4f} | Elevation: {risk['inputs_used']['elevation_m']} m MSL
            </div>
        </div>
        <div style="text-align: right; background: rgba(0,0,0,0.2); padding: 10px 18px; border-radius: 8px;">
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase;">Hydrological Stage</div>
            <div style="font-size: 20px; font-weight: 800;">{risk['status_text']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 6 Top Metric KPI Cards
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    with m1:
        rain_val = risk['inputs_used']['rainfall_mm']
        rain_note = "Normal" if rain_val < 15.5 else ("Moderate" if rain_val < 64.5 else "Heavy Rain")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🌧️ 24h Rainfall</div>
            <div class="metric-val">{rain_val} <span style="font-size: 14px;">mm</span></div>
            <div class="metric-sub">Category: <b>{rain_note}</b></div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        disch_val = risk['inputs_used']['river_discharge_m3s']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🌊 River Discharge</div>
            <div class="metric-val">{disch_val} <span style="font-size: 14px;">m³/s</span></div>
            <div class="metric-sub">Basin Hydrology Status</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        wl_val = risk['inputs_used']['water_level_m']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📏 Water Stage</div>
            <div class="metric-val">{wl_val} <span style="font-size: 14px;">m</span></div>
            <div class="metric-sub">Calculated Runoff Stage</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        elev_val = risk['inputs_used']['elevation_m']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⛰️ Terrain Elevation</div>
            <div class="metric-val">{elev_val} <span style="font-size: 14px;">m</span></div>
            <div class="metric-sub">Topography Above MSL</div>
        </div>
        """, unsafe_allow_html=True)

    with m5:
        hum_val = tele['humidity']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💧 Relative Humidity</div>
            <div class="metric-val">{hum_val} <span style="font-size: 14px;">%</span></div>
            <div class="metric-sub">Atmospheric Saturation</div>
        </div>
        """, unsafe_allow_html=True)

    with m6:
        temp_val = tele['temperature']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🌡️ Temperature</div>
            <div class="metric-val">{temp_val} <span style="font-size: 14px;">°C</span></div>
            <div class="metric-sub">Pressure: {tele['surface_pressure']:.0f} hPa</div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Section 2: Interactive Geospatial Map & Risk Gauge
    # ---------------------------------------------------------
    st.markdown("<div class='section-title'>🗺️ Interactive Geospatial Inundation Map & Regional Monitoring</div>", unsafe_allow_html=True)
    st.caption("The selected location is marked with a pulsing target indicator and flood risk impact buffer. Surrounding peripheral stations are color-coded to visualize watershed flood spread.")

    map_col, gauge_col = st.columns([7, 3])

    with map_col:
        # Create Folium Map with Target and Surrounding Stations
        flood_map = create_flood_map(place, risk, st.session_state.nearby_stations)
        st_folium(flood_map, width="100%", height=520, returned_objects=[])

    with gauge_col:
        # Probability Gauge
        gauge_fig = create_risk_gauge(risk['risk_score'], risk['category'], risk['color_hex'])
        st.plotly_chart(gauge_fig, use_container_width=True)

        # AI Prediction Details Box
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; padding: 14px 18px; border: 1px solid #e2e8f0; font-size: 13px; line-height: 1.6;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 6px;">🧠 AI Model Inference Summary</div>
            <div>• <b>ML Probability (XGB+RF):</b> <span style="color: {risk['color_hex']}; font-weight: bold;">{risk['ml_probability']}%</span></div>
            <div>• <b>Hydrological Index:</b> {risk['hydro_index']}%</div>
            <div>• <b>Combined Flood Score:</b> <span style="color: {risk['color_hex']}; font-weight: bold;">{risk['risk_score']}%</span></div>
            <div>• <b>Alert Category:</b> {risk['category']}</div>
            <div style="margin-top: 8px; font-size: 12px; color: #64748b;">{risk['description']}</div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Section 3: Hydrological Analytics & Forecasting Tabs
    # ---------------------------------------------------------
    st.markdown("<div class='section-title'>📊 Real-Time Hydrometeorological Analytics & Forecast</div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌧️ Precipitation Forecast (Next 36h)",
        "🌊 River Discharge Hydrograph (7-Day)",
        "🎯 Explainable AI (Factor Importance)",
        "📍 Surrounding Stations Matrix"
    ])

    with tab1:
        rain_chart = create_precipitation_forecast_chart(
            tele.get("hourly_times", []),
            tele.get("hourly_precipitation", [])
        )
        st.plotly_chart(rain_chart, use_container_width=True)
        st.caption("Hourly precipitation forecast supplied directly by Open-Meteo NWP (Numerical Weather Prediction) model. Dashed thresholds indicate IMD heavy rain alerts.")

    with tab2:
        discharge_chart = create_river_discharge_chart(
            tele.get("discharge_forecast_dates", []),
            tele.get("discharge_forecast_values", [])
        )
        st.plotly_chart(discharge_chart, use_container_width=True)
        st.caption("River discharge forecast retrieved from Global Flood Awareness System (GloFAS) hydrology nodes. The danger mark line represents typical bankfull capacity.")

    with tab3:
        r_col1, r_col2 = st.columns([5, 5])
        with r_col1:
            radar_fig = create_factor_radar_chart(risk["contributions"])
            st.plotly_chart(radar_fig, use_container_width=True)
        with r_col2:
            st.markdown("#### 🔬 Factor Contribution Breakdown")
            st.write("The AI and Hydrological system inspects multiple dynamic variables to assess the risk of inundation:")
            
            c_df = pd.DataFrame([
                {"Hydrologic Driver": k, "Impact / Saturation Level (%)": v}
                for k, v in risk["contributions"].items()
            ])
            st.dataframe(c_df, use_container_width=True, hide_index=True)

            st.markdown(f"""
            > **Primary Vulnerability Driver:** `{max(risk['contributions'], key=risk['contributions'].get)}` is currently the dominant factor driving the {risk['category']} status.
            """)

    with tab4:
        st_col1, st_col2 = st.columns([6, 4])
        with st_col1:
            st_comp_chart = create_nearby_comparison_chart(st.session_state.nearby_stations)
            st.plotly_chart(st_comp_chart, use_container_width=True)
        with st_col2:
            st.markdown("#### 📡 Peripheral Sensor Nodes")
            st_data = []
            for s in st.session_state.nearby_stations:
                st_data.append({
                    "Station": s["name"].split(" - ")[-1],
                    "Distance (km)": s.get("distance_km", 20.0),
                    "Risk Score": f"{s.get('risk', {}).get('risk_score', 0)}%",
                    "Alert": s.get('risk', {}).get('category', 'Normal')
                })
            st.dataframe(pd.DataFrame(st_data), use_container_width=True, hide_index=True)

    # ---------------------------------------------------------
    # Section 4: Emergency Protocols & Disaster Advisory
    # ---------------------------------------------------------
    st.markdown("<div class='section-title'>🛡️ Disaster Response Protocols & Safety Action Plan</div>", unsafe_allow_html=True)
    
    advisory = EMERGENCY_ADVISORIES.get(risk['category'], EMERGENCY_ADVISORIES["LOW RISK"])
    
    adv_col1, adv_col2 = st.columns([7, 3])
    
    with adv_col1:
        st.markdown(f"### {advisory['title']}")
        st.markdown("**Actionable Guidelines for Local Authorities & Residents:**")
        for g in advisory['guidelines']:
            st.markdown(f"- {g}")

    with adv_col2:
        st.markdown("""
        <div style="background: white; border-radius: 8px; padding: 16px; border: 1px solid #cbd5e1; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
            <div style="font-weight: bold; font-size: 14px; color: #0f172a; margin-bottom: 8px;">
                📞 Emergency Response Directory
            </div>
            <div style="font-size: 13px; line-height: 1.6; color: #334155;">
                <b>NDRF National Helpline:</b> 1078<br>
                <b>National Emergency SOS:</b> 112<br>
                <b>State Disaster Control:</b> 1070<br>
                <b>Ambulance / Medical:</b> 108<br>
                <b>Police Assistance:</b> 100
            </div>
            <hr style="margin: 10px 0; border: none; border-top: 1px solid #e2e8f0;">
            <div style="font-size: 12px; color: #64748b;">
                <b>Tactical Readiness:</b><br>
        """ + f"{advisory['ndrf_status']}</div></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Section 5: Export / Download Assessment Report
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("<div class='section-title'>📄 Project Report & Data Export</div>", unsafe_allow_html=True)

    report_payload = {
        "assessment_location": place["full_name"],
        "coordinates": {"latitude": place["latitude"], "longitude": place["longitude"]},
        "timestamp_generated": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "predicted_risk_score": f"{risk['risk_score']}%",
        "risk_category": risk["category"],
        "alert_level": risk["alert_level"],
        "hydrological_telemetry": risk["inputs_used"],
        "ml_probability": f"{risk['ml_probability']}%",
        "factor_contributions": risk["contributions"],
        "surrounding_stations_monitored": len(st.session_state.nearby_stations)
    }

    report_json = json.dumps(report_payload, indent=4)
    
    rep_c1, rep_c2 = st.columns([3, 7])
    with rep_c1:
        st.download_button(
            label="📥 Download Assessment Report (JSON)",
            data=report_json,
            file_name=f"flood_risk_report_{place['name'].lower()}_{time.strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
    with rep_c2:
        # Create CSV summary of current telemetry and prediction
        summary_df = pd.DataFrame([{
            "Location": place["name"],
            "Latitude": place["latitude"],
            "Longitude": place["longitude"],
            "Rainfall_mm": risk["inputs_used"]["rainfall_mm"],
            "River_Discharge_m3s": risk["inputs_used"]["river_discharge_m3s"],
            "Water_Level_m": risk["inputs_used"]["water_level_m"],
            "Elevation_m": risk["inputs_used"]["elevation_m"],
            "Risk_Score_Pct": risk["risk_score"],
            "Category": risk["category"],
            "Alert_Level": risk["alert_level"]
        }])
        st.download_button(
            label="📊 Download Telemetry & Prediction (CSV)",
            data=summary_df.to_csv(index=False),
            file_name=f"flood_telemetry_{place['name'].lower()}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 12px; padding: 10px 0;">
    Smart Flood Risk Prediction & Real-Time Monitoring System • 7th Semester B.Tech Capstone Project • Powered by Open-Meteo NWP, GloFAS & Scikit-Learn/XGBoost
</div>
""", unsafe_allow_html=True)
