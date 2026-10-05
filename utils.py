"""
utils.py
UI components, Plotly chart builders, emergency advisories, and export utilities.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any

# Emergency guidelines mapped to risk level
EMERGENCY_ADVISORIES = {
    "LOW RISK": {
        "title": "🟢 Normal Hydrological Conditions",
        "guidelines": [
            "Catchment basins and drainage channels are operating at normal capacity.",
            "Routine maintenance and culvert inspections recommended.",
            "Stay tuned to local weather forecasts for sudden cloudburst developments.",
            "No evacuation or flood barriers necessary at this stage."
        ],
        "ndrf_status": "Standby / Routine Readiness",
        "helplines": "Local Municipal Control: 100 / 112"
    },
    "MODERATE RISK": {
        "title": "🟡 Flood Watch & Advisory Active",
        "guidelines": [
            "Prepare emergency go-bags with essentials (first-aid, clean water, dry food, flashlights, documents).",
            "Clear municipal stormwater drains and neighborhood gutters of blockages.",
            "Move high-value assets and electrical equipment to upper floors.",
            "Avoid parking vehicles in low-lying underground basements or near riverbanks.",
            "Monitor water levels in local culverts and canals closely."
        ],
        "ndrf_status": "Stage-1 Alert: Regional SDRF Quick Response Teams Notified",
        "helplines": "State Disaster Management Helpline: 1070 | Ambulance: 108"
    },
    "HIGH RISK": {
        "title": "🟠 Severe Flood Warning - Action Required",
        "guidelines": [
            "Deploy sandbags along entry gates, doorways, and vulnerable perimeters.",
            "Turn off main electrical breakers and LPG gas cylinders before floodwaters enter premises.",
            "Identify nearest designated high-elevation relief shelters and evacuation routes.",
            "Do NOT attempt to drive or walk through moving floodwater ('Turn Around, Don't Drown').",
            "Elderly citizens, children, and livestock should be moved to higher elevation immediately."
        ],
        "ndrf_status": "Stage-2 Alert: NDRF/SDRF Inflatable Boats & Rescue Units Pre-deployed",
        "helplines": "NDRF Emergency HQ: 1078 / 011-24363260 | Disaster Control: 1077"
    },
    "CRITICAL RISK": {
        "title": "🔴 Catastrophic / Flash Flood Emergency",
        "guidelines": [
            "IMMEDIATE EVACUATION: Move to top floors, concrete building roofs, or designated high-ground shelters.",
            "Signal emergency rescue teams using bright cloth, whistles, or phone flashlights.",
            "Avoid electrical poles, fallen transformers, and submerged wires (high electrocution hazard).",
            "Drink only bottled or boiled water to prevent waterborne epidemic outbreaks (cholera/leptospirosis).",
            "Follow official directives broadcasted by District Disaster Management Authorities (DDMA)."
        ],
        "ndrf_status": "Red Alert: Full National Disaster Response Force (NDRF) Tactical Evacuation Active",
        "helplines": "National Disaster Control (Toll-Free): 1078 | Emergency SOS: 112"
    }
}

def create_risk_gauge(score: float, category: str, color_hex: str) -> go.Figure:
    """Builds a gauge chart for the flood risk probability."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>Flood Risk Probability</b><br><span style='font-size:14px;color:{color_hex}'>{category}</span>", 'font': {'size': 18, 'color': '#0f172a'}},
        number={'suffix': "%", 'font': {'size': 36, 'color': color_hex, 'weight': 'bold'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8", 'tickvals': [0, 25, 50, 75, 100]},
            'bar': {'color': color_hex, 'thickness': 0.3},
            'bgcolor': "#f8fafc",
            'borderwidth': 1,
            'bordercolor': "#cbd5e1",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(34, 197, 94, 0.2)'},
                {'range': [30, 60], 'color': 'rgba(234, 179, 8, 0.2)'},
                {'range': [60, 80], 'color': 'rgba(249, 115, 22, 0.2)'},
                {'range': [80, 100], 'color': 'rgba(239, 68, 68, 0.2)'},
            ],
            'threshold': {
                'line': {'color': "#dc2626", 'width': 3},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    fig.update_layout(
        height=260,
        margin=dict(l=25, r=25, t=50, b=25),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Segoe UI, sans-serif'}
    )
    return fig

def create_precipitation_forecast_chart(times: List[str], precipitation: List[float]) -> go.Figure:
    """Builds an hourly precipitation forecast chart with flood warning thresholds."""
    if not times or not precipitation:
        times = [f"+{i}h" for i in range(24)]
        precipitation = [0.0] * 24

    # Format timestamps for display
    display_times = []
    for t in times[:36]:
        if 'T' in t:
            display_times.append(t.split('T')[1][:5] + ' (' + t.split('T')[0][-5:] + ')')
        else:
            display_times.append(str(t))

    df_rain = pd.DataFrame({
        'Time': display_times,
        'Rainfall_mm': precipitation[:len(display_times)]
    })

    fig = go.Figure()

    # Rainfall bars
    fig.add_trace(go.Bar(
        x=df_rain['Time'],
        y=df_rain['Rainfall_mm'],
        name='Rainfall (mm/h)',
        marker=dict(
            color=df_rain['Rainfall_mm'],
            colorscale='Blues',
            cmin=0,
            cmax=25,
            line=dict(color='#2563eb', width=1)
        )
    ))

    # Alert Threshold Lines
    fig.add_hline(
        y=15.0,
        line_dash="dot",
        line_color="#eab308",
        annotation_text="Moderate Rain Threshold (15 mm/h)",
        annotation_position="top right",
        annotation_font=dict(size=10, color="#ca8a04")
    )
    fig.add_hline(
        y=35.0,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="Heavy Cloudburst Risk (>35 mm/h)",
        annotation_position="top right",
        annotation_font=dict(size=10, color="#dc2626")
    )

    fig.update_layout(
        title="<b>Hourly Precipitation Forecast (Next 36 Hours)</b>",
        xaxis_title="Timeline",
        yaxis_title="Precipitation (mm/h)",
        xaxis_tickangle=-45,
        height=320,
        margin=dict(l=40, r=30, t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(241, 245, 249, 0.5)',
        font=dict(family="Segoe UI, sans-serif", size=11)
    )
    return fig

def create_river_discharge_chart(dates: List[str], discharges: List[float]) -> go.Figure:
    """Builds a 7-day river discharge hydrograph."""
    if not dates or not discharges:
        dates = [f"Day {i+1}" for i in range(7)]
        discharges = [120.0, 135.0, 190.0, 240.0, 210.0, 175.0, 150.0]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=discharges,
        mode='lines+markers',
        name='River Discharge (m³/s)',
        line=dict(color='#0284c7', width=3),
        fill='tozeroy',
        fillcolor='rgba(2, 132, 199, 0.15)',
        marker=dict(size=6, color='#0369a1')
    ))

    # Warning Stage reference
    max_d = max(discharges) if discharges else 500
    warning_stage = max(350.0, max_d * 0.8)
    fig.add_hline(
        y=warning_stage,
        line_dash="dash",
        line_color="#f97316",
        annotation_text=f"River Danger Mark ({warning_stage:.0f} m³/s)",
        annotation_position="top left",
        annotation_font=dict(size=10, color="#ea580c")
    )

    fig.update_layout(
        title="<b>River Discharge Outlook (Discharge Hydrograph)</b>",
        xaxis_title="Date",
        yaxis_title="Discharge (m³/s)",
        height=320,
        margin=dict(l=40, r=30, t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(241, 245, 249, 0.5)',
        font=dict(family="Segoe UI, sans-serif", size=11)
    )
    return fig

def create_factor_radar_chart(contributions: Dict[str, float]) -> go.Figure:
    """Creates a radar chart showing the contribution of each hydrologic factor to flood risk."""
    categories = list(contributions.keys())
    values = list(contributions.values())
    # Close the radar loop
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.25)',
        line=dict(color='#2563eb', width=2),
        marker=dict(size=6, color='#1d4ed8'),
        name='Factor Influence'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=9, color="#64748b")
            )
        ),
        title="<b>Explainable AI: Key Hydrologic Drivers Breakdown</b>",
        height=340,
        margin=dict(l=40, r=40, t=50, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Segoe UI, sans-serif", size=11)
    )
    return fig

def create_nearby_comparison_chart(nearby_stations: List[Dict[str, Any]]) -> go.Figure:
    """Builds a horizontal bar chart comparing risk scores across nearby stations."""
    names = [s["name"].split(" - ")[-1] for s in nearby_stations]
    risks = [s.get("risk", {}).get("risk_score", 0) for s in nearby_stations]
    colors = [s.get("risk", {}).get("color_hex", "#3b82f6") for s in nearby_stations]

    fig = go.Figure(go.Bar(
        x=risks,
        y=names,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{r}%" for r in risks],
        textposition='outside'
    ))

    fig.update_layout(
        title="<b>Regional Risk Comparison (Surrounding Stations)</b>",
        xaxis_title="Flood Risk Score (%)",
        xaxis=dict(range=[0, 105]),
        height=300,
        margin=dict(l=30, r=30, t=45, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(241, 245, 249, 0.5)',
        font=dict(family="Segoe UI, sans-serif", size=11)
    )
    return fig
