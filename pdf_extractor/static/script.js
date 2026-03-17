document.addEventListener('DOMContentLoaded', () => {
    // --- Tabs Logic ---
    const tabs = ['extract', 'merge', 'extract-merge'];
    let currentTab = 'extract';

    tabs.forEach(tab => {
        const btn = document.getElementById(`tab-btn-${tab}`);
        btn.addEventListener('click', () => {
            // Update active tab styling
            tabs.forEach(t => {
                const b = document.getElementById(`tab-btn-${t}`);
                const content = document.getElementById(`tab-${t}`);
                if (t === tab) {
                    b.classList.remove('text-zinc-400', 'border-transparent');
                    b.classList.add('text-black', 'border-black');
                    content.classList.remove('hidden');
                    content.classList.add('block');
                } else {
                    b.classList.add('text-zinc-400', 'border-transparent');
                    b.classList.remove('text-black', 'border-black');
                    content.classList.add('hidden');
                    content.classList.remove('block');
                }
            });
            currentTab = tab;
        });
    });

    // --- Utility: Status Messages ---
    function showStatus(tab, message, type = 'info') {
        const statusEl = document.getElementById(tab === 'extract-merge' ? 'status-em' : `status-${tab}`);
        statusEl.textContent = message;
        statusEl.className = `mt-6 text-center font-bold rounded-xl px-5 py-3 w-full border text-sm uppercase tracking-tight ${
            type === 'error' ? 'bg-black text-white border-black' : 
            type === 'success' ? 'bg-zinc-100 text-black border-black' : 
            'bg-zinc-50 text-zinc-600 border-zinc-200'
        }`;
        statusEl.classList.remove('hidden');
    }

    function hideStatus(tab) {
        const statusEl = document.getElementById(tab === 'extract-merge' ? 'status-em' : `status-${tab}`);
        statusEl.classList.add('hidden');
    }

    // --- Utility: Upload File ---
    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch('/upload', { method: 'POST', body: formData });
        if (!response.ok) throw new Error('Upload failed');
        return await response.json();
    }

    // --- Tab 1: Extract ---
    const dropExtract = document.getElementById('drop-zone-extract');
    const inputExtract = document.getElementById('file-input-extract');
    const browseExtract = document.getElementById('browse-btn-extract');
    const btnExtract = document.getElementById('extract-btn');
    const infoExtract = document.getElementById('extract-file-info');
    const filenameExtract = document.getElementById('extract-filename');
    const pagecountExtract = document.getElementById('extract-pagecount');
    const rangesExtract = document.getElementById('extract-ranges');

    let extractFileId = null;

    browseExtract.addEventListener('click', () => inputExtract.click());
    dropExtract.addEventListener('click', (e) => { if (e.target !== browseExtract) inputExtract.click(); });
    
    // Drag/Drop Extract
    setupDropZone(dropExtract, inputExtract, async (files) => {
        if(files.length > 0) handleExtractFile(files[0]);
    });

    async function handleExtractFile(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showStatus('extract', 'Please select a PDF file.', 'error');
            return;
        }
        showStatus('extract', 'Uploading...', 'info');
        btnExtract.disabled = true;
        try {
            const data = await uploadFile(file);
            extractFileId = data.id;
            
            // Get info
            const infoRes = await fetch('/info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file: extractFileId })
            });
            if (infoRes.ok) {
                const infoData = await infoRes.json();
                filenameExtract.textContent = file.name;
                pagecountExtract.textContent = `Total Pages: ${infoData.pages}`;
                infoExtract.classList.remove('hidden');
                btnExtract.disabled = false;
                hideStatus('extract');
            } else {
                throw new Error('Could not read PDF info');
            }
        } catch (e) {
            showStatus('extract', e.message, 'error');
        }
    }

    btnExtract.addEventListener('click', async () => {
        if (!extractFileId) return;
        showStatus('extract', 'Extracting...', 'info');
        btnExtract.disabled = true;
        try {
            const response = await fetch('/extract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file: extractFileId, ranges: rangesExtract.value })
            });

            if (response.ok) {
                triggerDownload(await response.blob(), `Extracted_${filenameExtract.textContent}`);
                showStatus('extract', 'Extraction complete!', 'success');
            } else {
                const err = await response.json();
                showStatus('extract', err.error || 'Extraction failed', 'error');
            }
        } catch (e) {
            showStatus('extract', 'Error extracting pages', 'error');
        } finally {
            btnExtract.disabled = false;
        }
    });


    // --- Generic Multi-File Logic (Merge & Extract+Merge) ---
    function setupMultiFile(tabSuffix, templateId) {
        const dropZone = document.getElementById(`drop-zone-${tabSuffix}`);
        const fileInput = document.getElementById(`file-input-${tabSuffix}`);
        const browseBtn = document.getElementById(`browse-btn-${tabSuffix}`);
        const fileList = document.getElementById(`file-list-${tabSuffix}`);
        const emptyState = document.getElementById(`empty-state-${tabSuffix}`);
        const actionBtn = document.getElementById(tabSuffix === 'em' ? 'em-btn' : `merge-btn`);
        const template = document.getElementById(templateId);

        let filesData = [];

        new Sortable(fileList, {
            animation: 150,
            handle: '.cursor-grab',
            onEnd: updateUI
        });

        browseBtn.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('click', (e) => { if (e.target !== browseBtn) fileInput.click(); });
        setupDropZone(dropZone, fileInput, handleFiles);

        async function handleFiles(files) {
            const pdfs = Array.from(files).filter(f => f.name.toLowerCase().endsWith('.pdf'));
            if (pdfs.length === 0) return;
            
            showStatus(tabSuffix === 'em' ? 'extract-merge' : 'merge', `Uploading ${pdfs.length} files...`, 'info');
            actionBtn.disabled = true;

            for (const file of pdfs) {
                try {
                    const data = await uploadFile(file);
                    const id = data.id;
                    filesData.push({ id });

                    // render
                    if (emptyState && emptyState.parentNode === fileList) fileList.removeChild(emptyState);
                    
                    const clone = template.content.cloneNode(true);
                    const li = clone.querySelector('li');
                    li.dataset.id = id;
                    li.querySelector('.file-name').textContent = file.name;
                    
                    li.querySelector('.remove-btn').addEventListener('click', () => {
                        li.remove();
                        filesData = filesData.filter(item => item.id !== id);
                        updateUI();
                    });

                    fileList.appendChild(li);
                } catch (e) {
                    console.error('Upload error', e);
                }
            }
            updateUI();
            hideStatus(tabSuffix === 'em' ? 'extract-merge' : 'merge');
        }

        function updateUI() {
            const count = fileList.querySelectorAll('li.file-item').length;
            if (count === 0 && !fileList.contains(emptyState)) fileList.appendChild(emptyState);
            actionBtn.disabled = count < (tabSuffix === 'merge' ? 2 : 1);
        }

        actionBtn.addEventListener('click', async () => {
            const items = Array.from(fileList.querySelectorAll('li.file-item'));
            if (items.length < 1) return;

            const payloadFiles = items.map(li => {
                const obj = { id: li.dataset.id };
                if (tabSuffix === 'em') {
                    const input = li.querySelector('.range-input');
                    obj.ranges = input ? input.value : '';
                }
                return obj;
            });

            showStatus(tabSuffix === 'em' ? 'extract-merge' : 'merge', 'Processing...', 'info');
            actionBtn.disabled = true;

            try {
                const endpoint = tabSuffix === 'em' ? '/extract_merge' : '/merge';
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ files: payloadFiles })
                });

                if (response.ok) {
                    triggerDownload(await response.blob(), tabSuffix === 'em' ? 'Extracted_Merged.pdf' : 'Merged.pdf');
                    showStatus(tabSuffix === 'em' ? 'extract-merge' : 'merge', 'Success!', 'success');
                } else {
                    const err = await response.json();
                    showStatus(tabSuffix === 'em' ? 'extract-merge' : 'merge', err.error || 'Failed', 'error');
                }
            } catch (e) {
                showStatus(tabSuffix === 'em' ? 'extract-merge' : 'merge', 'Error processing files', 'error');
            } finally {
                actionBtn.disabled = false;
            }
        });
    }

    setupMultiFile('merge', 'template-merge-item');
    setupMultiFile('em', 'template-em-item');

    // --- Helpers ---
    function setupDropZone(zone, input, callback) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(e => {
            zone.addEventListener(e, ev => { ev.preventDefault(); ev.stopPropagation(); });
        });
        ['dragenter', 'dragover'].forEach(e => zone.addEventListener(e, () => zone.classList.add('bg-zinc-200')));
        ['dragleave', 'drop'].forEach(e => zone.addEventListener(e, () => zone.classList.remove('bg-zinc-200')));
        zone.addEventListener('drop', e => callback(e.dataTransfer.files));
        input.addEventListener('change', function() { callback(this.files); this.value = ''; });
    }

    function triggerDownload(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    }
});
