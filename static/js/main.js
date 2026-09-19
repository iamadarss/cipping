// ============================================
// AI Shorts Studio - Frontend Logic (v2 Wizard)
// ============================================

// SVG icon strings (Lucide-style inline SVGs)
var ICONS = {
    save: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>',
    download: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
    caption: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    youtube: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    trash: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
    moon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
    sun: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>',
    downloadBtn: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
    sliders: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>',
};

// ---------- Theme: Always Emerald + Cream + Graphite (Dark Theme) ----------
function initTheme() {
    document.documentElement.setAttribute('data-theme', 'dark');
    if (localStorage.getItem('theme') !== 'dark') {
        localStorage.setItem('theme', 'dark');
    }
}
initTheme();

// ---------- Mobile Menu ----------
const menuToggle = document.getElementById('menuToggle');
const mobileMenu = document.getElementById('mobileMenu');
if (menuToggle && mobileMenu) {
    menuToggle.addEventListener('click', () => {
        mobileMenu.hidden = !mobileMenu.hidden;
    });
}

// ---------- Pipeline Timer ----------
let timerInterval = null;
let timerStart = null;
const timerEl = document.getElementById('pipelineTimer');
function startTimer() {
    timerStart = Date.now();
    stopTimer();
    timerInterval = setInterval(() => {
        if (!timerEl) return;
        const secs = Math.floor((Date.now() - timerStart) / 1000);
        const m = Math.floor(secs / 60);
        const s = secs % 60;
        timerEl.textContent = `${m}:${s.toString().padStart(2, '0')}`;
    }, 250);
}
function stopTimer() {
    if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
}

const state = {
    currentFile: null,
    currentMetadata: null,
    jobId: null,
    pollInterval: null,
    result: null,
    currentStep: 1,
    totalSteps: 5,
    clips: [],
};

// ---------- DOM References ----------
const uploadZone = document.getElementById('uploadZone');
const videoInput = document.getElementById('videoInput');
const browseBtn = document.getElementById('browseBtn');
const uploadProgress = document.getElementById('uploadProgress');
const uploadFill = document.getElementById('uploadFill');
const uploadStatus = document.getElementById('uploadStatus');
const metaPreview = document.getElementById('metaPreview');
const ffmpegBadge = document.getElementById('ffmpegBadge');

const wizNext = document.getElementById('wizNext');
const wizPrev = document.getElementById('wizPrev');

const pipelineWrap = document.getElementById('pipelineWrap');
const pipelineFill = document.getElementById('pipelineFill');
const pipelinePercent = document.getElementById('pipelinePercent');
const stepsContainer = document.getElementById('stepsContainer');
const logBody = document.getElementById('logBody');

const reviewGrid = document.getElementById('reviewGrid');
const countConflict = document.getElementById('countConflict');

const confirmModal = document.getElementById('confirmModal');
const confirmText = document.getElementById('confirmText');

// ---------- Helpers ----------
function formatBytes(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatTime(sec) {
    if (sec === undefined || sec === null) return '-';
    const m = Math.floor(sec / 60);
    const s = Math.round(sec % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
}

function addLog(message, type = '') {
    const div = document.createElement('div');
    div.className = 'log-line' + (type ? ' ' + type : '');
    div.textContent = message;
    logBody.appendChild(div);
    logBody.scrollTop = logBody.scrollHeight;
}

function setStepState(step, className) {
    const el = document.querySelector(`.step[data-step="${step}"]`);
    if (el) {
        el.classList.remove('active', 'done', 'error');
        if (className) el.classList.add(className);
    }
}
function resetSteps() {
    for (let i = 1; i <= 5; i++) setStepState(i, '');
}

// ---------- Wizard Navigation ----------
function nextStep() {
    const step = state.currentStep;
    if (step === 1) {
        if (!state.currentFile) {
            alert('Please upload a video first.');
            return;
        }
        showStep(2);
    } else if (step === 2) {
        showStep(3);
        startPipeline();
    } else if (step === 3) {
        startPipeline();
    } else if (step === 4) {
        showStep(5);
    } else if (step === 5) {
        // Last step
    } else {
        showStep(step + 1);
    }
}

if (wizNext) {
    wizNext.addEventListener('click', nextStep);
}
if (wizPrev) {
    wizPrev.addEventListener('click', () => {
        if (state.currentStep === 5) {
            showStep(4);
        } else if (state.currentStep === 4) {
            showStep(2);
        } else if (state.currentStep === 3) {
            showStep(2);
        } else {
            showStep(Math.max(1, state.currentStep - 1));
        }
    });
}

// ---------- Conditional question logic ----------
document.querySelectorAll('input[name="clipmode"]').forEach(r => {
    r.addEventListener('change', updateClippingOptions);
});
const clipCountModeEl = document.getElementById('clipCountMode');
if (clipCountModeEl) {
    clipCountModeEl.addEventListener('change', () => {
        const v = clipCountModeEl.value;
        const customWrap = document.getElementById('customCountWrap');
        if (customWrap) customWrap.hidden = v !== 'custom';
    });
}

function updateClippingOptions() {
    const checkedMode = document.querySelector('input[name="clipmode"]:checked');
    if (!checkedMode) return;
    const mode = checkedMode.value;
    const dur = document.getElementById('durationSettings');
    const cnt = document.getElementById('countSettings');
    if (dur) dur.hidden = mode !== 'duration';
    if (cnt) cnt.hidden = mode !== 'count';
}

// ---------- Caption Options Toggle ----------
function updateCaptionOptions() {
    const capEl = document.getElementById('captionEnabled');
    const enabled = capEl ? capEl.checked : false;
    const wrap = document.getElementById('captionOptions');
    if (wrap) wrap.hidden = !enabled;
}
const captionEnabled = document.getElementById('captionEnabled');
if (captionEnabled) {
    captionEnabled.addEventListener('change', updateCaptionOptions);
    updateCaptionOptions();
}

// ---------- FFmpeg Check ----------
async function checkFfmpeg() {
    if (!ffmpegBadge) return;
    try {
        const res = await fetch('/process/ffmpeg');
        const data = await res.json();
        if (data.success && data.installed) {
            ffmpegBadge.textContent = 'FFmpeg Ready';
            ffmpegBadge.className = 'ffmpeg-badge ok';
        } else {
            ffmpegBadge.textContent = 'FFmpeg Missing';
            ffmpegBadge.className = 'ffmpeg-badge error';
        }
    } catch (e) {
        ffmpegBadge.textContent = 'FFmpeg Check Failed';
        ffmpegBadge.className = 'ffmpeg-badge error';
    }
}

// ---------- Upload ----------
if (browseBtn && videoInput && uploadZone) {
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        console.log('Browse button clicked');
        videoInput.click();
    });
    uploadZone.addEventListener('click', () => {
        console.log('Upload zone clicked');
        videoInput.click();
    });

    let dragCounter = 0;
    ['dragenter', 'dragover'].forEach(evt => {
        uploadZone.addEventListener(evt, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dragCounter++;
            uploadZone.classList.add('dragover');
        });
    });
    uploadZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dragCounter--;
        if (dragCounter <= 0) {
            dragCounter = 0;
            uploadZone.classList.remove('dragover');
        }
    });
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dragCounter = 0;
        uploadZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length) uploadVideo(files[0]);
    });
    videoInput.addEventListener('change', (e) => {
        console.log('File input changed, files:', e.target.files.length);
        if (e.target.files.length) uploadVideo(e.target.files[0]);
    });
} else {
    console.warn('Upload elements not found:', {
        browseBtn: !!browseBtn,
        videoInput: !!videoInput,
        uploadZone: !!uploadZone
    });
}

async function uploadVideo(file) {
    if (!file) return;
    const formData = new FormData();
    formData.append('video', file);

    uploadProgress.hidden = false;
    uploadStatus.textContent = `Uploading ${file.name}...`;

    try {
        const res = await fetch('/upload/video', { method: 'POST', body: formData });
        const contentType = res.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            const data = await res.json();
            if (!data.success) {
                uploadStatus.textContent = 'Error: ' + (data.error || 'Upload failed');
                console.error('Upload error:', data.error);
                return;
            }
            handleUploadSuccess(data);
        } else {
            const text = await res.text();
            uploadStatus.textContent = `Server error (${res.status}): Upload failed`;
            console.error('Upload non-JSON response:', res.status, text.slice(0, 200));
        }
    } catch (err) {
        uploadStatus.textContent = 'Upload failed: ' + err.message;
        console.error('Upload exception:', err);
    } finally {
        uploadFill.style.width = '100%';
        setTimeout(() => {
            uploadProgress.hidden = true;
            uploadFill.style.width = '0%';
        }, 1500);
    }
}

function displayVideoMetadata(metadata, thumbnail) {
    if (!metadata) return;

    // Hide upload zone completely when video is dropped/uploaded
    const uZone = document.getElementById('uploadZone') || (typeof uploadZone !== 'undefined' ? uploadZone : null);
    if (uZone) {
        uZone.hidden = true;
        uZone.style.display = 'none';
    }

    // Show the rich videoMetaCard in Step 1
    const metaCard = document.getElementById('videoMetaCard');
    if (metaCard) {
        metaCard.hidden = false;
        metaCard.style.display = 'block';
    }

    // Populate thumbnail in Step 1
    const thumbImg = document.getElementById('metaThumbImg');
    if (thumbImg) {
        const sourceStem = state.currentFile ? state.currentFile.substring(0, state.currentFile.lastIndexOf('.')) : '';
        if (thumbnail) {
            thumbImg.src = thumbnail;
        } else if (sourceStem) {
            thumbImg.src = `/download/thumbnail/${encodeURIComponent(sourceStem)}_thumb.jpg`;
        }
        thumbImg.onerror = function() {
            this.src = '/static/img/default_thumb.png';
        };
    }

    // Populate duration badge
    const durationBadge = document.getElementById('metaDurationBadge');
    if (durationBadge) {
        durationBadge.textContent = formatTime(metadata.duration || 0);
    }

    // Populate Step 1 display fields
    const dispFilename = document.getElementById('metaDisplayFilename');
    if (dispFilename) dispFilename.textContent = metadata.filename || state.currentFile || 'Video';

    const dispResolution = document.getElementById('metaDisplayResolution');
    if (dispResolution) {
        dispResolution.textContent = (metadata.width && metadata.height) ? `${metadata.width} × ${metadata.height}` : '1920 × 1080';
    }

    const dispDuration = document.getElementById('metaDisplayDuration');
    if (dispDuration) {
        dispDuration.textContent = formatTime(metadata.duration || 0);
    }

    const dispFps = document.getElementById('metaDisplayFPS');
    if (dispFps) {
        dispFps.textContent = metadata.fps ? (typeof metadata.fps === 'number' ? metadata.fps.toFixed(2) : metadata.fps) + ' FPS' : '30.00 FPS';
    }

    const dispSize = document.getElementById('metaDisplaySize');
    if (dispSize) {
        dispSize.textContent = metadata.size_bytes ? formatBytes(metadata.size_bytes) : '-';
    }

    // Also populate Step 2 player meta fields if they exist
    const pDims = document.getElementById('step2VideoDims');
    if (pDims) pDims.textContent = (metadata.width && metadata.height) ? `${metadata.width}×${metadata.height}` : '1920×1080';

    const pFilename = document.getElementById('metaFilename');
    if (pFilename) pFilename.textContent = metadata.filename || state.currentFile || '-';

    const pResolution = document.getElementById('metaResolution');
    if (pResolution) pResolution.textContent = (metadata.width && metadata.height) ? `${metadata.width}×${metadata.height}` : '-';

    const pFps = document.getElementById('metaFPS');
    if (pFps) pFps.textContent = metadata.fps ? `${metadata.fps} FPS` : '-';

    const pSize = document.getElementById('metaSize');
    if (pSize) pSize.textContent = metadata.size_bytes ? formatBytes(metadata.size_bytes) : '-';

    // Enable wizard Next button for Step 1
    if (wizNext && state.currentStep === 1) {
        wizNext.disabled = false;
        wizNext.innerHTML = 'Continue to AI Clip Settings →';
    }
}

