<script lang="ts">
  // import { sleep } from '../utils/utils';
  import ImageUploader from './ImageUploader.svelte';
  import PredictionResult from './PredictionResult.svelte';
// Adjusted path
  import { createEventDispatcher } from 'svelte';
  import { sampleMode } from '../utils/sampleMode';

  // State variables internal to this component
  let currentPrediction: string | null = null;
  let currentConfidence: number | null = null;
  let currentImageId: string | null = null;
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
      currentImageId = null;
      return;
    }

    currentPrediction = 'loading';
    currentConfidence = null;
    currentError = null;

    const formData = new FormData();
    formData.append('file', file);

    // Check if sample mode is enabled
    const isSample = $sampleMode;
    const url = isSample ? '/api/predict?sample=true' : '/api/predict';

    try {
      // Using the same API endpoint as before
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      // await sleep(300); // Slightly shorter simulated delay

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
      currentImageId = result.image_id;
      currentError = null;
      predictionConfirmed = null; // Reset confirmation state
      userSelectedClass = null;
      confirmationChoice = null; // Reset radio choice
      console.log("currentImageId: ", currentImageId);

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

  async function feedback(imageId: string, label: string) {
    console.log('inside feedback');
    console.log({imageId, label})
    const response = await fetch('/api/feedback', {
      method: 'POST',
      headers: {
            'Content-Type': 'application/json'
        },
      body: JSON.stringify({ image_id: imageId, label }),
    });
    if (!response.ok) {
      alert("Feedback failed: " + response.statusText);
      console.error('Feedback failed:', response);
      return;
    }
    const result = await response.json();
    console.log('Feedback successful:', result);
    alert("Feedback saved successfully.");
  }

  function handleConfirmationChoice() {
      if (confirmationChoice === 'yes') {
          if(!currentImageId || !currentPrediction) {
            alert("No image ID or prediction found. Please try again.");
            return;
          }
          feedback(currentImageId, currentPrediction);
          // handleSave(true);
      } else if (confirmationChoice === 'no') {
          predictionConfirmed = false; // Mark as incorrect to show dropdown
      } else {
          predictionConfirmed = null;
      }
  }

  function handleSaveForIncorrectCase(isCorrect: boolean) {
    let finalPrediction = isCorrect ? currentPrediction : userSelectedClass;
    if(!currentImageId || !finalPrediction) {
      alert("No image ID found. Please try again.");
      return;
    }

    feedback(currentImageId, finalPrediction);

    // if (!imageFile || !finalPrediction) {
    //   console.error("Cannot save: Image file or final prediction missing.");
    //   alert("Error: Cannot save data.");
    //   return;
    // }

    console.log(`Saving data: Image='${imageFile?.name || 'unknown'}', Prediction='${finalPrediction}', Correct=${isCorrect}`);
    // TODO: Implement actual API call to backend to save imageFile and finalPrediction
    // Example: dispatch('savePrediction', { imageFile, prediction: finalPrediction });
    alert(`Data for '${finalPrediction}' would be saved to the DB, thank you for your feedback.`);
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
  {#if !currentPrediction}
    <div class="uploader-wrapper">
      <div class="uploader-container">
        <ImageUploader onUpload={handleUpload} />
      </div>
    </div>
  {:else}
    <p class="description">
      Upload a brain MRI scan. The AI model will predict the tumor type (or lack thereof).
      Please confirm or correct the prediction to help improve the model.
    </p>

    <div class="uploader-container">
      <ImageUploader onUpload={handleUpload} />
    </div>
  {/if}

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
                <button on:click={() => handleSaveForIncorrectCase(false)} disabled={!userSelectedClass}>Save Correction</button>
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
    background: #ffffff;
    padding: 3rem;
    margin: 3rem 0;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
  }

  .description {
    margin-bottom: 2rem;
    color: #666;
    text-align: left;
    font-size: 0.9375rem;
    line-height: 1.6;
    font-weight: 400;
  }

  .uploader-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 400px);
    padding: 0;
  }

  .uploader-container {
    margin-bottom: 0;
    padding: 0;
    width: 100%;
  }

  .results-container {
    margin-top: 2rem;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    padding: 2rem;
    background: #ffffff;
  }

  .confirmation-area {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e5e5e5;
    transition: all 0.2s ease;
  }

  .confirmation-area.confirmed {
    background-color: #fafafa;
    padding: 1.5rem;
    text-align: center;
  }

  .confirmation-choices {
    border: none;
    padding: 0;
    margin: 0 0 1.5rem 0;
    display: flex;
    justify-content: flex-start;
    gap: 2rem;
    align-items: center;
  }

  .confirmation-choices legend {
    font-weight: 500;
    margin-bottom: 1rem;
    text-align: left;
    width: 100%;
    color: #1a1a1a;
    font-size: 0.9375rem;
  }

  .confirmation-choices label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    font-size: 0.9375rem;
    color: #1a1a1a;
    font-weight: 400;
  }

  .confirmation-choices input[type="radio"] {
    accent-color: #000000;
    cursor: pointer;
    width: 1em;
    height: 1em;
  }

  .manual-correction {
    margin-top: 1.5rem;
    padding: 1.5rem;
    background-color: #fafafa;
    border: 1px solid #e5e5e5;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .manual-correction label {
    font-weight: 500;
    color: #1a1a1a;
    font-size: 0.9375rem;
  }

  .manual-correction select {
    padding: 0.75rem;
    border-radius: 0;
    border: 1px solid #e5e5e5;
    min-width: 250px;
    font-family: inherit;
    font-size: 0.9375rem;
    background-color: #ffffff;
  }

  .manual-correction select:focus {
    outline: none;
    border-color: #1a1a1a;
  }

  .manual-correction button {
    padding: 0.875rem 2rem;
    font-size: 0.9375rem;
    cursor: pointer;
    border-radius: 0;
    background-color: #000000;
    color: #ffffff;
    border: 1px solid #000000;
    transition: all 0.2s ease;
    font-family: inherit;
    font-weight: 400;
  }

  .manual-correction button:hover {
    background-color: #ffffff;
    color: #000000;
  }

  .manual-correction button:disabled {
    background-color: #f5f5f5;
    color: #999;
    border-color: #e5e5e5;
    cursor: not-allowed;
  }

  .confirmation-message.positive {
    font-weight: 400;
    color: #1a1a1a;
    font-size: 0.9375rem;
  }

  :global(.results-container .result-container) {
    padding-bottom: 0;
  }

  @media (max-width: 768px) {
    .confirmation-choices {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
    }

    .manual-correction select {
      min-width: 100%;
      width: 100%;
    }

    .manual-correction button {
      width: 100%;
    }
  }
</style> 