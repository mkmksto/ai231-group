<script lang="ts">
  // Prop to receive the upload handler function from the parent (App.svelte)
  export let onUpload: (file: File | null) => void;

  let files: FileList | null = null;
  let previewUrl: string | null = null;

  function handleFileChange(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      files = target.files;
      const file = files[0];
      // Clean up previous preview URL if exists
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
      // Create a new preview URL
      previewUrl = URL.createObjectURL(file);

      // Call the parent component's upload handler
      onUpload(file);

      console.log('Selected file:', file.name);
    } else {
      files = null;
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
      previewUrl = null;
      // Notify parent that file was deselected/cleared
      onUpload(null);
    }

    // Clear the input value so the same file can be selected again
    target.value = '';
  }

  // Clean up the object URL when the component is destroyed
  import { onDestroy } from 'svelte';
  onDestroy(() => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
  });
</script>

<div class="uploader-container">
  <label for="file-upload" class="file-label">
    Choose Image
    <input
      id="file-upload"
      type="file"
      accept="image/*"
      on:change={handleFileChange}
      hidden
    />
  </label>

  {#if previewUrl}
    <div class="preview">
      <p>Preview:</p>
      <img src={previewUrl} alt="Preview of selected scan" />
    </div>
  {:else if files}
     <p>Selected: {files[0].name}</p> <!-- Show name if no preview yet -->
  {/if}

</div>

<style>
  .uploader-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem; /* Add gap between elements */
  }

  .file-label {
    display: inline-block;
    padding: 0.8rem 1.5rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.3s ease;
  }

  .file-label:hover {
    background-color: #0056b3;
  }

  /* Hide the actual file input */
  /* input[type="file"] is hidden using the 'hidden' attribute */

  .preview {
    margin-top: 1rem;
    text-align: center;
  }

  .preview img {
    max-width: 100%;
    max-height: 200px;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-top: 0.5rem;
  }

  p {
     color: #666; /* Inherit color from App.svelte or define as needed */
  }
</style> 