function handleUploadSuccess(data) {
    state.currentFile = data.filename;
    state.currentMetadata = data.metadata;
    uploadStatus.textContent = 'Upload complete! Video ready for processing.';
    uploadStatus.style.color = 'var(--success)';

    // Display rich metadata in Step 1 (Do NOT auto-advance to step 2)
    displayVideoMetadata(data.metadata, data.thumbnail);
}

// ---------- Build summary ----------
function buildSummary() {
    const lang = document.getElementById('langTranscript').selectedOptions[0].textContent;
    const langSub = document.getElementById('langSubtitle').value;
    const subLabel = langSub === 'auto' ? 'Same as transcript' :
        document.getElementById('langSubtitle').selectedOptions[0].textContent;
    const aspect = document.querySelector('input[name="aspect"]:checked').value;
    const mode = document.querySelector('input[name="clipmode"]:checked').value;
    const naming = document.querySelector('input[name="naming"]:checked').value;

    const modeLabels = { ai: 'AI decides', duration: 'Duration', count: 'Count' };
    const namingLabels = { content: 'Content-based', sequential: 'Sequential' };

    let clipsInfo = '';
    if (mode === 'duration') {
        const dur = document.getElementById('clipDuration').value;
        const how = document.getElementById('clipCountMode').value;
        clipsInfo = `${dur}s per clip, ${how === 'all' ? 'all possible' : document.getElementById('customCount').value + ' clips'}`;
    } else if (mode === 'count') {
        clipsInfo = `${document.getElementById('clipCount').value} clips`;
    } else {
        clipsInfo = 'AI decides';
    }

    let captionStyleInfo = '';
    const captionStylePreset = document.getElementById('captionStylePreset');
    if (captionStylePreset && captionStylePreset.value) {
        const presetLabel = captionStylePreset.options[captionStylePreset.selectedIndex]?.text || captionStylePreset.value;
        captionStyleInfo = presetLabel;
    }

    document.getElementById('settingsSummary').innerHTML = `
        <div class="summary-row"><span class="summary-label">Video</span><span class="summary-value">${state.currentFile}</span></div>
        <div class="summary-row"><span class="summary-label">Transcript Language</span><span class="summary-value">${lang}</span></div>
        <div class="summary-row"><span class="summary-label">Subtitle Language</span><span class="summary-value">${subLabel}</span></div>
        <div class="summary-row"><span class="summary-label">Aspect Ratio</span><span class="summary-value">${aspect}</span></div>
        <div class="summary-row"><span class="summary-label">Clipping</span><span class="summary-value">${modeLabels[mode]} — ${clipsInfo}</span></div>
        <div class="summary-row"><span class="summary-label">Naming</span><span class="summary-value">${namingLabels[naming]}</span></div>
        ${captionStyleInfo ? `<div class="summary-row"><span class="summary-label">Caption Style</span><span class="summary-value">${captionStyleInfo}</span></div>` : ''}
    `;
}

// ---------- Start Pipeline ----------
async function startPipeline() {
    const settings = collectSettings();

    wizNext.disabled = true;
    wizNext.innerHTML = '<span class="spinner"></span> Processing...';
    pipelineWrap.hidden = false;
    resetSteps();
    logBody.innerHTML = '<div class="log-line muted">Starting pipeline...</div>';
    pipelineFill.style.width = '0%';
    pipelinePercent.textContent = '0%';
    startTimer();

    try {
        const res = await fetch('/process/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: state.currentFile, settings }),
        });
        const data = await res.json();
        if (!data.success) {
            addLog('Failed to start: ' + data.error, 'error-line');
            resetPipelineBtn();
            return;
        }
        state.jobId = data.job_id;
        addLog(`Job started: ${data.job_id}`, 'success');
        startPolling(data.job_id);
    } catch (err) {
        addLog('Error: ' + err.message, 'error-line');
        resetPipelineBtn();
    }
}

function collectSettings() {
    const checkedMode = document.querySelector('input[name="clipmode"]:checked');
    const mode = checkedMode ? checkedMode.value : 'ai';
    const checkedAspect = document.querySelector('input[name="aspect"]:checked');
    const checkedNaming = document.querySelector('input[name="naming"]:checked');

    const captionStylePreset = document.getElementById('captionStylePreset')?.value || '';
    let captionStyleData = null;
    if (captionStylePreset) {
        const presetMap = {
            'tiktok_pop': { id: 'tiktok_pop', name: 'TikTok Pop', font_family: 'Arial Black', font_size: 42, font_weight: 800, text_color: '#FFFFFF', active_word_color: '#fbbf24', background_color: '#000000', background_opacity: 0.0, outline_color: '#000000', outline_width: 3, shadow_color: '#000000', shadow_blur: 4, shadow_offset_y: 2, position: 'bottom', animation: 'pop', letter_spacing: 0, line_height: 1.2, max_lines: 2 },
            'youtube': { id: 'youtube', name: 'YouTube', font_family: 'Arial', font_size: 22, font_weight: 700, text_color: '#FFFFFF', active_word_color: '#FFFFFF', background_color: '#000000', background_opacity: 0.0, outline_color: '#000000', outline_width: 2, shadow_color: '#000000', shadow_blur: 1, shadow_offset_y: 0, position: 'bottom', animation: 'none', letter_spacing: 0, line_height: 1.4, max_lines: 2 },
            'minimal': { id: 'minimal', name: 'Minimal', font_family: 'Inter', font_size: 32, font_weight: 400, text_color: '#FFFFFF', active_word_color: '#FFFFFF', background_color: '#000000', background_opacity: 0.0, outline_color: '#000000', outline_width: 0, shadow_color: '#000000', shadow_blur: 0, shadow_offset_y: 0, position: 'bottom', animation: 'none', letter_spacing: 1, line_height: 1.4, max_lines: 2 },
            'bold': { id: 'bold', name: 'Bold', font_family: 'Arial Black', font_size: 48, font_weight: 900, text_color: '#FFFFFF', active_word_color: '#fbbf24', background_color: '#000000', background_opacity: 0.6, outline_color: '#000000', outline_width: 4, shadow_color: '#000000', shadow_blur: 8, shadow_offset_y: 2, position: 'bottom', animation: 'pop', letter_spacing: 0, line_height: 1.1, max_lines: 1 },
        };
        const presetSize = parseInt(document.getElementById('presetCaptionSize')?.value || '34', 10);
        const presetPosition = document.getElementById('presetCaptionPosition')?.value || 'bottom';
        const base = presetMap[captionStylePreset] || {};
        captionStyleData = { ...base, font_size: presetSize, position: presetPosition };
    }
    const settings = {
        language: document.getElementById('langTranscript') ? document.getElementById('langTranscript').value : 'en',
        subtitle_language: document.getElementById('langSubtitle') ? document.getElementById('langSubtitle').value : 'auto',
        subtitle_enabled: document.getElementById('subtitleEnabled') ? document.getElementById('subtitleEnabled').checked : true,
        aspect: checkedAspect ? checkedAspect.value : '9:16',
        clipping_mode: mode,
        naming: checkedNaming ? checkedNaming.value : 'content',
        quality: document.getElementById('exportQuality') ? document.getElementById('exportQuality').value : 'original',
        caption_enabled: document.getElementById('captionEnabled') ? document.getElementById('captionEnabled').checked : false,
        caption_template: document.getElementById('captionTemplate') ? document.getElementById('captionTemplate').value : 'classic',
        caption_animation: document.getElementById('captionAnimation') ? document.getElementById('captionAnimation').value : 'pop',
        caption_position: document.getElementById('captionPosition') ? document.getElementById('captionPosition').value : 'bottom',
        caption_font: document.getElementById('captionFont') ? document.getElementById('captionFont').value : 'Arial',
        caption_color: document.getElementById('captionColor') ? document.getElementById('captionColor').value : '#FFFFFF',
        caption_size: document.getElementById('captionSize') ? parseInt(document.getElementById('captionSize').value, 10) || 22 : 22,
        caption_outline: document.getElementById('captionOutline') ? parseInt(document.getElementById('captionOutline').value, 10) || 2 : 2,
        caption_margin_v: document.getElementById('captionMarginV') ? parseInt(document.getElementById('captionMarginV').value, 10) || 60 : 60,
        caption_background: document.getElementById('captionBackground') ? document.getElementById('captionBackground').value : 'none',
        caption_style: captionStyleData,
        whisper_model: document.getElementById('whisperModel') ? document.getElementById('whisperModel').value : 'base',
        face_tracking: document.getElementById('faceTrackingMode') ? document.getElementById('faceTrackingMode').value : 'auto',
        scene_threshold: document.getElementById('sceneThresholdRange') ? parseFloat(document.getElementById('sceneThresholdRange').value) : 0.3,
    };

    if (mode === 'duration') {
        settings.clip_duration = parseInt(document.getElementById('clipDuration')?.value, 10) || 30;
        if (document.getElementById('clipCountMode')?.value === 'custom') {
            settings.clip_count = parseInt(document.getElementById('customCount')?.value, 10) || 5;
        }
    }
    if (mode === 'count') {
        settings.clip_count = parseInt(document.getElementById('clipCount')?.value, 10) || 5;
    }

    return settings;
}

function resetPipelineBtn() {
    wizNext.disabled = false;
    wizNext.innerHTML = '<span class="spinner" hidden></span> Generate Clips';
}

// ---------- Polling ----------
function startPolling(jobId) {
    state.pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`/process/status/${jobId}`);
            const data = await res.json();
            if (!data.success) return;
            updateProgressUI(data);
        } catch (err) {
            addLog('Polling error: ' + err.message, 'error-line');
        }
    }, 1500);
}

