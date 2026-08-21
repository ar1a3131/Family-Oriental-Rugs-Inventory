<script>
  import { base } from '$app/paths';
  import { categorizeRugs } from '$lib/categorizeRugs.js';
  import RugCard from '$lib/components/RugCard.svelte';
  import RugMap from '$lib/components/RugMap.svelte';
  import ViewNav from '$lib/ViewNav.svelte';

  // Reactive state using Svelte 5 runes
  let rugData = $state([]);
  let selectedHeader = $state(null);
  let selectedRugs = $state([]);
  let unspecifiedRugs = $state([]);
  let activeSidebarTab = $state('explorer');

  let groups = $state({ cityGroups: {}, regionGroups: {}, countryGroups: {} });

  // 1. Fetch data on load
  $effect(() => {
    async function fetchData() {
      const res = await fetch(`${base}/rugs_with_image_analysis.json`);
      rugData = await res.json();
      
      const parsed = categorizeRugs(rugData);
      groups = parsed;
      unspecifiedRugs = parsed.unmapped;
    }
    
    fetchData();
  });

  // Handler for map pin clicks
  function handleSelectGroup(header, rugs) {
    activeSidebarTab = 'explorer';
    selectedHeader = header;
    selectedRugs = rugs;
  }
</script>

<svelte:head>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <title>Rug Collection - Map Exploration</title>
</svelte:head>

<div class="layout">
  <aside class="sidebar">
    <header class="sidebar-header">
      <h2>Our Rug Inventory 𖢫</h2>
      
      <div class="link-group">
        <a 
          href="https://baseerorientalrugs.com" 
          target="_blank" 
          rel="noopener noreferrer" 
          class="store-link-btn"
          title="Visit Baseer Oriental Rugs Store"
        >
          <span>🌐 Family Business</span>
          <span class="external-arrow">↗</span>
        </a>

        <a 
          href="https://github.com/ar1a3131/Family-Oriental-Rugs-Inventory" 
          target="_blank" 
          rel="noopener noreferrer" 
          class="store-link-btn"
          title="Visit my GitHub repo"
        >
          <span>👾 Project GitHub Repo</span>
          <span class="external-arrow">↗</span>
        </a>
      </div>

      <ViewNav />
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

  <!-- Encapsulated Interactive Map -->
  <RugMap 
    cityGroups={groups.cityGroups} 
    regionGroups={groups.regionGroups} 
    countryGroups={groups.countryGroups} 
    onSelectGroup={handleSelectGroup} 
  />
</div>

<style>
  :global(body) { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8fafc; }
  .layout { display: flex; height: 100vh; }
  .sidebar { width: 340px; padding: 1.5rem; overflow-y: auto; border-right: 1px solid #e2e8f0; background: #ffffff; flex-shrink: 0; display: flex; flex-direction: column; }
  
  .sidebar-header h2 { margin: 0; font-size: 1.2rem; color: #0f172a; }
  .subtitle { color: #64748b; font-size: 0.85rem; margin: 0.25rem 0 1rem 0; }



  /* :global(body) { 
    margin: 0; 
    padding: 0; 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
    background: #f8fafc; 
  } */

  /* .layout { 
    display: flex; 
    height: 100vh; 
  } */

  /* Consolidated Sidebar Rules */
  /* .sidebar { 
    width: 380px; 
    padding: 1.25rem; 
    overflow-y: auto; 
    border-right: 1px solid #e2e8f0; 
    background: #ffffff; 
    z-index: 10; 
    display: flex; 
    flex-direction: column; 
    flex-shrink: 0;
  } */





  /* .sidebar-header h2 { 
    margin: 0; 
    font-size: 1.2rem; 
    color: #0f172a; 
  } */

  .subtitle { 
    color: #64748b; 
    font-size: 0.85rem; 
    margin: 0.4rem 0 0.8rem 0; 
  }

  .link-group {
  display: flex;
  gap: 0.5rem;
  margin: 0.5rem 0 1rem 0;
  width: 100%;
}

  /* Store & GitHub Link Buttons */
  .store-link-btn {
    display: inline-flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.3rem;
    margin: 0.4rem 0;
    padding: 0.5rem 0.5rem;
    font-size: 0.78rem;
    font-weight: 600;
    color: #1e293b;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    text-decoration: none;
    transition: all 0.15s ease;
    width: fit-content;
  }

  .store-link-btn:hover {
    background: #f1f5f9;
    border-color: #94a3b8;
    color: #0284c7;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .external-arrow {
    font-size: 0.8rem;
    color: #64748b;
    transition: transform 0.15s ease;
  }

  .store-link-btn:hover .external-arrow {
    transform: translate(1px, -1px);
    color: #0284c7;
  }

  /* Sidebar Navigation Tabs */
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

  /* Results Section */
  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #f1f5f9;
  }

  .results-header h3 { 
    margin: 0; 
    font-size: 1rem; 
    color: #0f172a; 
  }

  .results-count { 
    font-size: 0.75rem; 
    background: #e2e8f0; 
    color: #334155; 
    padding: 2px 8px; 
    border-radius: 12px; 
    font-weight: 600; 
  }

  .warning-count { 
    background: #ffedd5; 
    color: #c2410c; 
  }

  .rug-grid { 
    display: flex; 
    flex-direction: column; 
    gap: 1rem; 
  }

  .hint-box { 
    background: #f8fafc; 
    border: 1px solid #e2e8f0; 
    padding: 1rem; 
    border-radius: 8px; 
    font-size: 0.825rem; 
    color: #475569; 
    line-height: 1.6; 
  }

  .hint-box h4 { 
    margin: 0 0 0.5rem 0; 
    color: #1e293b; 
  }
</style>