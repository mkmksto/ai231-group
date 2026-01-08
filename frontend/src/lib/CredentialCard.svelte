<script lang="ts">
  import { Envelope, IdentificationCard, ShieldCheck, SignOut, User } from 'phosphor-svelte';
  import { createEventDispatcher } from 'svelte';
  import { sampleMode } from '../utils/sampleMode';

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
  let isSampleMode = false;

  function toggleSampleMode() {
    isSampleMode = !isSampleMode;
    sampleMode.set(isSampleMode);
  }
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
      <label class="sample-checkbox">
        <input type="checkbox" checked={isSampleMode} on:change={toggleSampleMode} />
        <span>Sample</span>
      </label>
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
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background-color: #ffffff;
    border-top: 1px solid #e5e5e5;
    z-index: 1200;
    color: #1a1a1a;
    transition: all 0.2s ease;
  }

  .credential-card.logged-in {
    /* Inherits base styles */
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 2rem;
    flex-wrap: wrap;
    overflow: hidden;
  }

  .info-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    white-space: nowrap;
    color: #666;
    background-color: #f5f5f5;
    padding: 0.5rem 1rem;
    border-radius: 15px;
  }

  .sample-checkbox {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #666;
    background-color: #f5f5f5;
    padding: 0.5rem 1rem;
    border-radius: 15px;
    cursor: pointer;
    white-space: nowrap;
  }

  .sample-checkbox input[type="checkbox"] {
    cursor: pointer;
    margin: 0;
  }

  .sample-checkbox span {
    user-select: none;
  }

  .credentials {
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: inline-block;
    vertical-align: middle;
  }

  .logout-button {
    background-color: #f5f5f5;
    border: none;
    color: #1a1a1a;
    cursor: pointer;
    padding: 0.5rem 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    font-size: 0.875rem;
    border-radius: 10px;
  }

  .logout-button:hover {
    background-color: #e5e5e5;
  }

  .credential-card.logged-out {
    max-width: 100%;
    padding: 1.5rem 2rem;
    justify-content: center;
  }

  .auth-form {
    width: 100%;
    max-width: 400px;
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .auth-form h4 {
    margin: 0 0 1rem 0;
    text-align: center;
    color: #1a1a1a;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    font-weight: 500;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-group label {
    font-size: 0.875rem;
    font-weight: 400;
    color: #666;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .form-group input {
    padding: 0.75rem;
    border: 1px solid #e5e5e5;
    border-radius: 0;
    font-size: 0.9375rem;
    background-color: #ffffff;
    font-family: inherit;
  }

  .form-group input:focus {
    outline: none;
    border-color: #1a1a1a;
  }

  .form-actions {
    margin-top: 0;
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .submit-button {
    padding: 0.875rem 2rem;
    border: 1px solid #000000;
    border-radius: 0;
    color: #ffffff;
    background-color: #000000;
    font-size: 1rem;
    font-weight: 400;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: inherit;
    letter-spacing: -0.01em;
  }

  .submit-button.login {
    background-color: #000000;
    color: #ffffff;
  }

  .submit-button.login:hover {
    background-color: #ffffff;
    color: #000000;
  }

  .submit-button.register {
    background-color: #000000;
    color: #ffffff;
  }

  .submit-button.register:hover {
    background-color: #ffffff;
    color: #000000;
  }

  .toggle-button {
    background: none;
    border: none;
    color: #666;
    text-decoration: underline;
    cursor: pointer;
    font-size: 0.875rem;
    padding: 0.5rem 0;
    margin-top: 0.5rem;
  }

  .toggle-button:hover {
    color: #1a1a1a;
  }

  @media (max-width: 768px) {
    .credential-card {
      padding: 1rem;
    }

    .credential-card.logged-in {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
    }

    .user-info {
      gap: 1rem;
      width: 100%;
    }

    .info-item {
      font-size: 0.8125rem;
    }

    .credentials {
      max-width: 150px;
    }

    .logout-button {
      width: 100%;
      justify-content: center;
    }

    .credential-card.logged-out {
      padding: 1.5rem 1rem;
    }
  }
</style> 