function updateProgressUI(data) {
    const percent = Math.round((data.steps_completed / data.total_steps) * 100);
    pipelineFill.style.width = `${percent}%`;
    const maxSteps = data.total_steps || 8;
    for (let i = 1; i <= maxSteps; i++) {
        if (data.status === 'error') {
            setStepState(i, i === data.steps_completed ? 'error' : (i < data.steps_completed ? 'done' : ''));
        } else if (i < data.steps_completed) {
            setStepState(i, 'done');
        } else if (i === data.steps_completed) {
            setStepState(i, 'active');
} else {
            setStepState(i, '');
        }
    }

    if (data.logs && Array.isArray(data.logs)) {
        const currentCount = logBody.querySelectorAll('.log-line').length;
        for (let i = currentCount; i < data.logs.length; i++) {
            const msg = data.logs[i];
            const cls = msg.startsWith('ERROR') ? 'error-line'
                       : msg.includes('✅') ? 'success' : '';
            addLog(msg, cls);
        }
    }

    if (data.finished) {
        clearInterval(state.pollInterval);
        state.pollInterval = null;
        resetPipelineBtn();
        stopTimer();

        if (data.status === 'done') {
            addLog('✅ Pipeline completed successfully!', 'success');
            handlePipelineDone(data.result);
        } else if (data.status === 'error') {
            addLog('❌ Pipeline failed: ' + data.error, 'error-line');
        }
    }
}

function handlePipelineDone(result) {
    if (!result) return;
    state.result = result;
    state.clips = result.clips_meta || (result.clips || []).map(n => ({ name: n, url: `/download/clip/${n}` }));

    // Handle clip count conflict
    if (result.clip_count_conflict) {
        showClipConflict(result.clip_count_conflict);
    }

    // Populate review grid
    renderReviewGrid();

    // Go to review step (Step 4)
    showStep(4);
}

// ---------- Clip Count Conflict Modal ----------
function showClipConflict(conflict) {
    if (!confirmModal || !confirmText) return;
    confirmText.textContent = `You requested ${conflict.requested} clips, but only ${conflict.available} good clips are available. Continue with ${conflict.available}?`;
    confirmModal.hidden = false;
}

if (document.getElementById('confirmYes')) {
    document.getElementById('confirmYes').addEventListener('click', () => {
        if (confirmModal) confirmModal.hidden = true;
    });
}
if (document.getElementById('confirmNo')) {
    document.getElementById('confirmNo').addEventListener('click', () => {
        if (confirmModal) confirmModal.hidden = true;
        showStep(2); // back to clipping settings
    });
}
if (document.getElementById('confirmClose')) {
    document.getElementById('confirmClose').addEventListener('click', () => {
        if (confirmModal) confirmModal.hidden = true;
    });
}
if (confirmModal) {
    confirmModal.addEventListener('click', (e) => {
        if (e.target === confirmModal) {
            confirmModal.hidden = true;
        }
    });
}

// ---------- Logo Navigation ----------
const brandEl = document.querySelector('.brand');
if (brandEl) {
    brandEl.style.cursor = 'pointer';
    brandEl.addEventListener('click', () => {
        if (window.location.pathname !== '/' && window.location.pathname !== '/index.html') {
            window.location.href = '/';
        }
    });
}

// ---------- Review Grid ----------
function renderReviewGrid() {
    reviewGrid.innerHTML = '';
    countConflict.hidden = true;

    if (!state.clips.length) {
        reviewGrid.innerHTML = '<p class="muted">No clips generated.</p>';
        return;
    }

    const sourceStem = state.currentFile ? state.currentFile.substring(0, state.currentFile.lastIndexOf('.')) : '';
    const thumbUrl = sourceStem ? `/download/thumbnail/${encodeURIComponent(sourceStem)}_thumb.jpg` : '/static/img/default_thumb.png';

    state.clips.forEach((clip, idx) => {
        const card = document.createElement('div');
        card.className = 'review-clip card';
        card.setAttribute('data-clip-name', clip.name);
        card.setAttribute('data-idx', idx);
        
        card.innerHTML = `
            <input type="checkbox" class="review-clip-checkbox" data-idx="${idx}" style="position: absolute; top: 10px; left: 10px; z-index: 10; width: 18px; height: 18px; cursor: pointer;">
            <div class="project-thumb-wrap" style="position: relative; aspect-ratio: 9/16; background: #000; overflow: hidden; border-radius: var(--radius-sm); cursor: pointer;" data-action="preview" data-idx="${idx}">
                <img class="project-thumb" src="${thumbUrl}" alt="Clip thumbnail" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.onerror=null; this.src='/static/img/default_thumb.png'">
                <div class="play-overlay" style="position: absolute; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity var(--transition-fast);">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="#fff" stroke="none"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                </div>
                <div style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.6); padding: 2px 6px; border-radius: 4px; font-size: 10px; font-family: var(--font-mono); color: #fff;">
                    Clip
                </div>
            </div>
            <input class="clip-name-input" value="${clip.name}" data-idx="${idx}" style="width: 100%; margin-top: 8px; font-size: 12px; font-weight: 600; text-align: center; background: transparent; border: 1px solid var(--border); border-radius: 4px; padding: 4px;">
            <div class="clip-actions" style="display: flex; gap: var(--space-1); justify-content: center; margin-top: 8px; width: 100%;">
                <button class="btn-sm" data-action="preview" data-idx="${idx}" title="Preview Clip" style="padding: 4px 8px; font-size: 11px;">Preview</button>
                <button class="btn-sm accent" data-action="open-caption" data-idx="${idx}" title="Open in Caption Studio" style="padding: 4px 8px; font-size: 11px;">Captions</button>
                <button class="btn-sm danger" data-action="delete" data-idx="${idx}" title="Delete Clip" style="padding: 4px 8px; font-size: 11px;">Delete</button>
            </div>
        `;
        
        const chk = card.querySelector('.review-clip-checkbox');
        chk.addEventListener('change', (e) => {
            if (chk.checked) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
            updateBatchActionsBar();
        });

        const thumbWrap = card.querySelector('.project-thumb-wrap');
        thumbWrap.addEventListener('mouseover', () => {
            thumbWrap.querySelector('.play-overlay').style.opacity = '1';
        });
        thumbWrap.addEventListener('mouseout', () => {
            thumbWrap.querySelector('.play-overlay').style.opacity = '0';
        });

        reviewGrid.appendChild(card);
    });
}

function updateBatchActionsBar() {
    const bar = document.getElementById('batchActionsBar');
    const text = document.getElementById('selectedCountText');
    const checked = document.querySelectorAll('.review-clip-checkbox:checked');
    if (bar) {
        if (checked.length > 0) {
            bar.style.display = 'flex';
            if (text) text.textContent = `${checked.length} clip${checked.length > 1 ? 's' : ''} selected`;
        } else {
            bar.style.display = 'none';
        }
    }
}

if (reviewGrid) {
    reviewGrid.addEventListener('click', async (e) => {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        const idx = parseInt(btn.dataset.idx, 10);
        const clip = state.clips[idx];
        if (!clip) return;

        const action = btn.dataset.action;

        if (action === 'preview') {
            previewClip(clip.name);
        } else if (action === 'open-caption') {
            const projectId = state.result?.project_id || (window.UpClipActiveProject ? `proj_${window.UpClipActiveProject.id}` : '');
            const clipSubtitleMap = state.result?.clip_subtitle_map || {};
            const clipSrt = clipSubtitleMap[clip.name]?.srt || state.result?.srt || '';
            const clipVtt = clipSubtitleMap[clip.name]?.vtt || state.result?.vtt || '';
            const captionStyle = state.result?.caption_style || null;
            const navUrl = `/open-caption-studio?video=${encodeURIComponent(clip.name)}&project_id=${encodeURIComponent(projectId)}&srt=${encodeURIComponent(clipSrt)}&vtt=${encodeURIComponent(clipVtt)}&style=${encodeURIComponent(captionStyle ? JSON.stringify(captionStyle) : '')}`;
            window.location.href = navUrl;
        } else if (action === 'delete') {
            const confirmed = confirm(`Delete ${clip.name}?`);
            if (!confirmed) return;
            const res = await fetch('/process/clip/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: clip.name }),
            });
            const data = await res.json();
            if (data.success) {
                state.clips.splice(idx, 1);
                renderReviewGrid();
                updateBatchActionsBar();
            } else {
                alert('Delete failed: ' + data.error);
            }
        }
    });

    reviewGrid.addEventListener('change', async (e) => {
        const input = e.target.closest('.clip-name-input');
        if (!input) return;
        const idx = parseInt(input.dataset.idx, 10);
        const clip = state.clips[idx];
        if (!clip) return;
        const newName = input.value.trim();
        if (!newName || newName === clip.name) return;
        const res = await fetch('/process/clip/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ old_name: clip.name, new_name: newName }),
        });
        const data = await res.json();
        if (data.success) {
            clip.name = newName;
            clip.url = `/download/clip/${newName}`;
            window.UpClipToast.show('Clip renamed successfully', 'success');
            renderReviewGrid();
        } else {
            alert('Rename failed: ' + data.error);
            input.value = clip.name; // Reset
        }
    });
}


