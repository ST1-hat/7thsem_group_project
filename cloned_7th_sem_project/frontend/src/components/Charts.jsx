import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar, Radar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
);

/**
 * 1. Precipitation Forecast Chart (36h curve)
 */
export function PrecipitationForecastChart({ times = [], values = [] }) {
  const labels = times.length > 0 
    ? times.map((t, i) => i % 3 === 0 ? t.split(' ')[1] || `T+${i}h` : '') 
    : Array.from({ length: 36 }, (_, i) => `+${i}h`);

  const data = {
    labels,
    datasets: [
      {
        label: 'Hourly Rainfall (mm)',
        data: values.length > 0 ? values : [0, 1.2, 3.4, 5.1, 7.8, 12.0, 18.5, 14.2, 9.0, 6.1, 4.0, 2.0],
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.12)',
        fill: true,
        tension: 0.35,
        pointRadius: 2.5,
        pointHoverRadius: 6
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0f172a',
        titleFont: { size: 12, weight: 'bold' },
        bodyFont: { size: 12 }
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { font: { size: 11 }, color: '#64748b' }
      },
      y: {
        title: { display: true, text: 'Rainfall (mm / hr)', font: { size: 11, weight: 'bold' }, color: '#475569' },
        ticks: { font: { size: 11 }, color: '#64748b' },
        grid: { color: '#f1f5f9' },
        suggestedMax: 25
      }
    }
  };

  return (
    <div style={{ height: '320px', width: '100%' }}>
      <Line data={data} options={options} />
    </div>
  );
}

/**
 * 2. River Discharge Hydrograph (7-day forecast)
 */
export function RiverDischargeChart({ dates = [], values = [] }) {
  const labels = dates.length > 0 
    ? dates.map(d => d.slice(5)) 
    : ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'];

  const data = {
    labels,
    datasets: [
      {
        label: 'River Discharge (m³/s)',
        data: values.length > 0 ? values : [800, 1100, 1600, 2400, 2900, 2200, 1500],
        borderColor: '#0284c7',
        backgroundColor: 'rgba(2, 132, 199, 0.18)',
        fill: true,
        tension: 0.3,
        pointRadius: 4,
        pointBackgroundColor: '#0284c7',
        pointHoverRadius: 7
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0f172a'
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { font: { size: 11 }, color: '#64748b' }
      },
      y: {
        title: { display: true, text: 'Discharge (m³/s)', font: { size: 11, weight: 'bold' }, color: '#475569' },
        ticks: { font: { size: 11 }, color: '#64748b' },
        grid: { color: '#f1f5f9' },
        suggestedMax: 3500
      }
    }
  };

  return (
    <div style={{ height: '320px', width: '100%' }}>
      <Line data={data} options={options} />
    </div>
  );
}

/**
 * 3. Explainable AI (XAI) Radar Chart
 */
export function FactorRadarChart({ contributions = {} }) {
  const keys = Object.keys(contributions);
  const labels = keys.length > 0 ? keys : [
    'Rainfall Intensity',
    'Water Level',
    'River Discharge',
    'Terrain Vulnerability',
    'Humidity',
    'Historical Flood'
  ];
  const values = keys.length > 0 ? Object.values(contributions) : [65, 80, 50, 70, 85, 90];

  const data = {
    labels,
    datasets: [
      {
        label: 'Feature Vulnerability Impact (%)',
        data: values,
        backgroundColor: 'rgba(239, 68, 68, 0.22)',
        borderColor: '#dc2626',
        pointBackgroundColor: '#dc2626',
        pointBorderColor: '#ffffff',
        pointHoverBackgroundColor: '#ffffff',
        pointHoverBorderColor: '#dc2626',
        borderWidth: 2
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      r: {
        angleLines: { color: '#e2e8f0' },
        grid: { color: '#f1f5f9' },
        pointLabels: {
          font: { size: 11, weight: 'bold' },
          color: '#334155'
        },
        ticks: {
          display: false,
          suggestedMin: 0,
          suggestedMax: 100
        }
      }
    }
  };

  return (
    <div style={{ height: '320px', width: '100%' }}>
      <Radar data={data} options={options} />
    </div>
  );
}

/**
 * 4. Peripheral Stations Comparison Bar Chart
 */
export function NearbyComparisonChart({ stations = [] }) {
  const labels = stations.map(s => s.name.split(' - ').pop() || s.name);
  const scores = stations.map(s => s.risk?.risk_score || 0);
  const colors = stations.map(s => s.risk?.color_hex || '#3b82f6');

  const data = {
    labels,
    datasets: [
      {
        label: 'Flood Risk (%)',
        data: scores,
        backgroundColor: colors,
        borderRadius: 6
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { font: { size: 11 }, color: '#64748b' }
      },
      y: {
        title: { display: true, text: 'Risk Score (%)', font: { size: 11, weight: 'bold' }, color: '#475569' },
        suggestedMax: 100,
        ticks: { font: { size: 11 }, color: '#64748b' },
        grid: { color: '#f1f5f9' }
      }
    }
  };

  return (
    <div style={{ height: '320px', width: '100%' }}>
      <Bar data={data} options={options} />
    </div>
  );
}

/**
 * 5. Radial Risk Gauge Component
 */
export function RiskGauge({ score = 0, category = 'LOW RISK', color = '#22c55e' }) {
  const radius = 68;
  const stroke = 12;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  // Semi-circle gauge (half circumference)
  const strokeDashoffset = circumference - (score / 100) * (circumference * 0.75);

  return (
    <div style={{ textAlign: 'center', padding: '16px 0' }}>
      <div style={{ position: 'relative', display: 'inline-block' }}>
        <svg height={radius * 2} width={radius * 2}>
          {/* Background track */}
          <circle
            stroke="#e2e8f0"
            fill="transparent"
            strokeWidth={stroke}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          {/* Progress arc */}
          <circle
            stroke={color}
            fill="transparent"
            strokeWidth={stroke}
            strokeDasharray={`${circumference} ${circumference}`}
            style={{
              strokeDashoffset,
              transition: 'stroke-dashoffset 0.8s ease-in-out',
              transform: 'rotate(-90deg)',
              transformOrigin: '50% 50%',
              strokeLinecap: 'round'
            }}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
        </svg>
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '26px', fontWeight: 900, color: '#0f172a', lineHeight: 1 }}>
            {score}%
          </div>
          <div style={{ fontSize: '10px', fontWeight: 800, textTransform: 'uppercase', color, marginTop: '4px' }}>
            {category}
          </div>
        </div>
      </div>
      <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 600, marginTop: '8px' }}>
        Calibrated XGBoost + RF + IMD Hydro Matrix
      </div>
    </div>
  );
}
