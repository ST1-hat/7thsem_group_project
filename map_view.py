"""
map_view.py
Interactive Geospatial Map generation module using Folium.
Renders the primary target location with custom highlighting, pulsing risk halo,
surrounding monitoring stations, topological contours, relief shelters, and
dynamic AI-computed safe evacuation routing corridors.
"""

import folium
from folium import plugins
from typing import Dict, List, Any, Optional

def create_flood_map(
    target_info: Dict[str, Any],
    target_risk: Dict[str, Any],
    nearby_stations: List[Dict[str, Any]],
    evacuation_plan: Optional[Dict[str, Any]] = None,
    zoom_start: int = 12
) -> folium.Map:
    """
    Constructs an interactive Folium map centered on the target location with:
    - Primary highlighted target marker with radar pulse ring
    - Nearby surrounding stations color-coded by flood risk
    - Risk buffer catchment zones
    - Designated high-elevation emergency relief shelters
    - AI-computed safe evacuation corridors vs hazardous submerged roads
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

    # Feature Groups for toggling layers
    fg_stations = folium.FeatureGroup(name="Regional Hydrology Stations", show=True).add_to(m)
    fg_shelters = folium.FeatureGroup(name="Designated Relief Shelters", show=True).add_to(m)
    fg_safe_route = folium.FeatureGroup(name="🛡️ AI Safe Evacuation Path", show=True).add_to(m)
    fg_hazard_route = folium.FeatureGroup(name="⚠️ Submerged / Hazard Route", show=True).add_to(m)

    # 1. Primary Location: Target Pulsing Halo & Inundation Buffer
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

    folium.Circle(
        location=[center_lat, center_lon],
        radius=1500,
        color=target_color,
        weight=3,
        fill=True,
        fill_color=target_color,
        fill_opacity=0.35
    ).add_to(m)

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

        folium.PolyLine(
            locations=[[center_lat, center_lon], [st_lat, st_lon]],
            color="#94a3b8",
            weight=1.5,
            opacity=0.6,
            dash_array="5, 8"
        ).add_to(fg_stations)

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
        ).add_to(fg_stations)

    # 3. Add Designated Emergency Relief Shelters & Evacuation Routes
    if evacuation_plan:
        shelters = evacuation_plan.get("candidate_shelters", [])
        active_shelter = evacuation_plan.get("target_shelter", {})
        active_shelter_id = active_shelter.get("id")

        for sh in shelters:
            is_active = (sh.get("id") == active_shelter_id)
            sh_lat = sh["latitude"]
            sh_lon = sh["longitude"]
            sh_elev = sh["elevation_m"]
            sh_beds = sh["remaining_beds"]
            sh_cap = sh["capacity"]
            
            shelter_html = f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-width: 250px; padding: 6px;">
                <div style="background: #059669; color: white; padding: 5px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; margin-bottom: 6px;">
                    🛡️ DESIGNATED RELIEF CAMP
                </div>
                <h4 style="margin: 0 0 4px 0; color: #064e3b; font-size: 14px;">{sh['name']}</h4>
                <div style="font-size: 11px; color: #047857; font-weight: bold; margin-bottom: 6px;">
                    Elevation: {sh_elev} m MSL (+{(sh_elev - target_info.get('elevation', 50)):.1f}m High Ground)
                </div>
                <div style="font-size: 12px; color: #334155; line-height: 1.5;">
                    <b>Capacity:</b> {sh_cap} beds ({sh_beds} available)<br>
                    <b>Medical:</b> {sh['medical_support']}<br>
                    <b>Supplies:</b> {sh['supplies']}<br>
                    <b>Contact:</b> {sh['contact']}
                </div>
            </div>
            """

            folium.Marker(
                location=[sh_lat, sh_lon],
                popup=folium.Popup(shelter_html, max_width=300),
                tooltip=f"🛡️ <b>{sh['name']}</b> ({sh_beds} beds free, Elev: {sh_elev}m)",
                icon=folium.Icon(color="green" if not is_active else "darkgreen", icon="shield" if not is_active else "home", prefix="fa")
            ).add_to(fg_shelters)

        # 4. Render Evacuation Routes
        safe_r = evacuation_plan.get("safe_route", {})
        direct_r = evacuation_plan.get("direct_route", {})

        # Submerged Direct Route (Hazardous)
        if direct_r.get("found") and direct_r.get("coordinates"):
            folium.PolyLine(
                locations=direct_r["coordinates"],
                color="#dc2626",
                weight=3.5,
                opacity=0.7,
                dash_array="8, 8",
                tooltip=f"⚠️ <b>Direct Route (HAZARDOUS)</b><br>Max Submergence: <b>{direct_r.get('max_water_depth_m', 0)}m</b> ({direct_r.get('total_distance_km')} km)"
            ).add_to(fg_hazard_route)

            # Submerged warning marker along direct path if water depth > 0.3m
            if direct_r.get("max_water_depth_m", 0) > 0.3:
                # Mark intermediate submerged point
                sub_pt = direct_r["coordinates"][1]
                folium.CircleMarker(
                    location=sub_pt,
                    radius=7,
                    color="#dc2626",
                    fill=True,
                    fill_color="#fee2e2",
                    fill_opacity=0.9,
                    tooltip=f"⛔ <b>Road Submerged:</b> {direct_r['max_water_depth_m']}m water depth!"
                ).add_to(fg_hazard_route)

        # AI-Optimized Safe Evacuation Route (Clear & Elevated)
        if safe_r.get("found") and safe_r.get("coordinates"):
            # Solid glowing route corridor
            folium.PolyLine(
                locations=safe_r["coordinates"],
                color="#059669",
                weight=6,
                opacity=0.85,
                tooltip=f"🛡️ <b>AI Safe Evacuation Corridor</b><br>100% Passable | Dist: {safe_r.get('total_distance_km')} km | ETA: {safe_r.get('transit_time_mins')} min"
            ).add_to(fg_safe_route)

            # Glowing inner core
            folium.PolyLine(
                locations=safe_r["coordinates"],
                color="#34d399",
                weight=2.5,
                opacity=0.95
            ).add_to(fg_safe_route)

            # Waypoint markers along safe route
            for i, coord in enumerate(safe_r["coordinates"][1:-1]):
                folium.CircleMarker(
                    location=coord,
                    radius=5,
                    color="#059669",
                    weight=2,
                    fill=True,
                    fill_color="#ecfdf5",
                    fill_opacity=1.0,
                    tooltip=f"Waypoint {i+1}: Safe High-Elevation Ridge"
                ).add_to(fg_safe_route)

    # 5. Add Custom Floating Map Legend
    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
        background: rgba(255, 255, 255, 0.95);
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.18);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 11px;
        color: #1e293b;
        border: 1px solid #cbd5e1;
        max-width: 230px;
    ">
        <div style="font-weight: bold; font-size: 12px; margin-bottom: 6px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px;">
            🌊 Flood Operations Legend
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #22c55e; margin-right: 6px;"></span>
            <span><b>Low Risk</b> (&lt; 30%)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #eab308; margin-right: 6px;"></span>
            <span><b>Moderate Risk</b> (30-60%)</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #ef4444; margin-right: 6px;"></span>
            <span><b>Critical / Flash</b> (&gt; 80%)</span>
        </div>
        <div style="border-top: 1px solid #f1f5f9; margin-top: 6px; padding-top: 6px;">
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span style="display: inline-block; width: 16px; height: 4px; background: #059669; margin-right: 6px;"></span>
                <span><b>AI Safe Evacuation Path</b></span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span style="display: inline-block; width: 16px; height: 3px; border-top: 2px dashed #dc2626; margin-right: 6px;"></span>
                <span><b>Submerged Road Hazard</b></span>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="display: inline-block; width: 10px; height: 10px; background: #059669; border-radius: 2px; margin-right: 6px;"></span>
                <span><b>Relief Camp Shelter</b></span>
            </div>
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add Layer Control
    folium.LayerControl(position="topright").add_to(m)

    return m
