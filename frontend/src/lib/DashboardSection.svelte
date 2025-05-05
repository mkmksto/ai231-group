<script lang="ts">
  export let title: string;
  export let sectionId: string;
  export let icon: any; // SvelteComponent type would be better with more setup

</script>

<section class="dashboard-section" id={sectionId}>
  <div class="section-header">
    <div class="header-content">
      <svelte:component this={icon} weight="duotone" size="28" />
      <h2>{title}</h2>
    </div>
  </div>

  <div class="section-content">
    <slot>Fallback content if no slot is provided.</slot>
  </div>
</section>

<style>
  .dashboard-section {
    width: 100%;
    margin-bottom: 1rem; /* Space between sections */
    background-color: #F9FBFC; /* Light background */
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    overflow: hidden; /* Contain children */
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 1rem 1.5rem;
    background: linear-gradient(135deg, #b3e5fc 0%, #81d4fa 100%); /* Brighter blue gradient */
    border: none;
    border-bottom: 1px solid #CFD8DC; /* Subtle separator */
    text-align: left;
    box-sizing: border-box;
  }

  .header-content {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .section-header h2 {
    margin: 0;
    font-size: 1.4rem;
    color: #01579b; /* Darker blue */
  }

  .section-content {
    padding: 1.5rem;
    color: #37474F; /* Dark grey text */
    background-color: white; /* Pure white content area */
  }

  /* Fallback content styling */
  .section-content > :global(p):first-child:last-child {
      color: #78909C;
      font-style: italic;
  }

</style> 