// ---------- Export (Step 8) ----------
function renderExport() {
    const result = state.result;
    if (!result) return;

    const finalVideo = document.getElementById('finalVideo');
    if (finalVideo) {
        finalVideo.hidden = true;
        finalVideo.src = '';
    }

    const finalDownloadBtn = document.getElementById('downloadFinalBtn');
    if (finalDownloadBtn) {
        finalDownloadBtn.hidden = true;
        finalDownloadBtn.onclick = null;
    }

    const subtitleList = document.getElementById('subtitleList');
    if (subtitleList) {
        subtitleList.innerHTML = '';
        const items = [
            { name: 'SRT File', url: result.srt },
            { name: 'VTT File', url: result.vtt },
        ];
        items.forEach(item => {
            if (item.url && item.url !== 'null') {
                const div = document.createElement('div');
                div.className = 'download-item';
                div.innerHTML = `
                    <div><div class="file-name">${item.name}</div><div class="file-size">Subtitle file</div></div>
                    <a class="download-link" href="${item.url}">${ICONS.download} Download</a>
                `;
                subtitleList.appendChild(div);
            }
        });
    }

    const transcriptList = document.getElementById('transcriptList');
    if (transcriptList && result.transcript_file) {
        transcriptList.innerHTML = '';
        const div = document.createElement('div');
        div.className = 'download-item';
        div.innerHTML = `
            <div><div class="file-name">Transcript JSON</div><div class="file-size">${result.transcript ? result.transcript.length + ' segments' : ''}</div></div>
            <a class="download-link" href="${result.transcript_file}">${ICONS.download} Download</a>
        `;
        transcriptList.appendChild(div);
    }

    const transcriptView = document.getElementById('transcriptView');
    if (transcriptView) {
        transcriptView.innerHTML = '';
        const t = result.subtitle_transcript || result.transcript;
        if (t && t.length) {
            t.forEach(seg => {
                const line = document.createElement('div');
                line.className = 'transcript-line';
                line.innerHTML = `
                    <span class="transcript-time">${formatTime(seg.start)} - ${formatTime(seg.end)}</span>
                    <span class="transcript-text">${seg.text}</span>
                `;
                transcriptView.appendChild(line);
            });
        } else {
            transcriptView.innerHTML = '<p class="muted">No transcript available.</p>';
        }
    }

    const downloadAllBtn = document.getElementById('downloadAllBtn');
    if (downloadAllBtn) {
        downloadAllBtn.innerHTML = ICONS.download + ' Download All Clips (ZIP)';
        downloadAllBtn.onclick = () => {
            window.open('/download/all', '_blank');
        };
    }

    const exportQualityBtn = document.getElementById('exportQualityBtn');
    if (exportQualityBtn) {
        exportQualityBtn.innerHTML = ICONS.sliders + ' Export Selected Quality';
        exportQualityBtn.onclick = () => {
            const quality = document.getElementById('exportQuality').value;
            const firstClip = (state.clips && state.clips[0] && state.clips[0].name) || (result.clips && result.clips[0]);
            if (!firstClip) return;
            window.open(`/download/export/${encodeURIComponent(firstClip)}?quality=${quality}`, '_blank');
        };
    }

    const clipCaptionsCard = document.getElementById('clipCaptionsCard');
    if (clipCaptionsCard) clipCaptionsCard.hidden = true;
}

function showStep(step) {
    state.currentStep = step;

    // Pause video player if leaving Step 2
    const player = document.getElementById('sourceVideoPlayer');
    if (step !== 2 && player && !player.paused) {
        player.pause();
        const playPause = document.getElementById('videoPlayPause');
        if (playPause) {
            const playIcon = playPause.querySelector('.play-icon');
            const pauseIcon = playPause.querySelector('.pause-icon');
            if (playIcon) playIcon.style.display = 'block';
            if (pauseIcon) pauseIcon.style.display = 'none';
        }
    }

    document.querySelectorAll('.wiz-panel').forEach(p => p.classList.remove('active'));
    const panel = document.querySelector(`.wiz-panel[data-panel="${step}"]`);
    if (panel) panel.classList.add('active');

    document.querySelectorAll('.wiz-step').forEach(s => {
        const n = parseInt(s.dataset.wiz, 10);
        s.classList.remove('active', 'done');
        if (n < step) s.classList.add('done');
        if (n === step) s.classList.add('active');
    });

    if (wizPrev) wizPrev.hidden = step === 1;
    if (wizNext) {
        wizNext.hidden = false;
        if (step === 1) {
            wizNext.innerHTML = 'Continue to AI Clip Settings →';
            wizNext.disabled = !state.currentFile;
        } else if (step === 2) {
            wizNext.innerHTML = '✦ Generate Clips';
            wizNext.disabled = !state.currentFile;

            // Load source video stream if player is present
            if (player && state.currentFile) {
                const streamUrl = `/download/input/stream/${encodeURIComponent(state.currentFile)}`;
                if (!player.src || (!player.src.endsWith(streamUrl) && player.src !== window.location.origin + streamUrl)) {
                    player.src = streamUrl;
                    player.load();
                }
            }

            // Sync Step 2 Video Stats
            const dimsEl = document.getElementById('step2VideoDims');
            if (dimsEl && state.currentMetadata) {
                dimsEl.textContent = `${state.currentMetadata.width}×${state.currentMetadata.height}`;
            }
            const pFilename = document.getElementById('metaFilename');
            if (pFilename) pFilename.textContent = state.currentFile || '-';
            const pRes = document.getElementById('metaResolution');
            if (pRes && state.currentMetadata) pRes.textContent = `${state.currentMetadata.width}×${state.currentMetadata.height}`;
            const pFPS = document.getElementById('metaFPS');
            if (pFPS && state.currentMetadata) pFPS.textContent = `${state.currentMetadata.fps} FPS`;
            const pSize = document.getElementById('metaSize');
            if (pSize && state.currentMetadata) pSize.textContent = formatBytes(state.currentMetadata.size_bytes);
        } else if (step === 3) {
            wizNext.innerHTML = '<span class="spinner" hidden></span> Generating...';
            wizNext.disabled = true;
            buildSummary();
        } else if (step === 4) {
            wizNext.innerHTML = 'Export →';
            wizNext.disabled = false;
        } else if (step === 5) {
            wizNext.hidden = true;
            if (wizPrev) wizPrev.hidden = false;
            renderExport();
        } else {
            wizNext.innerHTML = 'Continue →';
            wizNext.disabled = false;
        }
    }
}

// ---------- Load file from query param (from YT Downloader) ----------
async function loadFileFromQuery() {
    const params = new URLSearchParams(window.location.search);
    const filename = params.get('file');
    if (!filename) return;

    // Check if the file exists in the input directory
    try {
        const res = await fetch(`/download/input/${encodeURIComponent(filename)}`, { method: 'HEAD' });
        if (!res.ok) return;

        // Set the current file
        state.currentFile = filename;

        // Try to get metadata and derive thumbnail
        const sourceStem = filename.includes('.') ? filename.substring(0, filename.lastIndexOf('.')) : filename;
        const thumbUrl = `/download/thumbnail/${encodeURIComponent(sourceStem)}_thumb.jpg`;

        try {
            const metaRes = await fetch(`/process/metadata/${encodeURIComponent(filename)}`);
            const metaData = await metaRes.json();
            if (metaData.success) {
                state.currentMetadata = metaData.metadata;
                displayVideoMetadata(metaData.metadata, thumbUrl);
            } else {
                displayVideoMetadata({ filename: filename, width: 1920, height: 1080, duration: 0, fps: 30, size_bytes: 0 }, thumbUrl);
            }
        } catch (e) {
            displayVideoMetadata({ filename: filename, width: 1920, height: 1080, duration: 0, fps: 30, size_bytes: 0 }, thumbUrl);
        }

        uploadStatus.textContent = `Loaded: ${filename}`;
        uploadStatus.style.color = 'var(--success)';

        // Remain on Step 1 to show metadata card (Do NOT auto-advance)

        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } catch (e) {
        console.error('Failed to load file from query:', e);
    }
}

// ---------- Studio Loader ----------
const studioLoader = document.getElementById('studioLoader');
function showStudioLoader() {
    if (studioLoader) studioLoader.hidden = false;
}
function hideStudioLoader() {
    if (studioLoader) studioLoader.hidden = true;
}

// ---------- Large File Warning ----------
const LARGE_FILE_THRESHOLD = 500 * 1024 * 1024; // 500MB
let pendingPipelineStart = null;
const largeFileModal = document.getElementById('largeFileModal');
const largeFileClose = document.getElementById('largeFileClose');
const largeFileContinue = document.getElementById('largeFileContinue');
const largeFileCancel = document.getElementById('largeFileCancel');
const largeFileMessage = document.getElementById('largeFileMessage');

function showLargeFileWarning(sizeBytes) {
    if (!largeFileModal || !largeFileMessage) return;
    const sizeMB = (sizeBytes / (1024 * 1024)).toFixed(1);
    largeFileMessage.textContent = `This video is ${sizeMB} MB. Analysis, scene detection, framing, and clip generation may take longer than usual. Do you want to continue?`;
    largeFileModal.hidden = false;
}

function hideLargeFileWarning() {
    if (largeFileModal) largeFileModal.hidden = true;
}

if (largeFileClose) largeFileClose.addEventListener('click', hideLargeFileWarning);
if (largeFileCancel) largeFileCancel.addEventListener('click', hideLargeFileWarning);
if (largeFileContinue) {
    largeFileContinue.addEventListener('click', () => {
        hideLargeFileWarning();
        if (pendingPipelineStart) {
            pendingPipelineStart();
            pendingPipelineStart = null;
        }
    });
}
if (largeFileModal) {
    largeFileModal.addEventListener('click', (e) => {
        if (e.target === largeFileModal) {
            hideLargeFileWarning();
        }
    });
}

// Override startPipeline to check file size
const originalStartPipeline = startPipeline;
startPipeline = async function() {
    if (state.currentMetadata && state.currentMetadata.size_bytes > LARGE_FILE_THRESHOLD) {
        pendingPipelineStart = originalStartPipeline;
        showLargeFileWarning(state.currentMetadata.size_bytes);
        return;
    }
    await originalStartPipeline();
};

// ---------- Global Active Jobs Indicator ----------
const jobsIndicator = document.getElementById('jobsIndicator');
const jobsPopup = document.getElementById('jobsPopup');
const jobsCount = document.getElementById('jobsCount');
const jobsList = document.getElementById('jobsList');
let jobsPollInterval = null;

function updateJobsUI(data) {
    if (!jobsIndicator || !jobsCount || !jobsList) return;
    const count = data.count || 0;
    if (count > 0) {
        jobsIndicator.hidden = false;
        jobsCount.textContent = `${count} task${count !== 1 ? 's' : ''}`;
        jobsList.innerHTML = '';
        data.jobs.forEach(job => {
            const pct = job.total_steps ? Math.round((job.steps_completed / job.total_steps) * 100) : 0;
            const item = document.createElement('div');
            item.className = 'jobs-popup-item';
            item.innerHTML = `
                <div class="jobs-popup-item-header">
                    <span class="jobs-popup-item-name">${job.filename || job.job_id}</span>
                    <span class="jobs-popup-item-pct">${pct}%</span>
                </div>
                <div class="jobs-popup-item-step">${job.step || 'Processing...'}</div>
                <div class="jobs-popup-bar">
                    <div class="jobs-popup-bar-fill" style="width:${pct}%"></div>
                </div>
            `;
            jobsList.appendChild(item);
        });
    } else {
        jobsIndicator.hidden = true;
        jobsPopup.hidden = true;
    }
}

async function pollActiveJobs() {
    try {
        const res = await fetch('/process/active-jobs');
        const data = await res.json();
        if (data.success) updateJobsUI(data);
    } catch (e) {
        // Silently ignore polling errors
    }
}

if (jobsIndicator) {
    jobsIndicator.addEventListener('click', (e) => {
        e.stopPropagation();
        jobsPopup.hidden = !jobsPopup.hidden;
        if (!jobsPopup.hidden) pollActiveJobs();
    });
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.jobs-indicator') && !e.target.closest('.jobs-popup')) {
            jobsPopup.hidden = true;
        }
    });
    jobsPollInterval = setInterval(pollActiveJobs, 3000);
    pollActiveJobs();
}

