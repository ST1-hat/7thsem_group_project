import React from 'react';

/**
 * Sophisticated Black & White Shield and Waves Emblem
 */
export function ShieldWaves({ size = 26, color = '#0f172a', waveColor = '#ffffff' }) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      style={{ display: 'inline-block', verticalAlign: 'middle' }}
    >
      {/* Outer Armor Shield Contour */}
      <path 
        d="M12 2L4 5V11C4 16.5 7.4 21.6 12 23C16.6 21.6 20 16.5 20 11V5L12 2Z" 
        fill={color} 
        stroke={color} 
        strokeWidth="1.5" 
        strokeLinejoin="round" 
      />
      {/* Upper Wave Vector */}
      <path 
        d="M7 10C8.5 8.8 10.5 8.8 12 10C13.5 11.2 15.5 11.2 17 10" 
        stroke={waveColor} 
        strokeWidth="1.7" 
        strokeLinecap="round" 
      />
      {/* Lower Wave Vector */}
      <path 
        d="M7 14C8.5 12.8 10.5 12.8 12 14C13.5 15.2 15.5 15.2 17 14" 
        stroke={waveColor} 
        strokeWidth="1.7" 
        strokeLinecap="round" 
      />
    </svg>
  );
}

/**
 * Minimalist Monochrome Wave Icon
 */
export function MinimalWave({ size = 20, color = '#0f172a' }) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
      style={{ display: 'inline-block', verticalAlign: 'middle' }}
    >
      <path d="M2 6c3-2 6-2 9 0s6 2 9 0" />
      <path d="M2 12c3-2 6-2 9 0s6 2 9 0" />
      <path d="M2 18c3-2 6-2 9 0s6 2 9 0" />
    </svg>
  );
}

/**
 * Minimalist Outline Shield Icon
 */
export function MinimalShield({ size = 20, color = '#0f172a' }) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke={color} 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
      style={{ display: 'inline-block', verticalAlign: 'middle' }}
    >
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}
