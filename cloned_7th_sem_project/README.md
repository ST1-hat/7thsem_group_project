# 🌊 FloodSense AI — React Command Center & Disaster Support System

> **7th Semester B.Tech Major Capstone Group Project in Computer Science & Engineering**  
> An automated, end-to-end AI and geospatial decision-support platform integrating hydrometeorological telemetry, early warning classification, **Dijkstra-based safe evacuation pathfinding**, and **historical catastrophe stress-testing**.

---

## 🚀 3-Page System & Geospatial Intelligence

The application features a modern **React Framework** with **Bright Mode**, a sticky **Top Navigation Bar**, and a dedicated **3-Page Architecture**:

1. 🗺️ **Geospatial Map (`MapPage.jsx`)**:
   - **Free-Source Tile Providers (Zero API Key Required)**:
     - 🏗️ **ESRI World Topo Map**: Renders physical structures, bridges, topography, elevation contours, and river morphology.
     - 🛰️ **ESRI World Imagery**: High-resolution satellite photographic imagery displaying real physical building footprints, riverbeds, and dams.
     - 🗺️ **CartoDB Positron**: High-contrast, clean municipal street layouts.
     - ⛰️ **OpenTopoMap**: SRTM elevation contour lines and mountain ridges.
   - **Dynamic Flood Inundation Heatmap**: Integrated via `leaflet.heat` with smooth blue-to-red water depth density gradients.
   - **Physical Structures & Critical Infrastructure**:
     - 🌉 Arterial River Bridges & Viaducts (deck elevation & remaining water clearance)
     - 🚪 Hydraulic Sluice Gates & Barrages (backflow reversal alerts)
     - 🧱 Armored River Bunds & Levees (freeboard safety limits)
     - 🏥 Apex Trauma Hospitals & Rooftop Helipads
     - ⚡ Stormwater De-Watering Stations
   - **Dijkstra Evacuation Routing**: Solid Emerald High-Ground Corridor (100% passable) vs Red Dashed Submerged Roadway.
   - **Turn-by-turn waypoint manifest table**.

2. 📊 **Command Dashboard (`DashboardPage.jsx`)**:
   - Executive Alert Banners with IMD/CWC hazard levels.
   - 6 KPI metric cards (24h Rainfall, River Discharge, Water Stage, Elevation, Safe ETA, Shelter Capacity).
   - What-If Simulation Sandbox (cloudburst rainfall & dam surge stress-testing).
   - AI Model Synthesis (XGBoost + Random Forest ensemble) and Radial Risk Gauge.
   - 36h Hourly Precipitation NWP Curve.
   - 7-Day GloFAS River Discharge Hydrograph.
   - Explainable AI (XAI) Multi-Factor Radar.
   - Assessment manifest export (JSON & CSV).

3. 🛡️ **Safety Center (`SafetyPage.jsx`)**:
   - **24×7 Important Emergency Helplines**: 112 National SOS, 1078 NDRF, 108 Ambulance, 100 Police, 1070 Disaster Control, 1800-11-8151 CWC, 1800-180-1717 IMD, with one-click **Call** and **Copy Number** buttons.
   - **Interactive Preparedness Checklist**: Emergency Kit, Home Protection, and Evacuation Readiness with live completion progress bar.
   - **Critical Flood Survival Directives**: Actionable life-safety guidelines during active inundation.

---

## 🛠️ How to Launch

Run the unified runner:
```powershell
python start_app.py
```
*(Or double-click `start.bat` on Windows)*

- **React Frontend**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
