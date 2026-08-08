<!-- src/routes/+page.svelte -->
<script>
  import { CITY_COORDS } from '$lib/cityCoords.js';
  import { REGION_COORDS } from '$lib/regionCoords.js';
  import { COUNTRY_COORDS } from '$lib/countryCoords.js';
  import RugCard from '$lib/components/RugCard.svelte';

  // 1. Reactive state using Svelte 5 runes
  let rugData = $state([]);
  let selectedHeader = $state(null);
  let selectedRugs = $state([]);
  let unspecifiedRugs = $state([]);
  let activeSidebarTab = $state('explorer'); // 'explorer' | 'unspecified'

  let mapElement = $state(null);
  let map = $state(null);

  // Helper function to find matching coordinate key
  function findMatchingCoordKey(targetStr, coordsObject) {
    if (!targetStr || typeof targetStr !== 'string') return null;
    const cleanTarget = targetStr.trim().toLowerCase();
    
    // Direct lookup
    if (coordsObject[targetStr]) return targetStr;

    // Fuzzy string match
    return Object.keys(coordsObject).find(key => 
      cleanTarget.includes(key.toLowerCase()) || key.toLowerCase().includes(cleanTarget)
    ) || null;
  }

  // 2. Data fetching & Map render effect
  $effect(() => {
    let mapInstance = null;
    if (!mapElement) return;

    async function initMap() {
      const res = await fetch('/rugs_with_image_analysis.json');
      const data = await res.json();
      rugData = data;

      const L = await import('leaflet');

      // Define standard world bounds [Southwest, Northeast]
      const worldBounds = L.latLngBounds(
        L.latLng(-90, -180),
        L.latLng(90, 180)
      );

      // Initialize map with globe boundaries
      mapInstance = L.map(mapElement, { 
        zoomControl: false,
        minZoom: 2.5,
        maxBounds: worldBounds,
        maxBoundsViscosity: 1.0 // Rigid boundaries (prevents panning into empty gray space)
      }).setView([34.0, 48.0], 4);
      
      map = mapInstance;

      L.control.zoom({ position: 'topright' }).addTo(mapInstance);

      // CARTO Tile Layer with noWrap enabled
      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19,
        noWrap: true,       // Prevents horizontal repeating of tiles
        bounds: worldBounds // Constrains tile requests to the world area
      }).addTo(mapInstance);

      // Categorization Buckets
      const cityGroups = {};
      const regionGroups = {};
      const countryGroups = {};
      const unmapped = [];

      // Hierarchy Categorization: City -> Region -> Country -> Unspecified
      data.forEach(rug => {
        const parsed = rug.parsed_data || {};
        const rawCity = parsed.city && parsed.city !== 'Unknown' ? parsed.city : null;
        const rawRegion = parsed.region || parsed.regional_style || null;
        const rawCountry = parsed.country || parsed.country_of_origin || null;

        // 1. Try City
        const matchedCity = rawCity ? findMatchingCoordKey(rawCity, CITY_COORDS) : null;
        if (matchedCity) {
          cityGroups[matchedCity] = cityGroups[matchedCity] || [];
          cityGroups[matchedCity].push(rug);
          return;
        }

        // 2. Try Region
        const matchedRegion = rawRegion ? findMatchingCoordKey(rawRegion, REGION_COORDS) : null;
        if (matchedRegion) {
          regionGroups[matchedRegion] = regionGroups[matchedRegion] || [];
          regionGroups[matchedRegion].push(rug);
          return;
        }

        // 3. Try Country
        const matchedCountry = rawCountry ? findMatchingCoordKey(rawCountry, COUNTRY_COORDS || {}) : null;
        if (matchedCountry) {
          countryGroups[matchedCountry] = countryGroups[matchedCountry] || [];
          countryGroups[matchedCountry].push(rug);
          return;
        }

        // 4. Fallback: Unspecified
        unmapped.push(rug);
      });

      unspecifiedRugs = unmapped;

      // --- Render Markers ---

      // A. Render City Pins
      Object.entries(cityGroups).forEach(([cityName, rugs]) => {
        const coords = CITY_COORDS[cityName];
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

        const marker = L.marker([coords.lat, coords.lng], { icon }).addTo(mapInstance);
        marker.on('click', () => {
          activeSidebarTab = 'explorer';
          selectedHeader = `📍 City: ${cityName}`;
          selectedRugs = rugs;
          mapInstance.flyTo([coords.lat, coords.lng], 7, { duration: 1.2 });
        });
      });

      // B. Render Region Pins & Zones
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
        }).addTo(mapInstance);

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

        const marker = L.marker([config.lat, config.lng], { icon }).addTo(mapInstance);
        const handleClick = () => {
          activeSidebarTab = 'explorer';
          selectedHeader = `Region: ${regionName}`;
          selectedRugs = rugs;
          mapInstance.flyTo([config.lat, config.lng], 5, { duration: 1.2 });
        };

        circle.on('click', handleClick);
        marker.on('click', handleClick);
      });

      // C. Render Country Pins
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

        const marker = L.marker([coords.lat, coords.lng], { icon }).addTo(mapInstance);
        marker.on('click', () => {
          activeSidebarTab = 'explorer';
          selectedHeader = `Country: ${countryName}`;
          selectedRugs = rugs;
          mapInstance.flyTo([coords.lat, coords.lng], 4.5, { duration: 1.2 });
        });
      });
    }

    initMap();

    return () => {
      if (mapInstance) mapInstance.remove();
    };
  });
