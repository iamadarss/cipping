/**
 * UpClip Studio — YouTube Desk Frontend Controller
 * Complete UI/UX implementation matching Studio Hub standards.
 */

(function() {
    'use strict';

    // =========================================================================
    // 1. Application State
    // =========================================================================
    const state = {
        currentView: window.INITIAL_SECTION || 'overview',
        connected: false,
        channel: null,
        playlists: [],
        queue: [],
        schedules: [],
        history: [],
        errors: [],
        pollTimer: null,

        // Wizard State
        wizard: {
            step: 1,
            maxSteps: 6,
            file: null,
            videoId: null,
            filename: '',
            videoUrl: '',
            duration: 0,
            resolution: '',
            size: '',
            title: '',
            description: '',
            tags: [],
            categoryId: '22',
            playlistId: '',
            language: 'en',
            visibility: 'public',
            timingMode: 'now',
            scheduleDate: '',
            scheduleTime: '',
            scheduleTimezone: 'Asia/Kolkata',
            thumbnailUrl: '',
            customThumbnailFile: null,
        }
    };

    // =========================================================================
    // 2. DOM Elements Cache
    // =========================================================================
    const dom = {
        // Topbar
        topbarStatusPill: document.getElementById('topbarStatusPill'),
        deskConnectionBadge: document.getElementById('deskConnectionBadge'),
        btnDeskSettings: document.getElementById('btnDeskSettings'),

        // Navigation
        navBar: document.getElementById('deskNavBar'),
        navTabs: document.querySelectorAll('.desk-nav-tab'),
        viewPanes: document.querySelectorAll('.desk-view-pane'),
        queueBadgeCount: document.getElementById('queueBadgeCount'),
        scheduledBadgeCount: document.getElementById('scheduledBadgeCount'),

        // Overview
        kpiTotal: document.getElementById('kpiTotal'),
        kpiScheduled: document.getElementById('kpiScheduled'),
        kpiProcessing: document.getElementById('kpiProcessing'),
        kpiFailed: document.getElementById('kpiFailed'),
        kpiNextScheduled: document.getElementById('kpiNextScheduled'),
        kpiQueueStatus: document.getElementById('kpiQueueStatus'),
        kpiErrorStatus: document.getElementById('kpiErrorStatus'),
        recentUploadsList: document.getElementById('overviewRecentUploadsList'),
        upcomingSchedulesList: document.getElementById('overviewUpcomingSchedulesList'),
        overviewChannelAvatar: document.getElementById('overviewChannelAvatar'),
        overviewChannelName: document.getElementById('overviewChannelName'),
        overviewChannelDetails: document.getElementById('overviewChannelDetails'),
        btnConnectShortcut: document.getElementById('btnConnectShortcut'),

        // Quick Actions
        btnQuickUpload: document.getElementById('btnQuickUpload'),
        btnQuickSchedule: document.getElementById('btnQuickSchedule'),
        btnQuickQueue: document.getElementById('btnQuickQueue'),
        btnQuickHistory: document.getElementById('btnQuickHistory'),
        btnQuickConnect: document.getElementById('btnQuickConnect'),

        // Wizard Steps & Controls
        wizardStepper: document.getElementById('wizardStepper'),
        wizardStepNodes: document.querySelectorAll('.wizard-step-node'),
        wizardPanes: document.querySelectorAll('.wizard-step-pane'),
        btnWizardBack: document.getElementById('btnWizardBack'),
        btnWizardNext: document.getElementById('btnWizardNext'),
        wizardFooter: document.getElementById('wizardFooter'),

        // Step 1: Video
        uploadDropzone: document.getElementById('uploadDropzone'),
        videoFileInput: document.getElementById('videoFileInput'),
        btnBrowseVideo: document.getElementById('btnBrowseVideo'),
        btnPickLibrary: document.getElementById('btnPickLibrary'),
        selectedVideoCard: document.getElementById('selectedVideoCard'),
        videoElementPreview: document.getElementById('videoElementPreview'),
        selectedVideoFilename: document.getElementById('selectedVideoFilename'),
        selectedVideoDuration: document.getElementById('selectedVideoDuration'),
        selectedVideoResolution: document.getElementById('selectedVideoResolution'),
        selectedVideoSize: document.getElementById('selectedVideoSize'),
        btnChangeVideo: document.getElementById('btnChangeVideo'),

        // Step 2: Details
        inputVideoTitle: document.getElementById('inputVideoTitle'),
        titleCharCounter: document.getElementById('titleCharCounter'),
        inputVideoDescription: document.getElementById('inputVideoDescription'),
        descCharCounter: document.getElementById('descCharCounter'),

        // Step 3: Metadata
        tagInputBox: document.getElementById('tagInputBox'),
        tagInputField: document.getElementById('tagInputField'),
        selectCategory: document.getElementById('selectCategory'),
        selectPlaylist: document.getElementById('selectPlaylist'),
        selectLanguage: document.getElementById('selectLanguage'),

        // Step 4: Publish
        radioVisibility: document.querySelectorAll('input[name="videoVisibility"]'),
        radioTimingMode: document.querySelectorAll('input[name="publishingMode"]'),
        scheduleFieldsWrapper: document.getElementById('scheduleFieldsWrapper'),
        inputScheduleDate: document.getElementById('inputScheduleDate'),
        inputScheduleTime: document.getElementById('inputScheduleTime'),
        selectScheduleTimezone: document.getElementById('selectScheduleTimezone'),

        // Step 5: Thumbnail
        wizardThumbnailPreview: document.getElementById('wizardThumbnailPreview'),
        wizardThumbnailPlaceholder: document.getElementById('wizardThumbnailPlaceholder'),
        customThumbFileInput: document.getElementById('customThumbFileInput'),
        btnUploadThumbFile: document.getElementById('btnUploadThumbFile'),
        btnCaptureVideoFrame: document.getElementById('btnCaptureVideoFrame'),
        btnResetThumbnail: document.getElementById('btnResetThumbnail'),

        // Step 6: Review
        reviewThumbnailImg: document.getElementById('reviewThumbnailImg'),
        reviewTitle: document.getElementById('reviewTitle'),
        reviewDescription: document.getElementById('reviewDescription'),
        reviewVisibility: document.getElementById('reviewVisibility'),
        reviewTiming: document.getElementById('reviewTiming'),
        reviewCategory: document.getElementById('reviewCategory'),
        reviewTagsCount: document.getElementById('reviewTagsCount'),

        // Upload Progress State
        wizardProgressState: document.getElementById('wizard-progress-state'),
        uploadStatusIcon: document.getElementById('uploadStatusIcon'),
        uploadStatusTitle: document.getElementById('uploadStatusTitle'),
        uploadStatusMessage: document.getElementById('uploadStatusMessage'),
        uploadProgressBarContainer: document.getElementById('uploadProgressBarContainer'),
        uploadProgressBarFill: document.getElementById('uploadProgressBarFill'),
        uploadPercentText: document.getElementById('uploadPercentText'),
        uploadSpeedText: document.getElementById('uploadSpeedText'),
        uploadActionButtons: document.getElementById('uploadActionButtons'),
        btnUploadAnother: document.getElementById('btnUploadAnother'),

        // Queue
        queueFilterTabs: document.getElementById('queueFilterTabs'),
        queueSearchInput: document.getElementById('queueSearchInput'),
        queueItemsList: document.getElementById('queueItemsList'),

        // Scheduled
        scheduledItemsList: document.getElementById('scheduledItemsList'),

        // History
        historyFilterTabs: document.getElementById('historyFilterTabs'),
        historySearchInput: document.getElementById('historySearchInput'),
        historyTableBody: document.getElementById('historyTableBody'),

        // Connection
        connectionActiveCard: document.getElementById('connectionActiveCard'),
        connectionInactiveCard: document.getElementById('connectionInactiveCard'),
        channelAvatar: document.getElementById('channelAvatar'),
        channelTitle: document.getElementById('channelTitle'),
        channelHandle: document.getElementById('channelHandle'),
        channelSubscribers: document.getElementById('channelSubscribers'),
        channelVideoCount: document.getElementById('channelVideoCount'),
        btnRefreshConnection: document.getElementById('btnRefreshConnection'),
        btnDisconnectChannel: document.getElementById('btnDisconnectChannel'),

        // Settings
        deskSettingsForm: document.getElementById('deskSettingsForm'),
        settingDefaultVisibility: document.getElementById('settingDefaultVisibility'),
        settingDefaultCategory: document.getElementById('settingDefaultCategory'),
        settingDefaultTags: document.getElementById('settingDefaultTags'),

        // Modals & Toasts
        deskConfirmModal: document.getElementById('deskConfirmModal'),
        modalConfirmTitle: document.getElementById('modalConfirmTitle'),
        modalConfirmText: document.getElementById('modalConfirmText'),
        btnModalClose: document.getElementById('btnModalClose'),
        btnModalCancel: document.getElementById('btnModalCancel'),
        btnModalOk: document.getElementById('btnModalOk'),
        libraryPickerModal: document.getElementById('libraryPickerModal'),
        libraryVideosList: document.getElementById('libraryVideosList'),
        btnLibraryClose: document.getElementById('btnLibraryClose'),
        btnLibraryCancel: document.getElementById('btnLibraryCancel'),
        toastShelf: document.getElementById('toastShelf'),
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
            dom.modalConfirmTitle.textContent = title;
            dom.modalConfirmText.textContent = text;
            dom.deskConfirmModal.classList.add('active');

            const cleanup = () => {
                dom.btnModalOk.removeEventListener('click', onOk);
                dom.btnModalCancel.removeEventListener('click', onCancel);
                dom.btnModalClose.removeEventListener('click', onCancel);
                dom.deskConfirmModal.classList.remove('active');
            };
            const onOk = () => { cleanup(); resolve(true); };
            const onCancel = () => { cleanup(); resolve(false); };

            dom.btnModalOk.addEventListener('click', onOk);
            dom.btnModalCancel.addEventListener('click', onCancel);
            dom.btnModalClose.addEventListener('click', onCancel);
        });
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str).replace(/[&<>"']/g, m => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[m]));
    }

    function formatBytes(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    function formatDuration(seconds) {
        if (!seconds) return '0:00';
        seconds = Math.round(seconds);
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        const h = Math.floor(m / 60);
        if (h > 0) {
            return `${h}:${String(m % 60).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
        }
        return `${m}:${String(s).padStart(2, '0')}`;
    }

    function formatDate(ts) {
        if (!ts) return '-';
        const d = new Date(ts * 1000);
        return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }

    // =========================================================================
    // 4. Navigation & View Routing
    // =========================================================================
    function switchView(viewName, pushHistory = true) {
        state.currentView = viewName;

        // Update nav tabs
        dom.navTabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.view === viewName);
        });

        // Update view panes
        dom.viewPanes.forEach(pane => {
            const isTarget = pane.id === `view-${viewName}`;
            pane.style.display = isTarget ? 'block' : 'none';
            if (isTarget) pane.classList.add('active');
            else pane.classList.remove('active');
        });

        // Update URL cleanly without reloading
        if (pushHistory) {
            const url = viewName === 'overview' ? '/youtube-desk' : `/youtube-desk/${viewName}`;
            history.pushState({ view: viewName }, '', url);
        }

        // Fetch view-specific data
        switch (viewName) {
            case 'overview': loadOverview(); break;
            case 'queue': loadQueue(); break;
            case 'scheduled': loadScheduled(); break;
            case 'history': loadHistory(); break;
            case 'connection': loadConnection(); break;
            case 'settings': loadSettings(); break;
            case 'upload':
                if (state.wizard.step === 1) resetWizard();
                break;
        }

        if (window.lucide) window.lucide.createIcons();
    }

    // Handle browser forward/back
    window.addEventListener('popstate', (e) => {
        const view = (e.state && e.state.view) || 'overview';
        switchView(view, false);
    });

    // Sub-nav tab clicks
    dom.navTabs.forEach(tab => {
        tab.addEventListener('click', () => switchView(tab.dataset.view));
    });

    // Delegated data-nav clicks across the page
    document.addEventListener('click', (e) => {
        const navEl = e.target.closest('[data-nav]');
        if (navEl) {
            e.preventDefault();
            const targetView = navEl.dataset.nav;
            const targetMode = navEl.dataset.mode;
            switchView(targetView);
            if (targetMode === 'schedule' && targetView === 'upload') {
                state.wizard.timingMode = 'schedule';
                const rad = document.querySelector('input[name="publishingMode"][value="schedule"]');
                if (rad) {
                    rad.checked = true;
                    rad.dispatchEvent(new Event('change'));
                }
            }
        }
    });

    // Settings shortcut button
    dom.btnDeskSettings.addEventListener('click', () => switchView('settings'));

    // =========================================================================
    // 5. Data Fetching & Overview
    // =========================================================================
    async function loadOverview() {
        try {
            const [statusRes, queueRes, schedRes, histRes, errRes] = await Promise.all([
                fetch('/youtube/status').then(r => r.json()).catch(() => ({ connected: false })),
                fetch('/youtube/upload-queue').then(r => r.json()).catch(() => ({ items: [] })),
                fetch('/youtube/schedules').then(r => r.json()).catch(() => ({ schedules: [] })),
                fetch('/youtube/history').then(r => r.json()).catch(() => ({ history: [] })),
                fetch('/youtube/errors').then(r => r.json()).catch(() => ({ errors: [] })),
            ]);

            state.connected = statusRes.connected;
            state.channel = statusRes.channel;
            state.queue = queueRes.items || [];
            state.schedules = schedRes.schedules || [];
            state.history = histRes.history || [];
            state.errors = errRes.errors || [];

            // Update Connection Badges
            updateConnectionUI();

            // Update KPI values
            dom.kpiTotal.textContent = state.history.length;
            dom.kpiScheduled.textContent = state.schedules.length;
            dom.kpiProcessing.textContent = state.queue.filter(q => q.status === 'uploading' || q.status === 'processing').length;
            dom.kpiFailed.textContent = state.errors.length;

            // Badges in navbar
            dom.queueBadgeCount.textContent = state.queue.length;
            dom.scheduledBadgeCount.textContent = state.schedules.length;

            // Subtitle status details
            if (state.schedules.length > 0) {
                const next = state.schedules[0];
                dom.kpiNextScheduled.innerHTML = `<svg data-lucide="clock" width="12" height="12"></svg><span>Next: ${formatDate(next.scheduled_at)}</span>`;
            } else {
                dom.kpiNextScheduled.innerHTML = `<svg data-lucide="clock" width="12" height="12"></svg><span>No upcoming releases</span>`;
            }

            const activeQueue = state.queue.filter(q => q.status === 'uploading' || q.status === 'processing');
            if (activeQueue.length > 0) {
                dom.kpiQueueStatus.innerHTML = `<svg data-lucide="loader" width="12" height="12"></svg><span style="color:var(--primary);">${activeQueue.length} in progress</span>`;
            } else {
                dom.kpiQueueStatus.innerHTML = `<svg data-lucide="check-circle" width="12" height="12"></svg><span>Queue is idle</span>`;
            }

            if (state.errors.length > 0) {
                dom.kpiErrorStatus.innerHTML = `<svg data-lucide="alert-triangle" width="12" height="12"></svg><span style="color:var(--error);">${state.errors.length} failed upload</span>`;
            } else {
                dom.kpiErrorStatus.innerHTML = `<svg data-lucide="shield-check" width="12" height="12"></svg><span>All systems clear</span>`;
            }

            // Render Recent Uploads (Max 3-4 items)
            renderOverviewRecentUploads();

            // Render Upcoming Schedules (Max 3 items)
            renderOverviewSchedules();

            // Render Channel Card
            renderOverviewChannel();

            if (window.lucide) window.lucide.createIcons();
        } catch (err) {
            console.error('Error loading overview:', err);
        }
    }

    function updateConnectionUI() {
        if (state.connected && state.channel) {
            dom.topbarStatusPill.className = 'status-pill connected';
            dom.topbarStatusPill.innerHTML = '<span class="dot"></span><span>Connected</span>';
            dom.deskConnectionBadge.className = 'status-pill connected';
            dom.deskConnectionBadge.innerHTML = '<span class="dot"></span><span>Connected</span>';
        } else {
            dom.topbarStatusPill.className = 'status-pill disconnected';
            dom.topbarStatusPill.innerHTML = '<span class="dot"></span><span>Not Connected</span>';
            dom.deskConnectionBadge.className = 'status-pill disconnected';
            dom.deskConnectionBadge.innerHTML = '<span class="dot"></span><span>Not Connected</span>';
        }
    }

    function renderOverviewRecentUploads() {
        if (!state.history || state.history.length === 0) {
            dom.recentUploadsList.innerHTML = `
                <div class="compact-empty-state">
                    <svg data-lucide="video" width="32" height="32"></svg>
                    <h4>No Recent Uploads</h4>
                    <p>Videos you publish or schedule through UpClip Studio will appear here.</p>
                    <button class="btn btn-primary btn-sm" data-nav="upload">Upload First Video</button>
                </div>`;
            return;
        }

        const recent = state.history.slice(0, 4);
        dom.recentUploadsList.innerHTML = recent.map(item => `
            <div class="compact-video-row">
                <div class="compact-video-thumb">
                    ${item.thumbnail ? `<img src="${item.thumbnail}" style="width:100%;height:100%;object-fit:cover;">` : '<svg data-lucide="clapperboard" width="18" height="18"></svg>'}
                </div>
                <div class="compact-video-info">
                    <div class="compact-video-title">${escapeHtml(item.title || 'Untitled Video')}</div>
                    <div class="compact-video-meta">
                        <span class="status-pill connected" style="padding:2px 8px; font-size:10px;">${escapeHtml(item.status || 'published')}</span>
                        <span>•</span>
                        <span>${formatDate(item.published_at || item.created_at)}</span>
                        <span>•</span>
                        <span style="text-transform:capitalize;">${escapeHtml(item.visibility || 'public')}</span>
                    </div>
                </div>
                <div class="compact-video-actions">
                    ${item.youtube_video_id ? `<a href="https://youtu.be/${item.youtube_video_id}" target="_blank" class="btn btn-secondary btn-sm" style="padding:4px 8px;" title="View on YouTube"><svg data-lucide="external-link" width="13" height="13"></svg></a>` : ''}
                </div>
            </div>
        `).join('');
    }

    function renderOverviewSchedules() {
        if (!state.schedules || state.schedules.length === 0) {
            dom.upcomingSchedulesList.innerHTML = `
                <div class="compact-empty-state">
                    <svg data-lucide="calendar-x" width="28" height="28"></svg>
                    <h4>No Scheduled Uploads</h4>
                    <p>Schedule your next clip to automate publishing at peak hours.</p>
                    <button class="btn btn-secondary btn-sm" data-nav="upload" data-mode="schedule">Schedule Upload</button>
                </div>`;
            return;
        }

        const upcoming = state.schedules.slice(0, 3);
        dom.upcomingSchedulesList.innerHTML = upcoming.map(s => `
            <div class="compact-video-row">
                <div class="compact-video-thumb">
                    <svg data-lucide="calendar" width="18" height="18" style="color:var(--primary);"></svg>
                </div>
                <div class="compact-video-info">
                    <div class="compact-video-title">${escapeHtml(s.title || 'Scheduled Upload')}</div>
                    <div class="compact-video-meta">
                        <span style="color:var(--primary); font-weight:600;">${formatDate(s.scheduled_at)}</span>
                    </div>
                </div>
                <div class="compact-video-actions">
                    <button class="btn btn-outline btn-sm btn-cancel-schedule" data-id="${s.id}" style="padding:4px 8px; color:var(--error); border-color:rgba(239,68,68,0.3);" title="Cancel schedule">
                        <svg data-lucide="x" width="13" height="13"></svg>
                    </button>
                </div>
            </div>
        `).join('');
    }

    function renderOverviewChannel() {
        if (state.connected && state.channel) {
            dom.overviewChannelAvatar.innerHTML = state.channel.avatar
                ? `<img src="${state.channel.avatar}" style="width:100%;height:100%;object-fit:cover;">`
                : '<svg data-lucide="user" width="22" height="22"></svg>';
            dom.overviewChannelName.textContent = state.channel.title || 'YouTube Channel';
            dom.overviewChannelDetails.textContent = `${state.channel.subscribers || '0'} Subscribers • ${state.channel.video_count || '0'} Videos`;
            dom.btnConnectShortcut.textContent = 'Manage';
        } else {
            dom.overviewChannelAvatar.innerHTML = '<svg data-lucide="youtube" width="24" height="24"></svg>';
            dom.overviewChannelName.textContent = 'Channel Not Connected';
            dom.overviewChannelDetails.textContent = 'Connect your YouTube account to publish directly.';
            dom.btnConnectShortcut.textContent = 'Connect';
        }
    }

    // =========================================================================
    // 6. Multi-Step Upload Wizard Logic (Sections 9 & 10)
    // =========================================================================
    function setWizardStep(step) {
        state.wizard.step = step;

        // Update Stepper Pill Nodes
        dom.wizardStepNodes.forEach(node => {
            const nodeStep = parseInt(node.dataset.step, 10);
            node.classList.toggle('active', nodeStep === step);
            node.classList.toggle('completed', nodeStep < step);
            const circle = node.querySelector('.wizard-step-circle');
            if (nodeStep < step) {
                circle.innerHTML = '✓';
            } else {
                circle.textContent = nodeStep;
            }
        });

        // Update Panes
        dom.wizardPanes.forEach(pane => {
            pane.classList.toggle('active', pane.id === `wizard-step-${step}`);
        });

        // Update Bottom Nav Buttons
        dom.btnWizardBack.disabled = (step === 1);
        if (step === 6) {
            dom.btnWizardNext.innerHTML = state.wizard.timingMode === 'schedule'
                ? '<svg data-lucide="calendar-check" width="14" height="14"></svg><span>Schedule Release</span>'
                : '<svg data-lucide="upload-cloud" width="14" height="14"></svg><span>Publish to YouTube</span>';
        } else {
            dom.btnWizardNext.innerHTML = '<span>Continue</span><svg data-lucide="arrow-right" width="14" height="14"></svg>';
        }

        // Validate current step to enable/disable Next button
        validateCurrentStep();

        // Step-specific initializations
        if (step === 3 && state.playlists.length === 0) {
            loadPlaylistsDropdown();
        }
        if (step === 6) {
            populateReviewSummary();
        }

        if (window.lucide) window.lucide.createIcons();
    }

    function validateCurrentStep() {
        let isValid = false;
        switch (state.wizard.step) {
            case 1:
                isValid = !!state.wizard.videoId;
                break;
            case 2:
                isValid = !!state.wizard.title.trim();
                break;
            case 3:
                isValid = true; // Metadata is optional
                break;
            case 4:
                isValid = state.wizard.timingMode === 'now' || (!!state.wizard.scheduleDate && !!state.wizard.scheduleTime);
                break;
            case 5:
                isValid = true; // Thumbnail has fallback
                break;
            case 6:
                isValid = true;
                break;
        }
        dom.btnWizardNext.disabled = !isValid;
    }

    function resetWizard() {
        state.wizard = {
            step: 1,
            maxSteps: 6,
            file: null,
            videoId: null,
            filename: '',
            videoUrl: '',
            duration: 0,
            resolution: '',
            size: '',
            title: '',
            description: '',
            tags: [],
            categoryId: '22',
            playlistId: '',
            language: 'en',
            visibility: 'public',
            timingMode: 'now',
            scheduleDate: '',
            scheduleTime: '',
            scheduleTimezone: 'Asia/Kolkata',
            thumbnailUrl: '',
            customThumbnailFile: null,
        };

        dom.uploadDropzone.style.display = 'flex';
        dom.selectedVideoCard.style.display = 'none';
        dom.inputVideoTitle.value = '';
        dom.inputVideoDescription.value = '';
        dom.tagInputBox.querySelectorAll('.tag-chip').forEach(c => c.remove());
        dom.titleCharCounter.textContent = '0/100';
        dom.descCharCounter.textContent = '0/5000';
        dom.wizardFooter.style.display = 'flex';
        dom.wizardProgressState.style.display = 'none';

        // Reset default dates
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dom.inputScheduleDate.value = tomorrow.toISOString().split('T')[0];
        dom.inputScheduleTime.value = '19:00';

        setWizardStep(1);
    }

    // Step 1: File selection & upload to /youtube/import
    dom.btnBrowseVideo.addEventListener('click', (e) => {
        e.stopPropagation();
        dom.videoFileInput.click();
    });

    dom.uploadDropzone.addEventListener('click', () => dom.videoFileInput.click());

    dom.uploadDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dom.uploadDropzone.classList.add('dragover');
    });

    dom.uploadDropzone.addEventListener('dragleave', () => {
        dom.uploadDropzone.classList.remove('dragover');
    });

    dom.uploadDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dom.uploadDropzone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleVideoFileSelection(e.dataTransfer.files[0]);
        }
    });

    dom.videoFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleVideoFileSelection(e.target.files[0]);
        }
    });

    dom.btnChangeVideo.addEventListener('click', () => {
        dom.uploadDropzone.style.display = 'flex';
        dom.selectedVideoCard.style.display = 'none';
        state.wizard.videoId = null;
        validateCurrentStep();
    });

    async function handleVideoFileSelection(file) {
        state.wizard.file = file;
        state.wizard.filename = file.name;
        state.wizard.size = formatBytes(file.size);

        // Immediate local video preview
        const objUrl = URL.createObjectURL(file);
        dom.videoElementPreview.src = objUrl;
        dom.selectedVideoFilename.textContent = file.name;
        dom.selectedVideoSize.textContent = state.wizard.size;

        dom.uploadDropzone.style.display = 'none';
        dom.selectedVideoCard.style.display = 'flex';

        // Auto-fill initial title
        const cleanName = file.name.replace(/\.[^/.]+$/, '').replace(/[_-]+/g, ' ');
        state.wizard.title = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);
        dom.inputVideoTitle.value = state.wizard.title;
        dom.titleCharCounter.textContent = `${state.wizard.title.length}/100`;

        showToast('Uploading video to workspace...', 'info');

        try {
            const formData = new FormData();
            formData.append('video', file);

            const res = await fetch('/youtube/import', {
                method: 'POST',
                body: formData,
            });
            const data = await res.json();

            if (!res.ok || !data.success) {
                throw new Error(data.error || 'Failed to import video');
            }

            state.wizard.videoId = data.video_id;
            state.wizard.thumbnailUrl = data.thumbnail || '';
            state.wizard.duration = data.metadata ? data.metadata.duration : 0;
            state.wizard.resolution = data.metadata ? `${data.metadata.width}x${data.metadata.height}` : 'HD';

            dom.selectedVideoDuration.textContent = formatDuration(state.wizard.duration);
            dom.selectedVideoResolution.textContent = state.wizard.resolution;

            if (state.wizard.thumbnailUrl) {
                dom.wizardThumbnailPreview.src = state.wizard.thumbnailUrl;
                dom.wizardThumbnailPreview.style.display = 'block';
                dom.wizardThumbnailPlaceholder.style.display = 'none';
                dom.reviewThumbnailImg.src = state.wizard.thumbnailUrl;
            }

            showToast('Video ready for configuration', 'success');
            validateCurrentStep();
        } catch (err) {
            showToast(err.message, 'error');
            dom.uploadDropzone.style.display = 'flex';
            dom.selectedVideoCard.style.display = 'none';
        }
    }

    // Step 1: Project Library Picker Modal
    dom.btnPickLibrary.addEventListener('click', async (e) => {
        e.stopPropagation();
        dom.libraryPickerModal.classList.add('active');
        dom.libraryVideosList.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-muted);">Loading workspace media...</div>';

        try {
            const res = await fetch('/download/downloaded');
            const data = await res.json();
            const files = data.files || [];

            if (files.length === 0) {
                dom.libraryVideosList.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-muted);">No videos found in your input library.</div>';
                return;
            }

            dom.libraryVideosList.innerHTML = files.map(f => `
                <div class="compact-video-row" style="cursor:pointer;" data-filename="${escapeHtml(f.name)}">
                    <div class="compact-video-thumb">
                        <svg data-lucide="file-video" width="20" height="20"></svg>
                    </div>
                    <div class="compact-video-info">
                        <div class="compact-video-title">${escapeHtml(f.name)}</div>
                        <div class="compact-video-meta">
                            <span>${f.size}</span>
                            <span>•</span>
                            <span>${f.modified}</span>
                        </div>
                    </div>
                    <button type="button" class="btn btn-secondary btn-sm" style="pointer-events:none;">Select</button>
                </div>
            `).join('');

            if (window.lucide) window.lucide.createIcons();

            dom.libraryVideosList.querySelectorAll('.compact-video-row').forEach(row => {
                row.addEventListener('click', async () => {
                    const filename = row.dataset.filename;
                    dom.libraryPickerModal.classList.remove('active');
                    await importExistingLibraryVideo(filename);
                });
            });
        } catch (err) {
            dom.libraryVideosList.innerHTML = `<div style="color:var(--error); padding:10px;">Failed to load library: ${err.message}</div>`;
        }
    });

    dom.btnLibraryCancel.addEventListener('click', () => dom.libraryPickerModal.classList.remove('active'));
    dom.btnLibraryClose.addEventListener('click', () => dom.libraryPickerModal.classList.remove('active'));

    async function importExistingLibraryVideo(filename) {
        showToast('Linking library video...', 'info');
        try {
            const res = await fetch('/youtube/import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename })
            });
            const data = await res.json();

            if (!res.ok || !data.success) {
                throw new Error(data.error || 'Failed to select video');
            }

            state.wizard.videoId = data.video_id;
            state.wizard.filename = filename;
            state.wizard.thumbnailUrl = data.thumbnail || '';
            state.wizard.duration = data.metadata ? data.metadata.duration : 0;
            state.wizard.resolution = data.metadata ? `${data.metadata.width}x${data.metadata.height}` : 'HD';
            state.wizard.size = formatBytes(data.metadata ? data.metadata.file_size : 0);

            dom.selectedVideoFilename.textContent = filename;
            dom.selectedVideoSize.textContent = state.wizard.size;
            dom.selectedVideoDuration.textContent = formatDuration(state.wizard.duration);
            dom.selectedVideoResolution.textContent = state.wizard.resolution;

            dom.videoElementPreview.src = `/download/input/${filename}`;
            dom.uploadDropzone.style.display = 'none';
            dom.selectedVideoCard.style.display = 'flex';

            const cleanName = filename.replace(/\.[^/.]+$/, '').replace(/[_-]+/g, ' ');
            state.wizard.title = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);
            dom.inputVideoTitle.value = state.wizard.title;
            dom.titleCharCounter.textContent = `${state.wizard.title.length}/100`;

            if (state.wizard.thumbnailUrl) {
                dom.wizardThumbnailPreview.src = state.wizard.thumbnailUrl;
                dom.wizardThumbnailPreview.style.display = 'block';
                dom.wizardThumbnailPlaceholder.style.display = 'none';
                dom.reviewThumbnailImg.src = state.wizard.thumbnailUrl;
            }

            showToast('Video linked successfully', 'success');
            validateCurrentStep();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // Step 2: Details & Char Counters
    dom.inputVideoTitle.addEventListener('input', (e) => {
        state.wizard.title = e.target.value;
        dom.titleCharCounter.textContent = `${e.target.value.length}/100`;
        validateCurrentStep();
    });

    dom.inputVideoDescription.addEventListener('input', (e) => {
        state.wizard.description = e.target.value;
        dom.descCharCounter.textContent = `${e.target.value.length}/5000`;
    });

    // Step 3: Tags Chip Input
    dom.tagInputField.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            const tag = dom.tagInputField.value.trim().replace(/^#/, '');
            if (tag && !state.wizard.tags.includes(tag)) {
                addTagChip(tag);
                dom.tagInputField.value = '';
            }
        } else if (e.key === 'Backspace' && !dom.tagInputField.value && state.wizard.tags.length > 0) {
            removeTagChip(state.wizard.tags[state.wizard.tags.length - 1]);
        }
    });

    function addTagChip(tag) {
        state.wizard.tags.push(tag);
        const chip = document.createElement('span');
        chip.className = 'tag-chip';
        chip.dataset.tag = tag;
        chip.innerHTML = `${escapeHtml(tag)} <span class="tag-chip-remove">&times;</span>`;
        chip.querySelector('.tag-chip-remove').addEventListener('click', () => removeTagChip(tag));
        dom.tagInputBox.insertBefore(chip, dom.tagInputField);
    }

    function removeTagChip(tag) {
        state.wizard.tags = state.wizard.tags.filter(t => t !== tag);
        const chip = dom.tagInputBox.querySelector(`.tag-chip[data-tag="${tag}"]`);
        if (chip) chip.remove();
    }

    dom.selectCategory.addEventListener('change', (e) => {
        state.wizard.categoryId = e.target.value;
    });

    dom.selectPlaylist.addEventListener('change', (e) => {
        state.wizard.playlistId = e.target.value;
    });

    dom.selectLanguage.addEventListener('change', (e) => {
        state.wizard.language = e.target.value;
    });

    async function loadPlaylistsDropdown() {
        try {
            const res = await fetch('/youtube/playlists');
            const data = await res.json();
            state.playlists = data.playlists || [];
            dom.selectPlaylist.innerHTML = '<option value="">None (Don\'t add to playlist)</option>' +
                state.playlists.map(p => `<option value="${p.id}">${escapeHtml(p.title)}</option>`).join('');
        } catch (err) {
            console.warn('Could not load playlists:', err);
        }
    }

    // Step 4: Publish Settings
    dom.radioVisibility.forEach(rad => {
        rad.addEventListener('change', (e) => {
            state.wizard.visibility = e.target.value;
            dom.radioVisibility.forEach(r => r.closest('.radio-card').classList.toggle('active', r.checked));
        });
    });

    dom.radioTimingMode.forEach(rad => {
        rad.addEventListener('change', (e) => {
            state.wizard.timingMode = e.target.value;
            dom.radioTimingMode.forEach(r => r.closest('.radio-card').classList.toggle('active', r.checked));
            dom.scheduleFieldsWrapper.style.display = e.target.value === 'schedule' ? 'block' : 'none';
            validateCurrentStep();
        });
    });

    dom.inputScheduleDate.addEventListener('change', (e) => {
        state.wizard.scheduleDate = e.target.value;
        validateCurrentStep();
    });

    dom.inputScheduleTime.addEventListener('change', (e) => {
        state.wizard.scheduleTime = e.target.value;
        validateCurrentStep();
    });

    dom.selectScheduleTimezone.addEventListener('change', (e) => {
        state.wizard.scheduleTimezone = e.target.value;
    });

    // Step 5: Thumbnail Customization
    dom.btnUploadThumbFile.addEventListener('click', () => dom.customThumbFileInput.click());

    dom.customThumbFileInput.addEventListener('change', async (e) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            state.wizard.customThumbnailFile = file;
            const thumbUrl = URL.createObjectURL(file);
            dom.wizardThumbnailPreview.src = thumbUrl;
            dom.wizardThumbnailPreview.style.display = 'block';
            dom.wizardThumbnailPlaceholder.style.display = 'none';
            dom.btnResetThumbnail.style.display = 'inline-block';
            dom.reviewThumbnailImg.src = thumbUrl;

            // Upload thumbnail to server
            if (state.wizard.videoId) {
                const fd = new FormData();
                fd.append('video_id', state.wizard.videoId);
                fd.append('thumbnail', file);
                try {
                    await fetch('/youtube/thumbnail/upload', { method: 'POST', body: fd });
                    showToast('Thumbnail applied', 'success');
                } catch (err) {
                    console.warn('Custom thumb upload deferred:', err);
                }
            }
        }
    });

    dom.btnCaptureVideoFrame.addEventListener('click', async () => {
        if (!state.wizard.videoId) return;
        showToast('Capturing video frame...', 'info');
        try {
            const res = await fetch('/youtube/thumbnail/capture', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    video_id: state.wizard.videoId,
                    filename: state.wizard.filename,
                    timestamp: Math.min(2.0, state.wizard.duration || 1.0)
                })
            });
            const data = await res.json();
            if (data.success && data.thumbnail_url) {
                state.wizard.thumbnailUrl = data.thumbnail_url;
                dom.wizardThumbnailPreview.src = data.thumbnail_url;
                dom.wizardThumbnailPreview.style.display = 'block';
                dom.wizardThumbnailPlaceholder.style.display = 'none';
                dom.btnResetThumbnail.style.display = 'inline-block';
                dom.reviewThumbnailImg.src = data.thumbnail_url;
                showToast('Frame captured as thumbnail', 'success');
            } else {
                throw new Error(data.error || 'Frame capture failed');
            }
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    dom.btnResetThumbnail.addEventListener('click', () => {
        state.wizard.customThumbnailFile = null;
        if (state.wizard.thumbnailUrl) {
            dom.wizardThumbnailPreview.src = state.wizard.thumbnailUrl;
            dom.reviewThumbnailImg.src = state.wizard.thumbnailUrl;
        } else {
            dom.wizardThumbnailPreview.style.display = 'none';
            dom.wizardThumbnailPlaceholder.style.display = 'block';
        }
        dom.btnResetThumbnail.style.display = 'none';
    });

    // Step 6: Review Summary
    function populateReviewSummary() {
        dom.reviewTitle.textContent = state.wizard.title || 'Untitled Video';
        dom.reviewDescription.textContent = state.wizard.description || 'No description provided.';
        dom.reviewVisibility.textContent = state.wizard.visibility;
        dom.reviewTagsCount.textContent = `${state.wizard.tags.length} tags`;

        const catText = dom.selectCategory.options[dom.selectCategory.selectedIndex].text;
        dom.reviewCategory.textContent = catText;

        if (state.wizard.timingMode === 'schedule') {
            dom.reviewTiming.textContent = `Scheduled: ${state.wizard.scheduleDate} at ${state.wizard.scheduleTime} (${state.wizard.scheduleTimezone})`;
        } else {
            dom.reviewTiming.textContent = 'Publish Immediately';
        }
    }

    // Wizard Stepper Back / Next Buttons
    dom.btnWizardBack.addEventListener('click', () => {
        if (state.wizard.step > 1) {
            setWizardStep(state.wizard.step - 1);
        }
    });

    dom.btnWizardNext.addEventListener('click', async () => {
        if (state.wizard.step < 6) {
            setWizardStep(state.wizard.step + 1);
        } else {
            // Step 6: Trigger final publish or schedule
            await executeFinalPublish();
        }
    });

    async function executeFinalPublish() {
        const confirmed = await showConfirm(
            state.wizard.timingMode === 'schedule' ? 'Confirm Schedule' : 'Confirm Publish',
            `Are you ready to ${state.wizard.timingMode === 'schedule' ? 'schedule' : 'publish'} "${state.wizard.title}" to YouTube?`
        );
        if (!confirmed) return;

        // Hide wizard panes and footer, display progress state
        dom.wizardPanes.forEach(p => p.classList.remove('active'));
        dom.wizardProgressState.style.display = 'block';
        dom.wizardFooter.style.display = 'none';
        dom.uploadProgressBarFill.style.width = '20%';
        dom.uploadPercentText.textContent = '20%';
        dom.uploadSpeedText.textContent = 'Saving metadata...';

        try {
            // 1. Update Video Metadata
            await fetch(`/youtube/videos/${state.wizard.videoId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: state.wizard.title,
                    description: state.wizard.description,
                    tags: state.wizard.tags,
                    category_id: state.wizard.categoryId,
                    visibility: state.wizard.visibility,
                })
            });

            dom.uploadProgressBarFill.style.width = '50%';
            dom.uploadPercentText.textContent = '50%';

            if (state.wizard.timingMode === 'schedule') {
                // Schedule Mode
                dom.uploadSpeedText.textContent = 'Registering automated schedule...';
                const schedTimestamp = Math.floor(new Date(`${state.wizard.scheduleDate}T${state.wizard.scheduleTime}`).getTime() / 1000);

                const res = await fetch('/youtube/schedules', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        video_id: state.wizard.videoId,
                        scheduled_at: schedTimestamp,
                        timezone: state.wizard.scheduleTimezone,
                        title: state.wizard.title,
                        description: state.wizard.description
                    })
                });
                const data = await res.json();
                if (!res.ok || !data.success) throw new Error(data.error || 'Failed to schedule');

                dom.uploadProgressBarFill.style.width = '100%';
                dom.uploadPercentText.textContent = '100%';
                dom.uploadStatusIcon.innerHTML = '<svg data-lucide="calendar-check" width="32" height="32"></svg>';
                dom.uploadStatusTitle.textContent = 'Upload Scheduled Successfully!';
                dom.uploadStatusMessage.textContent = `Your video is queued to release on ${state.wizard.scheduleDate} at ${state.wizard.scheduleTime}.`;
                dom.uploadActionButtons.style.display = 'flex';
                showToast('Release scheduled!', 'success');
            } else {
                // Publish Now Mode
                dom.uploadSpeedText.textContent = 'Uploading to YouTube channels...';

                const res = await fetch('/youtube/upload/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ video_id: state.wizard.videoId })
                });
                const data = await res.json();
                if (!res.ok || !data.success) throw new Error(data.error || 'Failed to publish video');

                dom.uploadProgressBarFill.style.width = '100%';
                dom.uploadPercentText.textContent = '100%';
                dom.uploadStatusIcon.innerHTML = '<svg data-lucide="check-circle" width="32" height="32" style="color:var(--primary);"></svg>';
                dom.uploadStatusTitle.textContent = 'Video Published Successfully!';
                dom.uploadStatusMessage.textContent = 'Your video is now live on your YouTube channel.';
                dom.uploadActionButtons.style.display = 'flex';
                showToast('Video published to YouTube!', 'success');
            }

            if (window.lucide) window.lucide.createIcons();
        } catch (err) {
            dom.uploadProgressBarFill.style.background = 'var(--error)';
            dom.uploadStatusIcon.innerHTML = '<svg data-lucide="alert-circle" width="32" height="32" style="color:var(--error);"></svg>';
            dom.uploadStatusTitle.textContent = 'Upload Encountered an Issue';
            dom.uploadStatusMessage.textContent = err.message || 'Could not complete YouTube publish.';
            dom.uploadProgressBarContainer.style.display = 'none';
            dom.uploadActionButtons.style.display = 'flex';
            dom.uploadActionButtons.innerHTML = `
                <button class="btn btn-secondary btn-sm" id="btnEditSettings">Edit Settings</button>
                <button class="btn btn-primary btn-sm" id="btnRetryPublish">Retry</button>
            `;
            document.getElementById('btnEditSettings').addEventListener('click', () => {
                dom.wizardProgressState.style.display = 'none';
                dom.wizardFooter.style.display = 'flex';
                setWizardStep(4);
            });
            document.getElementById('btnRetryPublish').addEventListener('click', () => executeFinalPublish());
            if (window.lucide) window.lucide.createIcons();
            showToast(err.message, 'error');
        }
    }

    dom.btnUploadAnother.addEventListener('click', () => resetWizard());

    // =========================================================================
    // 7. Dedicated Pages: Queue, Scheduled, History, Connection
    // =========================================================================
    async function loadQueue() {
        dom.queueItemsList.innerHTML = '<div style="text-align:center; padding:32px; color:var(--text-muted);">Loading active queue...</div>';
        try {
            const res = await fetch('/youtube/upload-queue');
            const data = await res.json();
            state.queue = data.items || [];
            dom.queueBadgeCount.textContent = state.queue.length;

            if (state.queue.length === 0) {
                dom.queueItemsList.innerHTML = `
                    <div class="compact-empty-state">
                        <svg data-lucide="layers" width="32" height="32"></svg>
                        <h4>Queue is Empty</h4>
                        <p>No videos are currently queued or uploading.</p>
                        <button class="btn btn-primary btn-sm" data-nav="upload">Add Video to Queue</button>
                    </div>`;
                return;
            }

            renderQueueList(state.queue);
        } catch (err) {
            dom.queueItemsList.innerHTML = `<div style="color:var(--error); padding:20px;">Failed to load queue: ${err.message}</div>`;
        }
    }

    function renderQueueList(items) {
        dom.queueItemsList.innerHTML = items.map(q => `
            <div class="desk-card" style="margin-bottom:12px; padding:16px;">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
                    <div style="font-weight:700; font-size:14px; color:var(--text-primary);">${escapeHtml(q.title || 'Untitled Upload')}</div>
                    <span class="status-pill ${q.status === 'completed' ? 'connected' : q.status === 'failed' ? 'disconnected' : ''}">${q.status}</span>
                </div>
                <div style="height:6px; border-radius:3px; background:var(--surface-1); overflow:hidden; margin-bottom:8px;">
                    <div style="height:100%; width:${q.progress || (q.status === 'completed' ? 100 : 35)}%; background:var(--primary);"></div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px; color:var(--text-muted);">
                    <span>Visibility: ${escapeHtml(q.visibility || 'public')}</span>
                    <button class="btn btn-outline btn-sm btn-delete-queue" data-id="${q.id}" style="padding:2px 6px; font-size:11px; color:var(--error); border-color:rgba(239,68,68,0.3);">Cancel</button>
                </div>
            </div>
        `).join('');

        dom.queueItemsList.querySelectorAll('.btn-delete-queue').forEach(btn => {
            btn.addEventListener('click', async () => {
                const confirmed = await showConfirm('Cancel Upload', 'Are you sure you want to remove this item from the upload queue?');
                if (confirmed) {
                    await fetch(`/youtube/upload-queue/${btn.dataset.id}`, { method: 'DELETE' });
                    showToast('Item removed from queue', 'info');
                    loadQueue();
                }
            });
        });

        if (window.lucide) window.lucide.createIcons();
    }

    async function loadScheduled() {
        dom.scheduledItemsList.innerHTML = '<div style="text-align:center; padding:32px; color:var(--text-muted);">Loading scheduled uploads...</div>';
        try {
            const res = await fetch('/youtube/schedules');
            const data = await res.json();
            state.schedules = data.schedules || [];
            dom.scheduledBadgeCount.textContent = state.schedules.length;

            if (state.schedules.length === 0) {
                dom.scheduledItemsList.innerHTML = `
                    <div class="compact-empty-state">
                        <svg data-lucide="calendar-x" width="32" height="32"></svg>
                        <h4>No Scheduled Releases</h4>
                        <p>Plan your video releases in advance to automate your YouTube publishing workflow.</p>
                        <button class="btn btn-primary btn-sm" data-nav="upload" data-mode="schedule">Schedule a Video</button>
                    </div>`;
                return;
            }

            dom.scheduledItemsList.innerHTML = state.schedules.map(s => `
                <div class="compact-video-row" style="padding:14px; margin-bottom:10px;">
                    <div class="compact-video-thumb" style="width:84px; height:48px;">
                        <svg data-lucide="calendar" width="22" height="22" style="color:var(--primary);"></svg>
                    </div>
                    <div class="compact-video-info">
                        <div class="compact-video-title" style="font-size:14px;">${escapeHtml(s.title || 'Scheduled Video')}</div>
                        <div class="compact-video-meta">
                            <span style="color:var(--primary); font-weight:700;">${formatDate(s.scheduled_at)} (${escapeHtml(s.timezone || 'UTC')})</span>
                        </div>
                    </div>
                    <div class="compact-video-actions">
                        <button class="btn btn-outline btn-sm btn-cancel-schedule" data-id="${s.id}" style="color:var(--error); border-color:rgba(239,68,68,0.3);">Cancel</button>
                    </div>
                </div>
            `).join('');

            dom.scheduledItemsList.querySelectorAll('.btn-cancel-schedule').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const confirmed = await showConfirm('Cancel Schedule', 'Are you sure you want to cancel this scheduled release?');
                    if (confirmed) {
                        await fetch(`/youtube/schedules/${btn.dataset.id}`, { method: 'DELETE' });
                        showToast('Schedule cancelled', 'info');
                        loadScheduled();
                    }
                });
            });

            if (window.lucide) window.lucide.createIcons();
        } catch (err) {
            dom.scheduledItemsList.innerHTML = `<div style="color:var(--error); padding:20px;">Failed to load schedules: ${err.message}</div>`;
        }
    }

    async function loadHistory() {
        dom.historyTableBody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:32px; color:var(--text-muted);">Loading publishing history...</td></tr>';
        try {
            const res = await fetch('/youtube/history');
            const data = await res.json();
            state.history = data.history || [];

            if (state.history.length === 0) {
                dom.historyTableBody.innerHTML = `
                    <tr><td colspan="7">
                        <div class="compact-empty-state">
                            <svg data-lucide="file-text" width="32" height="32"></svg>
                            <h4>No Upload History Found</h4>
                            <p>Published and scheduled video uploads will be recorded here.</p>
                        </div>
                    </td></tr>`;
                return;
            }

            renderHistoryTable(state.history);
        } catch (err) {
            dom.historyTableBody.innerHTML = `<tr><td colspan="7" style="color:var(--error); padding:20px;">Failed to load history: ${err.message}</td></tr>`;
        }
    }

    function renderHistoryTable(items) {
        dom.historyTableBody.innerHTML = items.map(h => `
            <tr>
                <td>
                    <div style="width:60px; height:34px; border-radius:4px; overflow:hidden; background:#000;">
                        ${h.thumbnail ? `<img src="${h.thumbnail}" style="width:100%;height:100%;object-fit:cover;">` : '<div style="display:flex;align-items:center;justify-content:center;height:100%;"><svg data-lucide="video" width="14" height="14" style="color:var(--text-muted);"></svg></div>'}
                    </div>
                </td>
                <td style="font-weight:600; color:var(--text-primary); max-width:240px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                    ${escapeHtml(h.title || 'Untitled Video')}
                </td>
                <td>
                    <span class="status-pill connected" style="padding:2px 8px; font-size:10px;">${escapeHtml(h.status || 'published')}</span>
                </td>
                <td style="text-transform:capitalize;">${escapeHtml(h.visibility || 'public')}</td>
                <td>${formatDate(h.published_at || h.created_at)}</td>
                <td>${h.view_count || 0}</td>
                <td style="text-align:right;">
                    ${h.youtube_video_id ? `<a href="https://youtu.be/${h.youtube_video_id}" target="_blank" class="btn btn-secondary btn-sm" style="padding:4px 8px;" title="Watch on YouTube"><svg data-lucide="external-link" width="12" height="12"></svg></a>` : '-'}
                </td>
            </tr>
        `).join('');

        if (window.lucide) window.lucide.createIcons();
    }

    async function loadConnection() {
        try {
            const res = await fetch('/youtube/status');
            const data = await res.json();
            state.connected = data.connected;
            state.channel = data.channel;

            updateConnectionUI();

            if (state.connected && state.channel) {
                dom.connectionActiveCard.style.display = 'block';
                dom.connectionInactiveCard.style.display = 'none';

                dom.channelTitle.textContent = state.channel.title || 'Connected YouTube Channel';
                dom.channelHandle.textContent = state.channel.handle || '';
                dom.channelSubscribers.textContent = `${state.channel.subscribers || '0'} Subscribers`;
                dom.channelVideoCount.textContent = `${state.channel.video_count || '0'} Uploaded Videos`;

                if (state.channel.avatar) {
                    dom.channelAvatar.src = state.channel.avatar;
                } else {
                    dom.channelAvatar.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="%23888" stroke-width="2"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>';
                }
            } else {
                dom.connectionActiveCard.style.display = 'none';
                dom.connectionInactiveCard.style.display = 'block';
            }

            if (window.lucide) window.lucide.createIcons();
        } catch (err) {
            console.error('Failed to load connection status:', err);
        }
    }

    dom.btnRefreshConnection.addEventListener('click', async () => {
        showToast('Refreshing connection...', 'info');
        await loadConnection();
        showToast('Connection status updated', 'success');
    });

    dom.btnDisconnectChannel.addEventListener('click', async () => {
        const confirmed = await showConfirm('Disconnect Channel', 'Are you sure you want to disconnect this YouTube channel from UpClip Studio?');
        if (confirmed) {
            try {
                await fetch('/youtube/disconnect', { method: 'POST' });
                showToast('Channel disconnected', 'info');
                await loadConnection();
                await loadOverview();
            } catch (err) {
                showToast(err.message, 'error');
            }
        }
    });

    async function loadSettings() {
        try {
            const res = await fetch('/youtube/settings');
            const data = await res.json();
            if (data.settings) {
                if (data.settings.default_visibility) dom.settingDefaultVisibility.value = data.settings.default_visibility;
                if (data.settings.default_category) dom.settingDefaultCategory.value = data.settings.default_category;
                if (data.settings.default_tags) dom.settingDefaultTags.value = data.settings.default_tags;
            }
        } catch (err) {
            console.warn('Could not load settings:', err);
        }
    }

    dom.deskSettingsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            await fetch('/youtube/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    default_visibility: dom.settingDefaultVisibility.value,
                    default_category: dom.settingDefaultCategory.value,
                    default_tags: dom.settingDefaultTags.value,
                })
            });
            showToast('Settings saved successfully', 'success');
        } catch (err) {
            showToast('Failed to save settings', 'error');
        }
    });

    // Quick action buttons
    dom.btnQuickUpload.addEventListener('click', () => switchView('upload'));
    dom.btnQuickSchedule.addEventListener('click', () => {
        switchView('upload');
        state.wizard.timingMode = 'schedule';
        const rad = document.querySelector('input[name="publishingMode"][value="schedule"]');
        if (rad) {
            rad.checked = true;
            rad.dispatchEvent(new Event('change'));
        }
    });
    dom.btnQuickQueue.addEventListener('click', () => switchView('queue'));
    dom.btnQuickHistory.addEventListener('click', () => switchView('history'));
    dom.btnQuickConnect.addEventListener('click', () => switchView('connection'));

    // =========================================================================
    // 8. Initialization
    // =========================================================================
    function init() {
        // Initial view activation
        switchView(state.currentView, false);

        // Fetch initial overview
        loadOverview();

        // Background polling for queue if items are in flight (every 10s)
        setInterval(() => {
            if (state.currentView === 'overview' || state.currentView === 'queue') {
                const hasInFlight = state.queue.some(q => q.status === 'uploading' || q.status === 'processing');
                if (hasInFlight) {
                    if (state.currentView === 'overview') loadOverview();
                    if (state.currentView === 'queue') loadQueue();
                }
            }
        }, 10000);
    }

    init();

})();
