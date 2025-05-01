<script lang="ts">
  // We'll add imports and logic here later
  import ImageUploader from './lib/ImageUploader.svelte';
  import PredictionResult from './lib/PredictionResult.svelte';
  import { sleep } from './utils/utils';

  // State variables to hold the prediction results
  let currentPrediction: string | null = null; // 'loading', 'error', or tumor type like 'glioma_tumor'
  let currentConfidence: number | null = null;
  let currentError: string | null = null;

  async function handleUpload(file: File | null) {
    if (!file) {
      // Reset state if the file is deselected
      currentPrediction = null;
      currentConfidence = null;
      currentError = null;
      return;
    }

    // Set state to loading
    currentPrediction = 'loading';
    currentConfidence = null;
    currentError = null;

    const formData = new FormData();
    formData.append('file', file); // The backend should expect a file field named 'file'

    try {
      // NOTE: If your backend runs on a different port (e.g., 8000), you'll need to configure
      // a proxy in vite.config.ts to avoid CORS issues during development.
      // Example vite.config.ts addition:
      // server: {
      //   proxy: {
      //     '/api': 'http://localhost:8000', // Adjust port if needed
      //   },
      // },
      const response = await fetch('/api/predict', {
        method: 'POST',
        body: formData,
      });

      await sleep(1500);

      if (!response.ok) {
        // Handle HTTP errors (e.g., 4xx, 5xx)
        let errorMsg = `HTTP error! Status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMsg = errorData.detail || errorMsg; // Try to get specific error from backend
        } catch (e) { /* Ignore if error response isn't JSON */ }
        throw new Error(errorMsg);
      }

      // Assuming backend returns { prediction: 'some_tumor', confidence: 0.95 }
      const result = await response.json();

      // Update state with successful prediction
      currentPrediction = result.prediction;
      currentConfidence = result.confidence;
      currentError = null;

    } catch (err: any) {
      // Handle network errors or errors thrown above
      console.error('Upload failed:', err);
      currentPrediction = 'error';
      currentConfidence = null;
      currentError = err.message || 'Failed to fetch prediction.';
    }
  }

</script>

<main>
  <div class="title-container">
    <img src="/brain-logo.png" alt="Brain Logo" class="brain-logo" />
    <h1>Brain Tumor Classifier</h1>
  </div>

  <section class="upload-section">
    <h2>Upload Brain Scan Image</h2>
    <!-- Pass the upload handling function to ImageUploader -->
    <ImageUploader onUpload={handleUpload} />
    <!-- <p>[Image Upload Placeholder]</p> -->
  </section>

  <section class="results-section">
    <h2>Prediction Results</h2>
    <PredictionResult
      prediction={currentPrediction}
      confidence={currentConfidence}
      error={currentError}
    />
    <!-- <p>[Results Placeholder]</p> -->
  </section>

</main>

<style>
  /* Make body background dark to match screenshot */
  :global(body) {
    background-color: #333;
    color: #eee; /* Adjust default text color for contrast */
    margin: 0;
  }

  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    max-width: 800px;
    margin: 0 auto;
    font-family: sans-serif;
  }

  .title-container {
    display: flex;
    align-items: center;
    gap: 1rem; /* Space between logo and title */
    margin-bottom: 2rem;
  }

  .brain-logo {
    height: 4em; /* Adjust size as needed */
    width: auto;
  }

  h1 {
    color: #eee; /* Lighter color for dark background */
    margin-bottom: 0; /* Remove bottom margin as it's handled by title-container */
    font-size: 2.5em; /* Make title a bit larger */
    text-align: center;
  }

  section {
    width: 100%;
    border: 1px solid #555; /* Darker border */
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border-radius: 8px;
    background-color: #f9f9f9;
    color: #333; /* Text inside sections should be dark */
  }

  h2 {
    margin-top: 0;
    color: #555;
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
    text-align: center;
  }

  /* p { Removed unused selector */
  /*   color: #666; */
  /* } */
</style>
