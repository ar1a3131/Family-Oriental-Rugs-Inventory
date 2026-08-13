<script lang="ts">
  import { CITY_COORDS } from '$lib/cityCoords.js';
  import { REGION_COORDS } from '$lib/regionCoords.js';
  import { COUNTRY_COORDS } from '$lib/countryCoords.js';

  // Props passed down from +page.svelte
  let { cityGroups = {}, regionGroups = {}, countryGroups = {}, onSelectGroup } = $props();

  let mapElement = $state(null);
  let mapInstance = $state(null);
  let L = $state(null);
  let layerGroup = null;

  // EFFECT 1: Initialize the Leaflet Map ONCE
  $effect(() => {
    if (!mapElement) return;

    let active = true;

    async function initMap() {
      const leafletModule = await import('leaflet');
      if (!active || mapInstance) return;

      L = leafletModule.default || leafletModule;

      const worldBounds = L.latLngBounds(L.latLng(-90, -180), L.latLng(90, 180));

      const instance = L.map(mapElement, { 
        zoomControl: false,
        minZoom: 2.5,
        maxBounds: worldBounds,
        maxBoundsViscosity: 1.0 
      }).setView([34.0, 48.0], 4);

      L.control.zoom({ position: 'topright' }).addTo(instance);

      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19,
        noWrap: true,
        bounds: worldBounds
      }).addTo(instance);

      layerGroup = L.layerGroup().addTo(instance);
      mapInstance = instance;
    }

    initMap();

    return () => {
      active = false;
      if (mapInstance) {
        mapInstance.remove();
        mapInstance = null;
      }
    };
  });

  // EFFECT 2: Render or update markers whenever Map is ready OR data props change
  $effect(() => {
    if (!mapInstance || !L || !layerGroup) return;

    layerGroup.clearLayers();

    // A. City Pins
    Object.entries(cityGroups).forEach(([cityName, rugs]) => {
      const coords = CITY_COORDS[cityName];
      if (!coords) return;

      const icon = L.divIcon({
        className: 'custom-map-pin',
        html: `
          <div class="pin-badge">
            <span class="pin-count">${rugs.length}</span>
            <span class="pin-label">📍 ${cityName}</span>
          </div>
        `,
        iconSize: null,
        iconAnchor: [20, 16]
      });

      const marker = L.marker([coords.lat, coords.lng], { icon }).addTo(layerGroup);
      marker.on('click', () => {
        onSelectGroup(`📍 City: ${cityName}`, rugs);
        mapInstance.flyTo([coords.lat, coords.lng], 7, { duration: 1.2 });
      });
    });

    // B. Region Pins & Zones
    Object.entries(regionGroups).forEach(([regionName, rugs]) => {
      const config = REGION_COORDS[regionName];
      if (!config) return;

      const circle = L.circle([config.lat, config.lng], {
        color: config.color || '#3b82f6',
        fillColor: config.color || '#3b82f6',
        fillOpacity: 0.15,
        radius: config.radius || 150000,
        weight: 2,
        dashArray: '6, 8'
      }).addTo(layerGroup);

      const icon = L.divIcon({
        className: 'region-map-pin',
        html: `
          <div class="region-badge" style="border-color: ${config.color || '#3b82f6'};">
            <span class="region-pulse" style="background: ${config.color || '#3b82f6'};"></span>
            <span class="region-label">${regionName}</span>
            <span class="region-count">${rugs.length}</span>
          </div>
        `,
        iconSize: [120, 30],
        iconAnchor: [60, 15]
      });

      const marker = L.marker([config.lat, config.lng], { icon }).addTo(layerGroup);
      const handleClick = () => {
        onSelectGroup(`Region: ${regionName}`, rugs);
        mapInstance.flyTo([config.lat, config.lng], 5, { duration: 1.2 });
      };

      circle.on('click', handleClick);
      marker.on('click', handleClick);
    });

    // C. Country Pins
    Object.entries(countryGroups).forEach(([countryName, rugs]) => {
      const coords = COUNTRY_COORDS[countryName];
      if (!coords) return;

      const icon = L.divIcon({
        className: 'country-map-pin',
        html: `
          <div class="country-badge">
            <span class="country-flag">🌐</span>
            <span class="country-label">${countryName}</span>
            <span class="country-count">${rugs.length}</span>
          </div>
        `,
        iconSize: [110, 30],
        iconAnchor: [55, 15]
      });

      const marker = L.marker([coords.lat, coords.lng], { icon }).addTo(layerGroup);
      marker.on('click', () => {
        onSelectGroup(`Country: ${countryName}`, rugs);
        mapInstance.flyTo([coords.lat, coords.lng], 4.5, { duration: 1.2 });
      });
    });
  });
