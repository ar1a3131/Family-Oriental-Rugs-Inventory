<!-- src/lib/ViewNav.svelte -->
<script>
  import { page } from '$app/stores';
</script>

<nav class="view-nav">
  <a href="/" class="nav-btn" class:active={$page.url.pathname === '/'}>
    🗺️ Map View
  </a>
  <a href="/colors" class="nav-btn" class:active={$page.url.pathname === '/colors'}>
    🎨 Colors
  </a>
  <a href="/styles" class="nav-btn" class:active={$page.url.pathname === '/styles'}>
    🏷️ Styles
  </a>
</nav>

<style>
  .view-nav {
    display: flex;
    gap: 0.35rem;
    margin-bottom: 1.25rem;
    background: #f1f5f9;
    padding: 4px;
    border-radius: 8px;
  }

  .nav-btn {
    flex: 1;
    text-align: center;
    padding: 0.5rem 0.25rem;
    font-size: 0.78rem;
    font-weight: 600;
    text-decoration: none;
    color: #64748b;
    border-radius: 6px;
    transition: all 0.15s ease;
  }

  .nav-btn:hover {
    color: #0f172a;
    background: rgba(255, 255, 255, 0.6);
  }

  .nav-btn.active {
    background: #ffffff;
    color: #0f172a;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
</style>