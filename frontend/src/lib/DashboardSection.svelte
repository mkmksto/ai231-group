<script lang="ts">
  export let title: string;
  export let sectionId: string;
  export let icon: any;

</script>

<section class="dashboard-section" id={sectionId}>
  <div class="section-content">
    <slot>Fallback content if no slot is provided.</slot>
  </div>
</section>

<style>
  .dashboard-section {
    width: 100%;
    margin-bottom: 0;
    background-color: transparent;
    border: none;
    overflow: visible;
  }

  .section-content {
    padding: 0;
    color: #1a1a1a;
    background-color: transparent;
  }

  .section-content > :global(p):first-child:last-child {
    color: #666;
    font-style: normal;
  }

  @media (max-width: 768px) {
    .section-content {
      padding: 2rem 1.5rem;
    }
  }
</style> 