document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const fileList = document.getElementById('file-list');
    const emptyState = document.getElementById('empty-state');
    const template = document.getElementById('file-item-template');
    const mergeBtn = document.getElementById('merge-btn');
    const fileCountDisp = document.getElementById('file-count');
    const statusMessage = document.getElementById('status-message');

    let uploadedFiles = []; // Track uploaded files via ID

    // Setup drag-and-drop ordering with SortableJS
    new Sortable(fileList, {
        animation: 150,
        ghostClass: 'sortable-ghost',
        dragClass: 'sortable-drag',
        handle: '.file-item', // Make the entire row draggable
        onEnd: function (evt) {
            // Re-sync the array order based on DOM
            // Instead of doing array manipulation, we'll derive the ID order primarily from the DOM when merging
            updateUI();
        }
    });

    // -----------------------------------------------------
    // File Selection (Drag & Drop + Hidden Input)
    // -----------------------------------------------------

    // Prevent default browser behavior on drag-and-drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop zone
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('bg-indigo-50', 'border-indigo-400');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('bg-indigo-50', 'border-indigo-400');
        }, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    });

    // Handle click on browse button
    browseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        fileInput.click();
    });

    // Handle generic click in dropzone
    dropZone.addEventListener('click', (e) => {
        if (e.target !== browseBtn && !browseBtn.contains(e.target)) {
            fileInput.click();
        }
    });

    // Handle file changes from input
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
        // Reset so same file can be triggered again if user wants to
        this.value = '';
    });

    // -----------------------------------------------------
    // Status Bar Control
    // -----------------------------------------------------

    function showStatus(message, type = 'info') {
        statusMessage.textContent = message;
        // Reset classes
        statusMessage.classList.remove('hidden', 'bg-zinc-50', 'text-zinc-600', 'border-zinc-200', 
                                       'bg-zinc-100', 'text-black', 'border-black', 
                                       'bg-black', 'text-white', 'border-black');
        
        if (type === 'error') {
            statusMessage.classList.add('bg-black', 'text-white', 'border-black');
        } else if (type === 'success') {
            statusMessage.classList.add('bg-zinc-100', 'text-black', 'border-black');
        } else {
            statusMessage.classList.add('bg-zinc-50', 'text-zinc-600', 'border-zinc-200');
        }
    }

    function hideStatus() {
        statusMessage.classList.add('hidden');
    }

    // -----------------------------------------------------
    // File Processing & Upload
    // -----------------------------------------------------

    async function handleFiles(files) {
        const pdfFiles = Array.from(files).filter(file => 
            file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
        );
        
        if (pdfFiles.length === 0) {
            showStatus('Please select valid PDF files.', 'error');
            return;
        }

        if (pdfFiles.length < files.length) {
            showStatus('Some files were ignored because they are not PDFs.', 'error');
        } else {
            hideStatus();
        }

        showStatus(`Uploading ${pdfFiles.length} file(s)...`, 'info');
        mergeBtn.disabled = true;

        for (const file of pdfFiles) {
            await uploadFile(file);
        }

        updateUI();
        if (uploadedFiles.length > 0) {
            showStatus('Upload complete ready to merge.', 'success');
            setTimeout(hideStatus, 3000);
        }
    }

    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                uploadedFiles.push({
                    id: data.id,
                    filename: data.filename
                });
                renderFileItem(data.id, data.filename);
            } else {
                console.error(`Upload failed for ${file.name}`);
                showStatus(`Failed to upload ${file.name}`, 'error');
            }
        } catch (error) {
            console.error('Upload Error:', error);
            showStatus(`Error uploading ${file.name}`, 'error');
        }
    }

    function renderFileItem(id, filename) {
        // Remove empty state if present
        if (emptyState && emptyState.parentNode === fileList) {
            fileList.removeChild(emptyState);
        }

        const clone = template.content.cloneNode(true);
        const li = clone.querySelector('li');
        li.dataset.id = id;
        
        const nameSpan = clone.querySelector('.file-name');
        nameSpan.textContent = filename;
        nameSpan.title = filename; // Show full name on hover

        const removeBtn = clone.querySelector('.remove-btn');
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Avoid triggering grab
            li.remove();
            
            // Re-sync array
            uploadedFiles = uploadedFiles.filter(item => item.id !== id);
            updateUI();
        });

        fileList.appendChild(li);
    }

    function updateUI() {
        const fileCount = fileList.querySelectorAll('li.file-item').length;
        fileCountDisp.textContent = `${fileCount} file${fileCount !== 1 ? 's' : ''}`;
        
        if (fileCount === 0) {
            if (!fileList.contains(emptyState)) {
                fileList.appendChild(emptyState);
            }
            mergeBtn.disabled = true;
        } else {
            // Normal flow: enable merge if >= 2 files. 
            // In case of 1 file, it's just a single PDF, no point downloading merged copy unless user wants to.
            mergeBtn.disabled = fileCount < 2; 
        }
    }

    // -----------------------------------------------------
    // PDF Merge Request
    // -----------------------------------------------------

    mergeBtn.addEventListener('click', async () => {
        const currentDOMIds = Array.from(fileList.querySelectorAll('li.file-item')).map(li => li.dataset.id);
        
        if (currentDOMIds.length < 1) return;

        showStatus('Processing merge request... This may take a moment.', 'info');
        mergeBtn.disabled = true;
        mergeBtn.innerHTML = `
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Merging...
        `;

        try {
            const response = await fetch('/merge', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ files: currentDOMIds })
            });

            if (response.ok) {
                // Return a blob to trigger download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'Merged_Document.pdf';
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                showStatus('Merge completed successfully!', 'success');
            } else {
                const errorData = await response.json();
                showStatus(`Merge failed: ${errorData.error || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('Merge Error:', error);
            showStatus('An error occurred during merging.', 'error');
        } finally {
            // Restore button
            mergeBtn.innerHTML = `
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path></svg>
                <span>Merge PDFs</span>
            `;
            updateUI(); 
            setTimeout(() => { if (!statusMessage.classList.contains('bg-rose-50')) hideStatus() }, 4000);
        }
    });

    // Run initial UI update
    updateUI();
});
