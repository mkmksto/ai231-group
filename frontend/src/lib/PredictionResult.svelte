<script lang="ts">
  import WojakLoading from '../assets/wojak-loading-wojak.gif';

  // 'export let' defines a prop that can be passed to this component
  export let prediction: string | null = null; // e.g., 'glioma_tumor', 'no_tumor', 'loading', 'error'
  export let confidence: number | null = null; // e.g., 0.95
  export let error: string | null = null;
  export let highlight: boolean = false;

  // Reactive statement to derive the display message
  $: displayMessage = (() => {
    if (prediction === 'loading') {
      return 'Analyzing image...';
    } else if (prediction === 'error') {
      return `Error: ${error || 'An unknown error occurred.'}`;
    } else if (prediction) {
      let tumorType = prediction.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()); // Format the prediction string
      let confidenceText = confidence !== null ? ` (Confidence: ${(confidence * 100).toFixed(1)}%)` : '';
      return `Prediction: ${tumorType}${confidenceText}`;
    } else {
      return 'Upload an image to see the prediction.';
    }
  })();

  $: messageClass = (() => {
    if (prediction === 'error') return 'error';
    if (prediction && prediction !== 'loading') return 'success';
    return 'info'; // Default/loading state
  })();

</script>

<div class="result-container" class:highlighted={highlight}>
  {#if prediction === 'loading'}
    <img src={WojakLoading} alt="Loading..." class="loading-gif" style="width: 200px;" />
  {:else}
    <p class="message {messageClass}">
      {displayMessage}
    </p>
  {/if}
</div>

<style>
  .result-container {
    text-align: center;
    padding: 1rem 0;
  }

  .loading-gif {
    width: 100px;
    height: auto;
    margin: 1rem auto;
  }

  .message {
    font-size: 1.1rem;
    padding: 0.8rem;
    border-radius: 4px;
  }

  .info {
    color: #555;
    background-color: #f0f0f0;
    border: 1px solid #ddd;
  }

  .success {
    /* Base success styles */
    color: #155724;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    font-weight: bold;
    
    /* Badge/Pill Overrides */
    display: inline-block; /* Allow padding and border-radius */
    padding: 0.4rem 0.8rem;
    font-size: 1rem; /* Adjust size */
    border-radius: 16px; /* Pill shape */
  }

  .error {
    color: #721c24;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    font-weight: bold;
  }

  .highlighted .message.success { 
    border-color: #007bff;
    border-width: 2px;
    box-shadow: 0 0 5px rgba(0, 122, 255, 0.5); /* Add glow effect when highlighted */
  }
</style> 