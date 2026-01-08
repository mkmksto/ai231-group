<script lang="ts">
  // import WojakLoading from '../assets/wojak-loading-wojak.gif';
  import BrainGif from '../assets/ai-brain.gif';

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
        <img src={BrainGif} alt="Loading..." class="loading-gif" style="width: 300px; height:300px" />
  {:else}
    <p class="message {messageClass}">
      {displayMessage}
    </p>
  {/if}
</div>

<style>
  .result-container {
    text-align: left;
    padding: 0;
  }

  .loading-gif {
    width: 200px;
    height: auto;
    margin: 1rem auto;
    display: block;
  }

  .message {
    font-size: 1rem;
    padding: 0;
    border-radius: 0;
    font-weight: 400;
    display: inline-block;
  }

  .info {
    color: #666;
    background-color: transparent;
    border: none;
  }

  .success {
    color: #1a1a1a;
    background-color: transparent;
    border: none;
    font-weight: 500;
    display: inline-block;
    padding: 0;
    font-size: 1rem;
  }

  .error {
    color: #1a1a1a;
    background-color: #fafafa;
    border: 1px solid #e5e5e5;
    font-weight: 400;
    padding: 1rem;
    display: inline-block;
  }

  .highlighted .message.success {
    border: none;
    border-width: 0;
    box-shadow: none;
  }
</style> 
