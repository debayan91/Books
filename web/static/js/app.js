/**
 * PDF Toolkit Pro - Black & White Glassmorphic Application Logic
 * Strictly Light Mode with Thin Typography
 */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // Monochrome Toast Notification System
    // =========================================================================
    const toastContainer = document.getElementById('toast-container');

    function showToast(message, type = 'info', durationMs = 4000) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        
        let iconSvg = '';
        if (type === 'success') {
            iconSvg = `<svg class="w-4 h-4 text-black shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>`;
        } else if (type === 'error') {
            iconSvg = `<svg class="w-4 h-4 text-black shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>`;
        } else {
            iconSvg = `<svg class="w-4 h-4 text-black shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
        }

        toast.innerHTML = `${iconSvg}<span>${message}</span>`;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px) scale(0.95)';
            setTimeout(() => toast.remove(), 250);
        }, durationMs);
    }

    // Helper: Trigger file download in browser
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

    // Helper: Upload file to /upload
    async function uploadPdf(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            throw new Error('Only valid .pdf files are supported.');
        }
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch('/upload', { method: 'POST', body: formData });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.error || 'Failed to upload document.');
        }
        return data;
    }

    // Helper: Setup drag-and-drop zone
    function setupDropZone(dropEl, inputEl, onFiles) {
        ['dragenter', 'dragover'].forEach(name => {
            dropEl.addEventListener(name, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropEl.classList.add('drag-active');
            });
        });
        ['dragleave', 'drop'].forEach(name => {
            dropEl.addEventListener(name, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropEl.classList.remove('drag-active');
            });
        });
        dropEl.addEventListener('drop', (e) => {
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                onFiles(e.dataTransfer.files);
            }
        });
        dropEl.addEventListener('click', () => inputEl.click());
        inputEl.addEventListener('change', () => {
            if (inputEl.files && inputEl.files.length > 0) {
                onFiles(inputEl.files);
                inputEl.value = '';
            }
        });
    }

    // =========================================================================
    // Tab Navigation
    // =========================================================================
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.tab;
            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanels.forEach(p => p.classList.add('hidden'));

            btn.classList.add('active');
            const targetPanel = document.getElementById(`panel-${target}`);
            if (targetPanel) targetPanel.classList.remove('hidden');
        });
    });

    // =========================================================================
    // TAB 1: EXTRACT & SPLIT
    // =========================================================================
    const dropExtract = document.getElementById('drop-extract');
    const inputExtract = document.getElementById('input-extract');
    const cardExtract = document.getElementById('card-extract');
    const filenameExtract = document.getElementById('filename-extract');
    const pagesExtract = document.getElementById('pages-extract');
    const sizeExtract = document.getElementById('size-extract');
    const clearExtract = document.getElementById('clear-extract');
    const rangesExtract = document.getElementById('ranges-extract');
    const btnRunExtract = document.getElementById('btn-run-extract');

    let currentExtractFile = null;

    setupDropZone(dropExtract, inputExtract, async (files) => {
        try {
            showToast('Analyzing document...', 'info', 2000);
            const data = await uploadPdf(files[0]);
            currentExtractFile = data;
            filenameExtract.textContent = data.filename;
            pagesExtract.textContent = `Pages: ${data.total_pages}`;
            sizeExtract.textContent = `Size: ${data.size_human}`;

            dropExtract.classList.add('hidden');
            cardExtract.classList.remove('hidden');
            btnRunExtract.disabled = false;
            showToast(`Loaded ${data.filename}`, 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    clearExtract.addEventListener('click', () => {
        currentExtractFile = null;
        cardExtract.classList.add('hidden');
        dropExtract.classList.remove('hidden');
        btnRunExtract.disabled = true;
    });

    btnRunExtract.addEventListener('click', async () => {
        if (!currentExtractFile) return;
        const mode = document.querySelector('input[name="mode-extract"]:checked').value;
        const ranges = rangesExtract.value.trim();

        btnRunExtract.disabled = true;
        btnRunExtract.innerHTML = `<span class="spinner-bw mr-2"></span><span>Processing...</span>`;

        try {
            const res = await fetch('/extract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file: currentExtractFile.id, ranges: ranges, mode: mode })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Extraction failed.');
            }

            const blob = await res.blob();
            const ext = mode === 'split' ? '.zip' : '.pdf';
            const baseName = currentExtractFile.filename.replace(/\.pdf$/i, '');
            const dlName = mode === 'split' ? `Split_${baseName}${ext}` : `Extracted_${baseName}${ext}`;
            triggerDownload(blob, dlName);
            showToast(mode === 'split' ? 'Document split into ZIP!' : 'Extraction complete!', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btnRunExtract.disabled = false;
            btnRunExtract.innerHTML = `<span>Execute Extraction</span>`;
        }
    });

    // =========================================================================
    // TAB 2: MERGE PDFS
    // =========================================================================
    const dropMerge = document.getElementById('drop-merge');
    const inputMerge = document.getElementById('input-merge');
    const listMerge = document.getElementById('list-merge');
    const emptyMerge = document.getElementById('empty-merge');
    const mergeCountBadge = document.getElementById('merge-count-badge');
    const btnRunMerge = document.getElementById('btn-run-merge');

    let mergeFiles = [];

    new Sortable(listMerge, {
        animation: 180,
        handle: '.drag-handle',
        onEnd: () => {
            const items = listMerge.querySelectorAll('.merge-item');
            const newOrder = [];
            items.forEach(it => {
                const fid = it.dataset.id;
                const found = mergeFiles.find(f => f.id === fid);
                if (found) newOrder.push(found);
            });
            mergeFiles = newOrder;
        }
    });

    setupDropZone(dropMerge, inputMerge, async (files) => {
        let added = 0;
        showToast(`Loading ${files.length} document(s)...`, 'info', 2000);

        for (let i = 0; i < files.length; i++) {
            try {
                const data = await uploadPdf(files[i]);
                mergeFiles.push(data);
                renderMergeItem(data);
                added++;
            } catch (err) {
                showToast(`Failed: ${files[i].name} (${err.message})`, 'error');
            }
        }
        updateMergeState();
        if (added > 0) showToast(`Added ${added} files to merge list.`, 'success');
    });

    function renderMergeItem(file) {
        if (emptyMerge.parentNode === listMerge) {
            listMerge.removeChild(emptyMerge);
        }
        const li = document.createElement('li');
        li.className = 'merge-item flex items-center justify-between p-3.5 rounded-xl glass-nested';
        li.dataset.id = file.id;

        li.innerHTML = `
            <div class="flex items-center space-x-3.5 truncate">
                <div class="drag-handle cursor-grab text-zinc-400 hover:text-black transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 8h16M4 16h16"></path></svg>
                </div>
                <div class="truncate">
                    <p class="text-xs font-normal text-black truncate">${file.filename}</p>
                    <p class="text-[10px] font-light text-zinc-500">${file.total_pages} pages • ${file.size_human}</p>
                </div>
            </div>
            <button class="btn-remove-merge text-xs text-zinc-400 hover:text-black p-1.5 rounded transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        `;

        li.querySelector('.btn-remove-merge').addEventListener('click', () => {
            li.remove();
            mergeFiles = mergeFiles.filter(f => f.id !== file.id);
            updateMergeState();
        });

        listMerge.appendChild(li);
    }

    function updateMergeState() {
        mergeCountBadge.textContent = `${mergeFiles.length} file(s) added`;
        if (mergeFiles.length === 0 && !listMerge.contains(emptyMerge)) {
            listMerge.appendChild(emptyMerge);
        }
        btnRunMerge.disabled = mergeFiles.length < 2;
    }

    btnRunMerge.addEventListener('click', async () => {
        if (mergeFiles.length < 2) return;
        btnRunMerge.disabled = true;
        btnRunMerge.innerHTML = `<span class="spinner-bw mr-2"></span><span>Merging ${mergeFiles.length} Documents...</span>`;

        try {
            const ids = mergeFiles.map(f => f.id);
            const res = await fetch('/merge', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files: ids })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Merge failed.');
            }

            const blob = await res.blob();
            triggerDownload(blob, 'Merged_Document.pdf');
            showToast('Documents merged successfully!', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btnRunMerge.disabled = false;
            btnRunMerge.innerHTML = `<span>Merge Documents</span>`;
        }
    });

    // =========================================================================
    // TAB 3: EXTRACT & MERGE
    // =========================================================================
    const dropEm = document.getElementById('drop-em');
    const inputEm = document.getElementById('input-em');
    const listEm = document.getElementById('list-em');
    const emptyEm = document.getElementById('empty-em');
    const emCountBadge = document.getElementById('em-count-badge');
    const btnRunEm = document.getElementById('btn-run-em');

    let emFiles = [];

    new Sortable(listEm, {
        animation: 180,
        handle: '.drag-handle',
        onEnd: () => {
            const items = listEm.querySelectorAll('.em-item');
            const newOrder = [];
            items.forEach(it => {
                const fid = it.dataset.id;
                const found = emFiles.find(f => f.id === fid);
                if (found) newOrder.push(found);
            });
            emFiles = newOrder;
        }
    });

    setupDropZone(dropEm, inputEm, async (files) => {
        for (let i = 0; i < files.length; i++) {
            try {
                const data = await uploadPdf(files[i]);
                emFiles.push(data);
                renderEmItem(data);
            } catch (err) {
                showToast(`Failed: ${files[i].name}`, 'error');
            }
        }
        updateEmState();
    });

    function renderEmItem(file) {
        if (emptyEm.parentNode === listEm) {
            listEm.removeChild(emptyEm);
        }
        const li = document.createElement('li');
        li.className = 'em-item p-4 rounded-xl glass-nested space-y-2.5';
        li.dataset.id = file.id;

        li.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3.5 truncate">
                    <div class="drag-handle cursor-grab text-zinc-400 hover:text-black transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 8h16M4 16h16"></path></svg>
                    </div>
                    <div class="truncate">
                        <p class="text-xs font-normal text-black truncate">${file.filename}</p>
                        <p class="text-[10px] font-light text-zinc-500">${file.total_pages} pages</p>
                    </div>
                </div>
                <button class="btn-remove-em text-xs text-zinc-400 hover:text-black p-1.5 rounded transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>
            <div class="pl-7">
                <input type="text" class="em-ranges glass-input w-full rounded-lg px-3 py-1.5 text-xs placeholder:text-zinc-400" placeholder="Page ranges (e.g. 1-3, 5) or leave empty for all">
            </div>
        `;

        li.querySelector('.btn-remove-em').addEventListener('click', () => {
            li.remove();
            emFiles = emFiles.filter(f => f.id !== file.id);
            updateEmState();
        });

        listEm.appendChild(li);
    }

    function updateEmState() {
        emCountBadge.textContent = `${emFiles.length} file(s) added`;
        if (emFiles.length === 0 && !listEm.contains(emptyEm)) {
            listEm.appendChild(emptyEm);
        }
        btnRunEm.disabled = emFiles.length < 1;
    }

    btnRunEm.addEventListener('click', async () => {
        if (emFiles.length < 1) return;
        btnRunEm.disabled = true;
        btnRunEm.innerHTML = `<span class="spinner-bw mr-2"></span><span>Processing Extract & Merge...</span>`;

        try {
            const items = listEm.querySelectorAll('.em-item');
            const payload = [];
            items.forEach(it => {
                const fid = it.dataset.id;
                const ranges = it.querySelector('.em-ranges').value.trim();
                payload.push({ id: fid, ranges: ranges });
            });

            const res = await fetch('/extract_merge', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files: payload })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Extract & merge failed.');
            }

            const blob = await res.blob();
            triggerDownload(blob, 'Extracted_Merged_Document.pdf');
            showToast('Extract and merge complete!', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btnRunEm.disabled = false;
            btnRunEm.innerHTML = `<span>Extract & Merge All</span>`;
        }
    });

    // =========================================================================
    // TAB 4: 3-UP A4 PRINT PREP
    // =========================================================================
    const drop3up = document.getElementById('drop-3up');
    const input3up = document.getElementById('input-3up');
    const card3up = document.getElementById('card-3up');
    const filename3up = document.getElementById('filename-3up');
    const pages3up = document.getElementById('pages-3up');
    const estimate3up = document.getElementById('estimate-3up');
    const clear3up = document.getElementById('clear-3up');
    const btnRun3up = document.getElementById('btn-run-3up');
    const nupBtns = document.querySelectorAll('.btn-nup');
    const savingsBadge3up = document.getElementById('savings-badge-3up');

    let current3upFile = null;
    let selectedCols = 3;

    nupBtns.forEach(b => {
        b.addEventListener('click', () => {
            nupBtns.forEach(btn => {
                btn.className = 'btn-nup glass-nested p-3.5 rounded-xl text-center text-xs font-light';
            });
            b.className = 'btn-nup p-3.5 rounded-xl text-center text-xs font-normal bg-black text-white border border-black shadow-sm';
            selectedCols = parseInt(b.dataset.cols);
            update3upEstimate();
        });
    });

    setupDropZone(drop3up, input3up, async (files) => {
        try {
            showToast('Analyzing book layout...', 'info', 2000);
            const data = await uploadPdf(files[0]);
            current3upFile = data;
            filename3up.textContent = data.filename;
            pages3up.textContent = `Pages: ${data.total_pages}`;

            update3upEstimate();

            drop3up.classList.add('hidden');
            card3up.classList.remove('hidden');
            btnRun3up.disabled = false;
            showToast(`Loaded book: ${data.filename}`, 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    function update3upEstimate() {
        if (!current3upFile) return;
        const total = current3upFile.total_pages;
        const sheets = Math.ceil(total / selectedCols);
        estimate3up.textContent = `Estimated sheets: ${sheets} A4 landscape`;
        const savings = (1.0 - (sheets / total)) * 100;
        savingsBadge3up.textContent = `~${savings.toFixed(1)}% fewer pages`;
    }

    clear3up.addEventListener('click', () => {
        current3upFile = null;
        card3up.classList.add('hidden');
        drop3up.classList.remove('hidden');
        btnRun3up.disabled = true;
    });

    btnRun3up.addEventListener('click', async () => {
        if (!current3upFile) return;
        btnRun3up.disabled = true;
        btnRun3up.innerHTML = `<span class="spinner-bw mr-2"></span><span>Transforming Layout...</span>`;

        try {
            const res = await fetch('/api/3up', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file: current3upFile.id, cols: selectedCols })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Imposition failed.');
            }

            const blob = await res.blob();
            const baseName = current3upFile.filename.replace(/\.pdf$/i, '');
            triggerDownload(blob, `${baseName}_${selectedCols}up_a4.pdf`);
            showToast(`${selectedCols}-Up imposition generated successfully!`, 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btnRun3up.disabled = false;
            btnRun3up.innerHTML = `<span>Generate 3-Up Print PDF</span>`;
        }
    });

    // =========================================================================
    // TAB 5: PDF TO WORD (DOCX)
    // =========================================================================
    const dropDocx = document.getElementById('drop-docx');
    const inputDocx = document.getElementById('input-docx');
    const cardDocx = document.getElementById('card-docx');
    const filenameDocx = document.getElementById('filename-docx');
    const pagesDocx = document.getElementById('pages-docx');
    const clearDocx = document.getElementById('clear-docx');
    const startDocx = document.getElementById('start-docx');
    const endDocx = document.getElementById('end-docx');
    const btnRunDocx = document.getElementById('btn-run-docx');

    let currentDocxFile = null;

    setupDropZone(dropDocx, inputDocx, async (files) => {
        try {
            showToast('Loading document...', 'info', 2000);
            const data = await uploadPdf(files[0]);
            currentDocxFile = data;
            filenameDocx.textContent = data.filename;
            pagesDocx.textContent = `Pages: ${data.total_pages}`;

            dropDocx.classList.add('hidden');
            cardDocx.classList.remove('hidden');
            btnRunDocx.disabled = false;
            showToast(`Ready to convert ${data.filename}`, 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    clearDocx.addEventListener('click', () => {
        currentDocxFile = null;
        cardDocx.classList.add('hidden');
        dropDocx.classList.remove('hidden');
        btnRunDocx.disabled = true;
    });

    btnRunDocx.addEventListener('click', async () => {
        if (!currentDocxFile) return;
        btnRunDocx.disabled = true;
        btnRunDocx.innerHTML = `<span class="spinner-bw mr-2"></span><span>Converting to DOCX...</span>`;

        try {
            const startVal = startDocx.value ? parseInt(startDocx.value) - 1 : 0;
            const endVal = endDocx.value ? parseInt(endDocx.value) : null;

            const res = await fetch('/api/to_docx', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file: currentDocxFile.id, start_page: startVal, end_page: endVal })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Conversion failed.');
            }

            const blob = await res.blob();
            const baseName = currentDocxFile.filename.replace(/\.pdf$/i, '');
            triggerDownload(blob, `${baseName}.docx`);
            showToast('Converted to Microsoft Word document!', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btnRunDocx.disabled = false;
            btnRunDocx.innerHTML = `<span>Convert to Microsoft Word</span>`;
        }
    });

    // =========================================================================
    // TAB 6: COMPRESS PDF
    // =========================================================================
    const dropCompress = document.getElementById('drop-compress');
    const inputCompress = document.getElementById('input-compress');
    const cardCompress = document.getElementById('card-compress');
    const filenameCompress = document.getElementById('filename-compress');
    const pagesCompress = document.getElementById('pages-compress');
    const sizeCompress = document.getElementById('size-compress');
    const clearCompress = document.getElementById('clear-compress');
    const btnRunCompress = document.getElementById('btn-run-compress');

    let currentCompressFile = null;

    setupDropZone(dropCompress, inputCompress, async (files) => {
        try {
            showToast('Analyzing compression targets...', 'info', 2000);
            const data = await uploadPdf(files[0]);
            currentCompressFile = data;
            filenameCompress.textContent = data.filename;
            pagesCompress.textContent = `Pages: ${data.total_pages}`;
            sizeCompress.textContent = `Current size: ${data.size_human}`;

            dropCompress.classList.add('hidden');
            cardCompress.classList.remove('hidden');
            btnRunCompress.disabled = false;
            showToast(`Loaded ${data.filename}`, 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    clearCompress.addEventListener('click', () => {
        currentCompressFile = null;
        cardCompress.classList.add('hidden');
        dropCompress.classList.remove('hidden');
        btnRunCompress.disabled = true;
    });

    btnRunCompress.addEventListener('click', async () => {
        if (!currentCompressFile) return;
        const level = document.querySelector('input[name="level-compress"]:checked').value;

        btnRunCompress.disabled = true;
        btnRunCompress.innerHTML = `<span class="spinner-bw mr-2"></span><span>Optimizing PDF...</span>`;

        try {
            const res = await fetch('/compress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file: currentCompressFile.id, level: level })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Compression failed.');
            }

            const reductionPct = res.headers.get('X-Reduction-Pct') || '0';
            const blob = await res.blob();
            const baseName = currentCompressFile.filename.replace(/\.pdf$/i, '');
            triggerDownload(blob, `Compressed_${baseName}.pdf`);

            showToast(`Compression complete: reduced by ${reductionPct}%!`, 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btnRunCompress.disabled = false;
            btnRunCompress.innerHTML = `<span>Compress Document</span>`;
        }
    });

    // =========================================================================
    // TAB 7: PDF INSPECTOR
    // =========================================================================
    const dropInspector = document.getElementById('drop-inspector');
    const inputInspector = document.getElementById('input-inspector');
    const inspectorPlaceholder = document.getElementById('inspector-placeholder');
    const inspectorContent = document.getElementById('inspector-content');

    const inspPages = document.getElementById('insp-pages');
    const inspSize = document.getElementById('insp-size');
    const inspFormat = document.getElementById('insp-format');
    const inspEncrypted = document.getElementById('insp-encrypted');
    const inspTitle = document.getElementById('insp-title');
    const inspAuthor = document.getElementById('insp-author');
    const inspProducer = document.getElementById('insp-producer');
    const inspDims = document.getElementById('insp-dims');

    setupDropZone(dropInspector, inputInspector, async (files) => {
        try {
            showToast('Inspecting document metadata...', 'info', 2000);
            const uploadData = await uploadPdf(files[0]);

            const res = await fetch('/info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file: uploadData.id })
            });
            const info = await res.json();

            inspPages.textContent = info.total_pages;
            inspSize.textContent = info.file_size_human;
            inspFormat.textContent = info.first_page ? info.first_page.paper_size : 'Unknown';
            inspEncrypted.textContent = info.is_encrypted ? 'Password Protected' : 'None';
            inspEncrypted.className = info.is_encrypted ? 'text-lg font-light text-zinc-900 mt-0.5' : 'text-lg font-light text-black mt-0.5';

            inspTitle.textContent = info.title || '(Not specified)';
            inspAuthor.textContent = info.author || '(Not specified)';
            inspProducer.textContent = info.producer || '(Not specified)';

            if (info.first_page) {
                inspDims.textContent = `${info.first_page.width_mm} × ${info.first_page.height_mm} mm (${info.first_page.width_pt} × ${info.first_page.height_pt} pt) [${info.first_page.orientation}]`;
            } else {
                inspDims.textContent = 'N/A';
            }

            inspectorPlaceholder.classList.add('hidden');
            inspectorContent.classList.remove('hidden');
            showToast('Document inspected successfully!', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

});