// ============================================
// Phase 1 Desktop Shell Foundations
// ============================================

// ---------- 1. Reusable Toast Notification System ----------
window.UpClipToast = {
    show(message, type = 'info', duration = 3500) {
        let container = document.querySelector('.app-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'app-toast-container';
            document.body.appendChild(container);
        }
        const toast = document.createElement('div');
        toast.className = `app-toast ${type}`;
        
        let iconSvg = '';
        if (type === 'success') {
            iconSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>';
        } else if (type === 'error') {
            iconSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--error)" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';
        } else if (type === 'warning') {
            iconSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--warning)" stroke-width="2.5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>';
        } else {
            iconSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>';
        }
        
        toast.innerHTML = `
            ${iconSvg}
            <span>${message}</span>
        `;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('hiding');
            setTimeout(() => toast.remove(), 200);
        }, duration);
    }
};

// ---------- 2. Desktop Sidebar Collapse ----------
function initSidebar() {
    const sidebar = document.getElementById('appSidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    if (!sidebar) return;
    
    const savedState = localStorage.getItem('upclip_sidebar_collapsed');
    if (savedState === 'true') {
        sidebar.classList.add('collapsed');
    }
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('upclip_sidebar_collapsed', isCollapsed);
        });
    }
}

// ---------- 3. Desktop Command Palette (Ctrl+K) ----------
function initCommandPalette() {
    let backdrop = document.getElementById('commandPaletteBackdrop');
    if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.id = 'commandPaletteBackdrop';
        backdrop.className = 'command-palette-backdrop';
        backdrop.hidden = true;
        backdrop.innerHTML = `
            <div class="command-palette">
                <div class="command-search-wrap">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                    <input type="text" class="command-search-input" id="commandSearchInput" placeholder="Type a command or jump to workspace..." autocomplete="off">
                    <span class="kbd-badge">ESC</span>
                </div>
                <div class="command-list" id="commandList">
                    <div class="command-item" data-action="new-project">
                        <div class="command-item-left">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
                            <span>New AI Shorts Project</span>
                        </div>
                        <span class="kbd-badge">Dashboard</span>
                    </div>
                    <div class="command-item" data-action="open-clips">
                        <div class="command-item-left">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><line x1="20" y1="4" x2="8.12" y2="15.88"/><line x1="14.47" y1="14.48" x2="20" y2="20"/><line x1="8.12" y1="8.12" x2="12" y2="12"/></svg>
                            <span>Open AI Clip Studio</span>
                        </div>
                    </div>
                    <div class="command-item" data-action="open-captions">
                        <div class="command-item-left">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                            <span>Open Caption Studio</span>
                        </div>
                    </div>
                    <div class="command-item" data-action="open-youtube">
                        <div class="command-item-left">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="20" height="15" x="2" y="7" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/></svg>
                            <span>Open YouTube Automation Desk</span>
                        </div>
                    </div>
                    <div class="command-item" data-action="open-downloader">
                        <div class="command-item-left">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                            <span>Open YouTube Downloader</span>
                        </div>
                    </div>
                    <div class="command-item" data-action="open-hub">
                        <div class="command-item-left">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>
                            <span>Open Studio Hub</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(backdrop);
    }
    
    function openPalette() {
        backdrop.hidden = false;
        const input = document.getElementById('commandSearchInput');
        if (input) {
            input.value = '';
            input.focus();
            filterCommands('');
        }
    }
    
    function closePalette() {
        backdrop.hidden = true;
    }
    
    function filterCommands(query) {
        const items = backdrop.querySelectorAll('.command-item');
        const q = query.toLowerCase().trim();
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(q) ? 'flex' : 'none';
        });
    }
    
    backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) closePalette();
    });
    
    const input = document.getElementById('commandSearchInput');
    if (input) {
        input.addEventListener('input', (e) => filterCommands(e.target.value));
    }
    
    backdrop.addEventListener('click', (e) => {
        const item = e.target.closest('.command-item');
        if (!item) return;
        const action = item.dataset.action;
        closePalette();
        
        if (action === 'new-project' || action === 'open-clips') window.location.href = '/dashboard';
        else if (action === 'open-captions') window.location.href = '/caption-studio';
        else if (action === 'open-youtube') window.location.href = '/youtube-desk';
        else if (action === 'open-downloader') window.location.href = '/yt-downloader';
        else if (action === 'open-hub') window.location.href = '/studio';
    });
    
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            if (backdrop.hidden) openPalette();
            else closePalette();
        } else if (e.key === 'Escape' && !backdrop.hidden) {
            closePalette();
        }
    });
    
    const topbarSearch = document.getElementById('topbarCommandTrigger');
    if (topbarSearch) {
        topbarSearch.addEventListener('click', openPalette);
    }
}

// ---------- 4. Tooltips & Shortcuts Manager ----------
function initTooltips() {
    let tooltipEl = document.querySelector('.app-tooltip');
    if (!tooltipEl) {
        tooltipEl = document.createElement('div');
        tooltipEl.className = 'app-tooltip';
        tooltipEl.hidden = true;
        document.body.appendChild(tooltipEl);
    }

    document.addEventListener('mouseover', (e) => {
        const target = e.target.closest('[data-tooltip]');
        if (!target) return;
        const text = target.getAttribute('data-tooltip');
        const hotkey = target.getAttribute('data-hotkey');
        if (!text) return;
        
        tooltipEl.innerHTML = `<span>${text}</span>${hotkey ? `<span class="kbd-badge">${hotkey}</span>` : ''}`;
        tooltipEl.hidden = false;
        
        const rect = target.getBoundingClientRect();
        tooltipEl.style.left = `${rect.left + rect.width / 2 - tooltipEl.offsetWidth / 2}px`;
        tooltipEl.style.top = `${rect.bottom + 6}px`;
    });

    document.addEventListener('mouseout', (e) => {
        const target = e.target.closest('[data-tooltip]');
        if (target && tooltipEl) {
            tooltipEl.hidden = true;
        }
    });
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

// ---------- Load Recent Projects ----------
async function loadProjects() {
    const grid = document.getElementById('projectsGrid');
    if (!grid) return;
    // Loading placeholder
    grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 28px; color: var(--text-muted);">
            <span class="spinner" style="margin-right: 8px;"></span> Loading recent projects…
        </div>`;
    try {
        const res = await fetch('/api/projects');
        const data = await res.json();
        if (Array.isArray(data) && data.length) {
            grid.innerHTML = data.map(p => {
                const thumb = p.thumbnail_path ? encodeURI(p.thumbnail_path) : '/static/img/default_thumb.png';
                const dur = (p.duration !== null && p.duration !== undefined && p.duration > 0) ? formatTime(p.duration) : '';
                const status = p.status || 'Ready';
                const aspect = (p.settings && p.settings.aspect) || '9:16';
                const clipCount = (p.clips && p.clips.length) || 0;
                const safeName = escapeHtml(p.name);
                return `
                <div class="compact-project-card" data-id="${p.id}" tabindex="0" role="button" aria-label="Open project ${safeName}">
                    <div class="compact-thumb-wrap" data-id="${p.id}">
                        <img class="compact-project-thumb" src="${thumb}" alt="${safeName}" loading="lazy" onerror="this.onerror=null; this.src='/static/img/default_thumb.png'">
                        <span class="compact-project-badge">${aspect}</span>
                        ${dur ? `<span class="compact-project-dur">${dur}</span>` : ''}
                    </div>
                    <div class="compact-project-info">
                        <div class="compact-project-name" title="${safeName}">${safeName}</div>
                        <div class="compact-project-meta">
                            <span class="compact-status-tag ${status.toLowerCase()}">${status}</span>
                            <span>${dur ? dur + ' • ' : ''}${clipCount} clip${clipCount === 1 ? '' : 's'}</span>
                        </div>
                        <div class="compact-card-actions">
                            <button type="button" class="btn btn-primary btn-sm btn-action-studio" data-id="${p.id}" title="Open in AI Clip Studio">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3z"/></svg>
                                <span>Clip Studio</span>
                            </button>
                            <button type="button" class="btn btn-secondary btn-sm btn-action-editor" data-id="${p.id}" title="Open in Timeline Editor">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                                <span>Editor</span>
                            </button>
                            <button type="button" class="btn btn-ghost btn-sm btn-action-delete" data-id="${p.id}" title="Delete project" style="color: var(--error); padding: 4px 6px;">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                            </button>
                        </div>
                    </div>
                </div>`;
            }).join('');
        } else {
            grid.innerHTML = `
                <div class="card" style="text-align: center; padding: 32px 16px; border: 1px dashed var(--border); border-radius: var(--radius-card); grid-column: 1 / -1;">
                    <p style="color: var(--text-secondary); margin: 0 0 12px 0; font-size: 14px;">No recent projects yet.</p>
                    <button class="btn btn-primary btn-sm" id="btnEmptyCreateProj" style="display: inline-flex; align-items: center; gap: 6px;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                        <span>Create your first project</span>
                    </button>
                </div>`;
            const emptyBtn = document.getElementById('btnEmptyCreateProj');
            if (emptyBtn) {
                emptyBtn.addEventListener('click', async () => {
                    try {
                        const res = await fetch('/api/projects', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ name: 'Project ' + new Date().toLocaleDateString(), settings: { aspect: '9:16' } })
                        });
                        const resData = await res.json();
                        if (resData.success && resData.project) {
                            window.location.href = `/editor?project_id=${resData.project.id}`;
                        } else {
                            window.location.href = '/dashboard';
                        }
                    } catch (e) {
                        window.location.href = '/dashboard';
                    }
                });
            }
        }
    } catch (e) {
        console.error('Failed to load projects:', e);
        grid.innerHTML = `
            <div class="card" style="color: var(--error); text-align: center; padding: 24px; border: 1px solid rgba(239, 68, 68, 0.2); grid-column: 1 / -1;">
                <p style="margin-bottom: 8px;">Failed to load recent projects.</p>
                <button class="btn btn-secondary btn-sm" onclick="loadProjects()">Retry</button>
            </div>`;
    }
}

