<!-- src/lib/components/RugCard.svelte -->
<script>
  // 1. Accept props using the $props() rune
  let { rug = {} } = $props();

  // 2. Derive reactive values using the $derived() rune
  let parsed = $derived(rug.parsed_data || {});
  let title = $derived(rug.name || 'Untitled Traditional Rug');
  let imageUrl = $derived(rug.image_url || null);
  let city = $derived(parsed.city && parsed.city !== 'Unknown' ? parsed.city : null);
  let style = $derived(parsed.regional_style || parsed.region || 'Traditional');
  let colors = $derived(Array.isArray(parsed.colors) ? parsed.colors : []);
  let dimensions = $derived(parsed.dimensions || parsed.size || null);
  let material = $derived(parsed.material || null);

  // 3. Declare component state using the $state() rune
  let imageError = $state(false);
</script>

<article class="rug-card">
  <!-- Image Container with Fallback Handling -->
   <!-- <a 
      href={rug.product_url} 
      target="_blank" 
      rel="noopener noreferrer" 
      class="rug-card"
    > -->
    <div class="image-wrapper">
      {#if imageUrl && !imageError}
        <img 
          src={imageUrl} 
          alt={title} 
          loading="lazy" 
          onerror={() => (imageError = true)} 
        />
      {:else}
        <div class="image-placeholder">
          <span>📷 Image Unavailable</span>
        </div>
      {/if}
      
    </div>
    <!-- Detailed Metadata Content -->
    <div class="card-content">
      <h4 class="rug-title">{title}</h4>

      <div class="badge-group">
        {#if city}
          <span class="badge city-badge">📍 {city}</span>
        {/if}
        <span class="badge style-badge">🎨 {style}</span>
      </div>

      {#if dimensions || material}
        <dl class="meta-list">
          {#if dimensions}
            <div class="meta-item">
              <dt>Size:</dt>
              <dd>{dimensions}</dd>
            </div>
          {/if}
          {#if material}
            <div class="meta-item">
              <dt>Material:</dt>
              <dd>{material}</dd>
            </div>
          {/if}
        </dl>
      {/if}

      {#if colors.length > 0}
        <div class="color-section">
          <span class="color-label">Palette:</span>
          <div class="color-chips">
            {#each colors.slice(0, 4) as color}
              <span class="color-chip">{color}</span>
            {/each}
          </div>
        </div>
      {/if}
    </div>
    
  <!-- </a> -->
</article>

<style>
  .rug-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    overflow: hidden;
    text-decoration: none; /* Prevents default blue underline on text */
    color: inherit;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: flex;
    flex-direction: column;
  }

  .rug-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  }

  .image-wrapper {
    width: 100%;
    height: 180px;
    background: #f1f5f9;
    position: relative;
    overflow: hidden;
  }

  .image-wrapper img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .image-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    font-size: 0.8rem;
  }

  .card-content {
    padding: 0.85rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .rug-title {
    margin: 0;
    font-size: 0.9rem;
    font-weight: 600;
    color: #0f172a;
    line-height: 1.35;
  }

  .badge-group {
    display: flex;
    gap: 0.35rem;
    flex-wrap: wrap;
  }

  .badge {
    font-size: 0.7rem;
    font-weight: 500;
    padding: 2px 7px;
    border-radius: 4px;
  }

  .city-badge {
    background: #eff6ff;
    color: #1d4ed8;
  }

  .style-badge {
    background: #f8fafc;
    color: #475569;
    border: 1px solid #e2e8f0;
  }

  .meta-list {
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    font-size: 0.75rem;
  }

  .meta-item {
    display: flex;
    gap: 0.35rem;
  }

  .meta-item dt {
    color: #64748b;
    font-weight: 500;
  }

  .meta-item dd {
    margin: 0;
    color: #1e293b;
    font-weight: 600;
  }

  .color-section {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-top: 0.2rem;
  }

  .color-label {
    font-size: 0.7rem;
    color: #94a3b8;
  }

  .color-chips {
    display: flex;
    gap: 0.25rem;
    flex-wrap: wrap;
  }

  .color-chip {
    font-size: 0.65rem;
    background: #f1f5f9;
    color: #334155;
    padding: 1px 5px;
    border-radius: 3px;
    text-transform: capitalize;
  }
</style>