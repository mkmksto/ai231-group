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
    top: 40px; /* Adjusted down for the new title */
    left: 0;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between; /* Space out logo, links, menu button */
    padding: 0.5rem 1.5rem;
    background-color: #007AFF; /* Medical blue */
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
    align-items: center;
    gap: 0.6rem; /* Slightly increased gap */
    padding: 0.5rem 0.7rem; /* Adjusted padding */
    color: white;
    text-decoration: none;
    background: none;
    border: none;
    cursor: pointer;
    border-radius: 6px;
    transition: background-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out; /* Added shadow transition */
    font-size: 0.9rem; /* Slightly smaller font */

    /* Emboss Effect */
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 
        inset 1px 1px 1px rgba(255, 255, 255, 0.5), /* Inner highlight */
        inset -1px -1px 1px rgba(0, 0, 0, 0.1),  /* Inner shadow */
        1px 1px 2px rgba(0, 0, 0, 0.2);        /* Outer shadow */
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
      /* Hide text on smaller screens if needed, handled via media query */
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