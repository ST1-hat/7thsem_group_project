"""
map_view.py
Interactive Geospatial Map generation module using Folium.
Renders the primary target location with custom highlighting, pulsing risk halo,
surrounding monitoring stations, topological contours, and risk overlays.
"""

import folium
from folium import plugins
from typing import Dict, List, Any

def create_flood_map(
    target_info: Dict[str, Any],
    target_risk: Dict[str, Any],
    nearby_stations: List[Dict[str, Any]],
    zoom_start: int = 11
) -> folium.Map:
    """
    Constructs an interactive Folium map centered on the target location with:
    - Primary highlighted target marker with radar pulse ring
    - Nearby surrounding stations color-coded by flood risk
    - Risk buffer catchment zones
    - Interactive tooltips & rich popup cards
    - Topography & satellite map tile switches
    - Custom map legend
    """
    center_lat = target_info["latitude"]
    center_lon = target_info["longitude"]
    target_color = target_risk["color_hex"]

    # Base Folium Map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles="CartoDB positron",
        control_scale=True
    )

    # Alternate Tile Layers
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="OpenStreetMap Standard"
    ).add_to(m)

    folium.TileLayer(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
        name="Topography / Elevation (OpenTopoMap)"
    ).add_to(m)

    # 1. Primary Location: Target Pulsing Halo & Inundation Buffer
    # Outer risk impact buffer
    folium.Circle(
        location=[center_lat, center_lon],
        radius=4500,  # 4.5 km buffer
        color=target_color,
        weight=2,
        fill=True,
        fill_color=target_color,
        fill_opacity=0.18,
        tooltip=f"<b>Primary Monitoring Zone</b><br>Risk: {target_risk['category']} ({target_risk['risk_score']}%)"
    ).add_to(m)

    # Inner core zone
    folium.Circle(
        location=[center_lat, center_lon],
        radius=1500,
        color=target_color,
        weight=3,
        fill=True,
        fill_color=target_color,
        fill_opacity=0.35
    ).add_to(m)

    # Custom HTML popup for the primary target
    popup_html = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-width: 230px; padding: 6px;">
        <div style="background: {target_color}; color: white; padding: 6px 10px; border-radius: 6px; font-weight: bold; font-size: 14px; margin-bottom: 8px;">
            🚨 {target_risk['alert_level']}
        </div>
        <h4 style="margin: 0 0 6px 0; color: #1e293b; font-size: 15px;">{target_info['name']}</h4>
        <div style="font-size: 12px; color: #475569; line-height: 1.5;">
            <b>Flood Risk:</b> <span style="color: {target_color}; font-weight: bold; font-size: 13px;">{target_risk['risk_score']}% ({target_risk['category']})</span><br>
            <b>24h Rainfall:</b> {target_risk['inputs_used']['rainfall_mm']} mm<br>
            <b>River Discharge:</b> {target_risk['inputs_used']['river_discharge_m3s']} m³/s<br>
            <b>Water Level:</b> {target_risk['inputs_used']['water_level_m']} m<br>
            <b>Elevation:</b> {target_risk['inputs_used']['elevation_m']} m<br>
            <b>Coordinates:</b> {center_lat:.4f}, {center_lon:.4f}
        </div>
    </div>
    """
    
    # Primary Marker
    folium.Marker(
        location=[center_lat, center_lon],
        popup=folium.Popup(popup_html, max_width=320),
        tooltip=f"⭐ <b>TARGET: {target_info['name']}</b> ({target_risk['risk_score']}% Risk)",
        icon=folium.Icon(color="red" if target_risk['risk_score'] > 60 else "blue", icon="bullseye", prefix="fa")
    ).add_to(m)

    # 2. Add Nearby Peripheral Monitoring Stations
    for station in nearby_stations:
        st_lat = station["latitude"]
        st_lon = station["longitude"]
        st_name = station["name"]
        st_dist = station.get("distance_km", 20.0)
        st_risk = station.get("risk", target_risk)
        st_color = st_risk.get("color_hex", "#3b82f6")
        st_score = st_risk.get("risk_score", 30.0)

        # Connect station to center with subtle dashed line
        folium.PolyLine(
            locations=[[center_lat, center_lon], [st_lat, st_lon]],
            color="#94a3b8",
            weight=1.5,
            opacity=0.6,
            dash_array="5, 8"
        ).add_to(m)

        # Station Circle
        folium.CircleMarker(
            location=[st_lat, st_lon],
            radius=9,
            color=st_color,
            weight=2,
            fill=True,
            fill_color=st_color,
            fill_opacity=0.75,
            tooltip=f"📍 <b>{st_name}</b> ({st_dist} km)<br>Risk: <b>{st_score}%</b>"
        ).add_to(m)

        # Station Popup
        st_popup = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-width: 200px; padding: 4px;">
            <div style="background: {st_color}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-bottom: 6px;">
                {st_risk.get('alert_level', 'MONITORING')}
            </div>
            <b style="font-size: 13px; color: #0f172a;">{st_name}</b><br>
            <span style="font-size: 11px; color: #64748b;">Distance: {st_dist} km from center</span>
            <hr style="margin: 6px 0; border: none; border-top: 1px solid #e2e8f0;">
            <div style="font-size: 12px; color: #334155; line-height: 1.4;">
                <b>Predicted Risk:</b> <span style="color: {st_color}; font-weight: bold;">{st_score}%</span><br>
                <b>Category:</b> {st_risk.get('category', 'Moderate')}<br>
                <b>Rainfall:</b> {st_risk.get('inputs_used', {}).get('rainfall_mm', 0)} mm<br>
                <b>Elevation:</b> {st_risk.get('inputs_used', {}).get('elevation_m', 40)} m
            </div>
        </div>
        """
        folium.Marker(
            location=[st_lat, st_lon],
            popup=folium.Popup(st_popup, max_width=280),
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    background-color: {st_color};
                    border: 2px solid white;
                    border-radius: 50%;
                    width: 22px;
                    height: 22px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
                ">
                    {int(st_score)}%
                </div>
                """,
                icon_size=(22, 22),
                icon_anchor=(11, 11)
            )
        ).add_to(m)

    # 3. Add Custom Floating Map Legend
    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
        background: rgba(255, 255, 255, 0.94);
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.18);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 12px;
        color: #1e293b;
        border: 1px solid #cbd5e1;
        max-width: 220px;
    ">
        <div style="font-weight: bold; font-size: 13px; margin-bottom: 8px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px;">
            🌊 Flood Risk Levels
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <span style="display: inline-block; width: 14px; height: 14px; border-radius: 50%; background: #22c55e; margin-right: 8px;"></span>
            <span><b>Low Risk</b> (&lt; 30%)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <span style="display: inline-block; width: 14px; height: 14px; border-radius: 50%; background: #eab308; margin-right: 8px;"></span>
            <span><b>Moderate Risk</b> (30-60%)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <span style="display: inline-block; width: 14px; height: 14px; border-radius: 50%; background: #f97316; margin-right: 8px;"></span>
            <span><b>High Risk</b> (60-80%)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <span style="display: inline-block; width: 14px; height: 14px; border-radius: 50%; background: #ef4444; margin-right: 8px;"></span>
            <span><b>Critical / Flash</b> (&gt; 80%)</span>
        </div>
        <div style="font-size: 10px; color: #64748b; border-top: 1px solid #f1f5f9; padding-top: 4px;">
            ⭐ Highlighted = Selected Focus
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add Layer Control
    folium.LayerControl(position="topright").add_to(m)

    return m