</script>

<div class="map-container" bind:this={mapElement}></div>

<style>
  .map-container { 
    flex: 1; 
    height: 100%; 
    background: #f8fafc; 
  }

  /* OVERRIDE LEAFLET CONTAINER DEFAULT SIZES */
  :global(.custom-map-pin),
  :global(.region-map-pin),
  :global(.country-map-pin) {
    background: transparent !important;
    border: none !important;
    width: auto !important;
    height: auto !important;
  }

  /* City Pins */
  :global(.pin-badge) {
    display: inline-flex; 
    align-items: center;
    /* background: #ffffff; */
    border-radius: 20px; 
    padding: 3px 10px 3px 4px; 
    border: 2px solid #ffffff;
    box-shadow: 0 4px 10px rgba(9, 20, 147, 0.25); 
    cursor: pointer;
    white-space: nowrap;
    width: max-content;
  }
  
  :global(.pin-count) { 
    background: #626aff; 
    color: #ffffff; 
    font-size: 0.75rem; 
    font-weight: 700; 
    width: 22px; 
    height: 22px; 
    border-radius: 50%; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    margin-right: 6px; 
    flex-shrink: 0;
  }

  :global(.pin-label) { 
    font-size: 0.75rem; 
    font-weight: 600; 
    white-space: nowrap; 
    color: #0f172a;
  }

  /* Region Pins */
  :global(.region-badge) {
    display: inline-flex; 
    align-items: center; 
    background: rgba(255, 255, 255, 0.95);
    color: #1e293b; 
    border-radius: 16px; 
    padding: 4px 8px; 
    border: 2px dashed #64748b;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15); 
    cursor: pointer; 
    backdrop-filter: blur(4px);
    white-space: nowrap;
    width: max-content;
  }

  :global(.region-pulse) { 
    width: 8px; 
    height: 8px; 
    border-radius: 50%; 
    margin-right: 6px; 
    display: inline-block; 
    flex-shrink: 0;
  }

  :global(.region-label) { 
    font-size: 0.75rem; 
    font-weight: 700; 
    white-space: nowrap; 
    margin-right: 6px; 
  }

  :global(.region-count) { 
    font-size: 0.7rem; 
    background: #e2e8f0; 
    padding: 1px 6px; 
    border-radius: 10px; 
    font-weight: 600; 
    flex-shrink: 0;
  }

  /* Country Pins */
  :global(.country-badge) {
    display: inline-flex; 
    align-items: center; 
    background: #0062ff; 
    color: #f8fafc;
    border-radius: 14px; 
    padding: 4px 8px; 
    border: 1px solid #ffffff;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2); 
    cursor: pointer; 
    gap: 4px;
    white-space: nowrap;
    width: max-content;
  }

  :global(.country-flag) { font-size: 0.75rem; flex-shrink: 0; }
  :global(.country-label) { font-size: 0.75rem; font-weight: 600; white-space: nowrap; }
  :global(.country-count) { font-size: 0.7rem; background: #00214e; color: #ffffff; padding: 1px 6px; border-radius: 8px; font-weight: 700; flex-shrink: 0; }
</style>