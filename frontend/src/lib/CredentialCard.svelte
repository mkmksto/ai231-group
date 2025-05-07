<script lang="ts">
  import { Envelope, IdentificationCard, ShieldCheck, SignOut, User } from 'phosphor-svelte';
  import { createEventDispatcher } from 'svelte';

  // Define the User type matching App.svelte
  interface User {
    name: string;
    email: string;
    credentials?: string; // Optional for login display
    role: string;
  }

  // Accept the user object prop
  export let user: User | null = null;

  // Internal state for login/register form
  let isRegisterMode = false;
  // let email = '';
  // let password = '';
  // let name = '';
  // let credentials = '';

  const dispatch = createEventDispatcher();

  function handleLogout() {
    fetch("/api/auth/logout", {
      method: "POST",
      credentials: "include",
    });
    dispatch('logout');
  }

  function submitLogin() {
    // this sends a request to the backend which initiates the google oauth flow
    // the user is redirected to the google login page

    // if successful, the user is redirected back to the frontend
    console.log("handleContinueWithGoogle");
    setTimeout(() => {
      window.location.href = "/api/auth/google/login";
    }, 100);
  }

  // function submitRegister() {
  //     if (!name || !email || !password) {
  //         alert('Please enter name, email, and password.');
  //         return;
  //     }
  //      console.log('Dispatching register');
  //     dispatch('register', { name: name, email: email, pass: password, credentials: credentials });
  //      // Clear form after attempt
  //     name = '';
  //     email = '';
  //     password = '';
  //     credentials = '';
  //     isRegisterMode = false; // Switch back to login view after registration attempt
  // }

  function toggleMode() {
      isRegisterMode = !isRegisterMode;
      // // Clear fields when toggling
      // email = '';
      // password = '';
      // name = '';
      // credentials = '';
  }

</script>

{#if user}
  <!-- === LOGGED IN VIEW === -->
  <div class="credential-card logged-in">
    <div class="user-info">
      <div class="info-item">
        <User size={20} />
        <span>{user.name}</span>
      </div>
      <div class="info-item">
        <Envelope size={20} />
        <span>{user.email}</span>
      </div>
      <div class="info-item">
        <ShieldCheck size={20} />
        <span>{user.role}</span>
      </div>

      {#if user.credentials}
        <div class="info-item">
          <IdentificationCard size={20} />
          <span class="credentials" title={user.credentials}>{user.credentials}</span>
        </div>
      {/if}
    </div>
    <button class="logout-button" on:click={handleLogout} title="Logout">
      <SignOut size={20} />
    </button>
  </div>
{:else}
  <!-- === LOGGED OUT VIEW (LOGIN/REGISTER FORM) === -->
  <div class="credential-card logged-out">
    <!-- {#if isRegisterMode}
      <form class="auth-form" on:submit|preventDefault={submitRegister}>
        <h4><UserPlus size={20} /> Register New Account</h4>
        <div class="form-group">
            <User size={16} /><label for="reg-name">Name:</label>
            <input type="text" id="reg-name" bind:value={name} required placeholder="Your Name" />
        </div>
         <div class="form-group">
            <Envelope size={16} /><label for="reg-email">Email:</label>
            <input type="email" id="reg-email" bind:value={email} required placeholder="your@email.com" />
        </div>
        <div class="form-group">
            <Lock size={16} /><label for="reg-password">Password:</label>
            <input type="password" id="reg-password" bind:value={password} required placeholder="********" />
        </div>
         <div class="form-group">
            <ShieldCheck size={16} /><label for="reg-credentials">Credentials (Optional):</label>
            <input type="text" id="reg-credentials" bind:value={credentials} placeholder="e.g., MD, PhD"/>
        </div>
        <div class="form-actions">
          <button type="submit" class="submit-button register">Register</button>
          <button type="button" on:click={toggleMode} class="toggle-button">Switch to Login</button>
        </div>
      </form> -->
      <!-- LOGIN FORM -->
      <form class="auth-form" on:submit|preventDefault={submitLogin}>
         <div class="form-actions">
          <button type="submit" class="submit-button login">Continue with Google</button>
        </div>
      </form>
  </div>
{/if}

<style>
  .credential-card {
    position: fixed;
    bottom: 1rem;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 500px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 1.2rem;
    border-radius: 12px;
    background-color: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(10px) saturate(180%);
    -webkit-backdrop-filter: blur(10px) saturate(180%);
    border: 2px solid #007AFF;
    box-shadow: 0 4px 15px rgba(0, 122, 255, 0.2);
    z-index: 1200;
    color: #0056b3;
    transition: all 0.3s ease;
  }

  /* Logged In Specific Styles */
  .credential-card.logged-in {
      /* Inherits base styles, potentially add specific adjustments */
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    flex-wrap: nowrap;
    overflow: hidden;
  }

  .info-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    white-space: nowrap;
  }

  .credentials {
      max-width: 150px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      display: inline-block;
      vertical-align: middle;
  }

  .logout-button {
    background: none;
    border: none;
    color: #007AFF;
    cursor: pointer;
    padding: 0.3rem;
    display: flex;
    align-items: center;
    border-radius: 50%;
    transition: background-color 0.2s ease;
  }

  .logout-button:hover {
    background-color: rgba(0, 122, 255, 0.1);
  }

  /* Logged Out Specific Styles */
  .credential-card.logged-out {
      max-width: 400px; /* Slightly smaller for form */
      padding: 1.5rem; /* More padding for form */
      justify-content: center; /* Center the form */
  }

  .auth-form {
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 1rem;
  }

  .auth-form h4 {
      margin: 0 0 1rem 0;
      text-align: center;
      color: #0056b3;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
  }

  .form-group {
      display: flex;
      flex-direction: column; /* Labels on top */
      gap: 0.3rem;
  }

  .form-group label {
      font-size: 0.85rem;
      font-weight: 600;
      color: #333;
      display: flex;
      align-items: center;
      gap: 0.3rem;
  }

  .form-group input {
      padding: 0.6rem;
      border: 1px solid #ccc;
      border-radius: 6px;
      font-size: 0.9rem;
      background-color: rgba(255, 255, 255, 0.8);
  }

  .form-actions {
      margin-top: 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.8rem;
  }

  .submit-button {
      padding: 0.8rem;
      border: none;
      border-radius: 6px;
      color: white;
      font-size: 1rem;
      font-weight: bold;
      cursor: pointer;
      transition: background-color 0.2s ease;
  }

  .submit-button.login {
      background-color: #007AFF;
  }
  .submit-button.login:hover {
      background-color: #0056b3;
  }

   .submit-button.register {
      background-color: #28a745; /* Green for register */
  }
   .submit-button.register:hover {
      background-color: #218838;
  }

  .toggle-button {
      background: none;
      border: none;
      color: #007AFF;
      text-decoration: underline;
      cursor: pointer;
      font-size: 0.85rem;
      padding: 0.3rem;
  }
  .toggle-button:hover {
      color: #0056b3;
  }

  /* Responsive adjustments */
  @media (max-width: 600px) {
    /* Logged In */
    .credential-card.logged-in {
       width: 95%;
       padding: 0.6rem 1rem;
    }
    .user-info {
        gap: 0.8rem;
    }
    .info-item {
        font-size: 0.8rem;
        gap: 0.3rem;
    }
    .credentials {
        max-width: 100px;
    }
    
    /* Logged Out */
     .credential-card.logged-out {
       width: 90%;
       max-width: none;
       padding: 1.2rem;
     }
     .auth-form h4 {
         font-size: 1.1rem;
     }
  }
</style> 