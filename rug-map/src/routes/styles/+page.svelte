<!-- src/routes/styles/+page.svelte -->
<script>
  import { STYLE_CONFIG, getRugNormalizedStyles } from '$lib/styleMap.js';
  import ViewNav from '$lib/ViewNav.svelte';
  import { base } from '$app/paths'; 
  import RugCard from '$lib/components/RugCard.svelte';


  let rugData = $state([]);
  let selectedStyles = $state([]);
  let matchMode = $state('any'); // 'any' (OR logic) | 'all' (AND logic)

  // Fetch Data
  $effect(() => {
    async function loadData() {
      const res = await fetch(`${base}/rugs_with_image_analysis.json`);      
      rugData = await res.json();
    }
    loadData();
  });

  // Calculate rug counts per style key
  let styleCounts = $derived.by(() => {
    const counts = {};
    Object.keys(STYLE_CONFIG).forEach(key => (counts[key] = 0));

    rugData.forEach(rug => {
      const styles = getRugNormalizedStyles(rug);
      styles.forEach(sKey => {
        counts[sKey] = (counts[sKey] || 0) + 1;
      });
    });
    return counts;
  });

  // Derived filtered rug list
  let activeRugs = $derived.by(() => {
    if (selectedStyles.length === 0) return rugData;

    return rugData.filter(rug => {
      const rugStyles = getRugNormalizedStyles(rug);

      if (matchMode === 'all') {
        return selectedStyles.every(s => rugStyles.includes(s));
      } else {
        return selectedStyles.some(s => rugStyles.includes(s));
      }
    });
  });

  // Reassign state array to trigger Svelte 5 reactivity correctly
  function toggleStyle(styleKey) {
    if (selectedStyles.includes(styleKey)) {
      selectedStyles = selectedStyles.filter(s => s !== styleKey);
    } else {
      selectedStyles = [...selectedStyles, styleKey];
    }
  }

  function clearAll() {
    selectedStyles = [];
  }
</script>

<svelte:head>
  <title>Rug Collection - Style Exploration</title>
</svelte:head>

