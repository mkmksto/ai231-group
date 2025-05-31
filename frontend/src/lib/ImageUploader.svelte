<script lang="ts">
  // Prop to receive the upload handler function from the parent (App.svelte)
  export let onUpload: (file: File | null) => void;

  let files: FileList | null = null;
  let previewUrl: string | null = null;
  let isDragging = false;

  function handleFileChange(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      processFile(target.files[0]);
    } else {
      clearFile();
    }
    // Clear the input value so the same file can be selected again
    target.value = '';
  }

  function processFile(file: File) {
    files = new DataTransfer().files;
    (files as any).item = () => file;
    // Clean up previous preview URL if exists
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    // Create a new preview URL
    previewUrl = URL.createObjectURL(file);
    // Call the parent component's upload handler
    onUpload(file);
    console.log('Selected file:', file.name);
  }

  function clearFile() {
    files = null;
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    previewUrl = null;
    // Notify parent that file was deselected/cleared
    onUpload(null);
  }

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    isDragging = true;
  }

  function handleDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    isDragging = false;
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    isDragging = false;

    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      const file = event.dataTransfer.files[0];
      if (file.type.startsWith('image/')) {
        processFile(file);
      }
    }
  }

  // Clean up the object URL when the component is destroyed
  import { onDestroy } from 'svelte';
  onDestroy(() => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
  });
</script>

<div 
  class="uploader-container"
  class:dragging={isDragging}
  on:dragover={handleDragOver}
  on:dragleave={handleDragLeave}
  on:drop={handleDrop}
  role="button"
  tabindex="0"
>
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

  <p class="drag-hint">or drag and drop an image here</p>

</div>

<style>
  .uploader-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 2rem;
    border: 2px dashed #ccc;
    border-radius: 8px;
    transition: all 0.3s ease;
    background: rgba(255,255,255,0.18); /* White with 18% opacity */
  }

  .dragging {
    border-color: #007bff;
    background-color: rgba(0, 123, 255, 0.1);
  }

  .file-label {
    display: inline-block;
    padding: 0.8rem 1.5rem;
    background-color: #1877f2; /* Facebook blue */
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.3s ease;
  }

  .file-label:hover {
    background-color: #145db2; /* Slightly darker Facebook blue */
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
    color: #666;
  }

  .drag-hint {
    color: #999;
    font-size: 0.9rem;
    margin-top: 0.5rem;
  }
</style> 