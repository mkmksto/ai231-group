<script lang="ts">
  import { Bandaids, Bone, Brain, Dna, Eye, Heartbeat, Stethoscope, Virus } from 'phosphor-svelte';
  import BrainTumorSection from './lib/BrainTumorSection.svelte';
  import CredentialCard from './lib/CredentialCard.svelte';
  import DashboardSection from './lib/DashboardSection.svelte';
  import NavBar from './lib/NavBar.svelte';
// Icons for sections
  import AnimatedBackground from './lib/AnimatedBackground.svelte'; // <-- Import background

  // --- Navigation --- 
  const navItems = [
    { name: "Brain Tumor Classifier", id: "brain-neuro", icon: Brain }, // Renamed for clarity
    { name: "Cancer Diagnostics", id: "cancer", icon: Bandaids },
    { name: "Cardiology AI", id: "cardio", icon: Heartbeat },
    { name: "Respiratory Analysis", id: "respiratory", icon: Stethoscope },
    { name: "Ophthalmology Insights", id: "ophthalmology", icon: Eye },
    { name: "Gastroenterology Tools", id: "gastro", icon: Bandaids },
    { name: "Infectious Disease AI", id: "infectious", icon: Virus },
    { name: "Genetic Sequencing AI", id: "genetic", icon: Dna },
    { name: "Radiology Assistant", id: "radiology", icon: Bone },
  ];

  let activeSection: string | null = navItems[0].id; // Default to first section

  // --- User State (Simplified for Demo) ---
  // In a real app, this would come from auth state management
  interface User {
    name: string;
    email: string;
    credentials?: string; // Optional for login display
    role: string;
  }

  // let currentUser: User | null = { name: "Dr. Michael Quinto", email: "mquinto@diagnostech.ai", credentials: "MD, NeuroAI Specialist" }; // Example logged-in user
  let currentUser: User | null = null

  function handleLogout() {
    currentUser = null; // Set user to null on logout
    // TODO: Add actual logout logic (clear tokens, redirect, etc.)
    alert("Logged out successfully.");
  }

  // // Placeholder function to handle login attempt
  // function handleContinueWithGoogle(event: CustomEvent<{ email: string; pass: string }>) {
  //   console.log("handleContinueWithGoogle");
  //   setTimeout(() => {
  //     window.location.href = "/api/auth/google/login";
  //   }, 100);

  //   // const { email, pass } = event.detail;
  //   // console.log(`Simulating login for: ${email}`);
  //   // TODO: Replace with actual API call to backend for authentication
  //   // For demo: Log in anyone who tries
  //   // if (email && pass) {
  //   //   currentUser = {
  //   //     name: "Demo User", // Replace with name from backend
  //   //     email: email,
  //   //     credentials: "Demo Credentials" // Replace with credentials from backend if available
  //   //   };
  //   //   alert(`Logged in as ${currentUser.name} (simulated).`);
  //   // } else {
  //   //   alert("Login failed (simulated - need email/password).");
  //   // }
  // }

  // // Placeholder function to handle registration attempt
  // function handleRegister(event: CustomEvent<{ name: string; email: string; pass: string; credentials?: string }>) {
  //   const { name, email, pass, credentials } = event.detail;
  //   console.log(`Simulating registration for: ${name} <${email}>`);
  //   // TODO: Replace with actual API call to backend for registration
  //   // For demo: Register and log in the user immediately
  //   if (name && email && pass) {
  //     currentUser = { name, email, credentials };
  //     alert(`Registered and logged in as ${currentUser.name} (simulated).`);
  //   } else {
  //     alert("Registration failed (simulated - need name/email/password).");
  //   }
  // }

  async function getMe() {
    // this is where we get the user's information from the backend
    // then we conditionally render whether the person is logged in or not  based on the response
    // if no response / error, then we render the login page / footer
    // if with response, then we render their user info
    const response = await fetch("/api/me", {
      method: "GET",
      credentials: "include",
    });
    const data = await response.json() as User;
    console.log(data);
    currentUser = data;
  }

  getMe();


  // --- Navigation Handler ---
  function handleNavClick(event: CustomEvent<string>) {
    activeSection = event.detail; // Update active section based on NavBar click
    // Optional: Scroll to top of content area when nav changes
    const contentArea = document.querySelector('.dashboard-content');
    if (contentArea) {
      // Use a small timeout to ensure the content is rendered before scrolling
      setTimeout(() => { 
        contentArea.scrollTo({ top: 0, behavior: 'auto' }); 
      }, 0);
    }
  }

