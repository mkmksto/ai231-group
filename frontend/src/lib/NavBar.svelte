<script lang="ts">
  import { Brain, Heartbeat, Stethoscope, Virus, Eye, Bandaids, Dna, Bone, List } from 'phosphor-svelte';
  import { createEventDispatcher } from 'svelte';

  // Define navigation items with corresponding icons and section IDs
  export let navItems = [
    { name: "Brain & Neuro", id: "brain-neuro", icon: Brain },
    { name: "Cancer", id: "cancer", icon: Bandaids }, // Placeholder icon
    { name: "Cardio", id: "cardio", icon: Heartbeat },
    { name: "Respiratory", id: "respiratory", icon: Stethoscope }, // Placeholder icon
    { name: "Ophthalmology", id: "ophthalmology", icon: Eye },
    { name: "Gastro", id: "gastro", icon: Bandaids }, // Placeholder icon
    { name: "Infectious", id: "infectious", icon: Virus },
    { name: "Genetic", id: "genetic", icon: Dna },
    { name: "Radiology", id: "radiology", icon: Bone },
  ];

  export let activeSection: string | null = null; // Passed from parent to highlight active item

  const dispatch = createEventDispatcher();

  // Dispatch the clicked section ID to the parent
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
          <svelte:component this={item.icon} weight="duotone" size="28" />
          <span class="link-text">{item.name}</span>
        </button>
      </li>
    {/each}
  </ul>
  <button class="mobile-menu-button" on:click={() => dispatch('togglemenu')}>
      <List size="28" />
  </button>
</nav>

<style>
  .navbar {
    position: fixed;
    top: 50px;
    left: 0;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between; /* Space out logo, links, menu button */
    padding: 0.5rem 1.5rem;
    background-color: transparent;
    color: white;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    z-index: 1100; /* Above dashboard content */
    box-sizing: border-box;
  }

  .nav-links {
    list-style: none;
    display: flex;
    gap: 0.2rem; /* Reduced gap */
    margin: 0;
    padding: 0;
  }

  .nav-link {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.3rem;
    width: 8.5rem;
    height: 3.5rem;
    min-width: 7rem;
    max-width: 10rem;
    min-height: 3rem;
    max-height: 4rem;
    color: white;
    text-decoration: none;
    background: none;
    border: none;
    cursor: pointer;
    border-radius: 6px;
    transition: background-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    font-size: clamp(0.7rem, 0.9vw, 1rem);
    font-family: inherit;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 0 0.5rem;
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 
        inset 1px 1px 1px rgba(255, 255, 255, 0.5),
        inset -1px -1px 1px rgba(0, 0, 0, 0.1),
        1px 1px 2px rgba(0, 0, 0, 0.2);
  }

  .nav-link:hover {
    background-color: rgba(255, 255, 255, 0.2);
    box-shadow: 
        inset 1px 1px 2px rgba(255, 255, 255, 0.6), 
        inset -1px -1px 2px rgba(0, 0, 0, 0.15), 
        1px 1px 3px rgba(0, 0, 0, 0.25); /* Slightly enhance shadow on hover */
  }

  .nav-link.active {
    background-color: rgba(255, 255, 255, 0.1); /* Less intense background when active */
    font-weight: bold;
    /* "Pressed" effect for active button */
    box-shadow: 
        inset 1px 1px 1px rgba(0, 0, 0, 0.2), /* Inner shadow darker */
        inset -1px -1px 1px rgba(255, 255, 255, 0.4); /* Inner highlight opposite */
    border-color: rgba(0,0,0, 0.15);
  }

  .link-text {
    width: 100%;
    text-align: center;
    font-size: inherit;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
    font-family: inherit;
    word-break: break-word;
    white-space: normal;
    line-height: 1.1;
  }

  .mobile-menu-button {
    display: none; /* Hidden by default, shown on mobile */
    background: none;
    border: none;
    color: white;
    cursor: pointer;
  }

  /* Responsive adjustments */
  @media (max-width: 1024px) {
      .link-text {
          display: none; /* Hide text on smaller screens */
      }
      .nav-link {
          padding: 0.5rem; /* Adjust padding when text is hidden */
      }
      .nav-links {
          gap: 0.1rem;
      }
  }

   @media (max-width: 768px) {
     .nav-links {
       display: none; /* Hide links entirely on very small screens */
       /* Consider implementing a dropdown menu triggered by the button */
     }
     .mobile-menu-button {
       display: block; /* Show menu button */
     }
     .navbar {
         padding: 0.5rem 1rem;
     }
   }
</style> 