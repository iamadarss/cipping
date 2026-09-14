/**
 * UpClip Studio — YouTube Downloader Frontend Controller
 * Complete UI/UX implementation matching Studio Hub standards.
 */

(function() {
    'use strict';

    // =========================================================================
    // 1. Application State
    // =========================================================================
    const state = {
        currentTab: 'download',
        analysis: null,
        selectedFormat: { id: '1080p', type: 'video', quality: '1080p', ext: 'mp4' },
        playlistSelection: new Set(),
        activeTaskId: null,
        progressTimer: null,
        libraryFiles: [],
        libraryFilter: 'all',
        librarySearch: '',
    };

    // =========================================================================
    // 2. DOM Elements Cache
    // =========================================================================
    const dom = {
        // Navigation
        navTabs: document.querySelectorAll('#dlNavBar .desk-nav-tab'),
        tabPanes: document.querySelectorAll('.dl-tab-pane'),
        dlQueueBadge: document.getElementById('dlQueueBadge'),
        dlLibraryBadge: document.getElementById('dlLibraryBadge'),
        btnOpenInputFolder: document.getElementById('btnOpenInputFolder'),

        // Tab 1: Download
        inputYoutubeUrl: document.getElementById('inputYoutubeUrl'),
        btnPasteUrl: document.getElementById('btnPasteUrl'),
        btnAnalyzeUrl: document.getElementById('btnAnalyzeUrl'),
        urlValidationStatus: document.getElementById('urlValidationStatus'),
        analysisSkeleton: document.getElementById('analysisSkeleton'),

        // Video Analysis Result
        analysisResultCard: document.getElementById('analysisResultCard'),
        analysisThumbImg: document.getElementById('analysisThumbImg'),
        analysisDurationBadge: document.getElementById('analysisDurationBadge'),
        analysisVideoTitle: document.getElementById('analysisVideoTitle'),
        analysisChannelName: document.getElementById('analysisChannelName'),
        analysisViewsCount: document.getElementById('analysisViewsCount'),
        formatPillGrid: document.getElementById('formatPillGrid'),

        // Advanced Options
        btnToggleAdvanced: document.getElementById('btnToggleAdvanced'),
        advancedBody: document.getElementById('advancedBody'),
        advancedChevron: document.getElementById('advancedChevron'),
        advAudioBitrate: document.getElementById('advAudioBitrate'),
        advCustomFilename: document.getElementById('advCustomFilename'),
        chkEmbedSubs: document.getElementById('chkEmbedSubs'),
        btnStartDownload: document.getElementById('btnStartDownload'),
        btnStartDownloadText: document.getElementById('btnStartDownloadText'),

        // Playlist
        playlistCard: document.getElementById('playlistCard'),
        playlistTitle: document.getElementById('playlistTitle'),
        playlistMeta: document.getElementById('playlistMeta'),
        playlistItemsList: document.getElementById('playlistItemsList'),
        btnPlaylistSelectAll: document.getElementById('btnPlaylistSelectAll'),
        btnPlaylistClearAll: document.getElementById('btnPlaylistClearAll'),
        playlistSelectedCount: document.getElementById('playlistSelectedCount'),
        btnDownloadSelectedPlaylist: document.getElementById('btnDownloadSelectedPlaylist'),

        // Active Download Card
        activeDownloadProgressCard: document.getElementById('activeDownloadProgressCard'),
        activeDlTitle: document.getElementById('activeDlTitle'),
        activeDlFormat: document.getElementById('activeDlFormat'),
        activeDlProgressFill: document.getElementById('activeDlProgressFill'),
        activeDlPercent: document.getElementById('activeDlPercent'),
        activeDlSpeed: document.getElementById('activeDlSpeed'),
        activeDlEta: document.getElementById('activeDlEta'),
        btnCancelActiveDl: document.getElementById('btnCancelActiveDl'),

        // Tab 2: Queue
        btnRefreshQueue: document.getElementById('btnRefreshQueue'),
        dlQueueItemsContainer: document.getElementById('dlQueueItemsContainer'),

        // Tab 3: Library
        libraryFilterTabs: document.getElementById('libraryFilterTabs'),
        librarySearchInput: document.getElementById('librarySearchInput'),
        btnRefreshLibrary: document.getElementById('btnRefreshLibrary'),
        btnDeleteAllLibrary: document.getElementById('btnDeleteAllLibrary'),
        libraryTableBody: document.getElementById('libraryTableBody'),

        // Modals
        dlPreviewModal: document.getElementById('dlPreviewModal'),
        dlPreviewTitle: document.getElementById('dlPreviewTitle'),
        dlModalVideo: document.getElementById('dlModalVideo'),
        dlModalAudio: document.getElementById('dlModalAudio'),
        btnDlModalStudio: document.getElementById('btnDlModalStudio'),
        btnDlModalClose: document.getElementById('btnDlPreviewClose'),
        btnDlModalCloseFooter: document.getElementById('btnDlModalCloseFooter'),

        dlRenameModal: document.getElementById('dlRenameModal'),
        inputRenameFilename: document.getElementById('inputRenameFilename'),
        btnDlRenameCancel: document.getElementById('btnDlRenameCancel'),
        btnDlRenameConfirm: document.getElementById('btnDlRenameConfirm'),
        btnDlRenameClose: document.getElementById('btnDlRenameClose'),

        dlConfirmModal: document.getElementById('dlConfirmModal'),
        dlConfirmTitle: document.getElementById('dlConfirmTitle'),
        dlConfirmText: document.getElementById('dlConfirmText'),
        btnDlConfirmCancel: document.getElementById('btnDlConfirmCancel'),
        btnDlConfirmOk: document.getElementById('btnDlConfirmOk'),
        btnDlConfirmClose: document.getElementById('btnDlConfirmClose'),

        toastShelf: document.getElementById('dlToastShelf'),
    };

    // =========================================================================
    // 3. UI Helpers & Modals
    // =========================================================================
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast-pill ${type}`;
        const iconName = type === 'success' ? 'check-circle' : type === 'error' ? 'alert-circle' : 'info';
        toast.innerHTML = `<svg data-lucide="${iconName}" width="16" height="16"></svg><span>${escapeHtml(message)}</span>`;
        dom.toastShelf.appendChild(toast);
        if (window.lucide) window.lucide.createIcons();
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.25s ease reverse forwards';
            setTimeout(() => toast.remove(), 250);
        }, 3500);
    }

    function showConfirm(title, text) {
        return new Promise((resolve) => {
            dom.dlConfirmTitle.textContent = title;
            dom.dlConfirmText.textContent = text;
            dom.dlConfirmModal.classList.add('active');

            const cleanup = () => {
                dom.btnDlConfirmOk.removeEventListener('click', onOk);
                dom.btnDlConfirmCancel.removeEventListener('click', onCancel);
                dom.btnDlConfirmClose.removeEventListener('click', onCancel);
                dom.dlConfirmModal.classList.remove('active');
            };
            const onOk = () => { cleanup(); resolve(true); };
            const onCancel = () => { cleanup(); resolve(false); };

            dom.btnDlConfirmOk.addEventListener('click', onOk);
            dom.btnDlConfirmCancel.addEventListener('click', onCancel);
            dom.btnDlConfirmClose.addEventListener('click', onCancel);
        });
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str).replace(/[&<>"']/g, m => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[m]));
    }

    // =========================================================================
    // 4. Navigation & Tabs
    // =========================================================================
    function switchTab(tabName) {
        state.currentTab = tabName;

        dom.navTabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });

        dom.tabPanes.forEach(pane => {
            const isTarget = pane.id === `tab-${tabName}`;
            pane.style.display = isTarget ? 'block' : 'none';
            if (isTarget) pane.classList.add('active');
            else pane.classList.remove('active');
        });

        if (tabName === 'queue') loadQueue();
        if (tabName === 'library') loadLibrary();

        if (window.lucide) window.lucide.createIcons();
    }

    dom.navTabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // =========================================================================
    // 5. URL Validation & Analysis
    // =========================================================================
    const YT_REGEX = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|shorts\/|playlist\?list=)|youtu\.be\/)([a-zA-Z0-9_-]+)/i;

    function validateUrlInput() {
        const val = dom.inputYoutubeUrl.value.trim();
        if (!val) {
            dom.urlValidationStatus.innerHTML = '<span style="color:var(--text-muted);">Enter a valid YouTube URL to inspect available formats.</span>';
            dom.btnAnalyzeUrl.disabled = true;
            return false;
        }

        const isValid = YT_REGEX.test(val);
        if (isValid) {
            dom.urlValidationStatus.innerHTML = '<span style="color:var(--primary); font-weight:600;"><svg data-lucide="check" width="12" height="12" style="display:inline-block; vertical-align:middle;"></svg> Valid YouTube link detected. Click Analyze.</span>';
            dom.btnAnalyzeUrl.disabled = false;
        } else {
            dom.urlValidationStatus.innerHTML = '<span style="color:var(--warning);">Please enter a valid YouTube video, shorts, or playlist URL.</span>';
            dom.btnAnalyzeUrl.disabled = true;
        }
        if (window.lucide) window.lucide.createIcons();
        return isValid;
    }

    dom.inputYoutubeUrl.addEventListener('input', validateUrlInput);

    // Paste button
    dom.btnPasteUrl.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            if (text) {
                dom.inputYoutubeUrl.value = text.trim();
                if (validateUrlInput()) {
                    analyzeUrl();
                }
            }
        } catch (err) {
            dom.inputYoutubeUrl.focus();
        }
    });

    dom.btnAnalyzeUrl.addEventListener('click', analyzeUrl);

    async function analyzeUrl() {
        const url = dom.inputYoutubeUrl.value.trim();
        if (!url) return;

        // UI Loading state
        dom.btnAnalyzeUrl.disabled = true;
        dom.analysisSkeleton.style.display = 'block';
        dom.analysisResultCard.style.display = 'none';
        dom.playlistCard.style.display = 'none';

        try {
            const res = await fetch('/download/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            const data = await res.json();

            if (!res.ok || !data.success) {
                throw new Error(data.error || 'Failed to inspect YouTube URL');
            }

            state.analysis = data;

            if (data.is_playlist) {
                renderPlaylistCard(data);
            } else {
                renderVideoAnalysisCard(data);
            }

            showToast('URL analyzed successfully', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            dom.btnAnalyzeUrl.disabled = false;
            dom.analysisSkeleton.style.display = 'none';
        }
    }

    function renderVideoAnalysisCard(data) {
        dom.analysisResultCard.style.display = 'grid';
        dom.playlistCard.style.display = 'none';

        dom.analysisThumbImg.src = data.thumbnail || '';
        dom.analysisDurationBadge.textContent = data.duration_str || '0:00';
        dom.analysisVideoTitle.textContent = data.title || 'YouTube Video';
        dom.analysisChannelName.textContent = data.channel || 'Creator';
        dom.analysisViewsCount.textContent = data.view_count_str || '0 views';

        // Render Format Pills
        const formats = data.formats || [];
        dom.formatPillGrid.innerHTML = formats.map((f, idx) => `
            <div class="format-pill ${f.recommended ? 'active' : ''}" data-id="${f.id}" data-type="${f.type}" data-ext="${f.ext}">
                <div class="format-pill-res">${f.label}</div>
                <div class="format-pill-meta">${f.size} • ${f.ext}</div>
            </div>
        `).join('');

        // Select default format
        const defaultFmt = formats.find(f => f.recommended) || formats[0];
        if (defaultFmt) {
            state.selectedFormat = {
                id: defaultFmt.id,
                type: defaultFmt.type,
                quality: defaultFmt.id,
                ext: defaultFmt.ext
            };
        }

        dom.formatPillGrid.querySelectorAll('.format-pill').forEach(pill => {
            pill.addEventListener('click', () => {
                dom.formatPillGrid.querySelectorAll('.format-pill').forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                state.selectedFormat = {
                    id: pill.dataset.id,
                    type: pill.dataset.type,
                    quality: pill.dataset.id,
                    ext: pill.dataset.ext
                };
                updateDownloadButtonLabel();
            });
        });

        updateDownloadButtonLabel();
        if (window.lucide) window.lucide.createIcons();
    }

    function updateDownloadButtonLabel() {
        if (state.selectedFormat.type === 'audio') {
            dom.btnStartDownloadText.textContent = `Extract ${state.selectedFormat.id.toUpperCase()} Audio`;
        } else {
            dom.btnStartDownloadText.textContent = `Download Video (${state.selectedFormat.id})`;
        }
    }

    function renderPlaylistCard(data) {
        dom.playlistCard.style.display = 'block';
        dom.analysisResultCard.style.display = 'none';

        dom.playlistTitle.textContent = data.title || 'YouTube Playlist';
        dom.playlistMeta.textContent = `${data.video_count || 0} videos • by ${data.channel || 'Creator'}`;

        state.playlistSelection.clear();
        const entries = data.playlist_entries || [];

        dom.playlistItemsList.innerHTML = entries.map((entry, idx) => `
            <div class="compact-video-row" style="padding:10px; margin-bottom:4px;">
                <input type="checkbox" class="playlist-check" data-url="${escapeHtml(entry.url)}" data-title="${escapeHtml(entry.title)}" style="accent-color:var(--primary);" id="chk_pl_${idx}">
                <label for="chk_pl_${idx}" style="flex:1; display:flex; justify-content:space-between; cursor:pointer; font-size:13px; color:var(--text-primary); margin:0;">
                    <span style="font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:480px;">${escapeHtml(entry.title)}</span>
                    <span style="font-size:11px; color:var(--text-muted); font-family:var(--font-mono);">${entry.duration_str}</span>
                </label>
            </div>
        `).join('');

        dom.playlistItemsList.querySelectorAll('.playlist-check').forEach(chk => {
            chk.addEventListener('change', () => {
                if (chk.checked) state.playlistSelection.add(chk.dataset.url);
                else state.playlistSelection.delete(chk.dataset.url);
                updatePlaylistSelectionCount();
            });
        });

        updatePlaylistSelectionCount();
        if (window.lucide) window.lucide.createIcons();
    }

    function updatePlaylistSelectionCount() {
        dom.playlistSelectedCount.textContent = `${state.playlistSelection.size} videos selected`;
        dom.btnDownloadSelectedPlaylist.disabled = (state.playlistSelection.size === 0);
    }

    dom.btnPlaylistSelectAll.addEventListener('click', () => {
        dom.playlistItemsList.querySelectorAll('.playlist-check').forEach(chk => {
            chk.checked = true;
            state.playlistSelection.add(chk.dataset.url);
        });
        updatePlaylistSelectionCount();
    });

    dom.btnPlaylistClearAll.addEventListener('click', () => {
        dom.playlistItemsList.querySelectorAll('.playlist-check').forEach(chk => {
            chk.checked = false;
        });
        state.playlistSelection.clear();
        updatePlaylistSelectionCount();
    });

    // Advanced Options Accordion Toggle
    dom.btnToggleAdvanced.addEventListener('click', () => {
        const isHidden = dom.advancedBody.style.display === 'none';
        dom.advancedBody.style.display = isHidden ? 'block' : 'none';
        dom.advancedChevron.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
    });

    // =========================================================================
    // 6. Download Execution & Progress Tracking (Sections 20 & 21)
    // =========================================================================
    dom.btnStartDownload.addEventListener('click', async () => {
        if (!state.analysis) return;
        const url = dom.inputYoutubeUrl.value.trim();
        const fmt = state.selectedFormat.type;
        const quality = state.selectedFormat.quality;
        const audioFormat = (fmt === 'audio') ? quality : 'mp3';

        const customName = dom.advCustomFilename.value.trim();
        const titleHint = customName || state.analysis.title || 'YouTube Video';

        await triggerDownloadTask({
            url,
            format: fmt,
            quality: quality,
            audio_format: audioFormat,
            title: titleHint,
            async: true
        });
    });

    dom.btnDownloadSelectedPlaylist.addEventListener('click', async () => {
        if (state.playlistSelection.size === 0) return;
        const confirmed = await showConfirm(
            'Download Playlist Videos',
            `Start downloading ${state.playlistSelection.size} selected videos from this playlist?`
        );
        if (!confirmed) return;

        showToast(`Queueing ${state.playlistSelection.size} downloads...`, 'info');
        for (const url of state.playlistSelection) {
            await triggerDownloadTask({
                url,
                format: 'video',
                quality: 'best',
                async: true
            });
        }
        switchTab('queue');
    });

    async function triggerDownloadTask(payload) {
        try {
            const res = await fetch('/download/youtube', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (!res.ok || !data.success) {
                throw new Error(data.error || 'Failed to start download');
            }

            state.activeTaskId = data.task_id;
            dom.activeDownloadProgressCard.style.display = 'block';
            dom.activeDlTitle.textContent = payload.title || 'YouTube Video';
            dom.activeDlFormat.textContent = `${payload.quality} ${payload.format}`;
            dom.activeDlProgressFill.style.width = '5%';
            dom.activeDlPercent.textContent = '5%';
            dom.activeDlSpeed.textContent = 'Connecting...';
            dom.activeDlEta.textContent = 'ETA: calculating...';

            startProgressPolling(data.task_id);
            showToast('Download started', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    function startProgressPolling(taskId) {
        if (state.progressTimer) clearInterval(state.progressTimer);

        state.progressTimer = setInterval(async () => {
            try {
                const res = await fetch(`/download/progress/${taskId}`);
                const data = await res.json();

                if (!res.ok || !data.success || !data.task) {
                    clearInterval(state.progressTimer);
                    return;
                }

                const t = data.task;

                // Update active progress card
                dom.activeDlProgressFill.style.width = `${Math.min(100, t.percent || 0)}%`;
                dom.activeDlPercent.textContent = `${t.percent || 0}%`;
                dom.activeDlSpeed.textContent = t.speed_str || 'Downloading...';
                dom.activeDlEta.textContent = `ETA: ${t.eta_str || '--:--'}`;

                if (t.status === 'completed') {
                    clearInterval(state.progressTimer);
                    dom.activeDlProgressFill.style.width = '100%';
                    dom.activeDlPercent.textContent = '100%';
                    dom.activeDlSpeed.textContent = 'Download Complete!';
                    dom.activeDlEta.textContent = t.size_str || '';
                    showToast(`✓ Download completed: ${t.filename || ''}`, 'success');

                    setTimeout(() => {
                        dom.activeDownloadProgressCard.style.display = 'none';
                        loadLibrary();
                    }, 2500);
                } else if (t.status === 'error' || t.status === 'cancelled') {
                    clearInterval(state.progressTimer);
                    dom.activeDlSpeed.textContent = t.status === 'cancelled' ? 'Cancelled' : 'Failed';
                    showToast(t.error || 'Download was stopped.', 'error');
                }
            } catch (err) {
                console.warn('Progress poll error:', err);
            }
        }, 1000);
    }

    dom.btnCancelActiveDl.addEventListener('click', async () => {
        if (!state.activeTaskId) return;
        await fetch(`/download/cancel/${state.activeTaskId}`, { method: 'POST' });
        dom.activeDownloadProgressCard.style.display = 'none';
        if (state.progressTimer) clearInterval(state.progressTimer);
        showToast('Download cancelled', 'info');
    });

    // =========================================================================
    // 7. Queue & Library Management (Sections 21 & 22)
    // =========================================================================
    async function loadQueue() {
        dom.dlQueueItemsContainer.innerHTML = '<div style="text-align:center; padding:24px; color:var(--text-muted);">Checking active downloads...</div>';
        try {
            const res = await fetch('/download/queue');
            const data = await res.json();
            const queue = data.queue || [];
            dom.dlQueueBadge.textContent = queue.filter(q => q.status === 'downloading' || q.status === 'queued').length;

            if (queue.length === 0) {
                dom.dlQueueItemsContainer.innerHTML = `
                    <div class="compact-empty-state">
                        <svg data-lucide="layers" width="32" height="32"></svg>
                        <h4>Download Queue is Empty</h4>
                        <p>No active or pending download tasks in UpClip Studio.</p>
                        <button class="btn btn-primary btn-sm" onclick="document.querySelector('#dlNavBar button[data-tab=download]').click()">Download a Video</button>
                    </div>`;
                return;
            }

            dom.dlQueueItemsContainer.innerHTML = queue.map(q => `
                <div class="dl-queue-card">
                    <div style="display:flex; align-items:center; justify-content:space-between;">
                        <h4 style="font-size:14px; font-weight:700; color:var(--text-primary); margin:0;">${escapeHtml(q.title || 'YouTube Media')}</h4>
                        <span class="status-pill ${q.status === 'completed' ? 'connected' : q.status === 'error' ? 'disconnected' : ''}">${q.status}</span>
                    </div>
                    <div class="dl-progress-bar-wrap">
                        <div class="dl-progress-bar-fill" style="width:${q.percent || 0}%;"></div>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:11px; color:var(--text-muted);">
                        <span>${q.percent || 0}% • ${q.format} (${q.quality})</span>
                        <span>${q.speed_str || ''}</span>
                    </div>
                </div>
            `).join('');

            if (window.lucide) window.lucide.createIcons();
        } catch (err) {
            dom.dlQueueItemsContainer.innerHTML = `<div style="color:var(--error); padding:16px;">Failed to load queue: ${err.message}</div>`;
        }
    }

    dom.btnRefreshQueue.addEventListener('click', loadQueue);

    async function loadLibrary() {
        dom.libraryTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:32px; color:var(--text-muted);">Loading media library...</td></tr>';
        try {
            const res = await fetch('/download/downloaded');
            const data = await res.json();
            state.libraryFiles = data.files || [];
            dom.dlLibraryBadge.textContent = state.libraryFiles.length;

            renderLibraryTable();
        } catch (err) {
            dom.libraryTableBody.innerHTML = `<tr><td colspan="5" style="color:var(--error); padding:20px;">Failed to load media library: ${err.message}</td></tr>`;
        }
    }

    function renderLibraryTable() {
        let files = state.libraryFiles;

        if (state.libraryFilter === 'video') files = files.filter(f => !f.is_audio);
        if (state.libraryFilter === 'audio') files = files.filter(f => f.is_audio);

        if (state.librarySearch) {
            const q = state.librarySearch.toLowerCase();
            files = files.filter(f => f.name.toLowerCase().includes(q));
        }

        if (files.length === 0) {
            dom.libraryTableBody.innerHTML = `
                <tr><td colspan="5">
                    <div class="compact-empty-state">
                        <svg data-lucide="folder-open" width="32" height="32"></svg>
                        <h4>No Media Files Found</h4>
                        <p>Downloaded videos and audio tracks stored in your <code>input/</code> folder will appear here.</p>
                    </div>
                </td></tr>`;
            if (window.lucide) window.lucide.createIcons();
            return;
        }

        dom.libraryTableBody.innerHTML = files.map(f => `
            <tr>
                <td>
                    <div style="width:32px; height:32px; border-radius:var(--radius-xs); background:var(--surface-1); border:1px solid var(--border); display:flex; align-items:center; justify-content:center; color:${f.is_audio ? 'var(--info)' : 'var(--primary)'};">
                        <svg data-lucide="${f.is_audio ? 'music' : 'clapperboard'}" width="16" height="16"></svg>
                    </div>
                </td>
                <td style="font-weight:600; color:var(--text-primary); max-width:320px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                    ${escapeHtml(f.name)}
                </td>
                <td>${f.size}</td>
                <td>${f.modified}</td>
                <td style="text-align:right;">
                    <div style="display:inline-flex; gap:6px;">
                        <button class="btn btn-secondary btn-sm btn-lib-preview" data-name="${escapeHtml(f.name)}" data-path="${f.path}" data-audio="${f.is_audio}" title="Play preview" style="padding:4px 8px;">
                            <svg data-lucide="play" width="13" height="13"></svg>
                        </button>
                        <a href="/dashboard?file=${encodeURIComponent(f.name)}" class="btn btn-primary btn-sm" title="Open in AI Clip Studio" style="padding:4px 8px; text-decoration:none;">
                            <svg data-lucide="wand-sparkles" width="13" height="13"></svg>
                        </a>
                        <button class="btn btn-secondary btn-sm btn-lib-rename" data-name="${escapeHtml(f.name)}" title="Rename" style="padding:4px 8px;">
                            <svg data-lucide="edit-3" width="13" height="13"></svg>
                        </button>
                        <button class="btn btn-outline btn-sm btn-lib-delete" data-name="${escapeHtml(f.name)}" title="Delete" style="padding:4px 8px; color:var(--error); border-color:rgba(239,68,68,0.3);">
                            <svg data-lucide="trash" width="13" height="13"></svg>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        // Wire Action Events
        dom.libraryTableBody.querySelectorAll('.btn-lib-preview').forEach(btn => {
            btn.addEventListener('click', () => {
                const name = btn.dataset.name;
                const path = btn.dataset.path;
                const isAudio = btn.dataset.audio === 'true';

                dom.dlPreviewTitle.textContent = name;
                dom.btnDlModalStudio.href = `/dashboard?file=${encodeURIComponent(name)}`;

                if (isAudio) {
                    dom.dlModalVideo.style.display = 'none';
                    dom.dlModalAudio.src = path;
                    dom.dlModalAudio.style.display = 'block';
                    dom.dlModalAudio.play();
                } else {
                    dom.dlModalAudio.style.display = 'none';
                    dom.dlModalVideo.src = path;
                    dom.dlModalVideo.style.display = 'block';
                    dom.dlModalVideo.play();
                }

                dom.dlPreviewModal.classList.add('active');
            });
        });

        dom.libraryTableBody.querySelectorAll('.btn-lib-rename').forEach(btn => {
            btn.addEventListener('click', () => {
                const oldName = btn.dataset.name;
                dom.inputRenameFilename.value = oldName;
                dom.dlRenameModal.classList.add('active');

                const onConfirm = async () => {
                    const newName = dom.inputRenameFilename.value.trim();
                    if (newName && newName !== oldName) {
                        try {
                            const res = await fetch('/download/rename', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ old_name: oldName, new_name: newName })
                            });
                            const data = await res.json();
                            if (data.success) {
                                showToast('File renamed', 'success');
                                loadLibrary();
                            } else {
                                throw new Error(data.error || 'Rename failed');
                            }
                        } catch (err) {
                            showToast(err.message, 'error');
                        }
                    }
                    dom.dlRenameModal.classList.remove('active');
                };

                dom.btnDlRenameConfirm.onclick = onConfirm;
            });
        });

        dom.libraryTableBody.querySelectorAll('.btn-lib-delete').forEach(btn => {
            btn.addEventListener('click', async () => {
                const filename = btn.dataset.name;
                const confirmed = await showConfirm('Delete File', `Are you sure you want to delete "${filename}" from your workspace?`);
                if (confirmed) {
                    try {
                        const res = await fetch('/download/delete', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ filename })
                        });
                        const data = await res.json();
                        if (data.success) {
                            showToast('File deleted', 'info');
                            loadLibrary();
                        } else {
                            throw new Error(data.error || 'Delete failed');
                        }
                    } catch (err) {
                        showToast(err.message, 'error');
                    }
                }
            });
        });

        if (window.lucide) window.lucide.createIcons();
    }

    // Modal Close buttons
    dom.btnDlModalClose.addEventListener('click', () => {
        dom.dlModalVideo.pause();
        dom.dlModalAudio.pause();
        dom.dlPreviewModal.classList.remove('active');
    });
    dom.btnDlModalCloseFooter.addEventListener('click', () => {
        dom.dlModalVideo.pause();
        dom.dlModalAudio.pause();
        dom.dlPreviewModal.classList.remove('active');
    });

    dom.btnDlRenameCancel.addEventListener('click', () => dom.dlRenameModal.classList.remove('active'));
    dom.btnDlRenameClose.addEventListener('click', () => dom.dlRenameModal.classList.remove('active'));

    dom.btnOpenInputFolder.addEventListener('click', async () => {
        try {
            await fetch('/download/open-folder');
            showToast('Opening input folder in file explorer', 'info');
        } catch (err) {
            showToast('Could not open folder: ' + err.message, 'error');
        }
    });

    dom.btnRefreshLibrary.addEventListener('click', loadLibrary);

    dom.btnDeleteAllLibrary.addEventListener('click', async () => {
        const confirmed = await showConfirm('Delete All Downloaded Media', 'Are you sure you want to delete ALL source files in the input library? This action cannot be undone.');
        if (confirmed) {
            try {
                const res = await fetch('/download/delete-all', { method: 'POST' });
                const data = await res.json();
                if (data.success) {
                    showToast(`Deleted ${data.count} files`, 'info');
                    loadLibrary();
                } else {
                    throw new Error(data.error || 'Failed to delete all');
                }
            } catch (err) {
                showToast(err.message, 'error');
            }
        }
    });

    dom.libraryFilterTabs.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            dom.libraryFilterTabs.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            state.libraryFilter = tab.dataset.filter;
            renderLibraryTable();
        });
    });

    dom.librarySearchInput.addEventListener('input', (e) => {
        state.librarySearch = e.target.value;
        renderLibraryTable();
    });

    // =========================================================================
    // 8. Initialization
    // =========================================================================
    function init() {
        switchTab(state.currentTab);
        loadLibrary();
    }

    init();

})();
