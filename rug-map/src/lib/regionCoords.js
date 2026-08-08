// src/lib/regionCoords.js

/**
 * Geographic bounding centers, radii (in meters), and theme colors 
 * for broad rug-producing regions when exact city coordinates are missing.
 */
export const REGION_COORDS = {
//   'Serapi': { lat: 38.2482, lng: 47.0722, radius: 20000, color: '#f59e0b' },
  'Turkey': { lat: 39.0, lng: 35.0, radius: 320000, color: '#f59e0b' },
  // 'Caucasus': { lat: 41.5, lng: 46.5, radius: 220000, color: '#ec4899' },
//   'Persian': { lat: 32.0, lng: 53.0, radius: 550000, color: '#8b5cf6' },
//   'Iran': { lat: 32.0, lng: 53.0, radius: 550000, color: '#8b5cf6' },
  'South Central Asia': { lat: 37.1724, lng: 67.7872, radius: 450000, color: '#10b981' },
  'Turkman': { lat: 38.9697, lng: 59.5563, radius: 350000, color: '#10b981' },
//   'Turkmen': { lat: 38.5, lng: 59.0, radius: 350000, color: '#10b981' },
  'Kurdish': { lat: 36.5, lng: 44.0, radius: 250000, color: '#ef4444' },
  'Morocco': { lat: 31.8, lng: -6.5, radius: 300000, color: '#06b6d4' },
  'Baloch': { lat: 28.0, lng: 62.0, radius: 360000, color: '#f97316' },
//   'Kazakh': { lat: 48.0196, lng: 66.9237, radius: 350000, color: '#f97316' },
  'Unknown / General': { lat: 33.0, lng: 48.0, radius: 800000, color: '#64748b' },
  'Europe': { lat: 50.0000, lng: 10.0000, radius: 1000000, color: '#6b7280' },
  // @ts-ignore
  'Caucasus': { lat: 42.0000, lng: 45.0000, radius: 420000, color: '#8b5cf6' },
  'Bessarabian': { lat: 50.22, lng: 37.58, radius: 1150000, color: '#00d5ff' },
  'Bakhtiari': { lat: 32.1500, lng: 50.8500, radius: 50000, color: '#a855f7' }
};