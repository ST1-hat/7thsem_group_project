"""
evacuation_engine.py
AI-Powered Safe Evacuation Routing and Relief Shelter Allocation Engine.
Utilizes Graph Theory (Dijkstra / A* Search) with dynamic hydrological impedance
to compute optimal, high-elevation, non-submerged evacuation corridors away
from inundation danger zones toward designated emergency shelters.
"""

import math
import heapq
from typing import Dict, List, Tuple, Any

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two coordinates in kilometers."""
    r = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c

def generate_relief_shelters(
    origin_lat: float,
    origin_lon: float,
    city_name: str,
    base_elevation: float
) -> List[Dict[str, Any]]:
    """
    Generates designated emergency relief shelters positioned on higher
    topographical ground surrounding the target flood zone.
    """
    shelter_templates = [
        {
            "id": "shelter_1",
            "name": f"{city_name} District Indoor Stadium & Sports Complex",
            "type": "Primary Civic Shelter",
            "bearing_deg": 45,   # North-East high ground
            "dist_km": 3.4,
            "elevation_boost": 14.5,
            "capacity": 2500,
            "occupancy": 320,
            "medical_support": "Full Grade-A Medical ICU & Trauma Unit",
            "supplies": "Drinking Water, 72h NDRF Rations, Solar Genset",
            "contact": "DDMA Incident Commander: +91-98765-43210"
        },
        {
            "id": "shelter_2",
            "name": f"{city_name} Central University High-Ground Campus",
            "type": "Academic Relief Camp",
            "bearing_deg": 310,  # North-West Ridge
            "dist_km": 4.8,
            "elevation_boost": 18.0,
            "capacity": 3800,
            "occupancy": 850,
            "medical_support": "Paramedic Staff & Emergency First-Aid",
            "supplies": "Mass Kitchen, Clean Sanitation, Blanket Stock",
            "contact": "Campus Relief Officer: +91-94321-09876"
        },
        {
            "id": "shelter_3",
            "name": f"{city_name} Armed Police / Military Ridge Center",
            "type": "High-Capacity Fortified Shelter",
            "bearing_deg": 190,  # South Elevated Ridge
            "dist_km": 6.2,
            "elevation_boost": 24.0,
            "capacity": 5000,
            "occupancy": 120,
            "medical_support": "Army Field Hospital & Air-Evacuation Helipad",
            "supplies": "Amphibious Vehicles, Satellite Telecom, High-Capacity Genset",
            "contact": "NDRF Tactical Unit: +91-98111-22334"
        },
        {
            "id": "shelter_4",
            "name": f"{city_name} North Town Community Hall",
            "type": "Secondary Local Shelter",
            "bearing_deg": 120,  # South-East
            "dist_km": 2.6,
            "elevation_boost": 7.5,
            "capacity": 1200,
            "occupancy": 640,
            "medical_support": "Basic Medical Dispensary",
            "supplies": "Dry Food Packets, Emergency Lanterns",
            "contact": "Ward Disaster Volunteer: +91-97000-11223"
        }
    ]

    shelters = []
    for s in shelter_templates:
        rad = math.radians(s["bearing_deg"])
        # 1 deg lat ~= 111 km, 1 deg lon ~= 111 km * cos(lat)
        d_lat = (s["dist_km"] * math.cos(rad)) / 111.0
        d_lon = (s["dist_km"] * math.sin(rad)) / (111.0 * max(0.2, math.cos(math.radians(origin_lat))))
        
        sh_lat = round(origin_lat + d_lat, 5)
        sh_lon = round(origin_lon + d_lon, 5)
        sh_elev = round(base_elevation + s["elevation_boost"], 1)

        shelters.append({
            "id": s["id"],
            "name": s["name"],
            "type": s["type"],
            "latitude": sh_lat,
            "longitude": sh_lon,
            "distance_km": round(s["dist_km"], 2),
            "elevation_m": sh_elev,
            "capacity": s["capacity"],
            "occupancy": s["occupancy"],
            "remaining_beds": s["capacity"] - s["occupancy"],
            "medical_support": s["medical_support"],
            "supplies": s["supplies"],
            "contact": s["contact"]
        })

    return shelters

def build_evacuation_graph(
    origin_lat: float,
    origin_lon: float,
    shelter: Dict[str, Any],
    flood_risk_score: float,
    base_elevation: float
) -> Dict[str, Any]:
    """
    Constructs a topological waypoint network between the flooded origin and the designated shelter.
    Models both:
      1. Low-lying direct riverbank roads (vulnerable to flash waterlogging).
      2. High-ground ridge bypasses and elevated flyovers (safe corridors).
    """
    sh_lat = shelter["latitude"]
    sh_lon = shelter["longitude"]
    sh_elev = shelter["elevation_m"]

    # Midpoints & Waypoints
    mid_lat = (origin_lat + sh_lat) / 2.0
    mid_lon = (origin_lon + sh_lon) / 2.0

    # Low-lying path coordinates (swings toward river depression)
    delta_lat = sh_lat - origin_lat
    delta_lon = sh_lon - origin_lon

    # Perpendicular offsets
    perp_lat = -delta_lon * 0.4
    perp_lon = delta_lat * 0.4

    # Node Definitions
    nodes = {
        "START": {
            "name": "Flooded Ground Zero (Origin)",
            "lat": origin_lat,
            "lon": origin_lon,
            "elevation": base_elevation,
            "hazard": "High Inundation Exposure"
        },
        "WP_LOW_1": {
            "name": "Riverbank Embankment Road (Low Basin)",
            "lat": round(origin_lat + delta_lat * 0.35 + perp_lat, 5),
            "lon": round(origin_lon + delta_lon * 0.35 + perp_lon, 5),
            "elevation": round(base_elevation - 2.5, 1), # Depressed elevation
            "hazard": "Depressed Culvert / River Basin"
        },
        "WP_LOW_2": {
            "name": "Underpass Sluice Canal Crossway",
            "lat": round(origin_lat + delta_lat * 0.70 + perp_lat * 0.8, 5),
            "lon": round(origin_lon + delta_lon * 0.70 + perp_lon * 0.8, 5),
            "elevation": round(base_elevation - 1.0, 1),
            "hazard": "Low-Lying Drainage Basin"
        },
        "WP_HIGH_1": {
            "name": "South Ridge Arterial Expressway",
            "lat": round(origin_lat + delta_lat * 0.35 - perp_lat, 5),
            "lon": round(origin_lon + delta_lon * 0.35 - perp_lon, 5),
            "elevation": round(base_elevation + 8.5, 1), # Elevated ground
            "hazard": "Elevated Crest / Storm Drained"
        },
        "WP_HIGH_2": {
            "name": "Elevated Metro Corridor / Sector Flyover",
            "lat": round(origin_lat + delta_lat * 0.70 - perp_lat * 0.7, 5),
            "lon": round(origin_lon + delta_lon * 0.70 - perp_lon * 0.7, 5),
            "elevation": round(base_elevation + 12.0, 1),
            "hazard": "High Grade Flyover / Zero Inundation"
        },
        "SHELTER": {
            "name": shelter["name"],
            "lat": sh_lat,
            "lon": sh_lon,
            "elevation": sh_elev,
            "hazard": "Safe Emergency Shelter Zone"
        }
    }

    # Edges with distances and water depths
    # Water depth depends on risk score and elevation depression
    risk_factor = max(0.0, (flood_risk_score - 30.0) / 70.0)

    # Edge definition: (u, v, road_name, road_type, dist_factor)
    raw_edges = [
        # Direct / Low-lying route
        ("START", "WP_LOW_1", "Old Embankment Road", "Lowland Arterial", 1.0),
        ("WP_LOW_1", "WP_LOW_2", "Sluice Canal Link Road", "Underpass Highway", 1.05),
        ("WP_LOW_2", "SHELTER", "Riverside Shelter Approach", "Local Road", 0.95),

        # Elevated Safe Corridor route
        ("START", "WP_HIGH_1", "Civil Lines Elevated Connector", "High Ground Avenue", 1.15),
        ("WP_HIGH_1", "WP_HIGH_2", "Sector Ridge Flyover Expressway", "Grade-Separated Flyover", 1.20),
        ("WP_HIGH_2", "SHELTER", "Highland Terminal Access Blvd", "Arterial Boulevard", 1.05),

        # Cross connections
        ("WP_HIGH_1", "WP_LOW_2", "Connecting Down-Ramp", "Ramp Link", 1.3),
        ("WP_LOW_1", "WP_HIGH_2", "Emergency Escape Incline", "Incline Bypass", 1.4)
    ]

    adj: Dict[str, List[Dict[str, Any]]] = {n: [] for n in nodes}

    for u, v, road_name, road_type, d_factor in raw_edges:
        n_u, n_v = nodes[u], nodes[v]
        dist = haversine_distance(n_u["lat"], n_u["lon"], n_v["lat"], n_v["lon"]) * d_factor
        avg_elev = (n_u["elevation"] + n_v["elevation"]) / 2.0

        # Calculate realistic water depth on this road segment
        # If road average elevation is lower than base, floodwaters accumulate rapidly
        elev_deficit = max(0.0, (base_elevation + 2.0) - avg_elev)
        water_depth = 0.0
        if risk_factor > 0:
            if elev_deficit > 0:
                water_depth = round(risk_factor * (0.4 + elev_deficit * 0.35), 2)
            elif avg_elev < base_elevation + 6.0:
                water_depth = round(risk_factor * 0.15, 2)
            else:
                water_depth = 0.0  # Completely elevated

        if water_depth > 0.45:
            passability = "SUBMERGED / IMPASSABLE"
            hazard_level = "CRITICAL"
        elif water_depth > 0.15:
            passability = "WATERLOGGED / CAUTION"
            hazard_level = "WARNING"
        else:
            passability = "CLEAR & PASSABLE"
            hazard_level = "SAFE"

        edge_data_fwd = {
            "to": v,
            "road_name": road_name,
            "road_type": road_type,
            "distance_km": round(dist, 2),
            "water_depth_m": water_depth,
            "passability": passability,
            "hazard_level": hazard_level,
            "avg_elevation_m": round(avg_elev, 1)
        }
        edge_data_bwd = {
            "to": u,
            "road_name": road_name,
            "road_type": road_type,
            "distance_km": round(dist, 2),
            "water_depth_m": water_depth,
            "passability": passability,
            "hazard_level": hazard_level,
            "avg_elevation_m": round(avg_elev, 1)
        }
        adj[u].append(edge_data_fwd)
        adj[v].append(edge_data_bwd)

    return {"nodes": nodes, "adj": adj}

def solve_dijkstra_route(
    graph: Dict[str, Any],
    start_node: str,
    target_node: str,
    avoid_water: bool = True
) -> Dict[str, Any]:
    """
    Implements Dijkstra's Shortest Path Algorithm with dynamic hydrological impedance.
    - If avoid_water=False: Computes standard shortest distance (ignoring water logging).
    - If avoid_water=True: Strongly penalizes or blocks submerged/waterlogged road segments.
    """
    nodes = graph["nodes"]
    adj = graph["adj"]

    # Priority queue: (cost, current_node, path, edge_history)
    pq = [(0.0, start_node, [start_node], [])]
    visited = {}

    while pq:
        cost, current, path, edge_hist = heapq.heappop(pq)

        if current in visited and visited[current] <= cost:
            continue
        visited[current] = cost

        if current == target_node:
            # Build route summary
            total_dist = sum(e["distance_km"] for e in edge_hist)
            max_water = max((e["water_depth_m"] for e in edge_hist), default=0.0)
            avg_water = (sum(e["water_depth_m"] for e in edge_hist) / len(edge_hist)) if edge_hist else 0.0
            elev_gain = nodes[target_node]["elevation"] - nodes[start_node]["elevation"]

            # Coordinates list for Folium polyline
            coords = [[nodes[n]["lat"], nodes[n]["lon"]] for n in path]

            # Steps breakdown
            steps = []
            for i, e in enumerate(edge_hist):
                src_n = nodes[path[i]]
                dst_n = nodes[path[i+1]]
                steps.append({
                    "step_no": i + 1,
                    "instruction": f"Proceed along {e['road_name']} ({e['road_type']}) towards {dst_n['name']}",
                    "distance_km": e["distance_km"],
                    "water_depth_m": e["water_depth_m"],
                    "passability": e["passability"],
                    "hazard_level": e["hazard_level"],
                    "elevation_m": dst_n["elevation"]
                })

            # Estimated transit times
            # Normal vehicle ~ 35 km/h, foot ~ 4 km/h
            speed_kmh = 35.0 if max_water < 0.25 else (12.0 if max_water < 0.5 else 4.0)
            transit_time_mins = round((total_dist / speed_kmh) * 60.0 + (5.0 if max_water > 0.2 else 0.0), 1)

            is_safe = max_water < 0.3
            status_text = "🟢 SAFE CORRIDOR (CLEAR)" if is_safe else "🔴 HAZARDOUS / WATERLOGGED"

            return {
                "found": True,
                "path_nodes": path,
                "coordinates": coords,
                "total_distance_km": round(total_dist, 2),
                "transit_time_mins": transit_time_mins,
                "max_water_depth_m": max_water,
                "average_water_depth_m": round(avg_water, 2),
                "elevation_gain_m": round(elev_gain, 1),
                "is_safe": is_safe,
                "status_text": status_text,
                "steps": steps,
                "edge_history": edge_hist
            }

        for edge in adj[current]:
            nxt = edge["to"]
            dist = edge["distance_km"]
            water = edge["water_depth_m"]

            if avoid_water:
                # Heavy mathematical penalty for water depth & impassability
                if water >= 0.45:
                    penalty = 1000.0  # Impassable
                elif water > 0.15:
                    penalty = 50.0 * (water ** 2)
                else:
                    penalty = 0.0
                edge_cost = dist * (1.0 + penalty)
            else:
                # Raw distance metric
                edge_cost = dist

            heapq.heappush(pq, (cost + edge_cost, nxt, path + [nxt], edge_hist + [edge]))

    return {"found": False}

def compute_evacuation_plan(
    origin_lat: float,
    origin_lon: float,
    city_name: str,
    base_elevation: float,
    flood_risk_score: float,
    selected_shelter_id: str = None
) -> Dict[str, Any]:
    """
    Master function:
    1. Retrieves candidate emergency shelters.
    2. Identifies primary optimal shelter (or uses user-selected one).
    3. Builds spatial road network graph.
    4. Computes both:
       a) Direct Path (naive shortest distance, prone to submergence).
       b) AI Safe Evacuation Path (graph search avoiding inundated choke points).
    """
    shelters = generate_relief_shelters(origin_lat, origin_lon, city_name, base_elevation)

    # Pick shelter
    target_shelter = shelters[0]
    if selected_shelter_id:
        for s in shelters:
            if s["id"] == selected_shelter_id:
                target_shelter = s
                break

    # Build road network graph
    graph = build_evacuation_graph(origin_lat, origin_lon, target_shelter, flood_risk_score, base_elevation)

    # Compute naive direct route (ignoring water)
    direct_route = solve_dijkstra_route(graph, "START", "SHELTER", avoid_water=False)

    # Compute AI-optimized safe route (actively penalizing water)
    safe_route = solve_dijkstra_route(graph, "START", "SHELTER", avoid_water=True)

    # Calculate safety differential
    water_avoided = max(0.0, direct_route["max_water_depth_m"] - safe_route["max_water_depth_m"])

    return {
        "target_shelter": target_shelter,
        "candidate_shelters": shelters,
        "direct_route": direct_route,
        "safe_route": safe_route,
        "water_avoided_m": round(water_avoided, 2),
        "graph_nodes": graph["nodes"],
        "graph_edges": graph["adj"]
    }
