<script>
  import { onMount } from 'svelte';

  let rugData = [];
  let colorGroups = {};
  let selectedColor = 'all';
  let activeRugs = [];

  onMount(async () => {
    const res = await fetch('/rugs_with_image_analysis.json');
    rugData = await res.json();

    // Group rugs by extracted colors
    const groups = {};
    rugData.forEach(rug => {
      const colors = rug.parsed_data?.colors || ['Uncategorized'];
      colors.forEach(color => {
        const normalized = color.toLowerCase().trim();
        groups[normalized] = groups[normalized] || [];
        groups[normalized].push(rug);
      });
    });

    colorGroups = groups;
    activeRugs = rugData;
  });

  function filterByColor(color) {
    selectedColor = color;
    if (color === 'all') {
      activeRugs = rugData;
    } else {
      activeRugs = colorGroups[color] || [];
    }
  }
</script>

<svelte:head>
  <title>Rug Collection - Color Exploration</title>
</svelte:head>

<div class="layout">
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2>Rug Collection Exploration</h2>
      <p class="subtitle">Total Rugs: <strong>{rugData.length}</strong></p>
    </div>

    <!-- Navigation Bar for Switching Views -->
    <nav class="view-nav">
      <a href="/" class="nav-btn">🗺️ Map View</a>
      <a href="/colors" class="nav-btn active">🎨 View by Color</a>
    </nav>

    <h3>Filter Palette</h3>
    <div class="color-palette">
      <button 
        class="color-pill {selectedColor === 'all' ? 'active' : ''}" 
        on:click={() => filterByColor('all')}
      >
        All Colors ({rugData.length})
      </button>

      {#each Object.entries(colorGroups) as [color, rugs]}
        <button 
          class="color-pill {selectedColor === color ? 'active' : ''}" 
          on:click={() => filterByColor(color)}
        >
          <span class="color-dot" style="background-color: {color};"></span>
          <span class="color-name">{color}</span>
          <span class="count">({rugs.length})</span>
        </button>
      {/each}
    </div>
  </aside>

  <main class="gallery-container">
    <header class="gallery-header">
      <h2>Displaying {selectedColor.toUpperCase()} Rugs ({activeRugs.length})</h2>
    </header>

    <div class="rug-grid">
      {#each activeRugs as rug}
        <div class="rug-card">
          <div class="img-wrapper">
            {#if rug.image_url}
              <img src={rug.image_url} alt={rug.name} loading="lazy" />
            {/if}
          </div>
          <div class="card-info">
            <h4>{rug.name || 'Rug Item'}</h4>
            <span class="city-tag">{rug.parsed_data?.city || 'Unknown Origin'}</span>
            {#if rug.parsed_data?.colors?.length}
              <div class="colors-list">
                {#each rug.parsed_data.colors as c}
                  <span class="chip">{c}</span>
                {/each}
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  </main>
</div>

<style>
  :global(body) { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8fafc; }
  .layout { display: flex; height: 100vh; }
  .sidebar { width: 340px; padding: 1.5rem; overflow-y: auto; border-right: 1px solid #e2e8f0; background: #ffffff; flex-shrink: 0; }
  
  .sidebar-header h2 { margin: 0; font-size: 1.25rem; color: #0f172a; }
  .subtitle { color: #64748b; font-size: 0.85rem; margin: 0.25rem 0 1rem 0; }

  /* Navigation Tabs */
  .view-nav { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; background: #f1f5f9; padding: 4px; border-radius: 8px; }
  .nav-btn { flex: 1; text-align: center; padding: 0.5rem; font-size: 0.85rem; font-weight: 600; text-decoration: none; color: #64748b; border-radius: 6px; }
  .nav-btn.active, .nav-btn:hover { background: #ffffff; color: #0f172a; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }

  /* Color Palette Filter Buttons */
  .color-palette { display: flex; flex-direction: column; gap: 0.5rem; }
  .color-pill { display: flex; align-items: center; gap: 0.5rem; padding: 0.6rem 0.8rem; border: 1px solid #e2e8f0; background: #fff; border-radius: 8px; cursor: pointer; font-size: 0.85rem; text-transform: capitalize; transition: all 0.2s; }
  .color-pill:hover, .color-pill.active { border-color: #2563eb; background: #eff6ff; }
  .color-dot { width: 14px; height: 14px; border-radius: 50%; border: 1px solid rgba(0,0,0,0.1); flex-shrink: 0; }
  .color-name { flex: 1; text-align: left; font-weight: 500; }
  .count { color: #94a3b8; font-size: 0.75rem; }

  /* Main Gallery View */
  .gallery-container { flex: 1; padding: 2rem; overflow-y: auto; }
  .gallery-header h2 { margin: 0 0 1.5rem 0; font-size: 1.25rem; color: #1e293b; }
  
  .rug-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1.25rem; }
  .rug-card { background: #ffffff; border-radius: 10px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
  .img-wrapper { height: 180px; background: #f1f5f9; }
  .img-wrapper img { width: 100%; height: 100%; object-fit: cover; }
  .card-info { padding: 0.85rem; }
  .card-info h4 { margin: 0 0 0.35rem 0; font-size: 0.85rem; color: #0f172a; font-weight: 600; line-height: 1.3; }
  .city-tag { font-size: 0.75rem; color: #2563eb; font-weight: 500; display: block; margin-bottom: 0.5rem; }
  .colors-list { display: flex; gap: 0.25rem; flex-wrap: wrap; }
  .chip { font-size: 0.65rem; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; color: #475569; text-transform: capitalize; }
</style>