import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import MapPage from './pages/MapPage';
import DashboardPage from './pages/DashboardPage';
import SafetyPage from './pages/SafetyPage';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  // 3-page system: 'map' | 'dashboard' | 'safety'
  const [activePage, setActivePage] = useState('map');
  const [appMode, setAppMode] = useState('LIVE');
  const [currentPlace, setCurrentPlace] = useState('Patna');
  
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Simulation parameters (Live mode)
  const [simRain, setSimRain] = useState(0.0);
  const [simDischarge, setSimDischarge] = useState(0.0);
  const [selectedShelterId, setSelectedShelterId] = useState('shelter_1');

  // Historical scenarios
  const [historicalScenarios, setHistoricalScenarios] = useState([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState('patna_2019');
  const [scenarioStageIdx, setScenarioStageIdx] = useState(2);

  // Initial load
  useEffect(() => {
    // 1. Fetch available historical scenarios
    fetch(`${API_BASE}/api/historical/scenarios`)
      .then((res) => res.json())
      .then((data) => {
        if (data.scenarios && data.scenarios.length > 0) {
          setHistoricalScenarios(data.scenarios);
          setSelectedScenarioId(data.scenarios[0].id);
        }
      })
      .catch((err) => console.error('Failed to fetch historical scenarios:', err));

    // 2. Initial analysis for Patna
    fetchLiveAnalysis('Patna', 0.0, 0.0, 'shelter_1');
  }, []);

  // Fetch live analysis
  const fetchLiveAnalysis = async (placeQuery, rainAdd = 0.0, dischargeAdd = 0.0, shelterId = 'shelter_1') => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          place_query: placeQuery,
          sim_rain_add: rainAdd,
          sim_discharge_add: dischargeAdd,
          selected_shelter_id: shelterId
        })
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to analyze location');
      }
      const data = await res.json();
      setAnalysisData(data);
      setCurrentPlace(data.place_info.name);
      setAppMode('LIVE');
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch historical scenario stage analysis
  const fetchHistoricalAnalysis = async (scenId, stageIdx, shelterId = 'shelter_1') => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/historical/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_id: scenId,
          stage_idx: stageIdx,
          selected_shelter_id: shelterId
        })
      });
      if (!res.ok) {
        throw new Error('Failed to evaluate historical stage');
      }
      const data = await res.json();
      setAnalysisData(data);
      setCurrentPlace(data.place_info.name);
      setAppMode('HISTORICAL');
    } catch (err) {
      console.error('Historical replay error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Search handler
  const handleSearch = (placeName) => {
    setSimRain(0.0);
    setSimDischarge(0.0);
    fetchLiveAnalysis(placeName, 0.0, 0.0, selectedShelterId);
  };

  // Quick benchmark city
  const handleQuickCity = (cityName) => {
    setSimRain(0.0);
    setSimDischarge(0.0);
    fetchLiveAnalysis(cityName, 0.0, 0.0, selectedShelterId);
  };

  // Run simulation sliders
  const handleRunSimulation = (rainAdd, dischargeAdd) => {
    fetchLiveAnalysis(currentPlace, rainAdd, dischargeAdd, selectedShelterId);
  };

  const handleResetSimulation = () => {
    setSimRain(0.0);
    setSimDischarge(0.0);
    fetchLiveAnalysis(currentPlace, 0.0, 0.0, selectedShelterId);
  };

  // Change shelter selection
  const handleSelectShelter = async (shelterId) => {
    setSelectedShelterId(shelterId);
    if (appMode === 'LIVE') {
      fetchLiveAnalysis(currentPlace, simRain, simDischarge, shelterId);
    } else {
      fetchHistoricalAnalysis(selectedScenarioId, scenarioStageIdx, shelterId);
    }
  };

  // Mode toggle from Navbar
  const handleModeToggle = (newMode) => {
    setAppMode(newMode);
    if (newMode === 'HISTORICAL') {
      fetchHistoricalAnalysis(selectedScenarioId, scenarioStageIdx, selectedShelterId);
    } else {
      fetchLiveAnalysis(currentPlace, 0.0, 0.0, selectedShelterId);
    }
  };

  // Historical phase change
  const handleHistoricalPhaseChange = (scenId, stageIdx) => {
    setSelectedScenarioId(scenId);
    setScenarioStageIdx(stageIdx);
    fetchHistoricalAnalysis(scenId, stageIdx, selectedShelterId);
  };

  return (
    <div className="app-root">
      {/* ── Top Navigation Bar (3-Page System, Fixed at Top) ── */}
      <Navbar
        activePage={activePage}
        setActivePage={setActivePage}
        appMode={appMode}
        setAppMode={handleModeToggle}
        currentPlace={currentPlace}
        onSearch={handleSearch}
        onQuickCity={handleQuickCity}
      />

      {/* Loading Indicator */}
      {loading && (
        <div style={{
          position: 'fixed',
          top: '115px',
          right: '28px',
          background: '#1d4ed8',
          color: '#ffffff',
          padding: '8px 16px',
          borderRadius: '20px',
          fontSize: '12px',
          fontWeight: 700,
          boxShadow: '0 4px 12px rgba(29, 78, 216, 0.3)',
          zIndex: 2000,
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span className="pulse-dot" style={{ backgroundColor: '#60a5fa' }} />
          Executing AI Hydrological Synthesis...
        </div>
      )}

      {error && (
        <div style={{
          background: '#fee2e2',
          border: '1px solid #fca5a5',
          color: '#dc2626',
          padding: '12px 28px',
          textAlign: 'center',
          fontSize: '13px',
          fontWeight: 700
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* ── 3-Page Routing ── */}
      <main>
        {activePage === 'map' && (
          <MapPage
            analysisData={analysisData}
            selectedShelterId={selectedShelterId}
            onSelectShelter={handleSelectShelter}
          />
        )}

        {activePage === 'dashboard' && (
          <DashboardPage
            analysisData={analysisData}
            appMode={appMode}
            historicalScenarios={historicalScenarios}
            selectedScenarioId={selectedScenarioId}
            scenarioStageIdx={scenarioStageIdx}
            simRain={simRain}
            setSimRain={setSimRain}
            simDischarge={simDischarge}
            setSimDischarge={setSimDischarge}
            onRunSimulation={handleRunSimulation}
            onResetSimulation={handleResetSimulation}
            onHistoricalPhaseChange={handleHistoricalPhaseChange}
            onNavigateToMap={() => setActivePage('map')}
          />
        )}

        {activePage === 'safety' && (
          <SafetyPage />
        )}
      </main>

      {/* ── Bright Mode Footer ── */}
      <footer className="app-footer">
        <b>FloodSense AI</b> &mdash; Disaster Risk Intelligence &amp; Autonomous Evacuation Command &nbsp;&bull;&nbsp;
        7th Sem Major Capstone Project &nbsp;&bull;&nbsp; CSE / AI-ML &nbsp;&bull;&nbsp;
        Powered by XGBoost, Dijkstra Graph Search, GloFAS &amp; Open-Meteo
      </footer>
    </div>
  );
}