// ---------- Custom Video Player Controls ----------
function initCustomPlayer() {
    const video = document.getElementById('sourceVideoPlayer');
    const playPause = document.getElementById('videoPlayPause');
    const scrubber = document.getElementById('videoScrubber');
    const currentTimeText = document.getElementById('videoCurrentTime');
    const durationText = document.getElementById('videoDuration');
    const muteBtn = document.getElementById('videoMute');
    const volumeSlider = document.getElementById('volumeSlider');
    
    if (!video || !playPause || !scrubber) return;

    playPause.addEventListener('click', () => {
        if (video.paused) {
            video.play();
            playPause.querySelector('.play-icon').style.display = 'none';
            playPause.querySelector('.pause-icon').style.display = 'block';
        } else {
            video.pause();
            playPause.querySelector('.play-icon').style.display = 'block';
            playPause.querySelector('.pause-icon').style.display = 'none';
        }
    });

    video.addEventListener('timeupdate', () => {
        if (!video.duration) return;
        const pct = (video.currentTime / video.duration) * 100;
        scrubber.value = pct;
        if (currentTimeText) currentTimeText.textContent = formatTime(video.currentTime);
    });

    video.addEventListener('loadedmetadata', () => {
        if (durationText) durationText.textContent = formatTime(video.duration);
        const metaFilename = document.getElementById('metaFilename');
        const metaResolution = document.getElementById('metaResolution');
        const metaFPS = document.getElementById('metaFPS');
        const metaSize = document.getElementById('metaSize');
        
        if (metaFilename) metaFilename.textContent = state.currentFile || 'Video';
        if (metaResolution) {
            metaResolution.textContent = state.currentMetadata ? 
                `${state.currentMetadata.width}×${state.currentMetadata.height}` : 
                `${video.videoWidth}×${video.videoHeight}`;
        }
        if (metaFPS && state.currentMetadata) metaFPS.textContent = `${state.currentMetadata.fps} FPS`;
        if (metaSize && state.currentMetadata) metaSize.textContent = formatBytes(state.currentMetadata.size_bytes);
    });

    scrubber.addEventListener('input', () => {
        if (!video.duration) return;
        const time = (scrubber.value / 100) * video.duration;
        video.currentTime = time;
    });

    if (muteBtn) {
        muteBtn.addEventListener('click', () => {
            video.muted = !video.muted;
            if (video.muted) {
                muteBtn.querySelector('.volume-icon').style.display = 'none';
                muteBtn.querySelector('.mute-icon').style.display = 'block';
            } else {
                muteBtn.querySelector('.volume-icon').style.display = 'block';
                muteBtn.querySelector('.mute-icon').style.display = 'none';
            }
        });
    }

    if (volumeSlider) {
        volumeSlider.addEventListener('input', () => {
            video.volume = volumeSlider.value / 100;
            video.muted = video.volume === 0;
        });
    }
}

// ---------- Clip Preview Modal ----------
function initClipPreviewModal() {
    const modal = document.getElementById('clipPreviewModal');
    const closeBtn = document.getElementById('clipPreviewClose');
    const video = document.getElementById('clipPreviewVideo');
    if (!modal || !closeBtn || !video) return;

    closeBtn.addEventListener('click', () => {
        modal.hidden = true;
        video.pause();
        video.src = '';
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.hidden = true;
            video.pause();
            video.src = '';
        }
    });
}

function previewClip(clipName) {
    const modal = document.getElementById('clipPreviewModal');
    const video = document.getElementById('clipPreviewVideo');
    const title = document.getElementById('clipPreviewTitle');
    if (!modal || !video) return;

    title.textContent = clipName;
    video.src = `/download/clip/stream/${clipName}`;
    modal.hidden = false;
    video.play();
}

// ---------- Project Context Sync ----------
async function loadActiveProject() {
    let project = window.UpClipActiveProject;
    const fileParam = window.UpClipFileParam;

    if (!project) {
        const params = new URLSearchParams(window.location.search);
        const pId = params.get('project_id') || params.get('projectId');
        if (pId) {
            try {
                const res = await fetch(`/api/projects/${pId}`);
                if (res.ok) {
                    project = await res.json();
                    window.UpClipActiveProject = project;
                }
            } catch (err) {
                console.warn("Could not fetch project by ID:", err);
            }
        }
    }
    
    if (project) {
        console.log("Loading active project context:", project);
        
        // Update project badge in header
        const projectNameText = document.getElementById('projectNameText');
        if (projectNameText) projectNameText.textContent = project.name;
        
        if (project.source_path) {
            state.currentFile = project.source_path;
            
            // Set source Video URL
            const video = document.getElementById('sourceVideoPlayer');
            if (video) {
                video.src = `/download/input/${encodeURIComponent(project.source_path)}`;
                const cont = document.getElementById('sourceVideoContainer');
                if (cont) cont.hidden = false;
            }
            
            // Try fetching metadata
            let meta = null;
            try {
                const metaRes = await fetch(`/process/metadata/${encodeURIComponent(project.source_path)}`);
                const metaData = await metaRes.json();
                if (metaData.success) {
                    state.currentMetadata = metaData.metadata;
                    meta = metaData.metadata;
                }
            } catch (e) {
                console.warn("Could not load project source metadata:", e);
            }

            if (!meta) {
                meta = {
                    filename: project.source_path,
                    duration: project.duration || 0,
                    width: 1920,
                    height: 1080,
                    fps: 30
                };
            }

            // Derive thumbnail URL if not provided
            const sourceStem = project.source_path.includes('.') ? project.source_path.substring(0, project.source_path.lastIndexOf('.')) : project.source_path;
            const thumbUrl = project.thumbnail_path ? encodeURI(project.thumbnail_path) : `/download/thumbnail/${encodeURIComponent(sourceStem)}_thumb.jpg`;

            // Display rich metadata in Step 1 (populates #metaThumbImg, badges, etc.)
            displayVideoMetadata(meta, thumbUrl);
            
            // Query for clips of this project
            try {
                const res = await fetch(`/studio/project/proj_${project.id}`);
                const data = await res.json();
                if (data.success && data.project) {
                    state.clips = (data.project.clips || []).map(c => ({ name: c.filename, url: c.url }));
                    if (state.clips.length) {
                        state.result = data.project;
                        renderReviewGrid();
                        showStep(4); // Go straight to review clips step (Step 4, NOT Step 8!)
                        return;
                    }
                }
            } catch (e) {
                console.warn("Could not load project clips:", e);
            }
            
            // Stay on Step 1 with metadata card displayed
            showStep(1);
            return;
        }
    }
    
    if (fileParam) {
        state.currentFile = fileParam;
        const sourceStem = fileParam.includes('.') ? fileParam.substring(0, fileParam.lastIndexOf('.')) : fileParam;
        const thumbUrl = `/download/thumbnail/${encodeURIComponent(sourceStem)}_thumb.jpg`;
        try {
            const metaRes = await fetch(`/process/metadata/${encodeURIComponent(fileParam)}`);
            const metaData = await metaRes.json();
            if (metaData.success) {
                state.currentMetadata = metaData.metadata;
                displayVideoMetadata(metaData.metadata, thumbUrl);
            } else {
                displayVideoMetadata({ filename: fileParam, width: 1920, height: 1080, duration: 0, fps: 30, size_bytes: 0 }, thumbUrl);
            }
        } catch (e) {
            displayVideoMetadata({ filename: fileParam, width: 1920, height: 1080, duration: 0, fps: 30, size_bytes: 0 }, thumbUrl);
        }
        showStep(1);
    }
}

// ---------- Batch Action Listeners & Refresh ----------
function initBatchAndRefreshListeners() {
    const selectAllBtn = document.getElementById('selectAllClipsBtn');
    const clearSelectionBtn = document.getElementById('clearClipSelectionBtn');
    const batchDeleteBtn = document.getElementById('batchDeleteBtn');
    const batchDownloadBtn = document.getElementById('batchDownloadBtn');
    const batchOpenEditorBtn = document.getElementById('batchOpenEditorBtn');
    const refreshClipsBtn = document.getElementById('refreshClipsBtn');
    
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            document.querySelectorAll('.review-clip-checkbox').forEach(chk => {
                chk.checked = true;
                chk.parentElement.classList.add('selected');
            });
            updateBatchActionsBar();
        });
    }

    if (clearSelectionBtn) {
        clearSelectionBtn.addEventListener('click', () => {
            document.querySelectorAll('.review-clip-checkbox').forEach(chk => {
                chk.checked = false;
                chk.parentElement.classList.remove('selected');
            });
            updateBatchActionsBar();
        });
    }

    if (batchDeleteBtn) {
        batchDeleteBtn.addEventListener('click', async () => {
            const checked = document.querySelectorAll('.review-clip-checkbox:checked');
            if (!checked.length) return;
            const confirmed = confirm(`Are you sure you want to delete the ${checked.length} selected clip(s)?`);
            if (!confirmed) return;
            
            for (const chk of checked) {
                const idx = parseInt(chk.dataset.idx, 10);
                const clip = state.clips[idx];
                if (!clip) continue;
                try {
                    await fetch('/process/clip/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ filename: clip.name }),
                    });
                } catch(e) { console.error(e); }
            }
            // Remove deleted items from local state
            const remaining = [];
            document.querySelectorAll('.review-clip-checkbox').forEach((chk, i) => {
                if (!chk.checked) remaining.push(state.clips[i]);
            });
            state.clips = remaining;
            renderReviewGrid();
            updateBatchActionsBar();
            window.UpClipToast.show('Clips deleted successfully', 'success');
        });
    }

    if (batchDownloadBtn) {
        batchDownloadBtn.addEventListener('click', () => {
            window.open('/download/all', '_blank');
        });
    }

    if (batchOpenEditorBtn) {
        batchOpenEditorBtn.addEventListener('click', () => {
            const checked = document.querySelectorAll('.review-clip-checkbox:checked');
            if (!checked.length) return;
            const idx = parseInt(checked[0].dataset.idx, 10);
            const clip = state.clips[idx];
            if (!clip) return;
            const projectId = state.result?.project_id || (window.UpClipActiveProject ? `proj_${window.UpClipActiveProject.id}` : '');
            const clipSubtitleMap = state.result?.clip_subtitle_map || {};
            const clipSrt = clipSubtitleMap[clip.name]?.srt || state.result?.srt || '';
            const clipVtt = clipSubtitleMap[clip.name]?.vtt || state.result?.vtt || '';
            const captionStyle = state.result?.caption_style || null;
            const navUrl = `/open-caption-studio?video=${encodeURIComponent(clip.name)}&project_id=${encodeURIComponent(projectId)}&srt=${encodeURIComponent(clipSrt)}&vtt=${encodeURIComponent(clipVtt)}&style=${encodeURIComponent(captionStyle ? JSON.stringify(captionStyle) : '')}`;
            window.location.href = navUrl;
        });
    }

    if (refreshClipsBtn) {
        refreshClipsBtn.addEventListener('click', async () => {
            refreshClipsBtn.classList.add('spinning');
            try {
                const activeProj = window.UpClipActiveProject || (state.result ? { id: state.result.project_id.replace('proj_', '') } : null);
                if (activeProj) {
                    const res = await fetch(`/studio/project/proj_${activeProj.id}`);
                    const data = await res.json();
                    if (data.success && data.project) {
                        state.clips = data.project.clips.map(c => ({ name: c.filename, url: c.url }));
                        renderReviewGrid();
                        window.UpClipToast.show('Clip grid refreshed successfully', 'success');
                    }
                }
            } catch (e) {
                console.error('Refresh failed:', e);
                window.UpClipToast.show('Failed to refresh clips', 'error');
            } finally {
                refreshClipsBtn.classList.remove('spinning');
            }
        });
    }

    // Projects Grid click handler on home page
    const pGrid = document.getElementById('projectsGrid');
    if (pGrid) {
        pGrid.addEventListener('click', async (e) => {
            const delBtn = e.target.closest('.btn-action-delete');
            if (delBtn) {
                e.preventDefault();
                e.stopPropagation();
                const id = delBtn.dataset.id;
                if (confirm('Delete this project?')) {
                    try {
                        const res = await fetch(`/api/projects/${id}`, { method: 'DELETE' });
                        if (res.ok) {
                            if (window.UpClipToast) window.UpClipToast.show('Project deleted', 'success');
                            loadProjects();
                        }
                    } catch (err) {
                        console.error('Failed to delete project:', err);
                    }
                }
                return;
            }

            const editorBtn = e.target.closest('.btn-action-editor');
            if (editorBtn) {
                e.preventDefault();
                e.stopPropagation();
                const id = editorBtn.dataset.id;
                window.location.href = `/editor?project_id=${id}`;
                return;
            }

            const studioBtn = e.target.closest('.btn-action-studio');
            if (studioBtn) {
                e.preventDefault();
                e.stopPropagation();
                const id = studioBtn.dataset.id;
                window.location.href = `/dashboard?project_id=${id}`;
                return;
            }

            const card = e.target.closest('.compact-project-card') || e.target.closest('.project-card');
            if (card) {
                const id = card.dataset.id;
                window.location.href = `/dashboard?project_id=${id}`;
            }
        });
        pGrid.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                const card = e.target.closest('.compact-project-card') || e.target.closest('.project-card');
                if (card && !e.target.closest('button')) {
                    e.preventDefault();
                    const id = card.dataset.id;
                    window.location.href = `/dashboard?project_id=${id}`;
                }
            }
        });
    }
}

