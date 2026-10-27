import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  MapPin, 
  Shield, 
  Clock, 
  Activity, 
  Compass, 
  BarChart3,
  RefreshCw,
  Waves
} from 'lucide-react';
import { ShieldWaves } from './Icons';

export default function Navbar({
  activePage,
  setActivePage,
  appMode,
  setAppMode,
  currentPlace,
  onSearch,
  onQuickCity
}) {
  const [query, setQuery] = useState(currentPlace || 'Patna');
  const [suggestions, setSuggestions] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  // Sync input when currentPlace changes
  useEffect(() => {
    if (currentPlace) {
      setQuery(currentPlace);
    }
  }, [currentPlace]);

  // Debounced geocoding search suggestions
  useEffect(() => {
    if (!query || query.trim().length < 2) {
      setSuggestions([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/api/suggestions?q=${encodeURIComponent(query.trim())}`);
        if (res.ok) {
          const data = await res.json();
          setSuggestions(data.suggestions || []);
        }
      } catch (err) {
        // Fallback
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [query]);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setShowDropdown(false);
      onSearch(query.trim());
    }
  };

  const handleSelectSuggestion = (sug) => {
    setQuery(sug.name);
    setShowDropdown(false);
    onSearch(sug.name);
  };

  return (
    <header className="top-navbar">
      {/* Primary Brand & Nav Row */}
      <div className="navbar-inner">
        {/* Brand with Sophisticated Black & White Shield and Waves */}
        <div className="navbar-brand" onClick={() => setActivePage('map')}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            background: '#0f172a',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(15, 23, 42, 0.25)',
            flexShrink: 0
          }}>
            <ShieldWaves size={26} color="#0f172a" waveColor="#ffffff" />
          </div>
          <div>
            <div className="brand-title">FloodSense AI</div>
            <div className="brand-subtitle">Automated Flood Risk &amp; Evacuation Command</div>
          </div>
        </div>

        {/* 3-PAGE TOP NAVIGATION SYSTEM */}
        <nav className="navbar-nav">
          <button
            className={`nav-link ${activePage === 'map' ? 'active' : ''}`}
            onClick={() => setActivePage('map')}
          >
            <Compass size={16} />
            Geospatial Map
          </button>
          <button
            className={`nav-link ${activePage === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActivePage('dashboard')}
          >
            <BarChart3 size={16} />
            Command Dashboard
          </button>
          <button
            className={`nav-link ${activePage === 'safety' ? 'active' : ''}`}
            onClick={() => setActivePage('safety')}
          >
            <Shield size={16} />
            Safety Center
          </button>
        </nav>

        {/* Mode Indicator & Switcher */}
        <div className="navbar-actions">
          <span className={`mode-badge ${appMode === 'LIVE' ? 'live' : 'historical'}`}>
            {appMode === 'LIVE' ? (
              <>
                <span className="pulse-dot" />
                Live Telemetry
              </>
            ) : (
              <>
                <Clock size={13} />
                Historical Replay
              </>
            )}
          </span>

          <button
            className="mode-toggle-btn"
            onClick={() => setAppMode(appMode === 'LIVE' ? 'HISTORICAL' : 'LIVE')}
            title="Toggle between Real-time telemetry and Historical Catastrophe replay"
          >
            <RefreshCw size={14} />
            {appMode === 'LIVE' ? 'Historical Mode' : 'Live Mode'}
          </button>
        </div>
      </div>

      {/* Secondary Bar: Search & Quick Benchmark Hubs */}
      <div className="top-subbar">
        <div className="subbar-inner">
          <form className="search-container" ref={dropdownRef} onSubmit={handleSearchSubmit}>
            <div className="search-input-wrap">
              <Search size={17} color="#64748b" />
              <input
                type="text"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setShowDropdown(true);
                }}
                onFocus={() => setShowDropdown(true)}
                placeholder="Search city, basin, or river network (e.g., Guwahati, Kochi, Patna)..."
              />
              <button type="submit" className="search-btn">
                Search
              </button>
            </div>

            {/* Suggestions Dropdown */}
            {showDropdown && suggestions.length > 0 && (
              <div className="suggestions-dropdown">
                {suggestions.map((sug, idx) => (
                  <div
                    key={idx}
                    className="suggestion-item"
                    onClick={() => handleSelectSuggestion(sug)}
                  >
                    <MapPin size={14} color="#0f172a" />
                    <span>{sug.label}</span>
                  </div>
                ))}
              </div>
            )}
          </form>

          {/* Quick Benchmark Cities */}
          <div className="quick-chips-row">
            <span className="chip-label" style={{ color: '#475569' }}>
              Monitoring Hubs:
            </span>
            {['Patna', 'Guwahati', 'Kochi', 'Mumbai', 'Delhi', 'Cuttack', 'Varanasi'].map((city) => (
              <button
                key={city}
                className="quick-chip"
                onClick={() => {
                  setQuery(city);
                  onQuickCity(city);
                }}
              >
                {city}
              </button>
            ))}
          </div>
        </div>
      </div>
    </header>
  );
}
