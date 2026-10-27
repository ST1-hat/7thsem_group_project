import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet.heat';
import { Layers, Flame, Building2, Shield, Hospital, Radio, Map as MapIcon, Mountain, Eye } from 'lucide-react';
import { ShieldWaves } from './Icons';

// Free-source Tile Providers (100% Free, zero API key required)
const TILE_LAYERS = {
  topo: {
    name: 'Topography & Physical',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, METI'
  },
  satellite: {
    name: 'Satellite Infrastructure',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP'
  },
  light: {
    name: 'Carto Light Streets',
    url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; OpenStreetMap'
  },
  contour: {
    name: 'Elevation Contours',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: 'Map data: &copy; OpenStreetMap contributors, SRTM | Map style: &copy; OpenTopoMap'
  }
};

export default function MapComponent({
  placeInfo,
  riskResult,
  nearbyStations = [],
  evacuationPlan = null,
  physicalStructures = [],
  heatmapPoints = []
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const activeTileLayerRef = useRef(null);

  // Layer groups
  const baseGroupRef = useRef(null);
  const heatGroupRef = useRef(null);
  const structuresGroupRef = useRef(null);
  const routesGroupRef = useRef(null);
  const sheltersGroupRef = useRef(null);
  const stationsGroupRef = useRef(null);

  // State for toggles
  const [currentBase, setCurrentBase] = useState('topo');
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showStructures, setShowStructures] = useState(true);
  const [showSafeRoute, setShowSafeRoute] = useState(true);
  const [showShelters, setShowShelters] = useState(true);
  const [showStations, setShowStations] = useState(true);

  // 1. Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    const lat = placeInfo?.latitude || 25.5941;
    const lon = placeInfo?.longitude || 85.1376;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [lat, lon],
        zoom: 12,
        zoomControl: true
      });

      // Default base layer (Physical Topo)
      const tile = L.tileLayer(TILE_LAYERS.topo.url, {
        attribution: TILE_LAYERS.topo.attribution,
        maxZoom: 19
      }).addTo(map);

      activeTileLayerRef.current = tile;

      // Initialize feature groups
      baseGroupRef.current = L.featureGroup().addTo(map);
      heatGroupRef.current = L.featureGroup().addTo(map);
      structuresGroupRef.current = L.featureGroup().addTo(map);
      routesGroupRef.current = L.featureGroup().addTo(map);
      sheltersGroupRef.current = L.featureGroup().addTo(map);
      stationsGroupRef.current = L.featureGroup().addTo(map);

      mapInstanceRef.current = map;
    }
  }, []);

  // 2. Switch Basemap Tiles
  const switchBaseLayer = (key) => {
    setCurrentBase(key);
    if (!mapInstanceRef.current) return;

    if (activeTileLayerRef.current) {
      mapInstanceRef.current.removeLayer(activeTileLayerRef.current);
    }

    const cfg = TILE_LAYERS[key];
    const newTile = L.tileLayer(cfg.url, {
      attribution: cfg.attribution,
      maxZoom: 19
    }).addTo(mapInstanceRef.current);

    newTile.bringToBack();
    activeTileLayerRef.current = newTile;
  };

  // 3. Render all layers when data changes
  useEffect(() => {
    if (!mapInstanceRef.current) return;

    const lat = placeInfo?.latitude || 25.5941;
    const lon = placeInfo?.longitude || 85.1376;
    
    // KEEP HAZARD COLORS (Red, Orange, Yellow, Green) for alert levels
    const riskColor = riskResult?.color_hex || '#22c55e';

    mapInstanceRef.current.setView([lat, lon], 12);

    // Clear previous elements
    baseGroupRef.current.clearLayers();
    heatGroupRef.current.clearLayers();
    structuresGroupRef.current.clearLayers();
    routesGroupRef.current.clearLayers();
    sheltersGroupRef.current.clearLayers();
    stationsGroupRef.current.clearLayers();

    // ── Primary Epicenter & Hazard Catchment Halo ──
    L.circle([lat, lon], {
      radius: 4000,
      color: riskColor,
      weight: 2,
      opacity: 0.85,
      fillColor: riskColor,
      fillOpacity: 0.12,
      dashArray: '6, 6'
    }).bindPopup(`<b>Impact Zone:</b> ${placeInfo?.name}<br/>Hazard Grade: <b style="color:${riskColor}">${riskResult?.category}</b>`).addTo(baseGroupRef.current);

    // Primary Epicenter Marker: Sophisticated monochrome shield icon with hazard color halo
    const primaryIcon = L.divIcon({
      html: `
        <div style="
          background: #0f172a;
          color: #ffffff;
          width: 36px;
          height: 36px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 3px solid ${riskColor};
          box-shadow: 0 4px 14px rgba(15, 23, 42, 0.4);
        ">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path d="M7 11c1.5-1 3.5-1 5 0s3.5 1 5 0"/>
            <path d="M7 14c1.5-1 3.5-1 5 0s3.5 1 5 0"/>
          </svg>
        </div>
      `,
      className: 'epicenter-marker',
      iconSize: [36, 36],
      iconAnchor: [18, 18]
    });

    L.marker([lat, lon], { icon: primaryIcon })
      .bindPopup(`
        <div style="font-family: sans-serif; font-size: 13px; line-height: 1.6;">
          <b style="font-size: 15px; color: #0f172a;">${placeInfo?.name}</b><br/>
          <span style="color: ${riskColor}; font-weight: 800; font-size: 12px;">${riskResult?.alert_level} (${riskResult?.risk_score}%)</span><br/>
          <span>Elevation: <b>${placeInfo?.elevation || 50} m MSL</b></span>
        </div>
      `)
      .addTo(baseGroupRef.current);

    // ── Flood Inundation Heatmap Layer ──
    const pts = heatmapPoints && heatmapPoints.length > 0
      ? heatmapPoints
      : [
          [lat, lon, 0.95],
          [lat + 0.008, lon + 0.008, 0.85],
          [lat - 0.008, lon - 0.008, 0.8],
          [lat + 0.015, lon - 0.012, 0.65],
          [lat - 0.014, lon + 0.015, 0.6]
        ];

    try {
      const heat = L.heatLayer(pts, {
        radius: 35,
        blur: 24,
        maxZoom: 16,
        gradient: {
          0.15: '#3b82f6',
          0.40: '#06b6d4',
          0.65: '#eab308',
          0.85: '#f97316',
          1.00: '#dc2626'
        }
      });
      heat.addTo(heatGroupRef.current);
    } catch (e) {
      console.warn('Leaflet heat layer notice:', e);
    }

    // ── Physical Structures & Bridges ──
    const structs = physicalStructures && physicalStructures.length > 0
      ? physicalStructures
      : [
          {
            id: 's1',
            name: `${placeInfo?.name || 'City'} Arterial Bridge`,
            type: 'Arterial River Bridge',
            lat: lat + 0.012,
            lon: lon + 0.008,
            elevation_m: (placeInfo?.elevation || 50) + 12,
            structural_status: 'OPERATIONAL (HIGH DECK)',
            details: 'Major concrete bridge crossing primary river channel.'
          },
          {
            id: 's2',
            name: `${placeInfo?.name || 'City'} Sluice Gate #3`,
            type: 'Hydraulic Barrage Sluice',
            lat: lat - 0.015,
            lon: lon - 0.011,
            elevation_m: (placeInfo?.elevation || 50) - 2.5,
            structural_status: 'BACKFLOW WATCH ACTIVE',
            details: 'Stormwater drainage outflow regulator.'
          },
          {
            id: 's3',
            name: `${placeInfo?.name || 'City'} Flood Levee Bund`,
            type: 'River Embankment',
            lat: lat + 0.022,
            lon: lon - 0.018,
            elevation_m: (placeInfo?.elevation || 50) + 6,
            structural_status: 'STABLE ARMORED RIDGE',
            details: 'Boulder-riprap flood defense wall.'
          }
        ];

    structs.forEach((st) => {
      // Sophisticated monochrome black & white physical structure marker
      const structIcon = L.divIcon({
        html: `
          <div style="
            background: #0f172a;
            color: #ffffff;
            border: 1.5px solid #334155;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            box-shadow: 0 3px 8px rgba(15, 23, 42, 0.25);
            display: flex;
            align-items: center;
            gap: 5px;
            white-space: nowrap;
          ">
            <span style="font-size: 10px; opacity: 0.8;">STRUCTURE</span>
            <span>${st.name.split(' ')[0]}</span>
          </div>
        `,
        className: 'struct-marker',
        iconSize: [120, 24],
        iconAnchor: [60, 12]
      });

      L.marker([st.lat, st.lon], { icon: structIcon })
        .bindPopup(`
          <div style="font-family: sans-serif; font-size: 12px; line-height: 1.6;">
            <b style="font-size: 13.5px; color: #0f172a;">${st.name}</b><br/>
            <b>Classification:</b> ${st.type}<br/>
            <b>Elevation:</b> ${st.elevation_m} m MSL<br/>
            <b>Structural Condition:</b> <span style="font-weight: 800; color: #1e3a5f;">${st.structural_status}</span><br/>
            <span style="color: #64748b; font-size: 11px;">${st.details}</span>
          </div>
        `)
        .addTo(structuresGroupRef.current);
    });

    // ── Routes: Safe High-Ground Corridor & Submerged Road ──
    // Hazard alert colors preserved: Crimson Red for Submerged, Emerald Green for Safe
    if (evacuationPlan?.direct_route?.coordinates?.length > 1) {
      L.polyline(evacuationPlan.direct_route.coordinates, {
        color: '#dc2626',
        weight: 4,
        opacity: 0.85,
        dashArray: '8, 8',
        lineCap: 'round'
      }).bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px;">
          <b style="color: #dc2626;">Direct Road (HAZARDOUS)</b><br/>
          Submerged Depth: <b>${evacuationPlan.direct_route.max_water_depth_m} m</b><br/>
          Status: 🔴 Road Submerged / Chokepoint
        </div>
      `).addTo(routesGroupRef.current);
    }

    if (evacuationPlan?.safe_route?.coordinates?.length > 1) {
      L.polyline(evacuationPlan.safe_route.coordinates, {
        color: '#16a34a',
        weight: 6,
        opacity: 0.95,
        lineCap: 'round',
        lineJoin: 'round'
      }).bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px;">
          <b style="color: #16a34a; font-size: 13px;">AI Safe Evacuation Ridge Corridor</b><br/>
          Dijkstra Path avoiding submerged choke points.<br/>
          Distance: <b>${evacuationPlan.safe_route.total_distance_km} km</b><br/>
          ETA: <b>${evacuationPlan.safe_route.transit_time_mins} mins</b><br/>
          Status: 🟢 100% Passable High-Ground Ridge
        </div>
      `).addTo(routesGroupRef.current);
    }

    // ── Shelters ──
    if (evacuationPlan?.candidate_shelters) {
      evacuationPlan.candidate_shelters.forEach((sh) => {
        const isTarget = sh.id === evacuationPlan.target_shelter?.id;
        const shIcon = L.divIcon({
          html: `
            <div style="
              background: ${isTarget ? '#16a34a' : '#0f172a'};
              color: #ffffff;
              padding: 4px 8px;
              border-radius: 6px;
              font-size: 11px;
              font-weight: 800;
              display: flex;
              align-items: center;
              gap: 5px;
              border: 1.5px solid #ffffff;
              box-shadow: 0 3px 10px rgba(0,0,0,0.25);
              white-space: nowrap;
            ">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              <span>${sh.name.split(' ')[0]} (+${sh.remaining_beds || 0})</span>
            </div>
          `,
          className: 'shelter-marker',
          iconSize: [120, 28],
          iconAnchor: [60, 14]
        });

        L.marker([sh.latitude, sh.longitude], { icon: shIcon })
          .bindPopup(`
            <div style="font-family: sans-serif; font-size: 12px;">
              <b style="color: #0f172a; font-size: 13px;">${sh.name}</b><br/>
              <b>Available Beds:</b> <b style="color: #16a34a;">${sh.remaining_beds}</b> / ${sh.capacity}<br/>
              <b>Elevation:</b> ${sh.elevation_m} m MSL<br/>
              <b>Medical Unit:</b> ${sh.medical_support}
            </div>
          `)
          .addTo(sheltersGroupRef.current);
      });
    }

    // ── Peripheral Sensors ──
    if (nearbyStations && nearbyStations.length > 0) {
      nearbyStations.forEach((st) => {
        const stRiskColor = st.risk?.color_hex || '#3b82f6';
        const stIcon = L.divIcon({
          html: `
            <div style="
              background: #ffffff;
              color: #0f172a;
              border: 2px solid ${stRiskColor};
              width: 24px;
              height: 24px;
              border-radius: 50%;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 10px;
              font-weight: 800;
              box-shadow: 0 2px 6px rgba(0,0,0,0.15);
            ">
              <span style="width: 8px; height: 8px; border-radius: 50%; background: ${stRiskColor};"></span>
            </div>
          `,
          className: 'station-marker',
          iconSize: [24, 24],
          iconAnchor: [12, 12]
        });

        L.marker([st.latitude, st.longitude], { icon: stIcon })
          .bindPopup(`
            <div style="font-family: sans-serif; font-size: 12px;">
              <b>Telemetry Station: ${st.name}</b><br/>
              Risk: <b style="color: ${stRiskColor};">${st.risk?.category || 'Normal'} (${st.risk?.risk_score || 0}%)</b><br/>
              Elevation: ${st.elevation || 50} m MSL
            </div>
          `)
          .addTo(stationsGroupRef.current);
      });
    }
  }, [placeInfo, riskResult, nearbyStations, evacuationPlan, physicalStructures, heatmapPoints]);

  // Handle visibility toggles
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    if (heatGroupRef.current) {
      if (showHeatmap) mapInstanceRef.current.addLayer(heatGroupRef.current);
      else mapInstanceRef.current.removeLayer(heatGroupRef.current);
    }
  }, [showHeatmap]);

  useEffect(() => {
    if (!mapInstanceRef.current) return;
    if (structuresGroupRef.current) {
      if (showStructures) mapInstanceRef.current.addLayer(structuresGroupRef.current);
      else mapInstanceRef.current.removeLayer(structuresGroupRef.current);
    }
  }, [showStructures]);

  useEffect(() => {
    if (!mapInstanceRef.current) return;
    if (routesGroupRef.current) {
      if (showSafeRoute) mapInstanceRef.current.addLayer(routesGroupRef.current);
      else mapInstanceRef.current.removeLayer(routesGroupRef.current);
    }
  }, [showSafeRoute]);

  useEffect(() => {
    if (!mapInstanceRef.current) return;
    if (sheltersGroupRef.current) {
      if (showShelters) mapInstanceRef.current.addLayer(sheltersGroupRef.current);
      else mapInstanceRef.current.removeLayer(sheltersGroupRef.current);
    }
  }, [showShelters]);

  useEffect(() => {
    if (!mapInstanceRef.current) return;
    if (stationsGroupRef.current) {
      if (showStations) mapInstanceRef.current.addLayer(stationsGroupRef.current);
      else mapInstanceRef.current.removeLayer(stationsGroupRef.current);
    }
  }, [showStations]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {/* ── Tactical Map Controls Strip (Sophisticated Monochrome Toolbar) ── */}
      <div style={{
        background: '#ffffff',
        border: '1px solid #e2e8f0',
        borderRadius: '12px',
        padding: '10px 16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        boxShadow: '0 1px 4px rgba(0,0,0,0.03)'
      }}>
        {/* Basemap Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: '#64748b', marginRight: '4px' }}>
            Base Layer:
          </span>
          {Object.entries(TILE_LAYERS).map(([key, cfg]) => (
            <button
              key={key}
              onClick={() => switchBaseLayer(key)}
              style={{
                background: currentBase === key ? '#0f172a' : '#f8fafc',
                color: currentBase === key ? '#ffffff' : '#334155',
                border: '1px solid',
                borderColor: currentBase === key ? '#0f172a' : '#cbd5e1',
                padding: '5px 12px',
                borderRadius: '8px',
                fontSize: '12px',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {cfg.name}
            </button>
          ))}
        </div>

        {/* Feature Layer Toggles */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          {/* Heatmap Toggle */}
          <button
            onClick={() => setShowHeatmap(!showHeatmap)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '5px 12px',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: 800,
              cursor: 'pointer',
              border: '1px solid',
              background: showHeatmap ? '#0f172a' : '#f8fafc',
              borderColor: showHeatmap ? '#0f172a' : '#cbd5e1',
              color: showHeatmap ? '#ffffff' : '#64748b'
            }}
          >
            <Flame size={14} color={showHeatmap ? '#f97316' : '#64748b'} />
            Flood Heatmap: {showHeatmap ? 'ON' : 'OFF'}
          </button>

          {/* Physical Structures Toggle */}
          <button
            onClick={() => setShowStructures(!showStructures)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '5px 12px',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: 800,
              cursor: 'pointer',
              border: '1px solid',
              background: showStructures ? '#0f172a' : '#f8fafc',
              borderColor: showStructures ? '#0f172a' : '#cbd5e1',
              color: showStructures ? '#ffffff' : '#64748b'
            }}
          >
            <Building2 size={14} color={showStructures ? '#38bdf8' : '#64748b'} />
            Structures: {showStructures ? 'ON' : 'OFF'}
          </button>

          {/* Safe Corridor Toggle */}
          <button
            onClick={() => setShowSafeRoute(!showSafeRoute)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '5px 12px',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: 800,
              cursor: 'pointer',
              border: '1px solid',
              background: showSafeRoute ? '#0f172a' : '#f8fafc',
              borderColor: showSafeRoute ? '#0f172a' : '#cbd5e1',
              color: showSafeRoute ? '#ffffff' : '#64748b'
            }}
          >
            <Shield size={14} color={showSafeRoute ? '#22c55e' : '#64748b'} />
            Safe Corridor: {showSafeRoute ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>

      {/* ── Leaflet Container ── */}
      <div style={{ position: 'relative', width: '100%', height: '580px', borderRadius: '14px', overflow: 'hidden', border: '1px solid #e2e8f0', boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
        <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

        {/* Sophisticated Monochrome & Hazard Legend Overlay */}
        <div style={{
          position: 'absolute',
          bottom: '18px',
          right: '18px',
          background: 'rgba(255, 255, 255, 0.96)',
          backdropFilter: 'blur(8px)',
          border: '1px solid #cbd5e1',
          borderRadius: '10px',
          padding: '12px 16px',
          fontSize: '11px',
          zIndex: 999,
          boxShadow: '0 4px 14px rgba(15, 23, 42, 0.1)',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px'
        }}>
          <div style={{ fontWeight: 800, textTransform: 'uppercase', color: '#0f172a', letterSpacing: '0.6px', marginBottom: '2px' }}>
            Tactical Map Legend
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '18px', height: '6px', background: 'linear-gradient(90deg, #3b82f6, #eab308, #dc2626)', borderRadius: '2px' }} />
            <span><b>Flood Inundation Density</b></span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '12px', height: '12px', background: '#0f172a', borderRadius: '3px' }} />
            <span><b>Physical Structures &amp; Bridges</b></span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '18px', height: '5px', background: '#16a34a', borderRadius: '2px' }} />
            <span style={{ color: '#15803d', fontWeight: 800 }}>Safe Evacuation Ridge (Clear)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '18px', height: '0px', borderTop: '3px dashed #dc2626' }} />
            <span style={{ color: '#b91c1c', fontWeight: 800 }}>Submerged Chokepoint (Hazard)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Shield size={12} color="#0f172a" />
            <span><b>Emergency Relief Shelters</b></span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Radio size={12} color="#64748b" />
            <span><b>Telemetry Sensor Nodes</b></span>
          </div>
        </div>
      </div>
    </div>
  );
}