<div class="layout">
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2>Family Rug Inventory</h2>
      <p class="subtitle">Total Rugs: <strong>{rugData.length}</strong></p>
    </div>

    <!-- View Navigation -->
    <!-- <nav class="view-nav">
      <a href="/" class="nav-btn">🗺️ Map</a>
      <a href="/colors" class="nav-btn">🎨 Colors</a>
      <a href="/styles" class="nav-btn active">🏷️ Styles</a>
    </nav> -->
    <ViewNav />


    <!-- Filter Header & Controls -->
    <div class="filter-header">
      <h3>Filter Styles</h3>
      {#if selectedStyles.length > 0}
        <button class="clear-btn" onclick={clearAll}>Clear ({selectedStyles.length})</button>
      {/if}
    </div>

    <!-- Match Mode Switch (Only visible when >1 styles selected) -->
    {#if selectedStyles.length > 1}
      <div class="match-toggle">
        <span class="mode-label">Filter Logic:</span>
        <button 
          class="mode-btn" 
          class:active={matchMode === 'any'} 
          onclick={() => (matchMode = 'any')}
        >
          Match ANY
        </button>
        <button 
          class="mode-btn" 
          class:active={matchMode === 'all'} 
          onclick={() => (matchMode = 'all')}
        >
          Match ALL
        </button>
      </div>
    {/if}

    <!-- Style List -->
    <div class="style-palette">
      {#each Object.entries(STYLE_CONFIG) as [key, config]}
        {@const count = styleCounts[key] || 0}
        {@const isSelected = selectedStyles.includes(key)}
        <button 
          class="style-pill"
          class:active={isSelected}
          class:disabled={count === 0}
          disabled={count === 0}
          onclick={() => toggleStyle(key)}
        >
          <div class="checkbox" class:checked={isSelected}>
            {#if isSelected}✓{/if}
          </div>
          <span class="style-badge" style="background-color: {config.badgeColor};"></span>
          <span class="style-name">{config.label}</span>
          <span class="count">({count})</span>
        </button>
      {/each}
    </div>
  </aside>

  <main class="gallery-container">
    <header class="gallery-header">
      <div>
        <h2>Displaying {activeRugs.length} Rugs</h2>
        {#if selectedStyles.length > 0}
          <div class="active-chips">
            <span class="chip-label">Filtering by ({matchMode.toUpperCase()}):</span>
            {#each selectedStyles as key}
              <span class="active-chip" style="border-left: 4px solid {STYLE_CONFIG[key]?.badgeColor}">
                {STYLE_CONFIG[key]?.label || key}
                <button onclick={() => toggleStyle(key)}>✕</button>
              </span>
            {/each}
            <button class="clear-all-link" onclick={clearAll}>Clear Filters</button>
          </div>
        {:else}
          <p class="hint">Showing all rugs. Select one or more styles on the sidebar to filter.</p>
        {/if}
      </div>
    </header>

    <div class="rug-grid">
      {#each activeRugs as rug (rug.id || rug.name)}
        <RugCard {rug} />
      {/each}
    </div>
  </main>
</div>

<style>
  :global(body) { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8fafc; }
  .layout { display: flex; height: 100vh; }
  .sidebar { width: 340px; padding: 1.5rem; overflow-y: auto; border-right: 1px solid #e2e8f0; background: #ffffff; flex-shrink: 0; display: flex; flex-direction: column; }
  
  .sidebar-header h2 { margin: 0; font-size: 1.2rem; color: #0f172a; }
  .subtitle { color: #64748b; font-size: 0.85rem; margin: 0.25rem 0 1rem 0; }

  /* Navigation Tabs */
  /* .view-nav { display: flex; gap: 0.25rem; margin-bottom: 1.25rem; background: #f1f5f9; padding: 4px; border-radius: 8px; }
  .nav-btn { flex: 1; text-align: center; padding: 0.45rem 0.25rem; font-size: 0.78rem; font-weight: 600; text-decoration: none; color: #64748b; border-radius: 6px; }
  .nav-btn.active, .nav-btn:hover { background: #ffffff; color: #0f172a; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }

  .filter-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
  .filter-header h3 { margin: 0; font-size: 0.95rem; color: #1e293b; }
  .clear-btn { background: none; border: none; color: #0284c7; font-size: 0.75rem; font-weight: 600; cursor: pointer; padding: 0; }
  .clear-btn:hover { text-decoration: underline; } */

  /* Logic Toggle */
  .match-toggle { display: flex; align-items: center; gap: 0.3rem; background: #f8fafc; padding: 4px; border: 1px solid #e2e8f0; border-radius: 6px; margin-bottom: 0.75rem; }
  .mode-label { font-size: 0.7rem; font-weight: 600; color: #64748b; margin-right: auto; padding-left: 4px; }
  .mode-btn { border: none; background: transparent; font-size: 0.7rem; font-weight: 600; padding: 3px 8px; border-radius: 4px; color: #64748b; cursor: pointer; }
  .mode-btn.active { background: #0284c7; color: #ffffff; }

  /* Style Filter Buttons */
  .style-palette { display: flex; flex-direction: column; gap: 0.35rem; }
  .style-pill { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.65rem; border: 1px solid #e2e8f0; background: #fff; border-radius: 8px; cursor: pointer; font-size: 0.825rem; transition: all 0.15s ease; }
  .style-pill:hover { border-color: #cbd5e1; background: #f8fafc; }
  .style-pill.active { border-color: #0284c7; background: #f0f9ff; }
  .style-pill.disabled { opacity: 0.4; cursor: not-allowed; }

  .checkbox { width: 14px; height: 14px; border: 1px solid #cbd5e1; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 0.65rem; font-weight: bold; color: #0284c7; background: #fff; }
  .checkbox.checked { border-color: #0284c7; background: #e0f2fe; }

  .style-badge { width: 8px; height: 16px; border-radius: 3px; flex-shrink: 0; }
  .style-name { flex: 1; text-align: left; font-weight: 500; color: #334155; }
  .count { color: #94a3b8; font-size: 0.75rem; }

  /* Main Gallery View */
  .gallery-container { flex: 1; padding: 2rem; overflow-y: auto; }
  .gallery-header h2 { margin: 0 0 0.25rem 0; font-size: 1.25rem; color: #1e293b; }
  .hint { color: #64748b; font-size: 0.85rem; margin: 0 0 1.5rem 0; }

  .active-chips { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin: 0.75rem 0 1.5rem 0; }
  .chip-label { font-size: 0.75rem; color: #64748b; font-weight: 600; }
  .active-chip { display: inline-flex; align-items: center; gap: 0.4rem; background: #ffffff; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; }
  .active-chip button { border: none; background: transparent; color: #94a3b8; cursor: pointer; padding: 0; font-size: 0.75rem; }
  .active-chip button:hover { color: #ef4444; }
  .clear-all-link { background: none; border: none; color: #0284c7; font-size: 0.75rem; font-weight: 600; cursor: pointer; margin-left: 0.25rem; }

  .rug-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1.25rem; }
  .rug-card { background: #ffffff; border-radius: 10px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex; flex-direction: column; }
  .img-wrapper { height: 180px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; }
  .img-wrapper img { width: 100%; height: 100%; object-fit: cover; }
  .no-img { font-size: 0.75rem; color: #94a3b8; }
  
  .card-info { padding: 0.85rem; display: flex; flex-direction: column; flex: 1; }
  .card-info h4 { margin: 0 0 0.35rem 0; font-size: 0.85rem; color: #0f172a; font-weight: 600; line-height: 1.3; }
  .city-tag { font-size: 0.75rem; color: #0284c7; font-weight: 500; display: block; margin-bottom: 0.5rem; }
  
  .styles-list { display: flex; gap: 0.3rem; flex-wrap: wrap; margin-top: auto; }
  .chip { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.65rem; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; color: #475569; font-weight: 500; border: 1px solid transparent; }
  .chip.highlight { background: #e0f2fe; color: #0369a1; border-color: #bae6fd; }
  .chip-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
</style>