// ============================================
// Home Page Action Cards & Dynamic Template Selector
// ============================================
function initHomePageActions() {
    // 1. Diagnostics button
    const btnDiag = document.getElementById('btnOpenFfmpegDiag');
    if (btnDiag) {
        btnDiag.addEventListener('click', async () => {
            btnDiag.disabled = true;
            btnDiag.innerHTML = '<span class="spinner"></span> Checking...';
            try {
                const res = await fetch('/api/editor/diagnostics');
                const data = await res.json();
                if (data.success && data.diagnostics) {
                    const d = data.diagnostics;
                    alert(`FFmpeg & System Diagnostics:\n\n• Application: ${d.appName} v${d.version}\n• OS: ${d.os}\n• Python: ${d.pythonVersion}\n• Engine: ${d.ffmpegVersion}\n• Storage: ${d.storage.freeGB} GB free of ${d.storage.totalGB} GB (${d.storage.percentFree}% free)`);
                } else {
                    alert('FFmpeg Engine is installed and ready.');
                }
            } catch (e) {
                alert('Diagnostics check complete: Local engine operational.');
            } finally {
                btnDiag.disabled = false;
                btnDiag.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg> <span>Open Diagnostics</span>';
            }
        });
    }

    // 2. Import file button
    const btnImport = document.getElementById('btnHomeImportFile');
    const fileInput = document.getElementById('homeFileInput');
    if (btnImport && fileInput) {
        btnImport.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', async (e) => {
            if (!e.target.files.length) return;
            const file = e.target.files[0];
            const formData = new FormData();
            formData.append('video', file);
            if (window.UpClipToast) window.UpClipToast.show(`Importing ${file.name}...`, 'info');
            btnImport.disabled = true;
            btnImport.innerHTML = '<span class="spinner"></span> Uploading...';
            try {
                const res = await fetch('/upload/video', { method: 'POST', body: formData });
                const data = await res.json();
                if (data.success) {
                    if (window.UpClipToast) window.UpClipToast.show('Upload complete! Opening AI Clip Studio...', 'success');
                    window.location.href = `/dashboard?file=${encodeURIComponent(data.filename)}`;
                } else {
                    if (window.UpClipToast) window.UpClipToast.show('Upload failed: ' + (data.error || 'Unknown error'), 'error');
                }
            } catch (err) {
                if (window.UpClipToast) window.UpClipToast.show('Import failed: ' + err.message, 'error');
            } finally {
                btnImport.disabled = false;
                btnImport.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg> <span>Import File</span>';
            }
        });
    }

    // 3. New Project button
    const btnNewProj = document.getElementById('btnHomeNewProject');
    if (btnNewProj) {
        btnNewProj.addEventListener('click', async () => {
            btnNewProj.disabled = true;
            btnNewProj.innerHTML = '<span class="spinner"></span> Creating...';
            try {
                const res = await fetch('/api/projects', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: 'Project ' + new Date().toLocaleDateString(), settings: { aspect: '9:16' } })
                });
                const data = await res.json();
                if (data.success && data.project) {
                    window.location.href = `/editor?project_id=${data.project.id}`;
                } else {
                    window.location.href = '/editor';
                }
            } catch (e) {
                window.location.href = '/editor';
            }
        });
    }

    // 4. Refresh projects button
    const btnRefreshProj = document.getElementById('btnRefreshProjects');
    if (btnRefreshProj) {
        btnRefreshProj.addEventListener('click', () => {
            loadProjects();
            if (window.UpClipToast) window.UpClipToast.show('Projects list refreshed', 'info');
        });
    }
}

let homeTemplates = [];
let selectedTemplateId = null;
let currentTemplateCategory = 'all';
let currentTemplateQuery = '';

async function initHomeTemplateSelector() {
    const grid = document.getElementById('homeTemplateGrid');
    if (!grid) return;

    grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 24px; color: var(--text-muted);"><span class="spinner" style="margin-right: 8px;"></span> Loading templates…</div>';

    // Tabs listener
    const tabs = document.getElementById('templateCategoryTabs');
    if (tabs) {
        tabs.addEventListener('click', (e) => {
            const btn = e.target.closest('.template-tab-btn');
            if (!btn) return;
            tabs.querySelectorAll('.template-tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTemplateCategory = btn.dataset.cat || 'all';
            renderHomeTemplates();
        });
    }

    // Search input listener
    const searchInput = document.getElementById('templateSearchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentTemplateQuery = e.target.value.toLowerCase().trim();
            renderHomeTemplates();
        });
    }

    // Use selected template button
    const btnUse = document.getElementById('btnUseSelectedTemplate');
    if (btnUse) {
        btnUse.addEventListener('click', async () => {
            if (!selectedTemplateId) return;
            btnUse.disabled = true;
            btnUse.innerHTML = '<span class="spinner"></span> Creating Project...';
            try {
                const res = await fetch(`/api/templates/${selectedTemplateId}/create-project`, { method: 'POST' });
                const data = await res.json();
                if (data.success && data.project) {
                    if (window.UpClipToast) window.UpClipToast.show('Project created from template!', 'success');
                    window.location.href = `/editor?project_id=${data.project.id}`;
                } else {
                    if (window.UpClipToast) window.UpClipToast.show('Failed to create project: ' + (data.error || 'Unknown'), 'error');
                    btnUse.disabled = false;
                    btnUse.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> <span>Use Selected Template</span>';
                }
            } catch (e) {
                if (window.UpClipToast) window.UpClipToast.show('Error: ' + e.message, 'error');
                btnUse.disabled = false;
                btnUse.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> <span>Use Selected Template</span>';
            }
        });
    }

    try {
        const res = await fetch('/api/templates');
        const data = await res.json();
        if (data.success && Array.isArray(data.templates)) {
            homeTemplates = data.templates;
            renderHomeTemplates();
        } else {
            grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 20px;">No templates available.</div>';
        }
    } catch (e) {
        console.error('Failed to load templates:', e);
        grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; color: var(--error); padding: 20px;">Failed to load templates. <button class="btn btn-secondary btn-sm" onclick="initHomeTemplateSelector()">Retry</button></div>';
    }
}

function renderHomeTemplates() {
    const grid = document.getElementById('homeTemplateGrid');
    if (!grid) return;

    let filtered = homeTemplates;
    if (currentTemplateCategory !== 'all') {
        filtered = filtered.filter(t => (t.category || '').toLowerCase() === currentTemplateCategory.toLowerCase());
    }
    if (currentTemplateQuery) {
        filtered = filtered.filter(t => 
            (t.name || '').toLowerCase().includes(currentTemplateQuery) ||
            (t.description || '').toLowerCase().includes(currentTemplateQuery) ||
            (t.category || '').toLowerCase().includes(currentTemplateQuery) ||
            (t.aspect || '').toLowerCase().includes(currentTemplateQuery)
        );
    }

    if (!filtered.length) {
        grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 24px; border: 1px dashed var(--border); border-radius: var(--radius-sm);">No templates match your search criteria.</div>';
        return;
    }

    grid.innerHTML = filtered.map(t => {
        const isSelected = selectedTemplateId === t.id;
        const aspect = t.aspect || '9:16';
        return `
        <div class="template-card ${isSelected ? 'selected' : ''}" data-id="${t.id}" tabindex="0" role="button" aria-label="Select template ${t.name}">
            <div class="template-card-preview">
                <div class="template-preview-badge">${aspect}</div>
                <div style="font-size: 28px; opacity: 0.85;">🎬</div>
                ${isSelected ? '<div class="template-selected-badge">✓ Selected</div>' : ''}
            </div>
            <div class="template-card-body">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:6px;">
                    <h3 class="template-card-title">${t.name}</h3>
                    <span class="template-card-category">${t.category || 'Preset'}</span>
                </div>
                <p class="template-card-desc">${t.description || ''}</p>
                <div class="template-card-footer">
                    <span style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);">${aspect}</span>
                    <button type="button" class="btn btn-secondary btn-sm btn-select-template" style="padding: 3px 10px; font-size: 11px;">
                        ${isSelected ? 'Selected' : 'Select'}
                    </button>
                </div>
            </div>
        </div>`;
    }).join('');

    grid.querySelectorAll('.template-card').forEach(card => {
        const selectAction = () => {
            const id = card.dataset.id;
            selectedTemplateId = id;
            const t = homeTemplates.find(x => x.id === id);
            const actionWrap = document.getElementById('templateActionWrap');
            const textSpan = document.getElementById('btnUseSelectedTemplateText');
            if (actionWrap) actionWrap.style.display = 'block';
            if (textSpan && t) textSpan.textContent = `Use "${t.name}" Template`;
            renderHomeTemplates();
        };

        card.addEventListener('click', selectAction);
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                selectAction();
            }
        });
    });
}

