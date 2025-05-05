<script lang="ts">
  import ImageUploader from './ImageUploader.svelte';
  import PredictionResult from './PredictionResult.svelte';
  import { sleep } from '../utils/utils'; // Adjusted path
  import { createEventDispatcher } from 'svelte';

  // State variables internal to this component
  let currentPrediction: string | null = null;
  let currentConfidence: number | null = null;
  let currentError: string | null = null;
  let imageFile: File | null = null;
  let predictionConfirmed: boolean | null = null; // null: not asked, true: yes, false: no
  let userSelectedClass: string | null = null;
  let confirmationChoice: 'yes' | 'no' | null = null; // For radio buttons

  const dispatch = createEventDispatcher();

  // Passed from App.svelte or defined here
  const classMapping = {
    0: "glioma_tumor",
    1: "meningioma_tumor",
    2: "no_tumor",
    3: "pituitary_tumor",
  };
  const classOptions = Object.values(classMapping); // Use values directly for dropdown

  async function handleUpload(file: File | null) {
    imageFile = file;
    predictionConfirmed = null;
    userSelectedClass = null;
    confirmationChoice = null; // Reset radio button choice

    if (!file) {
      currentPrediction = null;
      currentConfidence = null;
      currentError = null;
      return;
    }

    currentPrediction = 'loading';
    currentConfidence = null;
    currentError = null;

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Using the same API endpoint as before
      const response = await fetch('/api/predict', {
        method: 'POST',
        body: formData,
      });

      await sleep(1000); // Slightly shorter simulated delay

      if (!response.ok) {
        let errorMsg = `HTTP error! Status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMsg = errorData.detail || errorMsg;
        } catch (e) { /* Ignore */ }
        throw new Error(errorMsg);
      }

      const result = await response.json();
      currentPrediction = result.prediction;
      currentConfidence = result.confidence;
      currentError = null;
      predictionConfirmed = null; // Reset confirmation state
      userSelectedClass = null;
      confirmationChoice = null; // Reset radio choice

    } catch (err: any) {
      console.error('Upload failed:', err);
      currentPrediction = 'error';
      currentConfidence = null;
      currentError = err.message || 'Failed to fetch prediction.';
      predictionConfirmed = null;
      userSelectedClass = null;
      confirmationChoice = null;
    }
  }

  function handleConfirmationChoice() {
      if (confirmationChoice === 'yes') {
          handleSave(true);
      } else if (confirmationChoice === 'no') {
          predictionConfirmed = false; // Mark as incorrect to show dropdown
      } else {
          predictionConfirmed = null;
      }
  }

  function handleSave(isCorrect: boolean) {
    let finalPrediction = isCorrect ? currentPrediction : userSelectedClass;

    if (!imageFile || !finalPrediction) {
      console.error("Cannot save: Image file or final prediction missing.");
      alert("Error: Cannot save data.");
      return;
    }

    console.log(`Saving data: Image='${imageFile.name}', Prediction='${finalPrediction}', Correct=${isCorrect}`);
    // TODO: Implement actual API call to backend to save imageFile and finalPrediction
    // Example: dispatch('savePrediction', { imageFile, prediction: finalPrediction });
    alert(`Data for '${finalPrediction}' would be saved to DB here.`);
    predictionConfirmed = true; // Mark as confirmed/saved
    
    // Optional: Clear state after saving
    // currentPrediction = null;
    // currentConfidence = null;
    // imageFile = null; 
    // confirmationChoice = null;
    // userSelectedClass = null;
  }

</script>

<div class="brain-tumor-classifier">
  <p class="description">
    Upload a brain MRI scan. The AI model will predict the tumor type (or lack thereof).
    Please confirm or correct the prediction to help improve the model.
  </p>

  <div class="uploader-container">
    <ImageUploader onUpload={handleUpload} />
  </div>

  {#if currentPrediction}
    <div class="results-container">
      <PredictionResult
        prediction={currentPrediction}
        confidence={currentConfidence}
        error={currentError}
        highlight={predictionConfirmed === null && currentPrediction !== 'loading' && currentPrediction !== 'error'} 
      />

      {#if currentPrediction !== 'loading' && currentPrediction !== 'error'}
        <div class="confirmation-area" class:confirmed={predictionConfirmed === true}>
          {#if predictionConfirmed === true}
             <p class="confirmation-message positive">✅ Prediction saved.</p>
          {:else}
            <fieldset class="confirmation-choices">
              <legend>Is this prediction correct?</legend>
              <label>
                <input type="radio" name="confirmation" value="yes" bind:group={confirmationChoice} on:change={handleConfirmationChoice} />
                <span>✅ Yes</span>
              </label>
              <label>
                <input type="radio" name="confirmation" value="no" bind:group={confirmationChoice} on:change={handleConfirmationChoice} />
                <span>❌ No, let me correct it</span>
              </label>
            </fieldset>

            {#if confirmationChoice === 'no'}
              <div class="manual-correction">
                <label for="correction-select">Select correct classification:</label>
                <select id="correction-select" bind:value={userSelectedClass}>
                  <option value={null} disabled>-- Please select --</option>
                  {#each classOptions as option}
                    <option value={option}>{option.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</option>
                  {/each}
                </select>
                <button on:click={() => handleSave(false)} disabled={!userSelectedClass}>Save Correction</button>
              </div>
            {/if}
          {/if} 
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .brain-tumor-classifier {
    /* Add specific styles if needed, or rely on App.svelte */
  }
  .description {
      margin-bottom: 1.5rem;
      color: #546E7A;
      text-align: center;
      font-size: 1rem;
  }
  .uploader-container {
      margin-bottom: 2rem;
      padding: 1rem;
      background-color: #ECEFF1; /* Light grey background for uploader */
      border-radius: 8px;
  }
  .results-container {
      margin-top: 1.5rem;
      border: 1px solid #CFD8DC;
      border-radius: 8px;
      padding: 1.5rem;
  }

  .confirmation-area {
      margin-top: 1.5rem;
      padding-top: 1.5rem;
      border-top: 1px dashed #B0BEC5;
      transition: background-color 0.3s ease;
  }

  .confirmation-area.confirmed {
      background-color: #E8F5E9; /* Light green when confirmed */
      padding: 1rem;
      border-radius: 6px;
      text-align: center;
  }

  .confirmation-choices {
    border: none;
    padding: 0 0 1rem 0;
    margin: 0 0 1rem 0;
    display: flex;
    justify-content: center;
    gap: 2rem; /* More space between radio buttons */
    align-items: center;
  }

  .confirmation-choices legend {
    font-weight: bold;
    margin-bottom: 0.8rem;
    text-align: center;
    width: 100%;
    color: #37474F;
  }

  .confirmation-choices label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    font-size: 1rem;
  }

  .confirmation-choices input[type="radio"] {
      accent-color: #007AFF; /* Style radio button color */
      cursor: pointer;
      width: 1.2em;
      height: 1.2em;
  }

  .manual-correction {
    margin-top: 1rem;
    padding: 1rem;
    background-color: #FFF9C4; /* Light yellow background */
    border: 1px solid #FFF176;
    border-radius: 6px;
    display: flex;
    flex-direction: column; /* Stack elements vertically */
    align-items: center;
    gap: 1rem;
  }

  .manual-correction label {
    font-weight: bold;
    color: #5f6368;
  }

  .manual-correction select {
    padding: 0.6rem;
    border-radius: 4px;
    border: 1px solid #ccc;
    min-width: 200px;
  }

  .manual-correction button {
    padding: 0.7rem 1.2rem;
    font-size: 0.9rem;
    cursor: pointer;
    border-radius: 4px;
    background-color: #fb8c00; /* Orange button */
    color: white;
    border: none;
    transition: background-color 0.2s ease;
  }

  .manual-correction button:hover {
     background-color: #e65100;
  }

  .manual-correction button:disabled {
     background-color: #bdbdbd;
     cursor: not-allowed;
  }

  .confirmation-message.positive {
    font-weight: bold;
    color: #1B5E20; /* Darker green */
  }

  /* Ensure PredictionResult styles don't conflict massively */
  :global(.results-container .result-container) {
    padding-bottom: 0; /* Remove default padding if needed */
  }

</style> 