</script>

<svelte:head>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</svelte:head>

<div class="layout">
  <aside class="sidebar">
    <header class="sidebar-header">
      <h2>Rug Collection Exploration</h2>
      <p class="subtitle">Total Rugs: <strong>{rugData.length}</strong></p>
    </header>

    <!-- Sidebar Navigation Tabs -->
    <nav class="sidebar-tabs">
      <button 
        class="tab-btn" 
        class:active={activeSidebarTab === 'explorer'} 
        onclick={() => (activeSidebarTab = 'explorer')}
      >
        🗺️ Map Selection
      </button>

      <button 
        class="tab-btn warning-tab" 
        class:active={activeSidebarTab === 'unspecified'} 
        onclick={() => (activeSidebarTab = 'unspecified')}
      >
        ⚠️ Unspecified Rugs ({unspecifiedRugs.length})
      </button>
    </nav>

    <!-- TAB 1: Map Selection Results -->
    {#if activeSidebarTab === 'explorer'}
      {#if selectedHeader}
        <section class="results-container">
          <div class="results-header">
            <h3>{selectedHeader}</h3>
            <span class="results-count">{selectedRugs.length} items</span>
          </div>

          <div class="rug-grid">
            {#each selectedRugs as rug (rug.id || rug.name)}
              <RugCard {rug} />
            {/each}
          </div>
        </section>
      {:else}
        <div class="hint-box">
          <h4>Location Mapping Hierarchy:</h4>
          <p>📍 <strong>City Pins:</strong> Direct match by city coordinates.</p>
          <p>⭕ <strong>Region Zones:</strong> Fallback match by cultural region or style.</p>
          <p>🌐 <strong>Country Pins:</strong> Broad fallback by country of origin.</p>
          <p>⚠️ <strong>Unspecified Tab:</strong> Rugs without any valid origin data are excluded from the map and listed separately.</p>
        </div>
      {/if}

    <!-- TAB 2: Unspecified Rugs List -->
    {:else if activeSidebarTab === 'unspecified'}
      <section class="results-container">
        <div class="results-header">
          <h3>Unspecified Origins</h3>
          <span class="results-count warning-count">{unspecifiedRugs.length} items</span>
        </div>
        <p class="tab-description">These rugs lacked verifiable city, region, or country metadata and are excluded from the interactive map.</p>

        <div class="rug-grid">
          {#each unspecifiedRugs as rug (rug.id || rug.name)}
            <RugCard {rug} />
          {/each}
        </div>
      </section>
    {/if}
  </aside>

  <main class="map-container" bind:this={mapElement}></main>
</div>

<style>
  :global(body) { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  .layout { display: flex; height: 100vh; }
  
  .sidebar { 
    width: 400px; 
    padding: 1.25rem; 
    overflow-y: auto; 
    border-right: 1px solid #e2e8f0; 
    background: #ffffff; 
    z-index: 10; 
    display: flex; 
    flex-direction: column; 
  }

  .sidebar-header h2 { margin: 0; font-size: 1.2rem; color: #0f172a; }
  .subtitle { color: #64748b; font-size: 0.85rem; margin: 0.2rem 0 0.8rem 0; }

  /* Sidebar Tabs */
  .sidebar-tabs {
    display: flex;
    gap: 0.4rem;
    margin-bottom: 1rem;
    background: #f1f5f9;
    padding: 4px;
    border-radius: 8px;
  }

  .tab-btn {
    flex: 1;
    border: none;
    background: transparent;
    padding: 0.55rem 0.4rem;
    font-size: 0.78rem;
    font-weight: 600;
    color: #64748b;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.15s ease, color 0.15s ease;
  }

  .tab-btn.active {
    background: #ffffff;
    color: #0f172a;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .tab-btn.warning-tab.active {
    color: #c2410c;
    background: #fff7ed;
  }

  .tab-description {
    font-size: 0.8rem;
    color: #64748b;
    margin-bottom: 1rem;
    line-height: 1.4;
  }

  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #f1f5f9;
  }
  .results-header h3 { margin: 0; font-size: 1rem; color: #0f172a; }
  .results-count { font-size: 0.75rem; background: #e2e8f0; color: #334155; padding: 2px 8px; border-radius: 12px; font-weight: 600; }
  .warning-count { background: #ffedd5; color: #c2410c; }

  .rug-grid { display: flex; flex-direction: column; gap: 1rem; }

  .map-container { flex: 1; height: 100%; background: #f8fafc; }
  .hint-box { background: #f8fafc; border: 1px solid #e2e8f0; padding: 1rem; border-radius: 8px; font-size: 0.825rem; color: #475569; line-height: 1.6; }
  .hint-box h4 { margin: 0 0 0.5rem 0; color: #1e293b; }

  /* City Pins */
  :global(.custom-map-pin) { background: transparent; border: none; }
  :global(.pin-badge) {
    display: flex; align-items: center;
    border-radius: 20px; padding: 3px 10px 3px 4px; border: 2px solid #ffffff;
    box-shadow: 0 4px 10px rgba(9, 20, 147, 0.25); cursor: pointer;
  }
  
  :global(.pin-count) { background: #626aff; color: #d6d6d6; font-size: 0.75rem; font-weight: 700; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 6px; }
  :global(.pin-label) { font-size: 0.75rem; font-weight: 600; white-space: nowrap; }

  /* Region Pins */
  :global(.region-map-pin) { background: transparent; border: none; }
  :global(.region-badge) {
    display: flex; align-items: center; background: rgba(255, 255, 255, 0.95);
    color: #1e293b; border-radius: 16px; padding: 4px 8px; border: 2px dashed #64748b;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15); cursor: pointer; backdrop-filter: blur(4px);
  }
  :global(.region-pulse) { width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; display: inline-block; }
  :global(.region-label) { font-size: 0.75rem; font-weight: 700; white-space: nowrap; margin-right: 6px; }
  :global(.region-count) { font-size: 0.7rem; background: #e2e8f0; padding: 1px 6px; border-radius: 10px; font-weight: 600; }

  /* Country Pins */
  :global(.country-map-pin) { background: transparent; border: none; }
  :global(.country-badge) {
    display: flex; align-items: center; background: #0062ff; color: #f8fafc;
    border-radius: 14px; padding: 4px 8px; border: 1px solid #ffffff;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2); cursor: pointer; gap: 4px;
  }
  :global(.country-flag) { font-size: 0.75rem; }
  :global(.country-label) { font-size: 0.75rem; font-weight: 600; }
  :global(.country-count) { font-size: 0.7rem; background: #00214e; color: #ffffff; padding: 1px 6px; border-radius: 8px; font-weight: 700; }
</style>