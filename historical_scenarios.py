"""
historical_scenarios.py
Curated historical disaster replay scenarios based on major Indian flood catastrophes.
Allows examiners and users to perform retrospective stress-testing and hour-by-hour
playback of peak hydrological deluges (e.g. Patna 2019, Kerala 2018, Delhi Yamuna 2023).
"""

from typing import Dict, List, Any

HISTORICAL_SCENARIOS = {
    "patna_2019": {
        "id": "patna_2019",
        "title": "Patna Urban Deluge (September 2019)",
        "tagline": "Unprecedented 340mm cloudburst with Ganga river backflow submerging Rajendra Nagar",
        "year": 2019,
        "location_name": "Patna",
        "full_name": "Patna, Bihar, India",
        "latitude": 25.5941,
        "longitude": 85.1376,
        "elevation_m": 53.0,
        "cwc_gauge_station": "Dighaghat / Gandhi Ghat (Ganges)",
        "danger_mark_m": 48.60,
        "hfl_record_m": 50.52,  # Highest Flood Level
        "summary": (
            "Between Sept 27 and Sept 30, 2019, intense late-monsoon rainfall pounded Patna. "
            "Simultaneous peak discharge in the Ganga and Punpun rivers led to backflow through "
            "urban drainage sluice gates, submerging low-lying residential sectors under 6-8 feet of water "
            "for nearly 5 days, requiring 14 NDRF battalions."
        ),
        "stages": [
            {
                "stage_idx": 0,
                "label": "T-24h: Pre-Monsoon Storm Inflow",
                "timestamp_str": "27 Sept 2019, 08:00 IST",
                "rainfall_24h": 48.0,
                "river_discharge": 1150.0,
                "water_level": 2.80,
                "temperature": 27.5,
                "humidity": 84,
                "surface_pressure": 1004.0,
                "cwc_status": "River Rising Steadily (Below Warning Mark)",
                "narrative": "Catchment soil saturated. Storm clouds massing over Gangetic plains. Municipal drains operating at 70% capacity.",
                "hourly_precipitation": [2.1, 3.4, 4.0, 5.2, 4.8, 6.0, 5.5, 7.2, 8.0, 6.5, 5.0, 4.2, 3.8, 3.5, 3.0, 2.8, 2.5, 2.0, 2.2, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5],
                "discharge_trend": [950, 1020, 1150, 1300, 1500, 1750, 1900]
            },
            {
                "stage_idx": 1,
                "label": "T-12h: Torrential Cloudburst Intensification",
                "timestamp_str": "27 Sept 2019, 20:00 IST",
                "rainfall_24h": 168.0,
                "river_discharge": 2350.0,
                "water_level": 4.60,
                "temperature": 25.0,
                "humidity": 94,
                "surface_pressure": 999.0,
                "cwc_status": "Approaching CWC Danger Level (48.60m MSL)",
                "narrative": "Intense torrential downpour exceeding 18 mm/hr. Water accumulates along Kankarbagh main drain. Underpasses submerged.",
                "hourly_precipitation": [6.5, 8.2, 11.0, 14.5, 17.0, 19.5, 21.0, 22.5, 20.0, 18.5, 16.0, 14.0, 12.5, 11.0, 10.5, 9.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0, 3.5, 3.0, 2.8, 2.5, 2.2, 2.0, 1.8, 1.5, 1.2, 1.0, 0.8],
                "discharge_trend": [1200, 1500, 1850, 2350, 2750, 3100, 3300]
            },
            {
                "stage_idx": 2,
                "label": "T-0h: Peak Inundation & Sluice Backflow Failure",
                "timestamp_str": "28 Sept 2019, 04:00 IST",
                "rainfall_24h": 342.5,
                "river_discharge": 3950.0,
                "water_level": 6.75,
                "temperature": 24.0,
                "humidity": 98,
                "surface_pressure": 994.0,
                "cwc_status": "HISTORIC DANGER MARK BREACH (50.52m MSL)",
                "narrative": "CRITICAL EMERGENCY: Ganga river exceeds HFL. Backflow inundates Rajendra Nagar, Boring Road, and Civil Lines. Power substations shut down.",
                "hourly_precipitation": [18.0, 24.5, 32.0, 38.5, 41.0, 36.0, 29.5, 24.0, 19.0, 15.5, 12.0, 10.5, 8.5, 7.0, 6.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.8, 2.5, 2.2, 2.0, 1.8, 1.5, 1.2, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2],
                "discharge_trend": [1800, 2400, 3100, 3950, 4200, 4100, 3800]
            },
            {
                "stage_idx": 3,
                "label": "T+24h: Receding Runoff & Active Evacuation",
                "timestamp_str": "29 Sept 2019, 12:00 IST",
                "rainfall_24h": 38.0,
                "river_discharge": 2850.0,
                "water_level": 4.90,
                "temperature": 26.5,
                "humidity": 88,
                "surface_pressure": 1002.0,
                "cwc_status": "Water Receding Slowly; Low-lying Basins Waterlogged",
                "narrative": "Precipitation recedes, but high water stage in main river impedes gravity drainage. Large-scale rescue operations underway with inflatable motorboats.",
                "hourly_precipitation": [3.5, 3.0, 2.8, 2.2, 2.0, 1.8, 1.5, 1.2, 1.0, 0.8, 0.6, 0.5, 0.5, 0.4, 0.3, 0.3, 0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "discharge_trend": [3950, 3600, 3200, 2850, 2500, 2200, 1950]
            }
        ]
    },

    "kerala_2018": {
        "id": "kerala_2018",
        "title": "Kerala Mega Floods (August 2018)",
        "tagline": "Simultaneous opening of 35 dams releasing massive floodwaters into Periyar Basin",
        "year": 2018,
        "location_name": "Kochi",
        "full_name": "Kochi, Ernakulam, Kerala, India",
        "latitude": 9.9312,
        "longitude": 76.2673,
        "elevation_m": 8.0,
        "cwc_gauge_station": "Neeleswaram / Kalady (Periyar River)",
        "danger_mark_m": 7.50,
        "hfl_record_m": 10.45,
        "summary": (
            "During August 2018, Kerala experienced 164% above-normal monsoon rainfall. "
            "To prevent structural dam overtopping, 35 major reservoirs (including Idukki and Mullaperiyar) "
            "opened their spillways simultaneously. The Periyar and Chalakudy rivers surged violently, "
            "submerging towns like Aluva, Paravur, and halting operations at Cochin International Airport."
        ),
        "stages": [
            {
                "stage_idx": 0,
                "label": "T-48h: Reservoir Capacity Warning",
                "timestamp_str": "14 Aug 2018, 06:00 IST",
                "rainfall_24h": 72.0,
                "river_discharge": 1350.0,
                "water_level": 3.40,
                "temperature": 26.0,
                "humidity": 89,
                "surface_pressure": 1003.0,
                "cwc_status": "Dam Inflow at 95% Full Reservoir Level (FRL)",
                "narrative": "Continuous Western Ghats catchment rains. Hydroelectric reservoirs nearing full storage. Blue alert issued for downstream riverine villages.",
                "hourly_precipitation": [3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.2, 6.5, 6.0, 5.5, 5.0, 4.8, 4.5, 4.2, 4.0, 3.8, 3.5, 3.2, 3.0, 2.8, 2.5, 2.5, 2.8, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0],
                "discharge_trend": [800, 950, 1150, 1350, 1600, 1900, 2200]
            },
            {
                "stage_idx": 1,
                "label": "T-24h: Red Alert & Multi-Dam Spillway Release",
                "timestamp_str": "15 Aug 2018, 14:00 IST",
                "rainfall_24h": 220.0,
                "river_discharge": 2900.0,
                "water_level": 6.80,
                "temperature": 24.5,
                "humidity": 96,
                "surface_pressure": 997.0,
                "cwc_status": "Dam Spillways Fully Opened; Periyar Exceeds Danger Mark",
                "narrative": "All 5 shutters of Cheruthoni dam opened. Over 1,500 m³/s released into Periyar. Aluva Mahadeva temple completely underwater.",
                "hourly_precipitation": [9.0, 11.5, 14.0, 16.5, 19.0, 21.5, 24.0, 22.0, 19.5, 17.0, 15.0, 13.5, 12.0, 11.0, 10.0, 9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0, 3.5, 3.2, 3.0, 2.8, 2.5, 2.2, 2.0, 1.8, 1.5, 1.2],
                "discharge_trend": [1400, 1800, 2300, 2900, 3400, 3800, 4100]
            },
            {
                "stage_idx": 2,
                "label": "T-0h: Historic Basin Deluge (Peak Submergence)",
                "timestamp_str": "16 Aug 2018, 02:00 IST",
                "rainfall_24h": 395.0,
                "river_discharge": 4450.0,
                "water_level": 9.80,
                "temperature": 23.5,
                "humidity": 99,
                "surface_pressure": 992.0,
                "cwc_status": "ALL-TIME RECORD INUNDATION (10.45m MSL)",
                "narrative": "CATASTROPHIC FLOOD: Kochi International Airport runway flooded. Entire ground floors submerged across Ernakulam coastal belt. Massive Navy & Fishermen boat rescue armada mobilized.",
                "hourly_precipitation": [22.0, 28.5, 35.0, 42.0, 45.0, 39.0, 33.5, 28.0, 22.5, 18.0, 14.5, 12.0, 10.5, 9.0, 8.0, 7.0, 6.0, 5.5, 5.0, 4.5, 4.0, 3.5, 3.0, 2.8, 2.5, 2.2, 2.0, 1.8, 1.5, 1.2, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5],
                "discharge_trend": [2500, 3200, 3900, 4450, 4600, 4300, 3900]
            },
            {
                "stage_idx": 3,
                "label": "T+24h: High Flood Standstill & Emergency Triage",
                "timestamp_str": "17 Aug 2018, 18:00 IST",
                "rainfall_24h": 58.0,
                "river_discharge": 3100.0,
                "water_level": 7.20,
                "temperature": 26.0,
                "humidity": 90,
                "surface_pressure": 999.0,
                "cwc_status": "Spillway Discharge Reduced; River Receding at 0.15 m/hr",
                "narrative": "Rain eases slightly. Over 1 million citizens sheltered in relief camps. Focus shifts to air-dropping food packets, medical triage, and power restoration.",
                "hourly_precipitation": [4.0, 3.5, 3.0, 2.8, 2.5, 2.2, 2.0, 1.8, 1.5, 1.2, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.4, 0.3, 0.3, 0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "discharge_trend": [4450, 4100, 3600, 3100, 2700, 2300, 2000]
            }
        ]
    },

    "delhi_2023": {
        "id": "delhi_2023",
        "title": "Delhi Yamuna Record River Breach (July 2023)",
        "tagline": "Yamuna stage smashes 45-year-old record reaching 208.66m inundating Ring Road and Red Fort",
        "year": 2023,
        "location_name": "New Delhi",
        "full_name": "New Delhi, Delhi, India",
        "latitude": 28.6692,
        "longitude": 77.2315,
        "elevation_m": 214.0,
        "cwc_gauge_station": "Old Railway Bridge (Yamuna)",
        "danger_mark_m": 205.33,
        "hfl_record_m": 208.66,
        "summary": (
            "In mid-July 2023, record cloudbursts across Himachal Pradesh and Haryana triggered massive releases "
            "from Hathnikund Barrage exceeding 359,000 cusecs. The Yamuna in Delhi shattered its 1978 record "
            "of 207.49m, rising to an unprecedented 208.66m, drowning the Ring Road, Monastery Market, "
            "ITO barrage, and breaching the perimeter of the historic Red Fort."
        ),
        "stages": [
            {
                "stage_idx": 0,
                "label": "T-36h: Hathnikund Surge Discharge Inflow",
                "timestamp_str": "11 July 2023, 10:00 IST",
                "rainfall_24h": 45.0,
                "river_discharge": 1750.0,
                "water_level": 3.20,
                "temperature": 29.0,
                "humidity": 82,
                "surface_pressure": 998.0,
                "cwc_status": "Yamuna Crosses Warning Mark (204.50m MSL)",
                "narrative": "Upstream pulse from Haryana arrives at Wazirabad. Floodplain evacuation initiated for agricultural hamlets along Yamuna khaddar.",
                "hourly_precipitation": [3.0, 3.2, 3.5, 4.0, 4.2, 4.5, 4.0, 3.8, 3.5, 3.2, 3.0, 2.8, 2.5, 2.2, 2.0, 1.8, 1.5, 1.2, 1.0, 1.0, 1.2, 1.5, 1.8, 2.0, 2.2, 2.5, 2.8, 3.0, 3.2, 3.5, 3.8, 4.0, 4.2, 4.5, 4.8, 5.0],
                "discharge_trend": [1100, 1350, 1550, 1750, 2100, 2500, 2900]
            },
            {
                "stage_idx": 1,
                "label": "T-18h: Breaching the 1978 Historic Record",
                "timestamp_str": "12 July 2023, 18:00 IST",
                "rainfall_24h": 92.0,
                "river_discharge": 2950.0,
                "water_level": 5.40,
                "temperature": 27.5,
                "humidity": 91,
                "surface_pressure": 994.0,
                "cwc_status": "Yamuna Crosses 1978 Record (207.49m MSL)",
                "narrative": "Water gushes over Kashmere Gate ISBT and Monastery Market. Traffic suspended across Old Railway Bridge. Water treatment plants flooded.",
                "hourly_precipitation": [5.5, 6.8, 8.2, 10.5, 12.0, 14.2, 13.5, 12.0, 10.5, 9.0, 8.0, 7.2, 6.5, 5.8, 5.2, 4.5, 4.0, 3.5, 3.0, 2.8, 2.5, 2.2, 2.0, 1.8, 1.5, 1.2, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1],
                "discharge_trend": [1600, 2050, 2500, 2950, 3400, 3800, 4100]
            },
            {
                "stage_idx": 2,
                "label": "T-0h: Historic All-Time Crest (208.66m MSL)",
                "timestamp_str": "13 July 2023, 17:00 IST",
                "rainfall_24h": 145.0,
                "river_discharge": 4150.0,
                "water_level": 7.35,
                "temperature": 26.0,
                "humidity": 96,
                "surface_pressure": 991.0,
                "cwc_status": "ALL-TIME RECORD PEAK: 208.66m MSL",
                "narrative": "CRITICAL URBAN CRISIS: Water reaches Supreme Court premises and Red Fort outer moat. Silt jams ITO barrage gates. Indian Army engineering columns called in.",
                "hourly_precipitation": [9.0, 11.5, 15.0, 18.5, 22.0, 19.5, 16.0, 13.5, 11.0, 9.5, 8.0, 7.0, 6.0, 5.2, 4.5, 4.0, 3.5, 3.0, 2.8, 2.5, 2.2, 2.0, 1.8, 1.5, 1.2, 1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.2, 0.2, 0.1, 0.1, 0.0],
                "discharge_trend": [2800, 3400, 3900, 4150, 4200, 3900, 3500]
            },
            {
                "stage_idx": 3,
                "label": "T+24h: Siphon Dewatering & Breach Sealing",
                "timestamp_str": "14 July 2023, 20:00 IST",
                "rainfall_24h": 12.0,
                "river_discharge": 2600.0,
                "water_level": 5.10,
                "temperature": 29.5,
                "humidity": 85,
                "surface_pressure": 997.0,
                "cwc_status": "Water Level Receding to 207.80m MSL",
                "narrative": "Rain stops. Indian Army and Navy divers successfully breach jammed gates at ITO barrage. Massive dewatering pumps clear flooded arterial roads.",
                "hourly_precipitation": [1.2, 1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.2, 0.2, 0.1, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "discharge_trend": [4150, 3800, 3200, 2600, 2200, 1900, 1650]
            }
        ]
    }
}

def get_available_scenarios() -> List[Dict[str, Any]]:
    """Returns metadata summary of all historical disaster scenarios."""
    return [
        {
            "id": s["id"],
            "title": s["title"],
            "tagline": s["tagline"],
            "year": s["year"],
            "location_name": s["location_name"],
            "cwc_gauge_station": s["cwc_gauge_station"],
            "hfl_record_m": s["hfl_record_m"],
            "stage_count": len(s["stages"])
        }
        for s in HISTORICAL_SCENARIOS.values()
    ]

def get_scenario(scenario_id: str) -> Dict[str, Any]:
    """Retrieves full historical scenario data by ID."""
    return HISTORICAL_SCENARIOS.get(scenario_id, HISTORICAL_SCENARIOS["patna_2019"])

def get_stage_telemetry(scenario_id: str, stage_idx: int) -> Dict[str, Any]:
    """
    Transforms historical stage metrics into standard telemetry format
    compatible with api_services.fetch_realtime_telemetry() and flood_engine.
    """
    scen = get_scenario(scenario_id)
    stages = scen["stages"]
    stage = stages[min(stage_idx, len(stages) - 1)]

    # Generate synthetic 36h date labels matching stage timestamp
    hourly_times = [f"+{h}h" for h in range(len(stage["hourly_precipitation"]))]
    discharge_dates = [f"Day {d+1}" for d in range(len(stage["discharge_trend"]))]

    return {
        "scenario_meta": scen,
        "stage_meta": stage,
        "rainfall_24h": stage["rainfall_24h"],
        "temperature": stage["temperature"],
        "humidity": stage["humidity"],
        "surface_pressure": stage["surface_pressure"],
        "river_discharge": stage["river_discharge"],
        "water_level": stage["water_level"],
        "elevation": scen["elevation_m"],
        "hourly_times": hourly_times,
        "hourly_precipitation": stage["hourly_precipitation"],
        "discharge_forecast_dates": discharge_dates,
        "discharge_forecast_values": stage["discharge_trend"],
        "data_source": f"Historical Archive: {scen['title']} - {stage['label']}"
    }
