import React, { useState } from 'react';
import { 
  Compass, 
  Layers, 
  ShieldCheck, 
  AlertTriangle, 
  Hospital, 
  Radio, 
  Navigation, 
  MapPin, 
  Clock, 
  TrendingUp,
  Sliders,
  ChevronRight
} from 'lucide-react';
import MapComponent from '../components/MapComponent';

export default function MapPage({
  analysisData,
  selectedShelterId,
  onSelectShelter
}) {
  const [showWaypoints, setShowWaypoints] = useState(true);

  if (!analysisData) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: '80px 20px' }}>
        <div style={{ display: 'inline-block', marginBottom: '14px' }}>
          <Compass size={40} color="#0f172a" />
        </div>
        <h2>Loading Geospatial Map Intelligence...</h2>
      </div>
    );
  }

  const { place_info, risk_result, nearby_stations, evacuation_plan } = analysisData;
  const safeRoute = evacuation_plan?.safe_route || {};
  const directRoute = evacuation_plan?.direct_route || {};
  const targetShelter = evacuation_plan?.target_shelter || {};
  const candidateShelters = evacuation_plan?.candidate_shelters || [];

  return (
    <div className="page-container">
      {/* Page Title & Status Strip */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', marginBottom: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="section-icon" style={{ background: '#0f172a', color: '#ffffff' }}>
            <Compass size={22} />
          </div>
          <div>
            <div className="section-title">Geospatial Disaster Command Map</div>
            <div className="section-sub">
              Location: <b>{place_info?.full_name}</b> &nbsp;|&nbsp; 
              Coordinates: {place_info?.latitude?.toFixed(4)}°N, {place_info?.longitude?.toFixed(4)}°E &nbsp;|&nbsp;
              Elevation: {place_info?.elevation || 50}m MSL
            </div>
          </div>
        </div>

        {/* Quick Corridor KPI Pill with Hazard Colors */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', background: '#ffffff', border: '1px solid #e2e8f0', padding: '6px 14px', borderRadius: '10px', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
          <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#64748b' }}>
            Evacuation Corridor:
          </div>
          <div style={{ fontSize: '13px', fontWeight: 800, color: '#16a34a' }}>
            {safeRoute?.total_distance_km || 0} km (ETA: {safeRoute?.transit_time_mins || 0}m)
          </div>
          <div style={{ fontSize: '11px', color: '#dc2626', fontWeight: 800, paddingLeft: '8px', borderLeft: '1px solid #e2e8f0' }}>
            Submergence Avoided: {evacuation_plan?.water_avoided_m || 0}m
          </div>
        </div>
      </div>

      {/* Main Map View & Tactical Controls */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 7.5fr) minmax(0, 2.5fr)', gap: '20px', marginBottom: '24px' }}>
        {/* Full-Feature Map */}
        <div>
          <MapComponent
            placeInfo={place_info}
            riskResult={risk_result}
            nearbyStations={nearby_stations}
            evacuationPlan={evacuation_plan}
            physicalStructures={analysisData.physical_structures}
            heatmapPoints={analysisData.heatmap_points}
          />
        </div>

        {/* Tactical Shelter & Layer Controls Sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Destination Shelter Card */}
          <div className="white-card" style={{ margin: 0 }}>
            <div className="card-title" style={{ fontSize: '14px', marginBottom: '10px' }}>
              <Hospital size={17} color="#16a34a" />
              Target Relief Shelter
            </div>

            <label style={{ fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', color: '#64748b' }}>
              Select Emergency Shelter:
            </label>
            <select
              style={{
                width: '100%',
                padding: '8px 10px',
                borderRadius: '8px',
                border: '1.5px solid #cbd5e1',
                fontSize: '12.5px',
                fontWeight: 600,
                color: '#0f172a',
                marginTop: '6px',
                marginBottom: '12px',
                outline: 'none',
                background: '#ffffff'
              }}
              value={targetShelter?.id}
              onChange={(e) => onSelectShelter(e.target.value)}
            >
              {candidateShelters.map((sh) => (
                <option key={sh.id} value={sh.id}>
                  {sh.name.split(' ')[0]} Camp (+{sh.elevation_m}m MSL)
                </option>
              ))}
            </select>

            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '12px', fontSize: '12px', lineHeight: 1.6 }}>
              <b style={{ color: '#065f46', fontSize: '13px', display: 'block', marginBottom: '4px' }}>
                🛡️ {targetShelter?.name}
              </b>
              <div><b>Type:</b> {targetShelter?.type}</div>
              <div><b>Available Beds:</b> <span style={{ color: '#16a34a', fontWeight: 800 }}>{targetShelter?.remaining_beds}</span> / {targetShelter?.capacity}</div>
              <div><b>Elevation:</b> {targetShelter?.elevation_m} m MSL</div>
              <div><b>Medical Support:</b> {targetShelter?.medical_support}</div>
              <div style={{ color: '#475569', fontSize: '11px', marginTop: '6px' }}>
                <b>Emergency Contact:</b> {targetShelter?.contact}
              </div>
            </div>
          </div>

          {/* Pathfinding Differential Summary */}
          <div className="white-card" style={{ margin: 0, fontSize: '12px', lineHeight: 1.8 }}>
            <div className="card-title" style={{ fontSize: '14px', marginBottom: '8px' }}>
              <Navigation size={17} color="#1d4ed8" />
              Dijkstra Routing Differential
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '4px' }}>
              <span>AI Safe Ridge Path:</span>
              <b style={{ color: '#16a34a' }}>{safeRoute?.total_distance_km} km (Clear)</b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', padding: '4px 0' }}>
              <span>Naive Direct Road:</span>
              <b style={{ color: '#dc2626' }}>{directRoute?.max_water_depth_m}m Submerged</b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', padding: '4px 0' }}>
              <span>Water Hazard Avoided:</span>
              <b style={{ color: '#1d4ed8' }}>{evacuation_plan?.water_avoided_m} m</b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '4px' }}>
              <span>Transit Time:</span>
              <b>⏱️ {safeRoute?.transit_time_mins} mins</b>
            </div>
          </div>
        </div>
      </div>

      {/* Turn-by-Turn Waypoints Table */}
      <div className="white-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <div className="card-title" style={{ margin: 0 }}>
            🧭 Turn-by-Turn Safe Corridor Navigation Manifest
          </div>
          <button 
            className="mode-toggle-btn"
            style={{ padding: '4px 12px', fontSize: '12px' }}
            onClick={() => setShowWaypoints(!showWaypoints)}
          >
            {showWaypoints ? 'Hide Waypoints' : 'Show Waypoints'}
          </button>
        </div>

        {showWaypoints && (
          <table className="styled-table">
            <thead>
              <tr>
                <th>Step</th>
                <th>Routing Waypoint Instruction</th>
                <th>Segment Distance</th>
                <th>Target Elevation</th>
                <th>Water Depth</th>
                <th>Passability Status</th>
              </tr>
            </thead>
            <tbody>
              {(safeRoute?.steps || []).map((step) => (
                <tr key={step.step_no}>
                  <td><b>#{step.step_no}</b></td>
                  <td>{step.instruction}</td>
                  <td>{step.distance_km} km</td>
                  <td>{step.elevation_m} m MSL</td>
                  <td>{step.water_depth_m} m</td>
                  <td>
                    <span style={{ 
                      color: step.passability.includes('PASSABLE') ? '#16a34a' : '#ea580c',
                      fontWeight: 800,
                      background: step.passability.includes('PASSABLE') ? '#dcfce7' : '#ffedd5',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '11px'
                    }}>
                      {step.passability}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
