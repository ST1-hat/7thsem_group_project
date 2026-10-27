import React, { useState } from 'react';
import { 
  AlertTriangle, 
  Droplets, 
  Waves, 
  Ruler, 
  Mountain, 
  Clock, 
  Hospital, 
  Sliders, 
  Download, 
  TrendingUp,
  Cpu,
  Compass,
  ArrowRight,
  Shield,
  CloudRain,
  Activity,
  Target,
  Radio,
  FileSpreadsheet,
  FileCode,
  PhoneCall
} from 'lucide-react';
import { ShieldWaves } from '../components/Icons';
import { 
  PrecipitationForecastChart, 
  RiverDischargeChart, 
  FactorRadarChart, 
  NearbyComparisonChart, 
  RiskGauge 
} from '../components/Charts';

export default function DashboardPage({
  analysisData,
  appMode,
  historicalScenarios = [],
  selectedScenarioId,
  scenarioStageIdx,
  simRain,
  setSimRain,
  simDischarge,
  setSimDischarge,
  onRunSimulation,
  onResetSimulation,
  onHistoricalPhaseChange,
  onNavigateToMap
}) {
  const [activeTab, setActiveTab] = useState('precipitation');
  const [showSandbox, setShowSandbox] = useState(false);

  if (!analysisData) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: '80px 20px' }}>
        <div style={{ display: 'inline-block', marginBottom: '14px' }}>
          <ShieldWaves size={48} color="#0f172a" waveColor="#ffffff" />
        </div>
        <h2>Initializing FloodSense AI Command Pipeline...</h2>
      </div>
    );
  }

  const { place_info, telemetry, risk_result, nearby_stations, evacuation_plan, advisory } = analysisData;
  const safeRoute = evacuation_plan?.safe_route || {};
  const targetShelter = evacuation_plan?.target_shelter || {};

  const currentScenario = historicalScenarios.find(s => s.id === selectedScenarioId) || historicalScenarios[0];
  const stages = currentScenario?.stages || [];

  const handleExportJson = () => {
    const report = {
      operating_mode: appMode,
      assessment_location: place_info?.full_name,
      coordinates: { latitude: place_info?.latitude, longitude: place_info?.longitude },
      timestamp_generated: new Date().toISOString(),
      predicted_risk_score: `${risk_result?.risk_score}%`,
      risk_category: risk_result?.category,
      alert_level: risk_result?.alert_level,
      hydrological_telemetry: risk_result?.inputs_used,
      ml_probability: `${risk_result?.ml_probability}%`,
      factor_contributions: risk_result?.contributions,
      evacuation_plan: {
        target_shelter: targetShelter?.name,
        free_beds: targetShelter?.remaining_beds,
        safe_corridor_distance_km: safeRoute?.total_distance_km,
        safe_corridor_eta_mins: safeRoute?.transit_time_mins,
        water_avoided_m: evacuation_plan?.water_avoided_m
      }
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `flood_report_${place_info?.name?.toLowerCase() || 'assessment'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportCsv = () => {
    const headers = [
      'Location', 'Mode', 'Latitude', 'Longitude', 'Rainfall_mm', 'River_Discharge_m3s',
      'Water_Level_m', 'Elevation_m', 'Risk_Score_Pct', 'Category', 'Alert_Level'
    ];
    const row = [
      `"${place_info?.name || ''}"`,
      appMode,
      place_info?.latitude || 0,
      place_info?.longitude || 0,
      risk_result?.inputs_used?.rainfall_mm || 0,
      risk_result?.inputs_used?.river_discharge_m3s || 0,
      risk_result?.inputs_used?.water_level_m || 0,
      risk_result?.inputs_used?.elevation_m || 0,
      risk_result?.risk_score || 0,
      `"${risk_result?.category || ''}"`,
      `"${risk_result?.alert_level || ''}"`
    ];
    const csvContent = `${headers.join(',')}\n${row.join(',')}`;
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `flood_telemetry_${place_info?.name?.toLowerCase() || 'assessment'}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="page-container">
      {/* ── Historical Retro Replay Control Strip ── */}
      {appMode === 'HISTORICAL' && currentScenario && (
        <div className="history-banner">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '14px' }}>
            <div>
              <div style={{ fontSize: '11px', letterSpacing: '1.2px', fontWeight: 800, textTransform: 'uppercase', color: '#bfdbfe', marginBottom: '4px' }}>
                Retrospective Stress-Testing • {currentScenario.title}
              </div>
              <div style={{ fontSize: '22px', fontWeight: 900 }}>
                Phase {scenarioStageIdx + 1}/{stages.length}: {stages[scenarioStageIdx]?.label}
              </div>
              <div style={{ fontSize: '13px', opacity: 0.95, marginTop: '4px' }}>
                Timestamp: <b>{stages[scenarioStageIdx]?.timestamp_str}</b> &nbsp;|&nbsp;
                CWC Gauge: <b>{currentScenario.cwc_gauge_station}</b> &nbsp;|&nbsp;
                Status: <b>{stages[scenarioStageIdx]?.cwc_status}</b>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <button 
                className="search-btn" 
                style={{ background: '#f59e0b', color: '#0f172a' }}
                onClick={() => onHistoricalPhaseChange(selectedScenarioId, 2)}
              >
                Jump to Peak Inundation
              </button>
              <button 
                className="search-btn" 
                style={{ background: 'rgba(255,255,255,0.2)' }}
                onClick={() => {
                  const nextIdx = (scenarioStageIdx + 1) % stages.length;
                  onHistoricalPhaseChange(selectedScenarioId, nextIdx);
                }}
              >
                Next Phase
              </button>
            </div>
          </div>

          <div style={{ fontSize: '12.5px', marginTop: '12px', background: 'rgba(0,0,0,0.22)', padding: '10px 16px', borderLeft: '4px solid #60a5fa', borderRadius: '8px' }}>
            <b>Ground Reality:</b> {stages[scenarioStageIdx]?.narrative}
          </div>

          <div style={{ marginTop: '16px', background: 'rgba(255,255,255,0.1)', padding: '12px 16px', borderTop: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 700, marginBottom: '6px' }}>
              <span>Timeline Replay Slider:</span>
              <span>{stages[scenarioStageIdx]?.label}</span>
            </div>
            <input
              type="range"
              min={0}
              max={stages.length - 1}
              step={1}
              value={scenarioStageIdx}
              onChange={(e) => onHistoricalPhaseChange(selectedScenarioId, parseInt(e.target.value, 10))}
              className="custom-range"
            />
          </div>
        </div>
      )}

      {/* ── Live Mode Simulation Sandbox ── */}
      {appMode === 'LIVE' && (
        <div className="simulation-box">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => setShowSandbox(!showSandbox)}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Sliders size={18} color="#0f172a" />
              <div>
                <b style={{ fontSize: '14.5px', color: '#0f172a' }}>What-If Hydrological Simulation Sandbox</b>
                <span style={{ fontSize: '12px', color: '#64748b', marginLeft: '10px' }}>Stress-test cloudburst precipitation & upstream dam release surges</span>
              </div>
            </div>
            <button className="mode-toggle-btn" style={{ padding: '4px 12px', fontSize: '12px' }}>
              {showSandbox ? 'Hide Sandbox' : 'Open Sandbox'}
            </button>
          </div>

          {showSandbox && (
            <div style={{ marginTop: '18px', paddingTop: '16px', borderTop: '1px solid #e2e8f0' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
                <div className="slider-group">
                  <div className="slider-header">
                    <span>Precipitation Inflow Surge:</span>
                    <b>+{simRain} mm / 24h</b>
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={250}
                    step={10}
                    value={simRain}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value);
                      setSimRain(val);
                      onRunSimulation(val, simDischarge);
                    }}
                    className="custom-range"
                  />
                </div>

                <div className="slider-group">
                  <div className="slider-header">
                    <span>Dam Discharge / Catchment Surge:</span>
                    <b>+{simDischarge} m³/s</b>
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={4000}
                    step={100}
                    value={simDischarge}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value);
                      setSimDischarge(val);
                      onRunSimulation(simRain, val);
                    }}
                    className="custom-range"
                  />
                </div>

                <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                  <button
                    className="mode-toggle-btn"
                    style={{ width: '100%', height: '42px', justifyContent: 'center' }}
                    onClick={onResetSimulation}
                  >
                    Reset to Live Telemetry
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Executive Hazard Alert Banner (HAZARD COLOR PRESERVED) ── */}
      <div 
        className="alert-banner" 
        style={{ background: `linear-gradient(135deg, ${risk_result?.color_hex || '#16a34a'} 0%, ${risk_result?.color_hex || '#16a34a'}e6 100%)` }}
      >
        <div>
          <div className="alert-tag">Hazard Classification Status</div>
          <div className="alert-title">
            {risk_result?.alert_level} — {risk_result?.category} ({risk_result?.risk_score}%)
          </div>
          <div className="alert-sub">
            Location: <b>{place_info?.full_name}</b> &nbsp;|&nbsp;
            Coordinates: {place_info?.latitude?.toFixed(4)}°N, {place_info?.longitude?.toFixed(4)}°E &nbsp;|&nbsp;
            Base Elevation: {risk_result?.inputs_used?.elevation_m} m MSL
          </div>
        </div>
        <div className="alert-right-badge">
          <div className="alert-right-label">Hydrologic Threshold</div>
          <div className="alert-right-val">{risk_result?.status_text}</div>
        </div>
      </div>

      {/* ── 6 KPI Metric Cards (Monochrome Icons with Hazard-Coded Statuses) ── */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: '#0f172a', color: '#ffffff' }}>
            <Droplets size={19} />
          </div>
          <div className="metric-label">24h Cumulative Rainfall</div>
          <div className="metric-val">
            {risk_result?.inputs_used?.rainfall_mm} <span className="metric-unit">mm</span>
          </div>
          <div className="metric-sub" style={{ color: risk_result?.inputs_used?.rainfall_mm > 64.5 ? '#dc2626' : '#64748b', fontWeight: risk_result?.inputs_used?.rainfall_mm > 64.5 ? 800 : 500 }}>
            {risk_result?.inputs_used?.rainfall_mm < 15.5 ? 'Normal Infiltration' : risk_result?.inputs_used?.rainfall_mm < 64.5 ? 'Moderate Runoff' : 'Heavy Deluge'}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: '#0f172a', color: '#ffffff' }}>
            <Waves size={19} />
          </div>
          <div className="metric-label">River Discharge Rate</div>
          <div className="metric-val">
            {risk_result?.inputs_used?.river_discharge_m3s} <span className="metric-unit">m³/s</span>
          </div>
          <div className="metric-sub">GloFAS River Basin Model</div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: '#0f172a', color: '#ffffff' }}>
            <Ruler size={19} />
          </div>
          <div className="metric-label">Runoff Stage Level</div>
          <div className="metric-val">
            {risk_result?.inputs_used?.water_level_m} <span className="metric-unit">m</span>
          </div>
          <div className="metric-sub">Surface Water Depth</div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: '#0f172a', color: '#ffffff' }}>
            <Mountain size={19} />
          </div>
          <div className="metric-label">Terrain Elevation</div>
          <div className="metric-val">
            {risk_result?.inputs_used?.elevation_m} <span className="metric-unit">m</span>
          </div>
          <div className="metric-sub">Mean Sea Level (MSL)</div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: '#0f172a', color: '#ffffff' }}>
            <Clock size={19} />
          </div>
          <div className="metric-label">Safe Corridor Transit</div>
          <div className="metric-val">
            {safeRoute?.transit_time_mins || 15} <span className="metric-unit">mins</span>
          </div>
          <div className="metric-sub">
            Status: <b style={{ color: safeRoute?.is_safe ? '#16a34a' : '#ea580c' }}>{safeRoute?.is_safe ? 'PASSABLE (CLEAR)' : 'CAUTION'}</b>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: '#0f172a', color: '#ffffff' }}>
            <Hospital size={19} />
          </div>
          <div className="metric-label">Shelter Capacity</div>
          <div className="metric-val">
            {targetShelter?.remaining_beds || 2000} <span className="metric-unit">beds</span>
          </div>
          <div className="metric-sub">Distance: <b>{targetShelter?.dist_km || 3.4} km</b></div>
        </div>
      </div>

      {/* ── AI Model Synthesis & Radial Gauge Row ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 4fr) minmax(0, 6fr)', gap: '20px', marginBottom: '24px' }}>
        <div className="white-card" style={{ margin: 0 }}>
          <div className="card-title">
            <Cpu size={18} color="#0f172a" />
            AI Machine Learning Synthesis
          </div>
          <RiskGauge
            score={risk_result?.risk_score || 0}
            category={risk_result?.category || 'LOW RISK'}
            color={risk_result?.color_hex || '#22c55e'}
          />
          <div style={{ fontSize: '12px', lineHeight: 1.8, borderTop: '1px solid #f1f5f9', paddingTop: '12px', color: '#475569' }}>
            <div>• <b>Ensemble ML Probability:</b> <span style={{ color: risk_result?.color_hex, fontWeight: 'bold' }}>{risk_result?.ml_probability}%</span></div>
            <div>• <b>Physical Hydrological Index:</b> {risk_result?.hydro_index}%</div>
            <div>• <b>Combined Vulnerability Score:</b> <span style={{ color: risk_result?.color_hex, fontWeight: 'bold' }}>{risk_result?.risk_score}%</span></div>
          </div>
        </div>

        {/* Quick Map Callout Card with Monochrome Waves & Shield */}
        <div className="white-card" style={{ margin: 0, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)' }}>
          <div>
            <div className="card-title" style={{ color: '#0f172a' }}>
              <Compass size={18} color="#0f172a" />
              Geospatial Command Map &amp; Evacuation Corridors
            </div>
            <p style={{ fontSize: '13px', color: '#475569', lineHeight: 1.7, marginBottom: '14px' }}>
              View full interactive Leaflet map with satellite imagery, physical topography, flood inundation heatmaps,
              and Dijkstra safe high-ground pathfinding.
            </p>
            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '10px 14px', fontSize: '12.5px', color: '#0f172a' }}>
              <span style={{ color: '#16a34a', fontWeight: 800 }}>Safe Ridge Corridor:</span> {safeRoute?.total_distance_km || 0} km (100% Passable) &nbsp;|&nbsp;
              <span style={{ color: '#dc2626', fontWeight: 800 }}>Submergence Avoided:</span> {evacuation_plan?.water_avoided_m || 0}m
            </div>
          </div>

          <div style={{ marginTop: '16px' }}>
            <button
              className="search-btn"
              style={{ width: '100%', justifyContent: 'center', height: '42px', fontSize: '14px', background: '#0f172a' }}
              onClick={onNavigateToMap}
            >
              <Compass size={16} />
              Open Interactive Geospatial Map
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* ── Forecast & Analytics Tabs ── */}
      <div className="section-header">
        <div className="section-icon" style={{ background: '#0f172a', color: '#ffffff' }}>
          <TrendingUp size={20} />
        </div>
        <div>
          <div className="section-title">Telemetry Forecasts &amp; Explainable AI Analytics</div>
          <div className="section-sub">36-hour rainfall forecast, 7-day GloFAS hydrographs, and multi-factor vulnerability radar</div>
        </div>
      </div>

      <div className="tabs-nav">
        <button
          className={`tab-btn ${activeTab === 'precipitation' ? 'active' : ''}`}
          onClick={() => setActiveTab('precipitation')}
        >
          <CloudRain size={15} />
          Precipitation Forecast (36h)
        </button>
        <button
          className={`tab-btn ${activeTab === 'hydrograph' ? 'active' : ''}`}
          onClick={() => setActiveTab('hydrograph')}
        >
          <Activity size={15} />
          River Discharge Hydrograph
        </button>
        <button
          className={`tab-btn ${activeTab === 'xai' ? 'active' : ''}`}
          onClick={() => setActiveTab('xai')}
        >
          <Target size={15} />
          Explainable AI (XAI)
        </button>
        <button
          className={`tab-btn ${activeTab === 'nearby' ? 'active' : ''}`}
          onClick={() => setActiveTab('nearby')}
        >
          <Radio size={15} />
          Surrounding Sensor Nodes
        </button>
      </div>

      {/* TAB 1: PRECIPITATION */}
      {activeTab === 'precipitation' && (
        <div className="white-card">
          <div className="card-title">
            <CloudRain size={17} color="#0f172a" />
            36-Hour Hourly Precipitation Curve (Open-Meteo NWP)
          </div>
          <PrecipitationForecastChart
            times={telemetry?.hourly_times}
            values={telemetry?.hourly_precipitation}
          />
        </div>
      )}

      {/* TAB 2: HYDROGRAPH */}
      {activeTab === 'hydrograph' && (
        <div className="white-card">
          <div className="card-title">
            <Activity size={17} color="#0f172a" />
            7-Day River Discharge Hydrograph (GloFAS Hydrology Nodes)
          </div>
          <RiverDischargeChart
            dates={telemetry?.discharge_forecast_dates}
            values={telemetry?.discharge_forecast_values}
          />
        </div>
      )}

      {/* TAB 3: XAI */}
      {activeTab === 'xai' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 5fr) minmax(0, 5fr)', gap: '20px' }}>
          <div className="white-card">
            <div className="card-title">
              <Target size={17} color="#0f172a" />
              Multi-Factor Vulnerability Radar
            </div>
            <FactorRadarChart contributions={risk_result?.contributions} />
          </div>

          <div className="white-card">
            <div className="card-title">
              <Cpu size={17} color="#0f172a" />
              Hydrological Feature Contribution Breakdown
            </div>
            <table className="styled-table" style={{ marginBottom: '16px' }}>
              <thead>
                <tr>
                  <th>Hydrologic / Physical Variable</th>
                  <th>Contribution Weight</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(risk_result?.contributions || {}).map(([key, val]) => (
                  <tr key={key}>
                    <td><b>{key}</b></td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <div style={{ flex: 1, background: '#f1f5f9', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: `${val}%`, height: '100%', background: val > 65 ? '#dc2626' : val > 40 ? '#ea580c' : '#16a34a' }} />
                        </div>
                        <span style={{ fontWeight: 800, width: '45px' }}>{val}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: SURROUNDING SENSORS */}
      {activeTab === 'nearby' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 6fr) minmax(0, 4fr)', gap: '20px' }}>
          <div className="white-card">
            <div className="card-title">
              <Radio size={17} color="#0f172a" />
              Peripheral Sensor Network Telemetry
            </div>
            <NearbyComparisonChart stations={nearby_stations} />
          </div>

          <div className="white-card">
            <div className="card-title">
              Regional Hydrology Stations
            </div>
            <table className="styled-table">
              <thead>
                <tr>
                  <th>Sensor Station</th>
                  <th>Distance</th>
                  <th>Risk Score</th>
                </tr>
              </thead>
              <tbody>
                {nearby_stations.map((st, i) => (
                  <tr key={i}>
                    <td><b>{st.name}</b></td>
                    <td>{st.distance_km || 20} km</td>
                    <td><b style={{ color: st.risk?.color_hex }}>{st.risk?.risk_score || 0}%</b></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Disaster Protocols Strip ── */}
      <div className="section-header">
        <div className="section-icon" style={{ background: '#0f172a', color: '#ffffff' }}>
          <AlertTriangle size={20} />
        </div>
        <div>
          <div className="section-title">Disaster Response Protocols &amp; Directives</div>
          <div className="section-sub">Standard Operating Procedures calibrated to current risk severity</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 7fr) minmax(0, 3fr)', gap: '20px', marginBottom: '28px' }}>
        <div className="white-card">
          <div className="card-title">
            <Shield size={17} color="#0f172a" />
            {advisory?.title || 'Operational Emergency Directives'}
          </div>
          <ul style={{ paddingLeft: '20px', fontSize: '13px', lineHeight: 2, color: '#334155' }}>
            {(advisory?.guidelines || []).map((g, i) => (
              <li key={i}>{g}</li>
            ))}
          </ul>
        </div>

        <div className="white-card">
          <div className="card-title">
            <PhoneCall size={17} color="#0f172a" />
            Emergency Contacts
          </div>
          <div style={{ fontSize: '13px', lineHeight: 2, color: '#334155' }}>
            <div><b>NDRF National Helpline:</b> <span style={{ color: '#0f172a', fontWeight: 800 }}>1078</span></div>
            <div><b>National Emergency SOS:</b> <span style={{ color: '#dc2626', fontWeight: 800 }}>112</span></div>
            <div><b>Disaster Control Room:</b> <span style={{ color: '#0f172a', fontWeight: 800 }}>1070</span></div>
            <div><b>Emergency Medical:</b> <span style={{ color: '#16a34a', fontWeight: 800 }}>108</span></div>
            <div><b>Police Dispatch:</b> <span style={{ color: '#0f172a', fontWeight: 800 }}>100</span></div>
          </div>
          <hr style={{ margin: '12px 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />
          <div style={{ fontSize: '11.5px', color: '#64748b' }}>
            <b>Battalion Status:</b> {advisory?.ndrf_status || 'Level 1 Standby'}
          </div>
        </div>
      </div>

      {/* ── Export Assessment Report ── */}
      <div className="white-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
        <div>
          <b style={{ fontSize: '15px', color: '#0f172a' }}>Export Disaster Assessment Manifest</b>
          <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
            Generate and download assessment manifests in JSON or CSV format.
          </div>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="search-btn" style={{ background: '#0f172a' }} onClick={handleExportJson}>
            <FileCode size={15} />
            Download JSON
          </button>
          <button className="search-btn" style={{ background: '#334155' }} onClick={handleExportCsv}>
            <FileSpreadsheet size={15} />
            Download CSV
          </button>
        </div>
      </div>
    </div>
  );
}
