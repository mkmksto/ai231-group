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
    gap: 1.5rem;
    padding: 3rem 2rem;
    border: 1px dashed #e5e5e5;
    border-radius: 15px;
    transition: all 0.2s ease;
    background: #ffffff;
  }

  .dragging {
    border-color: #1a1a1a;
    background-color: #fafafa;
  }

  .file-label {
    display: inline-block;
    padding: 0.875rem 2rem;
    background-color: #000000;
    color: #ffffff;
    border: 1px solid #000000;
    border-radius: 15px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 400;
    transition: all 0.2s ease;
    font-family: inherit;
    letter-spacing: -0.01em;
  }

  .file-label:hover {
    background-color: #ffffff;
    color: #000000;
  }

  .preview {
    margin-top: 0;
    text-align: center;
    width: 100%;
  }

  .preview p {
    margin-bottom: 1rem;
    color: #666;
    font-size: 0.9375rem;
  }

  .preview img {
    max-width: 100%;
    max-height: 300px;
    border: 1px solid #e5e5e5;
    border-radius: 15px;
    margin-top: 0.5rem;
  }

  p {
    color: #666;
    font-size: 0.9375rem;
    margin: 0;
  }

  .drag-hint {
    color: #999;
    font-size: 0.875rem;
    margin-top: 0;
    font-weight: 400;
  }

  @media (max-width: 768px) {
    .uploader-container {
      padding: 2rem 1rem;
    }
  }
</style> 