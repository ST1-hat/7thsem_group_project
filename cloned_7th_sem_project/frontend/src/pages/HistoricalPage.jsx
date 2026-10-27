import React, { useState, useEffect } from 'react';
import { BookOpen, History, MapPin, Play, Zap, ArrowRight, ShieldAlert } from 'lucide-react';

export default function HistoricalPage({
  currentCity = 'Patna',
  historicalScenarios = [],
  selectedScenarioId,
  setSelectedScenarioId,
  scenarioStageIdx,
  setScenarioStageIdx,
  onLoadScenarioStage,
  onBackToLive
}) {
  const [histData, setHistData] = useState(null);
  const [activeCity, setActiveCity] = useState(currentCity);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/historical-data?city=${encodeURIComponent(activeCity)}`)
      .then((res) => res.json())
      .then((data) => setHistData(data))
      .catch((err) => console.error('Error fetching historical records:', err));
  }, [activeCity]);

  const activeScenario = historicalScenarios.find(s => s.id === selectedScenarioId) || historicalScenarios[0];
  const stages = activeScenario?.stages || [];
  const currentStage = stages[scenarioStageIdx] || stages[0];

  const severityColor = (sev) => {
    switch (sev) {
      case 'CRITICAL': return { bg: '#fee2e2', text: '#dc2626', border: '#fca5a5' };
      case 'HIGH': return { bg: '#ffedd5', text: '#ea580c', border: '#fdba74' };
      default: return { bg: '#fef3c7', text: '#d97706', border: '#fde68a' };
    }
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div className="section-header" style={{ marginTop: '4px' }}>
        <div className="section-icon" style={{ background: '#eff6ff', color: '#1d4ed8' }}>
          <BookOpen size={24} />
        </div>
        <div>
          <div className="section-title">Historical Flood Catastrophe Archives &amp; CWC Replay</div>
          <div className="section-sub">Documented Indian deluge benchmarks, hydrograph re-evaluations, and timeline stress-testing</div>
        </div>
      </div>

      {/* ── Area-Specific Historical Search Strip ── */}
      <div className="white-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', marginBottom: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MapPin size={18} color="#1d4ed8" />
            <b style={{ fontSize: '15px', color: '#0f172a' }}>Filter Area-Specific Disaster Archives:</b>
          </div>
          <div className="quick-chips-row">
            {(histData?.available_cities || ['Patna', 'Kochi', 'Guwahati', 'Mumbai', 'Delhi', 'Cuttack', 'Varanasi']).map((c) => (
              <button
                key={c}
                className={`quick-chip ${activeCity.toLowerCase() === c.toLowerCase() ? 'active' : ''}`}
                style={{
                  background: activeCity.toLowerCase() === c.toLowerCase() ? '#1d4ed8' : '#f1f5f9',
                  color: activeCity.toLowerCase() === c.toLowerCase() ? '#ffffff' : '#334155'
                }}
                onClick={() => setActiveCity(c)}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* Display matched events */}
        {histData?.records && histData.records.length > 0 ? (
          <div>
            <div style={{ background: '#eff6ff', borderLeft: '4px solid #1d4ed8', padding: '10px 16px', borderRadius: '0 8px 8px 0', fontSize: '12.5px', color: '#1e3a5f', marginBottom: '16px' }}>
              Showing <b>{histData.records.length}</b> verified historical deluge records for <b>{histData.matched_city}</b> from CWC, IMD, and NDMA archives.
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {histData.records.map((rec, i) => {
                const colors = severityColor(rec.severity);
                return (
                  <div key={i} className="white-card" style={{ border: '1px solid #e2e8f0', margin: 0, padding: '18px 22px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px' }}>
                      <div>
                        <span style={{ background: '#eff6ff', color: '#1d4ed8', fontSize: '11px', fontWeight: 800, padding: '3px 10px', borderRadius: '20px' }}>
                          {rec.year}
                        </span>
                        <div style={{ fontSize: '17px', fontWeight: 800, color: '#0f172a', margin: '4px 0 2px' }}>
                          {rec.event}
                        </div>
                        <div style={{ fontSize: '12.5px', color: '#64748b' }}>
                          🌊 River Basin: <b>{rec.river}</b>
                        </div>
                        <div style={{ fontSize: '12.5px', color: '#475569', margin: '8px 0 12px', maxWidth: '750px' }}>
                          <b>Root Cause:</b> {rec.cause}
                        </div>
                      </div>

                      <div style={{ background: colors.bg, border: `1px solid ${colors.border}`, padding: '8px 16px', borderRadius: '10px', textAlign: 'center' }}>
                        <div style={{ fontSize: '10px', fontWeight: 800, textTransform: 'uppercase', color: colors.text, letterSpacing: '0.5px' }}>Severity</div>
                        <div style={{ fontSize: '18px', fontWeight: 900, color: colors.text }}>{rec.severity}</div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', borderTop: '1px solid #f1f5f9', paddingTop: '12px' }}>
                      <div className="metric-card" style={{ padding: '8px 14px', flex: 1, minWidth: '120px' }}>
                        <span className="metric-label">Peak Rain</span>
                        <div className="metric-val" style={{ fontSize: '18px' }}>{rec.peak_rainfall_mm} <span className="metric-unit">mm</span></div>
                      </div>
                      <div className="metric-card" style={{ padding: '8px 14px', flex: 1, minWidth: '120px' }}>
                        <span className="metric-label">Peak Discharge</span>
                        <div className="metric-val" style={{ fontSize: '18px' }}>{rec.peak_discharge_m3s?.toLocaleString()} <span className="metric-unit">m³/s</span></div>
                      </div>
                      <div className="metric-card" style={{ padding: '8px 14px', flex: 1, minWidth: '120px' }}>
                        <span className="metric-label">HFL Record</span>
                        <div className="metric-val" style={{ fontSize: '18px' }}>{rec.hfl_m} <span className="metric-unit">m</span></div>
                      </div>
                      <div className="metric-card" style={{ padding: '8px 14px', flex: 1, minWidth: '120px' }}>
                        <span className="metric-label">Area Flooded</span>
                        <div className="metric-val" style={{ fontSize: '18px' }}>{rec.affected_area_km2} <span className="metric-unit">km²</span></div>
                      </div>
                      <div className="metric-card" style={{ padding: '8px 14px', flex: 1, minWidth: '120px' }}>
                        <span className="metric-label">Displaced</span>
                        <div className="metric-val" style={{ fontSize: '18px' }}>{rec.displaced_thousands}K</div>
                      </div>
                      <div className="metric-card" style={{ padding: '8px 14px', flex: 1, minWidth: '120px' }}>
                        <span className="metric-label">Casualties</span>
                        <div className="metric-val" style={{ fontSize: '18px', color: '#dc2626' }}>{rec.deaths}</div>
                      </div>
                      <div className="metric-card" style={{ padding: '8px 14px', flex: 1, minWidth: '120px' }}>
                        <span className="metric-label">Economic Loss</span>
                        <div className="metric-val" style={{ fontSize: '18px' }}>₹{rec.economic_loss_crore?.toLocaleString()} Cr</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '30px', color: '#64748b' }}>
            No specific regional records matched for "{activeCity}". Check out the major Indian flood archive below.
          </div>
        )}
      </div>

      {/* ── Disaster Replay Simulator Preview Strip ── */}
      <div className="section-header">
        <div className="section-icon" style={{ background: '#fef3c7', color: '#b45309' }}>
          <History size={22} />
        </div>
        <div>
          <div className="section-title">Disaster Replay Simulator</div>
          <div className="section-sub">Replay historical hourly telemetry through the AI model to stress-test Dijkstra evacuation</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 5fr) minmax(0, 5fr)', gap: '20px', marginBottom: '28px' }}>
        {/* Catastrophe Selector */}
        <div className="white-card">
          <div className="card-title">
            📁 Select Historical Disaster:
          </div>
          <select
            style={{
              width: '100%',
              padding: '10px 14px',
              borderRadius: '8px',
              border: '1.5px solid #cbd5e1',
              fontSize: '13.5px',
              fontWeight: 700,
              color: '#0f172a',
              outline: 'none',
              background: '#ffffff',
              marginBottom: '14px'
            }}
            value={selectedScenarioId}
            onChange={(e) => setSelectedScenarioId(e.target.value)}
          >
            {historicalScenarios.map((sc) => (
              <option key={sc.id} value={sc.id}>
                🌊 {sc.title} ({sc.year})
              </option>
            ))}
          </select>

          {activeScenario && (
            <div style={{ fontSize: '12.5px', lineHeight: 1.8, background: '#f8fafc', padding: '16px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
              <div style={{ fontWeight: 800, fontSize: '14px', color: '#1e3a5f', marginBottom: '6px' }}>
                {activeScenario.title}
              </div>
              <p style={{ color: '#475569', marginBottom: '10px' }}>{activeScenario.summary}</p>
              <div><b>CWC Gauge Station:</b> {activeScenario.cwc_gauge_station}</div>
              <div><b>Danger Mark:</b> {activeScenario.danger_mark_m} m MSL</div>
              <div><b>All-Time HFL Record:</b> {activeScenario.hfl_record_m} m MSL</div>
            </div>
          )}
        </div>

        {/* Phase Details & Trigger */}
        <div className="white-card">
          <div className="card-title">
            ⏱️ Select Replay Phase ({scenarioStageIdx + 1}/{stages.length})
          </div>

          <div style={{ marginBottom: '14px' }}>
            <input
              type="range"
              min={0}
              max={stages.length - 1}
              step={1}
              value={scenarioStageIdx}
              onChange={(e) => setScenarioStageIdx(parseInt(e.target.value, 10))}
              className="custom-range"
            />
          </div>

          {currentStage && (
            <div style={{ fontSize: '12.5px', lineHeight: 1.8, background: '#f8fafc', padding: '16px', borderRadius: '10px', border: '1px solid #e2e8f0', marginBottom: '16px' }}>
              <div style={{ fontWeight: 800, fontSize: '14px', color: '#1e3a5f' }}>
                Phase: {currentStage.label}
              </div>
              <div>🕒 <b>Timestamp:</b> {currentStage.timestamp_str}</div>
              <div>🌧️ <b>Rainfall (24h):</b> {currentStage.rainfall_24h} mm</div>
              <div>🌊 <b>River Discharge:</b> {currentStage.river_discharge} m³/s</div>
              <div>📏 <b>Runoff Water Level:</b> {currentStage.water_level} m</div>
              <div>💧 <b>CWC Status:</b> {currentStage.cwc_status}</div>
              <div style={{ fontStyle: 'italic', color: '#64748b', marginTop: '6px' }}>
                📌 {currentStage.narrative}
              </div>
            </div>
          )}

          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button
              className="search-btn"
              style={{ background: '#1d4ed8', flex: 1, justifyContent: 'center' }}
              onClick={() => onLoadScenarioStage(selectedScenarioId, scenarioStageIdx)}
            >
              <Play size={15} />
              Replay This Phase in Dashboard
            </button>
            <button
              className="search-btn"
              style={{ background: '#ea580c', flex: 1, justifyContent: 'center' }}
              onClick={() => onLoadScenarioStage(selectedScenarioId, 2)}
            >
              <Zap size={15} />
              Jump to Peak Flood
            </button>
          </div>
        </div>
      </div>

      {/* ── India-wide Catastrophe Summary Table ── */}
      <div className="section-header">
        <div className="section-icon" style={{ background: '#f0fdf4', color: '#16a34a' }}>
          <History size={22} />
        </div>
        <div>
          <div className="section-title">Major Indian Flood Catastrophe Benchmark Archive</div>
          <div className="section-sub">Certified CWC gauge station records for model validation and academic stress-testing</div>
        </div>
      </div>

      <div className="white-card">
        <table className="styled-table">
          <thead>
            <tr>
              <th>Catastrophe Event</th>
              <th>Year</th>
              <th>River Basin / CWC Gauge</th>
              <th>HFL Record (m)</th>
              <th>Replay Phases</th>
              <th>Catastrophe Summary</th>
            </tr>
          </thead>
          <tbody>
            {(histData?.catastrophe_archive || []).map((cat, i) => (
              <tr key={i}>
                <td><b>{cat.catastrophe}</b></td>
                <td>{cat.year}</td>
                <td>{cat.river_basin}</td>
                <td><b>{cat.hfl_record_m} m</b></td>
                <td>{cat.timeline_phases} Phases</td>
                <td style={{ color: '#64748b' }}>{cat.summary}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Validation Callout */}
      <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '12px', padding: '18px 24px', fontSize: '13px', lineHeight: 1.8, color: '#1e3a5f', marginTop: '20px' }}>
        <b style={{ fontSize: '14px', display: 'block', marginBottom: '4px' }}>📌 Why Historical Catastrophe Playback Matters for Capstone Validation:</b>
        1. <b>Eliminates Dry-Day Bias:</b> On sunny presentation days, live weather APIs report 0mm rain. Historical time-travel allows evaluators to assess peak disaster scenarios on demand.<br />
        2. <b>Validates Evacuation Routing:</b> Tests Dijkstra graph avoidance on real submerged road networks during record inundations.<br />
        3. <b>Ground-Truth Model Calibration:</b> Demonstrates that AI probability spikes correspond directly to documented CWC Danger Level breaches.
      </div>
    </div>
  );
}
