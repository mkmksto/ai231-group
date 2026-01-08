<script lang="ts">
  import { Brain } from 'phosphor-svelte';
  import BrainTumorSection from './lib/BrainTumorSection.svelte';
  import CredentialCard from './lib/CredentialCard.svelte';
  import DashboardSection from './lib/DashboardSection.svelte';
  import NavBar from './lib/NavBar.svelte';

  // --- Navigation --- 
  const navItems = [
    { name: "Brain Tumor Classifier", id: "brain-neuro", icon: Brain },
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
  <div class="app-header">
    <h1 class="app-title">DiagnosTech-AI</h1>
  </div>
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

  {#if !currentUser}
    <div class="landing-bg">
      <div class="landing-content">
        <h1 class="landing-title">DiagnosTech-AI</h1>
        <p class="landing-tagline">Empowering doctors with AI-driven diagnostics</p>
        <button class="google-login-btn" on:click={() => window.location.href = '/api/auth/google/login'}>
          Continue with Google →
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  /* --- Global Styles / Resets --- */
  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    color: #1a1a1a;
    overflow-x: hidden;
    min-height: 100vh;
    background-color: #ffffff;
  }

  :global(h1, h2, h3, h4, h5, h6) {
    font-family: inherit;
    color: #1a1a1a;
    font-weight: 500;
    letter-spacing: -0.02em;
  }

  .app-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    background-color: #ffffff;
    border-bottom: 1px solid #e5e5e5;
    width: 100%;
    padding: 1.5rem 0;
  }

  .app-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 500;
    color: #1a1a1a;
    letter-spacing: -0.01em;
  }

  .app-container {
    display: flex;
    flex-direction: column;
    position: relative;
    min-height: 100vh;
    background-color: #ffffff;
  }

  .dashboard-content {
    padding-top: 100px;
    padding-bottom: 120px;
    max-width: 1200px;
    margin: 0 auto;
    padding-left: 2rem;
    padding-right: 2rem;
    width: 100%;
    box-sizing: border-box;
  }

  .placeholder-content {
    padding: 3rem 2rem;
    text-align: center;
    background-color: #fafafa;
    border-radius: 0;
    border: 1px solid #e5e5e5;
    color: #666;
  }

  .placeholder-content p {
    margin-bottom: 0.5rem;
  }

  .ai-use-case-card {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 0;
    box-shadow: none;
    margin-top: 1rem;
    border: 1px solid #e5e5e5;
    text-align: left;
  }

  .ai-use-case-card h4 {
    margin-top: 0;
    color: #1a1a1a;
  }

  .landing-bg {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100vw;
    height: 100vh;
    background-color: #ffffff;
    z-index: 2000;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .landing-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem;
  }

  .landing-title {
    font-size: 2.5rem;
    font-weight: 500;
    margin-bottom: 1rem;
    color: #1a1a1a;
    letter-spacing: -0.03em;
  }

  .landing-tagline {
    font-size: 1rem;
    margin-bottom: 3rem;
    color: #666;
    font-weight: 400;
  }

  .google-login-btn {
    background: #000000;
    color: #ffffff;
    border: 1px solid #000000;
    border-radius: 0;
    padding: 0.875rem 2rem;
    font-size: 1rem;
    font-weight: 400;
    cursor: pointer;
    transition: all 0.2s ease;
    letter-spacing: -0.01em;
  }

  .google-login-btn:hover {
    background: #ffffff;
    color: #000000;
  }

  @media (max-width: 768px) {
    .dashboard-content {
      padding-left: 1rem;
      padding-right: 1rem;
    }

    .landing-title {
      font-size: 2rem;
    }
  }
</style>