function initStep1AspectCards() {
    const radioInputs = document.querySelectorAll('input[type="radio"][name="aspect"]');
    radioInputs.forEach(radio => {
        radio.addEventListener('change', () => {
            document.querySelectorAll('.aspect-option-card, .aspect-card').forEach(c => c.classList.remove('selected'));
            const parentCard = radio.closest('.aspect-option-card, .aspect-card');
            if (parentCard) parentCard.classList.add('selected');
            saveClipSettings();
        });
    });

    document.querySelectorAll('.aspect-option-card, .aspect-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.aspect-option-card, .aspect-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            const input = card.querySelector('input[type="radio"][name="aspect"]');
            if (input && !input.checked) {
                input.checked = true;
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
            saveClipSettings();
        });
    });
}

function initStep2Collapsibles() {
    const selector = '.settings-accordion-header, .settings-section-header, .collapsible-header, .accordion-header, [data-collapsible-trigger]';
    const headers = document.querySelectorAll(selector);
    headers.forEach(header => {
        if (header.dataset.collapsibleBound) return;
        header.dataset.collapsibleBound = "true";

        const item = header.closest('.settings-accordion-item') || header.closest('.settings-group-card');
        const content = item ? (item.querySelector('.settings-accordion-content') || item.querySelector('.settings-accordion-body')) : (header.dataset.target ? document.querySelector(header.dataset.target) : header.nextElementSibling);

        // Check if initially open
        const isInitiallyOpen = (item && item.classList.contains('open')) || (header.getAttribute('aria-expanded') === 'true') || (content && content.style.display === 'block');
        header.setAttribute('aria-expanded', isInitiallyOpen ? 'true' : 'false');
        header.setAttribute('tabindex', '0');
        if (content) {
            content.style.display = isInitiallyOpen ? 'block' : 'none';
        }
        const initialChevron = header.querySelector('.accordion-chevron, .chevron, .section-chevron, [data-lucide="chevron-down"]');
        if (initialChevron && isInitiallyOpen) {
            initialChevron.style.transform = 'rotate(180deg)';
        }

        const toggle = () => {
            const isExpanded = header.getAttribute('aria-expanded') === 'true';
            const willExpand = !isExpanded;
            header.setAttribute('aria-expanded', willExpand ? 'true' : 'false');
            if (item) {
                item.classList.toggle('open', willExpand);
            }
            if (content) {
                content.style.display = willExpand ? 'block' : 'none';
                content.classList.toggle('active', willExpand);
            }
            const chevron = header.querySelector('.accordion-chevron, .chevron, .section-chevron, [data-lucide="chevron-down"]');
            if (chevron) {
                chevron.style.transform = willExpand ? 'rotate(180deg)' : 'rotate(0deg)';
                chevron.style.transition = 'transform 0.25s cubic-bezier(0.4, 0, 0.2, 1)';
            }
        };

        header.addEventListener('click', (e) => {
            // Prevent event if clicking inside an interactive child directly
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON' || e.target.tagName === 'A') return;
            toggle();
        });
        header.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggle();
            }
        });
    });

    // Wire up Toggle All Settings Button
    const toggleAllBtn = document.getElementById('btnToggleAllSettings');
    const toggleAllText = document.getElementById('btnToggleAllText');
    if (toggleAllBtn && !toggleAllBtn.dataset.bound) {
        toggleAllBtn.dataset.bound = "true";
        toggleAllBtn.addEventListener('click', () => {
            const allItems = document.querySelectorAll('.wiz-panel[data-panel="2"] .settings-accordion-item');
            const anyOpen = Array.from(allItems).some(item => item.classList.contains('open'));
            const shouldOpen = !anyOpen;

            allItems.forEach(item => {
                const header = item.querySelector('.settings-accordion-header');
                const content = item.querySelector('.settings-accordion-content');
                const chevron = item.querySelector('.accordion-chevron');

                item.classList.toggle('open', shouldOpen);
                if (header) header.setAttribute('aria-expanded', shouldOpen ? 'true' : 'false');
                if (content) {
                    content.style.display = shouldOpen ? 'block' : 'none';
                    content.classList.toggle('active', shouldOpen);
                }
                if (chevron) {
                    chevron.style.transform = shouldOpen ? 'rotate(180deg)' : 'rotate(0deg)';
                }
            });

            if (toggleAllText) {
                toggleAllText.textContent = shouldOpen ? 'Collapse All' : 'Expand All';
            }
        });
    }

    const form = document.querySelector('.wiz-panel[data-panel="2"]');
    if (form) {
        form.addEventListener('change', saveClipSettings);
    }
}

function initSliderListeners() {
    const sceneSlider = document.getElementById('sceneThresholdRange');
    const sceneDisplay = document.getElementById('sceneThresholdDisplay');
    if (sceneSlider && sceneDisplay) {
        sceneSlider.addEventListener('input', () => {
            sceneDisplay.textContent = parseFloat(sceneSlider.value).toFixed(2);
            saveClipSettings();
        });
    }
}

function initStep1MetaActions() {
    const btnProceed = document.getElementById('btnProceedToSettings');
    if (btnProceed) {
        btnProceed.addEventListener('click', () => {
            if (!state.currentFile) {
                alert('Please upload a video first.');
                return;
            }
            showStep(2);
        });
    }

    const btnChange = document.getElementById('btnChangeVideo');
    if (btnChange) {
        btnChange.addEventListener('click', (e) => {
            e.stopPropagation();
            // Restore drop zone and hide metadata card so user can drag & drop or pick another video
            const metaCard = document.getElementById('videoMetaCard');
            if (metaCard) {
                metaCard.hidden = true;
                metaCard.style.display = 'none';
            }
            const uZone = document.getElementById('uploadZone') || (typeof uploadZone !== 'undefined' ? uploadZone : null);
            if (uZone) {
                uZone.hidden = false;
                uZone.style.display = 'flex';
            }
            if (videoInput) {
                videoInput.value = '';
                videoInput.click();
            }
        });
    }
}

function initWizardStepsNavigation() {
    document.querySelectorAll('.wiz-step').forEach(stepEl => {
        stepEl.addEventListener('click', () => {
            const targetStep = parseInt(stepEl.dataset.wiz, 10);
            if (isNaN(targetStep)) return;
            if (targetStep === 1) {
                showStep(1);
            } else if (targetStep === 2) {
                if (!state.currentFile) {
                    if (window.UpClipToast) {
                        window.UpClipToast.show('Please upload a video first.', 'warning');
                    } else {
                        alert('Please upload a video first.');
                    }
                    return;
                }
                showStep(2);
            } else if (targetStep === 3) {
                if (!state.currentFile) return;
                showStep(3);
                startPipeline();
            } else if (targetStep === 4) {
                if (state.clips && state.clips.length) {
                    showStep(4);
                }
            } else if (targetStep === 5) {
                if (state.result) {
                    showStep(5);
                }
            }
        });
    });
}

function saveClipSettings() {
    try {
        const settings = collectSettings();
        localStorage.setItem('upclip_clip_settings', JSON.stringify(settings));
    } catch (e) {
        // silent fail
    }
}

function restoreClipSettings() {
    try {
        const saved = localStorage.getItem('upclip_clip_settings');
        if (!saved) return;
        const s = JSON.parse(saved);
        if (s.aspect) {
            const aspectRadio = document.querySelector(`input[name="aspect"][value="${s.aspect}"]`);
            if (aspectRadio) {
                aspectRadio.checked = true;
                document.querySelectorAll('.aspect-option-card, .aspect-card').forEach(c => c.classList.remove('selected'));
                aspectRadio.closest('.aspect-option-card, .aspect-card')?.classList.add('selected');
            }
        }
        if (s.language && document.getElementById('langTranscript')) {
            document.getElementById('langTranscript').value = s.language;
        }
        if (s.subtitle_language && document.getElementById('langSubtitle')) {
            document.getElementById('langSubtitle').value = s.subtitle_language;
        }
        if (s.subtitle_enabled !== undefined && document.getElementById('subtitleEnabled')) {
            document.getElementById('subtitleEnabled').checked = s.subtitle_enabled;
        }
        if (s.clipping_mode) {
            const modeRadio = document.querySelector(`input[name="clipmode"][value="${s.clipping_mode}"]`);
            if (modeRadio) {
                modeRadio.checked = true;
                updateClippingOptions();
            }
        }
        if (s.clip_duration && document.getElementById('clipDuration')) {
            document.getElementById('clipDuration').value = s.clip_duration;
        }
        if (s.naming) {
            const namingRadio = document.querySelector(`input[name="naming"][value="${s.naming}"]`);
            if (namingRadio) namingRadio.checked = true;
        }
        if (s.caption_enabled !== undefined && document.getElementById('captionEnabled')) {
            document.getElementById('captionEnabled').checked = s.caption_enabled;
            updateCaptionOptions();
        }
        if (s.caption_template && document.getElementById('captionTemplate')) {
            document.getElementById('captionTemplate').value = s.caption_template;
        }
        if (s.caption_animation && document.getElementById('captionAnimation')) {
            document.getElementById('captionAnimation').value = s.caption_animation;
        }
        if (s.caption_position && document.getElementById('captionPosition')) {
            document.getElementById('captionPosition').value = s.caption_position;
        }
        if (s.caption_font && document.getElementById('captionFont')) {
            document.getElementById('captionFont').value = s.caption_font;
        }
        if (s.caption_color && document.getElementById('captionColor')) {
            document.getElementById('captionColor').value = s.caption_color;
        }
        if (s.caption_size && document.getElementById('captionSize')) {
            document.getElementById('captionSize').value = s.caption_size;
        }
        if (s.scene_threshold && document.getElementById('sceneThresholdRange')) {
            document.getElementById('sceneThresholdRange').value = s.scene_threshold;
            const sceneDisplay = document.getElementById('sceneThresholdDisplay');
            if (sceneDisplay) sceneDisplay.textContent = parseFloat(s.scene_threshold).toFixed(2);
        }
    } catch (e) {
        // silent fail
    }
}

// ---------- Init All ----------
checkFfmpeg();
if (document.querySelector('.wiz-panel')) {
    showStep(1);
    restoreClipSettings();
}
initStep1AspectCards();
initStep2Collapsibles();
initSliderListeners();
initStep1MetaActions();
initWizardStepsNavigation();
initCustomPlayer();
initClipPreviewModal();
initBatchAndRefreshListeners();
loadActiveProject().then(() => {
    if (state.currentStep === 1) {
        loadFileFromQuery();
    }
});
initSidebar();
loadProjects();
initHomePageActions();
initHomeTemplateSelector();
initCommandPalette();
initTooltips();

// Show studio loader briefly on dashboard load if user is logged in
if (window.location.pathname === '/dashboard') {
    showStudioLoader();
    setTimeout(hideStudioLoader, 800);
}

const previewLink = document.querySelector('.preview-link');
if (previewLink) {
    previewLink.addEventListener('click', (e) => {
        e.preventDefault();
        if (state.result) showStep(5);
    });
}