</script>

<div class="app-container">
  <AnimatedBackground /> <!-- <-- Render background component -->
  <h1 class="app-title">DiagnosTech-AI</h1> 
  <NavBar {navItems} {activeSection} on:navclick={handleNavClick} /> 

  <main class="dashboard-content">
    <!-- Render only the active section -->
    {#each navItems as item (item.id)}
      {#if activeSection === item.id}
        <DashboardSection title={item.name} sectionId={item.id} icon={item.icon}>
          <!-- Slot content for each section -->
          {#if item.id === 'brain-neuro'}
            <!-- Embed the brain tumor classifier here -->
            <BrainTumorSection />
          {:else}
            <!-- Placeholder content for other sections -->
            <div class="placeholder-content">
              <p>AI applications for <strong>{item.name}</strong> will be displayed here.</p>
              <p><em>(Content under development)</em></p>
              <!-- Example of potential card structure 
              <div class="ai-use-case-card">
                <h4>Condition Detection Example</h4>
                <p>Using AI to analyze {item.name.toLowerCase().includes('radiology') ? 'images' : 'data'} for early detection of [Specific Condition].</p>
              </div>
              -->
            </div>
          {/if}
        </DashboardSection>
      {/if} 
    {/each}
  </main>

  <CredentialCard 
    user={currentUser} 
    on:logout={handleLogout}
  />
</div>

<style>
  /* --- Global Styles / Resets --- */
  :global(body) {
    margin: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Modern sans-serif */
    color: #333;
    overflow-x: hidden; /* Prevent horizontal scrollbars potentially caused by fixed elements */
    min-height: 100vh; 
    /* Background is now handled by the AnimatedBackground component */
  }

  :global(h1, h2, h3, h4, h5, h6) {
    font-family: 'Roboto', sans-serif; /* Optional: Different font for headers */
    color: #1A237E; /* Dark indigo */
  }

  .app-title {
    position: fixed;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    margin: 0;
    padding: 0.5rem 0;
    font-size: 1.5rem; /* Adjust size as needed */
    color: #007AFF; /* Match navbar blue */
    width: 100%;
    text-align: center;
    background-color: rgba(10, 25, 47, 0.85); /* Dark blue semi-transparent */
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
    z-index: 1300; /* Highest z-index */
    font-weight: 600;
    color: #ccd6f6; /* Lighter text color for dark bg */
  }

  .app-container {
    display: flex;
    flex-direction: column;
    position: relative; /* Ensure z-index stacking context */
  }

  .dashboard-content {
    padding-top: 100px; 
    padding-bottom: 100px;
    max-width: 1100px;
    margin: 0 auto;
    padding-left: 1rem;
    padding-right: 1rem;
    width: 100%;
    box-sizing: border-box;
    overflow-y: auto;
    height: calc(100vh - 100px - 100px); /* Adjust if CredentialCard height changes */
    position: relative; /* Ensure content stays above background */
    z-index: 10;
  }

  .placeholder-content {
    padding: 2rem;
    text-align: center;
    background-color: #f5f7fa;
    border-radius: 6px;
    border: 1px dashed #ccc;
    color: #6c757d;
  }

  .placeholder-content p {
      margin-bottom: 0.5rem;
  }

   /* Basic styling for potential AI use case cards */
   .ai-use-case-card {
      background-color: white;
      padding: 1rem;
      border-radius: 6px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
      margin-top: 1rem;
      border-left: 4px solid #007AFF;
      text-align: left;
   }
    .ai-use-case-card h4 {
        margin-top: 0;
        color: #0056b3;
    }

</style>