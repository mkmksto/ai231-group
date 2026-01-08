<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let navItems: Array<{ name: string; id: string; icon: any }> = [];
  export let activeSection: string | null = null;

  const dispatch = createEventDispatcher();

  function handleNavClick(sectionId: string) {
    dispatch('navclick', sectionId);
  }
</script>

<nav class="navbar">
  <ul class="nav-links">
    {#each navItems as item}
      <li>
        <button
          class="nav-link"
          class:active={activeSection === item.id}
          on:click={() => handleNavClick(item.id)}
          title={item.name}
        >
          <span class="link-text">{item.name}</span>
        </button>
      </li>
    {/each}
  </ul>
</nav>

<style>
  .navbar {
    position: fixed;
    top: 70px;
    left: 0;
    right: 0;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    background-color: #ffffff;
    /* border-bottom: 1px solid #e5e5e5; */
    z-index: 999;
    box-sizing: border-box;
  }

  .nav-links {
    list-style: none;
    display: flex;
    gap: 0;
    margin: 0;
    padding: 0;
    width: 100%;
    max-width: 1200px;
    justify-content: center;
  }

  .nav-link {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.5rem;
    color: #666;
    text-decoration: none;
    background: none;
    border: none;
    /* border-bottom: 1px solid transparent; */
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.9375rem;
    font-family: inherit;
    font-weight: 400;
    letter-spacing: -0.01em;
    border-radius: 15px;
    margin-top: 1rem;
  }

  .nav-link:hover {
    color: #1a1a1a;
    background-color: #f5f5f5;
  }

  .nav-link.active {
    color: #1a1a1a;
    background-color: #f5f5f5;
    border-bottom-color: #1a1a1a;
    font-weight: 500;
  }

  .link-text {
    text-align: center;
    display: block;
    font-family: inherit;
    white-space: nowrap;
  }

  @media (max-width: 768px) {
    .navbar {
      top: 60px;
    }

    .nav-link {
      padding: 0.875rem 1rem;
      font-size: 0.875rem;
    }
  }
</style> 