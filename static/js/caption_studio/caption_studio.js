/**
 * UpClip Studio — Caption Studio Engine (Step 3)
 * Features:
 * - Clean Initial State: No preset auto-selected on load; playback controls, timeline & caption overlay
 *   are strictly hidden until video is imported.
 * - Video Import: Local instant preview + background upload to /upload/video to retrieve server filename.
 * - Working Caption Import: Supports .srt, .vtt, .json via POST /api/caption-studio/import.
 * - AI Auto-Caption Modal: Supports Hinglish (transliteration: Hindi in English script e.g. "vah kutta hai"),
 *   Hindi (Devanagari), and English with Whisper AI integration.
 * - 12 High-Retention Creator Grade Presets: Hormozi, MrBeast, Ali Abdaal, Neon Cyberpunk, Vox Yellow, etc.
 * - Working Video Export Modal: Resolution, FPS, MP4 format, FFmpeg burned caption render & direct download.
 * - Full Undo & Redo System: Stack history with Ctrl+Z / Ctrl+Y shortcuts and topbar button states.
 * - Live Karaoke Caption Sync: Synchronized highlight on video timeupdate.
 */

(function () {
    'use strict';

    // =========================================================================
    // 1. STATE DEFINITION
    // =========================================================================
    const state = {
        videoLoaded: false,
        videoElement: null,
        serverFilename: '',
        projectId: '',
        captions: [],
        activeCategory: 'all',
        activePresetId: null, // Clean initial state: no preset selected until chosen
    };

    const activeStyle = {
        fontFamily: 'Montserrat',
        fontWeight: '900',
        fontSize: 38,
        letterSpacing: 0,
        lineHeight: 1.2,
        textColor: '#FFFFFF',
        activeWordColor: '#22C55E',
        textOpacity: 100,
        textCase: 'uppercase', // uppercase | capitalize | normal
        textAlign: 'center',  // left | center | right
        posYPercent: 80,
        posXPercent: 50,
        scale: 100,
        strokeEnabled: true,
        strokeColor: '#000000',
        strokeWidth: 3.5,
        shadowEnabled: true,
        shadowColor: '#000000',
        shadowBlur: 8,
        shadowY: 3,
        glowEnabled: false,
        glowColor: '#10B981',
        glowIntensity: 12,
        bgMode: 'none', // none | solid | semi | highlight
        bgColor: '#000000',
        bgOpacity: 0,
        bgPadding: 8,
        bgRadius: 6,
        animation: 'pop',
    };

    // =========================================================================
    // 2. UNDO & REDO STACK
    // =========================================================================
    const undoStack = [];
    const redoStack = [];
    const MAX_HISTORY = 40;
    let isPerformingUndoRedo = false;

    function pushHistory() {
        if (isPerformingUndoRedo) return;
        undoStack.push({
            style: JSON.parse(JSON.stringify(activeStyle)),
            captions: JSON.parse(JSON.stringify(state.captions || [])),
            presetId: state.activePresetId,
        });
        if (undoStack.length > MAX_HISTORY) {
            undoStack.shift();
        }
        redoStack.length = 0; // Clear redo on new action
        updateUndoRedoButtonUI();
    }

    function undo() {
        if (undoStack.length === 0) return;
        isPerformingUndoRedo = true;
        redoStack.push({
            style: JSON.parse(JSON.stringify(activeStyle)),
            captions: JSON.parse(JSON.stringify(state.captions || [])),
            presetId: state.activePresetId,
        });

        const prevState = undoStack.pop();
        Object.assign(activeStyle, prevState.style);
        state.captions = prevState.captions;
        state.activePresetId = prevState.presetId;

        applyStyleToControls(activeStyle);
        updatePresetCardActiveUI();
        updateLiveCaptionOverlay();
        updateUndoRedoButtonUI();
        isPerformingUndoRedo = false;
        showToast('Undone', 'info', 1000);
    }

    function redo() {
        if (redoStack.length === 0) return;
        isPerformingUndoRedo = true;
        undoStack.push({
            style: JSON.parse(JSON.stringify(activeStyle)),
            captions: JSON.parse(JSON.stringify(state.captions || [])),
            presetId: state.activePresetId,
        });

        const nextState = redoStack.pop();
        Object.assign(activeStyle, nextState.style);
        state.captions = nextState.captions;
        state.activePresetId = nextState.presetId;

        applyStyleToControls(activeStyle);
        updatePresetCardActiveUI();
        updateLiveCaptionOverlay();
        updateUndoRedoButtonUI();
        isPerformingUndoRedo = false;
        showToast('Redone', 'info', 1000);
    }

    function updateUndoRedoButtonUI() {
        if (el.undoBtn) {
            if (undoStack.length > 0) {
                el.undoBtn.classList.add('can-undo');
                el.undoBtn.removeAttribute('disabled');
            } else {
                el.undoBtn.classList.remove('can-undo');
                el.undoBtn.setAttribute('disabled', 'true');
            }
        }
        if (el.redoBtn) {
            if (redoStack.length > 0) {
                el.redoBtn.classList.add('can-redo');
                el.redoBtn.removeAttribute('disabled');
            } else {
                el.redoBtn.classList.remove('can-redo');
                el.redoBtn.setAttribute('disabled', 'true');
            }
        }
    }

    // =========================================================================
    // 3. 12 ULTRA HIGH-QUALITY DESIGNER PRESETS (Creator Grade)
    // =========================================================================
    const PRESETS = [
        {
            id: 'action_hormozi',
            name: 'Hormozi Viral',
            category: 'viral',
            platform: 'Viral / Reels',
            tagClass: 'tag-viral',
            previewWord1: 'VIRAL',
            previewWord2: 'HOOK',
            style: {
                fontFamily: 'Montserrat',
                fontWeight: '900',
                fontSize: 38,
                textColor: '#FFFFFF',
                activeWordColor: '#22C55E',
                textCase: 'uppercase',
                strokeEnabled: true,
                strokeColor: '#000000',
                strokeWidth: 3.5,
                shadowEnabled: true,
                shadowColor: '#000000',
                shadowBlur: 8,
                shadowY: 3,
                glowEnabled: false,
                bgMode: 'none',
                animation: 'pop',
            }
        },
        {
            id: 'mrbeast_impact',
            name: 'MrBeast Punch',
            category: 'youtube',
            platform: 'YouTube Shorts',
            tagClass: 'tag-youtube',
            previewWord1: 'IMPACT',
            previewWord2: 'PUNCH',
            style: {
                fontFamily: 'Anton',
                fontWeight: '900',
                fontSize: 42,
                textColor: '#FFFFFF',
                activeWordColor: '#FACC15',
                textCase: 'uppercase',
                strokeEnabled: true,
                strokeColor: '#000000',
                strokeWidth: 4,
                shadowEnabled: true,
                shadowColor: '#000000',
                shadowBlur: 10,
                shadowY: 4,
                glowEnabled: false,
                bgMode: 'none',
                animation: 'pop',
            }
        },
        {
            id: 'ali_abdaal_clean',
            name: 'Ali Abdaal Clean',
            category: 'instagram',
            platform: 'Instagram / Reels',
            tagClass: 'tag-instagram',
            previewWord1: 'CLEAN',
            previewWord2: 'FOCUS',
            style: {
                fontFamily: 'Inter',
                fontWeight: '700',
                fontSize: 32,
                textColor: '#F8FAFC',
                activeWordColor: '#14B8A6',
                textCase: 'normal',
                strokeEnabled: false,
                strokeWidth: 0,
                shadowEnabled: true,
                shadowColor: '#000000',
                shadowBlur: 4,
                shadowY: 2,
                bgMode: 'semi',
                bgColor: '#0F172A',
                bgOpacity: 65,
                bgPadding: 10,
                bgRadius: 8,
                animation: 'fade_in',
            }
        },
        {
            id: 'neon_cyberpunk',
            name: 'Neon Cyberpunk',
            category: 'tiktok',
            platform: 'TikTok',
            tagClass: 'tag-tiktok',
            previewWord1: 'NEON',
            previewWord2: 'PULSE',
            style: {
                fontFamily: 'Bebas Neue',
                fontWeight: '800',
                fontSize: 44,
                textColor: '#00FFCC',
                activeWordColor: '#FF007F',
                textCase: 'uppercase',
                strokeEnabled: true,
                strokeColor: '#000000',
                strokeWidth: 2,
                shadowEnabled: false,
                glowEnabled: true,
                glowColor: '#00FFCC',
                glowIntensity: 18,
                bgMode: 'none',
                animation: 'pop',
            }
        },
        {
            id: 'vox_yellow_pop',
            name: 'Vox Canary',
            category: 'youtube',
            platform: 'YouTube Shorts',
            tagClass: 'tag-youtube',
            previewWord1: 'EXPLAINER',
            previewWord2: 'FACT',
            style: {
                fontFamily: 'DM Sans',
                fontWeight: '800',
                fontSize: 36,
                textColor: '#FFFFFF',
                activeWordColor: '#FDE047',
                textCase: 'uppercase',
                strokeEnabled: true,
                strokeColor: '#18181B',
                strokeWidth: 2.5,
                shadowEnabled: true,
                shadowColor: '#000000',
                shadowBlur: 6,
                shadowY: 2,
                bgMode: 'semi',
                bgColor: '#09090B',
                bgOpacity: 80,
                bgPadding: 8,
                bgRadius: 6,
                animation: 'pop',
            }
        },
        {
            id: 'tiktok_bubble_pop',
            name: 'TikTok Candy',
            category: 'tiktok',
            platform: 'TikTok',
            tagClass: 'tag-tiktok',
            previewWord1: 'BUBBLE',
            previewWord2: 'SWEET',
            style: {
                fontFamily: 'Poppins',
                fontWeight: '900',
                fontSize: 38,
                textColor: '#FFFFFF',
                activeWordColor: '#EC4899',
                textCase: 'uppercase',
                strokeEnabled: true,
                strokeColor: '#581C87',
                strokeWidth: 3,
                shadowEnabled: true,
                shadowColor: '#000000',
                shadowBlur: 8,
                shadowY: 3,
                bgMode: 'none',
                animation: 'pop',
            }
        },
        {
            id: 'goggins_fire',
            name: 'Goggins Fire',
            category: 'viral',
            platform: 'Viral Reel',
            tagClass: 'tag-viral',
            previewWord1: 'STAY',
            previewWord2: 'HARD',
            style: {
                fontFamily: 'Oswald',
                fontWeight: '700',
                fontSize: 42,
                textColor: '#FFFFFF',
                activeWordColor: '#F97316',
                textCase: 'uppercase',
                strokeEnabled: true,
                strokeColor: '#7C2D12',
                strokeWidth: 3,
                shadowEnabled: true,
                shadowColor: '#000000',
                shadowBlur: 10,
                shadowY: 3,
                glowEnabled: true,
                glowColor: '#EA580C',
                glowIntensity: 12,
                bgMode: 'none',
                animation: 'pop',
            }
        },
        {
            id: 'retro_terminal',
            name: 'Matrix Terminal',
            category: 'viral',
            platform: 'Tech Reel',
            tagClass: 'tag-viral',
            previewWord1: 'DEV',
            previewWord2: 'MATRIX',
            style: {
                fontFamily: 'Fira Code',
                fontWeight: '700',
                fontSize: 30,
                textColor: '#E2E8F0',
                activeWordColor: '#10B981',
                textCase: 'normal',
                strokeEnabled: false,
                strokeWidth: 0,
                shadowEnabled: true,
                shadowColor: '#000000',
                shadowBlur: 4,
                shadowY: 1,
                bgMode: 'solid',
                bgColor: '#0B0F19',
                bgOpacity: 90,
                bgPadding: 8,
                bgRadius: 6,
                animation: 'fade_in',
            }
        },
        {
            id: 'luxury_gold',
            name: 'Luxury Champagne',
            category: 'instagram',
            platform: 'Aesthetic',
            tagClass: 'tag-instagram',
            previewWord1: 'ELITE',
            previewWord2: 'LUXURY',
            style: {
                fontFamily: 'Plus Jakarta Sans',
                fontWeight: '800',
                fontSize: 34,
                textColor: '#F8FAFC',
                activeWordColor: '#F59E0B',
                textCase: 'uppercase',
                letterSpacing: 1,
                strokeEnabled: true,
                strokeColor: '#451A03',
                strokeWidth: 2,
                shadowEnabled: true,
                shadowColor: '#000000',
                shadowBlur: 8,
                shadowY: 2,
                bgMode: 'semi',
                bgColor: '#18181B',
                bgOpacity: 75,
                bgPadding: 8,
                bgRadius: 8,
                animation: 'pop',
            }
        },
        {
            id: 'sunset_glow',
            name: 'Sunset Glow',
            category: 'tiktok',
            platform: 'Shorts / TikTok',
            tagClass: 'tag-tiktok',
            previewWord1: 'WARM',
            previewWord2: 'VIBES',
            style: {
                fontFamily: 'Outfit',
                fontWeight: '800',
                fontSize: 38,
                textColor: '#FEF08A',
                activeWordColor: '#FB7185',
                textCase: 'uppercase',
                strokeEnabled: true,
                strokeColor: '#4C0519',
                strokeWidth: 2.5,
                shadowEnabled: true,
                shadowColor: '#000000',
                shadowBlur: 8,
                shadowY: 2,
                glowEnabled: true,
                glowColor: '#FB7185',
                glowIntensity: 10,
                bgMode: 'none',
                animation: 'pop',
            }
        },
        {
            id: 'glitch_gamer',
            name: 'Glitch Lime',
            category: 'youtube',
            platform: 'Gaming Shorts',
            tagClass: 'tag-youtube',
            previewWord1: 'LEVEL',
            previewWord2: 'UP',
            style: {
                fontFamily: 'Anton',
                fontWeight: '900',
                fontSize: 40,
                textColor: '#FFFFFF',
                activeWordColor: '#A3E635',
                textCase: 'uppercase',
                strokeEnabled: true,
                strokeColor: '#000000',
                strokeWidth: 3.5,
                shadowEnabled: true,
                shadowColor: '#000000',
                shadowBlur: 10,
                shadowY: 3,
                glowEnabled: true,
                glowColor: '#84CC16',
                glowIntensity: 12,
                bgMode: 'none',
                animation: 'pop',
            }
        },
        {
            id: 'minimalist_mono',
            name: 'Monochrome Modern',
            category: 'all',
            platform: 'All Platforms',
            tagClass: 'tag-viral',
            previewWord1: 'PURE',
            previewWord2: 'FOCUS',
            style: {
                fontFamily: 'Inter',
                fontWeight: '800',
                fontSize: 34,
                textColor: '#FFFFFF',
                activeWordColor: '#94A3B8',
                textCase: 'uppercase',
                strokeEnabled: false,
                strokeWidth: 0,
                shadowEnabled: true,
                shadowColor: '#000000',
                shadowBlur: 12,
                shadowY: 3,
                bgMode: 'none',
                animation: 'fade_in',
            }
        },
    ];

    // DOM Elements Cache
    let el = {};

    // =========================================================================
    // 4. INITIALIZATION
    // =========================================================================
    document.addEventListener('DOMContentLoaded', () => {
        cacheDomElements();
        initSidebar();
        initTopBarActions();
        initVideoDropZone();
        initBottomTransportControls();
        initPresetsColumn();
        initSettingsAccordions();
        initSettingsFormSync();
        initCaptionImport();
        initGenerateCaptionsModal();
        initCustomPresetsSystem();
        initExportModal();
        initUndoRedo();
        initPreloadData();

        // Enforce clean initial state:
        // Do NOT select any preset card by default.
        applyStyleToControls(activeStyle);
        updatePresetCardActiveUI();

        // Ensure caption overlay and transport remain hidden until video is loaded
        if (!state.videoLoaded) {
            if (el.captionOverlayContainer) el.captionOverlayContainer.style.display = 'none';
            if (el.videoBottomTransport) el.videoBottomTransport.style.display = 'none';
        }

        if (window.lucide) {
            window.lucide.createIcons();
        }
    });

    function cacheDomElements() {
        el = {
            appSidebar: document.getElementById('appSidebar'),
            sidebarToggle: document.getElementById('sidebarToggle'),
            undoBtn: document.getElementById('undoBtn'),
            redoBtn: document.getElementById('redoBtn'),
            importVideoTopBtn: document.getElementById('importVideoTopBtn'),
            importCaptionsTopBtn: document.getElementById('importCaptionsTopBtn'),
            generateCaptionsTopBtn: document.getElementById('generateCaptionsTopBtn'),
            exportVideoTopBtn: document.getElementById('exportVideoTopBtn'),
            videoFileInput: document.getElementById('videoFileInput'),
            captionFileInput: document.getElementById('captionFileInput'),
            videoDropZone: document.getElementById('videoDropZone'),
            captionVideo: document.getElementById('captionVideo'),
            mobilePhoneFrame: document.getElementById('mobilePhoneFrame'),
            captionOverlayContainer: document.getElementById('captionOverlayContainer'),
            captionDragBox: document.getElementById('captionDragBox'),
            videoBottomTransport: document.getElementById('videoBottomTransport'),
            videoTimelineWrap: document.getElementById('videoTimelineWrap'),
            videoProgressBar: document.getElementById('videoProgressBar'),
            videoProgressFill: document.getElementById('videoProgressFill'),
            videoProgressThumb: document.getElementById('videoProgressThumb'),
            currentTimeDisplay: document.getElementById('currentTimeDisplay'),
            durationTimeDisplay: document.getElementById('durationTimeDisplay'),
            btnSeekLeft: document.getElementById('btnSeekLeft'),
            btnPlayPause: document.getElementById('btnPlayPause'),
            btnSeekRight: document.getElementById('btnSeekRight'),
            btnToggleMute: document.getElementById('btnToggleMute'),
            playPauseIcon: document.getElementById('playPauseIcon'),
            muteIcon: document.getElementById('muteIcon'),
            presetFilterPills: document.getElementById('presetFilterPills'),
            presetsGrid: document.getElementById('presetsGrid'),
            savePresetBtn: document.getElementById('savePresetBtn'),
            myPresetsBtn: document.getElementById('myPresetsBtn'),
            resetStyleBtn: document.getElementById('resetStyleBtn'),
            captionContextData: document.getElementById('captionContextData'),
            toastContainer: document.getElementById('toastContainer'),

            // Modals
            generateCaptionsModal: document.getElementById('generateCaptionsModal'),
            generateModalCloseBtn: document.getElementById('generateModalCloseBtn'),
            genLanguageSelect: document.getElementById('genLanguageSelect'),
            genStyleSelect: document.getElementById('genStyleSelect'),
            genModelSelect: document.getElementById('genModelSelect'),
            genProgressPanel: document.getElementById('genProgressPanel'),
            genProgressStatus: document.getElementById('genProgressStatus'),
            genReadyPanel: document.getElementById('genReadyPanel'),
            genReadyCountText: document.getElementById('genReadyCountText'),
            genPreviewBox: document.getElementById('genPreviewBox'),
            genCancelBtn: document.getElementById('genCancelBtn'),
            genStartBtn: document.getElementById('genStartBtn'),
            genApplyBtn: document.getElementById('genApplyBtn'),

            savePresetModal: document.getElementById('savePresetModal'),
            savePresetCloseBtn: document.getElementById('savePresetCloseBtn'),
            presetNameInput: document.getElementById('presetNameInput'),
            presetSaveSummary: document.getElementById('presetSaveSummary'),
            savePresetCancelBtn: document.getElementById('savePresetCancelBtn'),
            savePresetConfirmBtn: document.getElementById('savePresetConfirmBtn'),

            myPresetsModal: document.getElementById('myPresetsModal'),
            myPresetsCloseBtn: document.getElementById('myPresetsCloseBtn'),
            myPresetsList: document.getElementById('myPresetsList'),
            myPresetsDismissBtn: document.getElementById('myPresetsDismissBtn'),

            exportVideoModal: document.getElementById('exportVideoModal'),
            exportModalCloseBtn: document.getElementById('exportModalCloseBtn'),
            exportResolutionSelect: document.getElementById('exportResolutionSelect'),
            exportFpsSelect: document.getElementById('exportFpsSelect'),
            exportFormatSelect: document.getElementById('exportFormatSelect'),
            exportProgressPanel: document.getElementById('exportProgressPanel'),
            exportProgressSpinner: document.getElementById('exportProgressSpinner'),
            exportStatusText: document.getElementById('exportStatusText'),
            exportSrtOnlyBtn: document.getElementById('exportSrtOnlyBtn'),
            exportVttOnlyBtn: document.getElementById('exportVttOnlyBtn'),
            exportJsonOnlyBtn: document.getElementById('exportJsonOnlyBtn'),
            exportCancelBtn: document.getElementById('exportCancelBtn'),
            exportStartRenderBtn: document.getElementById('exportStartRenderBtn'),
            exportDownloadLinkBtn: document.getElementById('exportDownloadLinkBtn'),

            // Settings Form Inputs
            fontFamilySelect: document.getElementById('fontFamilySelect'),
            fontWeightSelect: document.getElementById('fontWeightSelect'),
            fontSizeRange: document.getElementById('fontSizeRange'),
            fontSizeDisplay: document.getElementById('fontSizeDisplay'),
            fontSizeDecBtn: document.getElementById('fontSizeDecBtn'),
            fontSizeIncBtn: document.getElementById('fontSizeIncBtn'),
            fontMetaBadge: document.getElementById('fontMetaBadge'),
            letterSpacingRange: document.getElementById('letterSpacingRange'),
            letterSpacingDisplay: document.getElementById('letterSpacingDisplay'),
            lineHeightRange: document.getElementById('lineHeightRange'),
            lineHeightDisplay: document.getElementById('lineHeightDisplay'),
            posTopBtn: document.getElementById('posTopBtn'),
            posMiddleBtn: document.getElementById('posMiddleBtn'),
            posBottomBtn: document.getElementById('posBottomBtn'),
            alignLeftBtn: document.getElementById('alignLeftBtn'),
            alignCenterBtn: document.getElementById('alignCenterBtn'),
            alignRightBtn: document.getElementById('alignRightBtn'),
            posYPercentRange: document.getElementById('posYPercentRange'),
            posYPercentDisplay: document.getElementById('posYPercentDisplay'),
            posXPercentRange: document.getElementById('posXPercentRange'),
            posXPercentDisplay: document.getElementById('posXPercentDisplay'),
            captionScaleSlider: document.getElementById('captionScaleSlider'),
            captionScaleDisplay: document.getElementById('captionScaleDisplay'),
            textColorPicker: document.getElementById('textColorPicker'),
            textColorHex: document.getElementById('textColorHex'),
            activeWordColorPicker: document.getElementById('activeWordColorPicker'),
            activeWordColorHex: document.getElementById('activeWordColorHex'),
            textOpacityRange: document.getElementById('textOpacityRange'),
            textOpacityDisplay: document.getElementById('textOpacityDisplay'),
            strokeColorPicker: document.getElementById('strokeColorPicker'),
            strokeColorHex: document.getElementById('strokeColorHex'),
            strokeWidthRange: document.getElementById('strokeWidthRange'),
            strokeWidthDisplay: document.getElementById('strokeWidthDisplay'),
            shadowToggle: document.getElementById('shadowToggle'),
            shadowColorPicker: document.getElementById('shadowColorPicker'),
            shadowBlurRange: document.getElementById('shadowBlurRange'),
            shadowBlurDisplay: document.getElementById('shadowBlurDisplay'),
            shadowYRange: document.getElementById('shadowYRange'),
            shadowYDisplay: document.getElementById('shadowYDisplay'),
            glowToggle: document.getElementById('glowToggle'),
            glowColorPicker: document.getElementById('glowColorPicker'),
            glowIntensityRange: document.getElementById('glowIntensityRange'),
            glowIntensityDisplay: document.getElementById('glowIntensityDisplay'),
            bgModeSelect: document.getElementById('bgModeSelect'),
            bgColorPicker: document.getElementById('bgColorPicker'),
            bgOpacityRange: document.getElementById('bgOpacityRange'),
            bgOpacityDisplay: document.getElementById('bgOpacityDisplay'),
            bgPaddingRange: document.getElementById('bgPaddingRange'),
            bgPaddingDisplay: document.getElementById('bgPaddingDisplay'),
            bgRadiusRange: document.getElementById('bgRadiusRange'),
            bgRadiusDisplay: document.getElementById('bgRadiusDisplay'),
            animationTypeSelect: document.getElementById('animationTypeSelect'),
            caseUpperBtn: document.getElementById('caseUpperBtn'),
            caseTitleBtn: document.getElementById('caseTitleBtn'),
            caseNormalBtn: document.getElementById('caseNormalBtn'),
        };
    }

    // =========================================================================
    // 5. SIDEBAR COLLAPSE / EXPAND
    // =========================================================================
    function initSidebar() {
        if (!el.appSidebar || !el.sidebarToggle) return;

        const savedState = localStorage.getItem('upclip_sidebar_collapsed');
        if (savedState === 'true') {
            el.appSidebar.classList.add('collapsed');
        }

        el.sidebarToggle.addEventListener('click', () => {
            el.appSidebar.classList.toggle('collapsed');
            const isCollapsed = el.appSidebar.classList.contains('collapsed');
            localStorage.setItem('upclip_sidebar_collapsed', isCollapsed);
        });
    }

    // =========================================================================
    // 6. TOPBAR ACTIONS & UNDO / REDO HOOKS
    // =========================================================================
    function initTopBarActions() {
        if (el.importVideoTopBtn && el.videoFileInput) {
            el.importVideoTopBtn.addEventListener('click', () => el.videoFileInput.click());
        }

        if (el.importCaptionsTopBtn && el.captionFileInput) {
            el.importCaptionsTopBtn.addEventListener('click', () => {
                if (!state.videoLoaded) {
                    showToast('Please import a video first.', 'warning');
                    return;
                }
                el.captionFileInput.click();
            });
        }

        if (el.generateCaptionsTopBtn) {
            el.generateCaptionsTopBtn.addEventListener('click', () => {
                if (!state.videoLoaded) {
                    showToast('Please import a video first.', 'warning');
                    return;
                }
                openGenerateModal();
            });
        }

        if (el.exportVideoTopBtn) {
            el.exportVideoTopBtn.addEventListener('click', () => {
                if (!state.videoLoaded) {
                    showToast('Please import a video first.', 'warning');
                    return;
                }
                openExportModal();
            });
        }
    }

    function initUndoRedo() {
        if (el.undoBtn) {
            el.undoBtn.addEventListener('click', undo);
        }
        if (el.redoBtn) {
            el.redoBtn.addEventListener('click', redo);
        }

        // Global Keyboard Shortcuts (Ctrl+Z / Ctrl+Y / Cmd+Z / Cmd+Shift+Z)
        window.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
                if (e.shiftKey) {
                    e.preventDefault();
                    redo();
                } else {
                    e.preventDefault();
                    undo();
                }
            } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') {
                e.preventDefault();
                redo();
            }
        });

        updateUndoRedoButtonUI();
    }

    // =========================================================================
    // 7. VIDEO IMPORT & DRAG & DROP
    // =========================================================================
    function initVideoDropZone() {
        const dropZone = el.videoDropZone;
        const fileInput = el.videoFileInput;
        if (!dropZone || !fileInput) return;

        dropZone.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                loadVideoFile(e.target.files[0]);
            }
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('drag-active');
            });
        });

        ['dragleave', 'dragend'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('drag-active');
            });
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('drag-active');

            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                const file = e.dataTransfer.files[0];
                if (file.type.startsWith('video/') || /\.(mp4|mov|webm|m4v|mkv)$/i.test(file.name)) {
                    loadVideoFile(file);
                } else {
                    showToast('Please drop a valid video file (.mp4, .mov, .webm)', 'warning');
                }
            }
        });
    }

    function loadVideoFile(file) {
        const objectUrl = URL.createObjectURL(file);
        loadVideoSource(objectUrl, file.name);

        // Upload video file to server in background so Whisper & FFmpeg export have it on disk
        const formData = new FormData();
        formData.append('video', file);

        showToast('Processing video...', 'info', 2000);
        fetch('/upload/video', {
            method: 'POST',
            body: formData,
        })
        .then(r => r.json())
        .then(res => {
            if (res.success) {
                state.serverFilename = res.filename;
                state.projectId = res.project_id || '';
                showToast(`Video ready for AI captioning: ${res.filename}`, 'success', 2500);
            } else {
                console.warn('Upload server warning:', res.error);
            }
        })
        .catch(err => {
            console.warn('Video background upload error:', err);
        });
    }

    function loadVideoSource(url, filename = '') {
        const video = el.captionVideo;
        const dropZone = el.videoDropZone;
        if (!video) return;

        video.src = url;
        video.style.display = 'block';
        if (dropZone) dropZone.style.display = 'none';

        state.videoLoaded = true;
        state.videoElement = video;
        if (filename && !state.serverFilename) {
            state.serverFilename = filename;
        }

        // Unhide caption overlay container and bottom transport controls strictly AFTER video import
        if (el.captionOverlayContainer) {
            el.captionOverlayContainer.style.display = 'flex';
        }
        if (el.videoBottomTransport) {
            el.videoBottomTransport.style.display = 'flex';
        }

        updateLiveCaptionOverlay();

        video.play().then(() => {
            updatePlayPauseButtonIcon(false);
        }).catch(() => {
            updatePlayPauseButtonIcon(true);
        });

        showToast(filename ? `Loaded: ${filename}` : 'Video loaded successfully', 'success');
    }

    // =========================================================================
    // 8. INTEGRATED BOTTOM VIDEO TRANSPORT & TIMELINE SCRUB
    // =========================================================================
    function initBottomTransportControls() {
        const video = el.captionVideo;
        const frame = el.mobilePhoneFrame;

        if (!video || !frame) return;

        // Play / Pause toggle
        if (el.btnPlayPause) {
            el.btnPlayPause.addEventListener('click', (e) => {
                e.stopPropagation();
                if (!state.videoLoaded) return;
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
            });
        }

        // Seek Left (-5s)
        if (el.btnSeekLeft) {
            el.btnSeekLeft.addEventListener('click', (e) => {
                e.stopPropagation();
                if (!state.videoLoaded) return;
                video.currentTime = Math.max(0, video.currentTime - 5);
                showToast('-5s', 'info', 800);
            });
        }

        // Seek Right (+5s)
        if (el.btnSeekRight) {
            el.btnSeekRight.addEventListener('click', (e) => {
                e.stopPropagation();
                if (!state.videoLoaded) return;
                const dur = video.duration || 0;
                video.currentTime = Math.min(dur, video.currentTime + 5);
                showToast('+5s', 'info', 800);
            });
        }

        // Mute / Unmute
        if (el.btnToggleMute) {
            el.btnToggleMute.addEventListener('click', (e) => {
                e.stopPropagation();
                video.muted = !video.muted;
                updateMuteButtonIcon(video.muted);
            });
        }

        // Timeline Progress Updates & Karaoke sync
        video.addEventListener('timeupdate', () => {
            const current = video.currentTime || 0;
            const duration = video.duration || 0;
            const pct = duration > 0 ? (current / duration) * 100 : 0;

            if (el.videoProgressFill) el.videoProgressFill.style.width = `${pct}%`;
            if (el.videoProgressThumb) el.videoProgressThumb.style.left = `${pct}%`;
            if (el.currentTimeDisplay) el.currentTimeDisplay.textContent = formatTime(current);
            if (el.durationTimeDisplay) el.durationTimeDisplay.textContent = formatTime(duration);

            // Sync live karaoke caption playback if captions are loaded
            syncCaptionsToTime(current);
        });

        video.addEventListener('loadedmetadata', () => {
            if (el.durationTimeDisplay) el.durationTimeDisplay.textContent = formatTime(video.duration || 0);
        });

        // Timeline click / drag scrubbing
        let isScrubbing = false;

        function seekFromMouseEvent(e) {
            if (!state.videoLoaded || !video.duration) return;
            const rect = el.videoTimelineWrap.getBoundingClientRect();
            const posX = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
            const ratio = posX / rect.width;
            video.currentTime = ratio * video.duration;
        }

        if (el.videoTimelineWrap) {
            el.videoTimelineWrap.addEventListener('mousedown', (e) => {
                isScrubbing = true;
                seekFromMouseEvent(e);
            });

            window.addEventListener('mousemove', (e) => {
                if (isScrubbing) {
                    seekFromMouseEvent(e);
                }
            });

            window.addEventListener('mouseup', () => {
                if (isScrubbing) {
                    isScrubbing = false;
                }
            });
        }

        // Video state sync
        video.addEventListener('play', () => updatePlayPauseButtonIcon(false));
        video.addEventListener('pause', () => updatePlayPauseButtonIcon(true));

        // When mouse leaves phone frame, video keeps playing smoothly
        frame.addEventListener('mouseleave', () => {
            if (state.videoLoaded && video.paused) {
                video.play().catch(() => {});
            }
        });
    }

    function updatePlayPauseButtonIcon(isPaused) {
        if (!el.btnPlayPause) return;
        if (isPaused) {
            el.btnPlayPause.innerHTML = `<svg data-lucide="play" width="16" height="16" style="margin-left:1px;"></svg>`;
        } else {
            el.btnPlayPause.innerHTML = `<svg data-lucide="pause" width="16" height="16"></svg>`;
        }
        if (window.lucide) window.lucide.createIcons();
    }

    function updateMuteButtonIcon(isMuted) {
        if (!el.btnToggleMute) return;
        if (isMuted) {
            el.btnToggleMute.innerHTML = `<svg data-lucide="volume-x" width="14" height="14" style="color:var(--error,#EF4444);"></svg>`;
        } else {
            el.btnToggleMute.innerHTML = `<svg data-lucide="volume-2" width="14" height="14"></svg>`;
        }
        if (window.lucide) window.lucide.createIcons();
    }

    function formatTime(sec) {
        if (isNaN(sec) || sec < 0) return '00:00';
        const m = Math.floor(sec / 60);
        const s = Math.floor(sec % 60);
        return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }

    // =========================================================================
    // 9. COLUMN 1: TRENDING PRESETS IMPLEMENTATION
    // =========================================================================
    function initPresetsColumn() {
        if (!el.presetsGrid) return;

        // Category filter tabs
        if (el.presetFilterPills) {
            const pills = el.presetFilterPills.querySelectorAll('.filter-pill');
            pills.forEach(pill => {
                pill.addEventListener('click', () => {
                    pills.forEach(p => p.classList.remove('active'));
                    pill.classList.add('active');
                    state.activeCategory = pill.getAttribute('data-category') || 'all';
                    renderPresets();
                });
            });
        }

        renderPresets();
    }

    function renderPresets() {
        if (!el.presetsGrid) return;
        el.presetsGrid.innerHTML = '';

        const allPresets = [...PRESETS, ...customPresets];
        const filtered = allPresets.filter(p => {
            if (state.activeCategory === 'all') return true;
            return p.category === state.activeCategory;
        });

        filtered.forEach(preset => {
            const card = document.createElement('div');
            card.className = `preset-card ${preset.id === state.activePresetId ? 'active' : ''}`;
            card.setAttribute('data-preset-id', preset.id);

            // Calculate preview styling inline
            const st = preset.style;
            let textShadow = 'none';
            if (st.glowEnabled) {
                textShadow = `0 0 ${st.glowIntensity || 12}px ${st.glowColor || '#00FFCC'}`;
            } else if (st.shadowEnabled) {
                textShadow = `0 ${st.shadowY || 2}px ${st.shadowBlur || 6}px ${st.shadowColor || '#000000'}`;
            }

            const textStroke = st.strokeEnabled ? `${st.strokeWidth || 2}px ${st.strokeColor || '#000000'}` : 'none';
            const bgCss = st.bgMode === 'semi' ? `background: rgba(15,23,42,0.7); border-radius: 6px; padding: 4px 8px;` :
                          st.bgMode === 'solid' ? `background: ${st.bgColor || '#000000'}; border-radius: 4px; padding: 4px 8px;` : '';

            card.innerHTML = `
                <div class="preset-card-header">
                    <span class="preset-card-title">${preset.name}</span>
                    <span class="preset-platform-tag ${preset.tagClass || ''}">${preset.platform}</span>
                </div>
                <div class="preset-preview-box">
                    <span style="
                        font-family: '${st.fontFamily}', sans-serif;
                        font-weight: ${st.fontWeight};
                        font-size: 16px;
                        color: ${st.textColor};
                        text-transform: ${st.textCase || 'uppercase'};
                        -webkit-text-stroke: ${textStroke};
                        text-shadow: ${textShadow};
                        ${bgCss}
                        letter-spacing: 0.5px;
                    ">
                        ${preset.previewWord1} <span style="color:${st.activeWordColor};">${preset.previewWord2}</span>
                    </span>
                </div>
            `;

            card.addEventListener('click', () => {
                selectPreset(preset);
            });

            el.presetsGrid.appendChild(card);
        });
    }

    function selectPreset(preset) {
        pushHistory();
        state.activePresetId = preset.id;

        // Merge preset style into activeStyle
        Object.assign(activeStyle, preset.style);

        updatePresetCardActiveUI();
        applyStyleToControls(activeStyle);
        updateLiveCaptionOverlay();
        showToast(`Preset: ${preset.name} applied`, 'success', 1500);
    }

    function updatePresetCardActiveUI() {
        if (!el.presetsGrid) return;
        const allCards = el.presetsGrid.querySelectorAll('.preset-card');
        allCards.forEach(c => {
            if (state.activePresetId && c.getAttribute('data-preset-id') === state.activePresetId) {
                c.classList.add('active');
            } else {
                c.classList.remove('active');
            }
        });
    }

    // =========================================================================
    // 10. COLUMN 2: SETTINGS ACCORDIONS & CONTROLS
    // =========================================================================
    function initSettingsAccordions() {
        const headers = document.querySelectorAll('.accordion-header');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const group = header.closest('.accordion-group');
                if (group) {
                    group.classList.toggle('open');
                }
            });
        });

        // Reset Style Button
        if (el.resetStyleBtn) {
            el.resetStyleBtn.addEventListener('click', () => {
                pushHistory();
                const defaultPreset = PRESETS[0];
                selectPreset(defaultPreset);
                showToast('Reset to default Hormozi preset', 'info');
            });
        }
    }

    function initSettingsFormSync() {
        // Font Family
        if (el.fontFamilySelect) {
            el.fontFamilySelect.addEventListener('change', (e) => {
                pushHistory();
                activeStyle.fontFamily = e.target.value;
                updateMetaBadge();
                updateLiveCaptionOverlay();
            });
        }

        // Font Weight
        if (el.fontWeightSelect) {
            el.fontWeightSelect.addEventListener('change', (e) => {
                pushHistory();
                activeStyle.fontWeight = e.target.value;
                updateLiveCaptionOverlay();
            });
        }

        // Font Size Slider
        if (el.fontSizeRange) {
            el.fontSizeRange.addEventListener('input', (e) => {
                activeStyle.fontSize = parseInt(e.target.value, 10);
                if (el.fontSizeDisplay) el.fontSizeDisplay.textContent = activeStyle.fontSize;
                updateMetaBadge();
                updateLiveCaptionOverlay();
            });
            el.fontSizeRange.addEventListener('change', () => pushHistory());
        }

        // Font Size Stepper (-)
        if (el.fontSizeDecBtn) {
            el.fontSizeDecBtn.addEventListener('click', () => {
                pushHistory();
                activeStyle.fontSize = Math.max(16, activeStyle.fontSize - 2);
                if (el.fontSizeRange) el.fontSizeRange.value = activeStyle.fontSize;
                if (el.fontSizeDisplay) el.fontSizeDisplay.textContent = activeStyle.fontSize;
                updateMetaBadge();
                updateLiveCaptionOverlay();
            });
        }

        // Font Size Stepper (+)
        if (el.fontSizeIncBtn) {
            el.fontSizeIncBtn.addEventListener('click', () => {
                pushHistory();
                activeStyle.fontSize = Math.min(96, activeStyle.fontSize + 2);
                if (el.fontSizeRange) el.fontSizeRange.value = activeStyle.fontSize;
                if (el.fontSizeDisplay) el.fontSizeDisplay.textContent = activeStyle.fontSize;
                updateMetaBadge();
                updateLiveCaptionOverlay();
            });
        }

        // Letter Spacing
        if (el.letterSpacingRange) {
            el.letterSpacingRange.addEventListener('input', (e) => {
                activeStyle.letterSpacing = parseInt(e.target.value, 10);
                if (el.letterSpacingDisplay) el.letterSpacingDisplay.textContent = activeStyle.letterSpacing;
                updateLiveCaptionOverlay();
            });
            el.letterSpacingRange.addEventListener('change', () => pushHistory());
        }

        // Line Height
        if (el.lineHeightRange) {
            el.lineHeightRange.addEventListener('input', (e) => {
                activeStyle.lineHeight = parseFloat(e.target.value);
                if (el.lineHeightDisplay) el.lineHeightDisplay.textContent = activeStyle.lineHeight.toFixed(1);
                updateLiveCaptionOverlay();
            });
            el.lineHeightRange.addEventListener('change', () => pushHistory());
        }

        // Position Quick Anchors
        [el.posTopBtn, el.posMiddleBtn, el.posBottomBtn].forEach(btn => {
            if (!btn) return;
            btn.addEventListener('click', () => {
                pushHistory();
                [el.posTopBtn, el.posMiddleBtn, el.posBottomBtn].forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const y = parseInt(btn.getAttribute('data-y'), 10);
                activeStyle.posYPercent = y;
                if (el.posYPercentRange) el.posYPercentRange.value = y;
                if (el.posYPercentDisplay) el.posYPercentDisplay.textContent = y;
                updateLiveCaptionOverlay();
            });
        });

        // Alignment Buttons
        [el.alignLeftBtn, el.alignCenterBtn, el.alignRightBtn].forEach(btn => {
            if (!btn) return;
            btn.addEventListener('click', () => {
                pushHistory();
                [el.alignLeftBtn, el.alignCenterBtn, el.alignRightBtn].forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                activeStyle.textAlign = btn.getAttribute('data-align');
                updateLiveCaptionOverlay();
            });
        });

        // Y Position Slider
        if (el.posYPercentRange) {
            el.posYPercentRange.addEventListener('input', (e) => {
                activeStyle.posYPercent = parseInt(e.target.value, 10);
                if (el.posYPercentDisplay) el.posYPercentDisplay.textContent = activeStyle.posYPercent;
                updateLiveCaptionOverlay();
            });
            el.posYPercentRange.addEventListener('change', () => pushHistory());
        }

        // X Position Slider
        if (el.posXPercentRange) {
            el.posXPercentRange.addEventListener('input', (e) => {
                activeStyle.posXPercent = parseInt(e.target.value, 10);
                if (el.posXPercentDisplay) el.posXPercentDisplay.textContent = activeStyle.posXPercent;
                updateLiveCaptionOverlay();
            });
            el.posXPercentRange.addEventListener('change', () => pushHistory());
        }

        // Scale Slider
        if (el.captionScaleSlider) {
            el.captionScaleSlider.addEventListener('input', (e) => {
                activeStyle.scale = parseInt(e.target.value, 10);
                if (el.captionScaleDisplay) el.captionScaleDisplay.textContent = activeStyle.scale;
                updateLiveCaptionOverlay();
            });
            el.captionScaleSlider.addEventListener('change', () => pushHistory());
        }

        // Colors
        if (el.textColorPicker) {
            el.textColorPicker.addEventListener('input', (e) => {
                activeStyle.textColor = e.target.value;
                if (el.textColorHex) el.textColorHex.textContent = e.target.value.toUpperCase();
                updateLiveCaptionOverlay();
            });
            el.textColorPicker.addEventListener('change', () => pushHistory());
        }

        if (el.activeWordColorPicker) {
            el.activeWordColorPicker.addEventListener('input', (e) => {
                activeStyle.activeWordColor = e.target.value;
                if (el.activeWordColorHex) {
                    el.activeWordColorHex.textContent = e.target.value.toUpperCase();
                    el.activeWordColorHex.style.color = e.target.value;
                }
                updateLiveCaptionOverlay();
            });
            el.activeWordColorPicker.addEventListener('change', () => pushHistory());
        }

        if (el.textOpacityRange) {
            el.textOpacityRange.addEventListener('input', (e) => {
                activeStyle.textOpacity = parseInt(e.target.value, 10);
                if (el.textOpacityDisplay) el.textOpacityDisplay.textContent = activeStyle.textOpacity;
                updateLiveCaptionOverlay();
            });
            el.textOpacityRange.addEventListener('change', () => pushHistory());
        }

        // Stroke
        if (el.strokeColorPicker) {
            el.strokeColorPicker.addEventListener('input', (e) => {
                activeStyle.strokeColor = e.target.value;
                if (el.strokeColorHex) el.strokeColorHex.textContent = e.target.value.toUpperCase();
                updateLiveCaptionOverlay();
            });
            el.strokeColorPicker.addEventListener('change', () => pushHistory());
        }

        if (el.strokeWidthRange) {
            el.strokeWidthRange.addEventListener('input', (e) => {
                activeStyle.strokeWidth = parseInt(e.target.value, 10);
                activeStyle.strokeEnabled = activeStyle.strokeWidth > 0;
                if (el.strokeWidthDisplay) el.strokeWidthDisplay.textContent = activeStyle.strokeWidth;
                updateLiveCaptionOverlay();
            });
            el.strokeWidthRange.addEventListener('change', () => pushHistory());
        }

        // Shadow & Glow
        if (el.shadowToggle) {
            el.shadowToggle.addEventListener('change', (e) => {
                pushHistory();
                activeStyle.shadowEnabled = e.target.checked;
                updateLiveCaptionOverlay();
            });
        }

        if (el.shadowColorPicker) {
            el.shadowColorPicker.addEventListener('input', (e) => {
                activeStyle.shadowColor = e.target.value;
                updateLiveCaptionOverlay();
            });
            el.shadowColorPicker.addEventListener('change', () => pushHistory());
        }

        if (el.shadowBlurRange) {
            el.shadowBlurRange.addEventListener('input', (e) => {
                activeStyle.shadowBlur = parseInt(e.target.value, 10);
                if (el.shadowBlurDisplay) el.shadowBlurDisplay.textContent = activeStyle.shadowBlur;
                updateLiveCaptionOverlay();
            });
            el.shadowBlurRange.addEventListener('change', () => pushHistory());
        }

        if (el.shadowYRange) {
            el.shadowYRange.addEventListener('input', (e) => {
                activeStyle.shadowY = parseInt(e.target.value, 10);
                if (el.shadowYDisplay) el.shadowYDisplay.textContent = activeStyle.shadowY;
                updateLiveCaptionOverlay();
            });
            el.shadowYRange.addEventListener('change', () => pushHistory());
        }

        if (el.glowToggle) {
            el.glowToggle.addEventListener('change', (e) => {
                pushHistory();
                activeStyle.glowEnabled = e.target.checked;
                updateLiveCaptionOverlay();
            });
        }

        if (el.glowColorPicker) {
            el.glowColorPicker.addEventListener('input', (e) => {
                activeStyle.glowColor = e.target.value;
                updateLiveCaptionOverlay();
            });
            el.glowColorPicker.addEventListener('change', () => pushHistory());
        }

        if (el.glowIntensityRange) {
            el.glowIntensityRange.addEventListener('input', (e) => {
                activeStyle.glowIntensity = parseInt(e.target.value, 10);
                if (el.glowIntensityDisplay) el.glowIntensityDisplay.textContent = activeStyle.glowIntensity;
                updateLiveCaptionOverlay();
            });
            el.glowIntensityRange.addEventListener('change', () => pushHistory());
        }

        // Background Box
        if (el.bgModeSelect) {
            el.bgModeSelect.addEventListener('change', (e) => {
                pushHistory();
                activeStyle.bgMode = e.target.value;
                updateLiveCaptionOverlay();
            });
        }

        if (el.bgColorPicker) {
            el.bgColorPicker.addEventListener('input', (e) => {
                activeStyle.bgColor = e.target.value;
                updateLiveCaptionOverlay();
            });
            el.bgColorPicker.addEventListener('change', () => pushHistory());
        }

        if (el.bgOpacityRange) {
            el.bgOpacityRange.addEventListener('input', (e) => {
                activeStyle.bgOpacity = parseInt(e.target.value, 10);
                if (el.bgOpacityDisplay) el.bgOpacityDisplay.textContent = activeStyle.bgOpacity;
                updateLiveCaptionOverlay();
            });
            el.bgOpacityRange.addEventListener('change', () => pushHistory());
        }

        if (el.bgPaddingRange) {
            el.bgPaddingRange.addEventListener('input', (e) => {
                activeStyle.bgPadding = parseInt(e.target.value, 10);
                if (el.bgPaddingDisplay) el.bgPaddingDisplay.textContent = activeStyle.bgPadding;
                updateLiveCaptionOverlay();
            });
            el.bgPaddingRange.addEventListener('change', () => pushHistory());
        }

        if (el.bgRadiusRange) {
            el.bgRadiusRange.addEventListener('input', (e) => {
                activeStyle.bgRadius = parseInt(e.target.value, 10);
                if (el.bgRadiusDisplay) el.bgRadiusDisplay.textContent = activeStyle.bgRadius;
                updateLiveCaptionOverlay();
            });
            el.bgRadiusRange.addEventListener('change', () => pushHistory());
        }

        // Casing Buttons
        [el.caseUpperBtn, el.caseTitleBtn, el.caseNormalBtn].forEach(btn => {
            if (!btn) return;
            btn.addEventListener('click', () => {
                pushHistory();
                [el.caseUpperBtn, el.caseTitleBtn, el.caseNormalBtn].forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                activeStyle.textCase = btn.getAttribute('data-case');
                updateLiveCaptionOverlay();
            });
        });

        // Animation
        if (el.animationTypeSelect) {
            el.animationTypeSelect.addEventListener('change', (e) => {
                pushHistory();
                activeStyle.animation = e.target.value;
                updateLiveCaptionOverlay();
            });
        }
    }

    function applyStyleToControls(st) {
        if (el.fontFamilySelect) el.fontFamilySelect.value = st.fontFamily || 'Inter';
        if (el.fontWeightSelect) el.fontWeightSelect.value = st.fontWeight || '700';
        if (el.fontSizeRange) el.fontSizeRange.value = st.fontSize || 42;
        if (el.fontSizeDisplay) el.fontSizeDisplay.textContent = st.fontSize || 42;
        if (el.letterSpacingRange) el.letterSpacingRange.value = st.letterSpacing || 0;
        if (el.letterSpacingDisplay) el.letterSpacingDisplay.textContent = st.letterSpacing || 0;
        if (el.lineHeightRange) el.lineHeightRange.value = st.lineHeight || 1.2;
        if (el.lineHeightDisplay) el.lineHeightDisplay.textContent = (st.lineHeight || 1.2).toFixed(1);

        if (el.textColorPicker) el.textColorPicker.value = st.textColor || '#FFFFFF';
        if (el.textColorHex) el.textColorHex.textContent = (st.textColor || '#FFFFFF').toUpperCase();
        if (el.activeWordColorPicker) el.activeWordColorPicker.value = st.activeWordColor || '#10B981';
        if (el.activeWordColorHex) {
            el.activeWordColorHex.textContent = (st.activeWordColor || '#10B981').toUpperCase();
            el.activeWordColorHex.style.color = st.activeWordColor || '#10B981';
        }
        if (el.textOpacityRange) el.textOpacityRange.value = st.textOpacity !== undefined ? st.textOpacity : 100;
        if (el.textOpacityDisplay) el.textOpacityDisplay.textContent = st.textOpacity !== undefined ? st.textOpacity : 100;

        if (el.strokeColorPicker) el.strokeColorPicker.value = st.strokeColor || '#000000';
        if (el.strokeColorHex) el.strokeColorHex.textContent = (st.strokeColor || '#000000').toUpperCase();
        if (el.strokeWidthRange) el.strokeWidthRange.value = st.strokeEnabled ? (st.strokeWidth || 3) : 0;
        if (el.strokeWidthDisplay) el.strokeWidthDisplay.textContent = st.strokeEnabled ? (st.strokeWidth || 3) : 0;

        if (el.shadowToggle) el.shadowToggle.checked = Boolean(st.shadowEnabled);
        if (el.shadowColorPicker) el.shadowColorPicker.value = st.shadowColor || '#000000';
        if (el.shadowBlurRange) el.shadowBlurRange.value = st.shadowBlur !== undefined ? st.shadowBlur : 6;
        if (el.shadowBlurDisplay) el.shadowBlurDisplay.textContent = st.shadowBlur !== undefined ? st.shadowBlur : 6;
        if (el.shadowYRange) el.shadowYRange.value = st.shadowY !== undefined ? st.shadowY : 2;
        if (el.shadowYDisplay) el.shadowYDisplay.textContent = st.shadowY !== undefined ? st.shadowY : 2;

        if (el.glowToggle) el.glowToggle.checked = Boolean(st.glowEnabled);
        if (el.glowColorPicker) el.glowColorPicker.value = st.glowColor || '#10B981';
        if (el.glowIntensityRange) el.glowIntensityRange.value = st.glowIntensity !== undefined ? st.glowIntensity : 12;
        if (el.glowIntensityDisplay) el.glowIntensityDisplay.textContent = st.glowIntensity !== undefined ? st.glowIntensity : 12;

        if (el.bgModeSelect) el.bgModeSelect.value = st.bgMode || 'none';
        if (el.bgColorPicker) el.bgColorPicker.value = st.bgColor || '#000000';
        if (el.bgOpacityRange) el.bgOpacityRange.value = st.bgOpacity !== undefined ? st.bgOpacity : 0;
        if (el.bgOpacityDisplay) el.bgOpacityDisplay.textContent = st.bgOpacity !== undefined ? st.bgOpacity : 0;

        if (el.posYPercentRange) el.posYPercentRange.value = st.posYPercent || 80;
        if (el.posYPercentDisplay) el.posYPercentDisplay.textContent = st.posYPercent || 80;
        if (el.posXPercentRange) el.posXPercentRange.value = st.posXPercent || 50;
        if (el.posXPercentDisplay) el.posXPercentDisplay.textContent = st.posXPercent || 50;
        if (el.captionScaleSlider) el.captionScaleSlider.value = st.scale || 100;
        if (el.captionScaleDisplay) el.captionScaleDisplay.textContent = st.scale || 100;

        updateMetaBadge();
    }

    function updateMetaBadge() {
        if (el.fontMetaBadge) {
            el.fontMetaBadge.textContent = `${activeStyle.fontFamily} • ${activeStyle.fontSize}px`;
        }
    }

    // =========================================================================
    // 11. CAPTION IMPORT (.srt, .vtt, .json)
    // =========================================================================
    function initCaptionImport() {
        if (!el.captionFileInput) return;

        el.captionFileInput.addEventListener('change', (e) => {
            if (!e.target.files || !e.target.files[0]) return;
            const file = e.target.files[0];

            const formData = new FormData();
            formData.append('file', file);
            if (state.projectId) {
                formData.append('project_id', state.projectId);
            }

            showToast(`Importing ${file.name}...`, 'info');
            fetch('/api/caption-studio/import', {
                method: 'POST',
                body: formData,
            })
            .then(r => r.json())
            .then(res => {
                if (res.success && res.captions && res.captions.length > 0) {
                    pushHistory();
                    state.captions = res.captions;
                    showToast(`Successfully imported ${res.captions.length} captions!`, 'success', 3000);
                    updateLiveCaptionOverlay();
                } else {
                    showToast(res.error || 'Failed to import captions', 'error');
                }
            })
            .catch(err => {
                showToast(`Import error: ${err.message}`, 'error');
            })
            .finally(() => {
                el.captionFileInput.value = '';
            });
        });
    }

    // =========================================================================
    // 12. AI AUTO-CAPTION MODAL & WHISPER INTEGRATION (WITH APPLY CAPTIONS)
    // =========================================================================
    let pendingGeneratedCaptions = [];

    function initGenerateCaptionsModal() {
        if (!el.generateCaptionsModal) return;

        if (el.generateModalCloseBtn) {
            el.generateModalCloseBtn.addEventListener('click', closeGenerateModal);
        }
        if (el.genCancelBtn) {
            el.genCancelBtn.addEventListener('click', closeGenerateModal);
        }

        if (el.genStartBtn) {
            el.genStartBtn.addEventListener('click', () => {
                triggerAutoCaptionGeneration();
            });
        }

        if (el.genApplyBtn) {
            el.genApplyBtn.addEventListener('click', () => {
                applyGeneratedCaptions();
            });
        }
    }

    function openGenerateModal() {
        if (!el.generateCaptionsModal) return;
        el.generateCaptionsModal.style.display = 'flex';
        pendingGeneratedCaptions = [];
        if (el.genProgressPanel) el.genProgressPanel.style.display = 'none';
        if (el.genReadyPanel) el.genReadyPanel.style.display = 'none';
        if (el.genStartBtn) {
            el.genStartBtn.style.display = 'inline-flex';
            el.genStartBtn.disabled = false;
        }
        if (el.genApplyBtn) el.genApplyBtn.style.display = 'none';
    }

    function closeGenerateModal() {
        if (el.generateCaptionsModal) {
            el.generateCaptionsModal.style.display = 'none';
        }
    }

    function triggerAutoCaptionGeneration() {
        if (!state.serverFilename) {
            showToast('Video file is still processing on the server, please wait 2 seconds...', 'warning');
            return;
        }

        const language = el.genLanguageSelect ? el.genLanguageSelect.value : 'hinglish';
        const style = el.genStyleSelect ? el.genStyleSelect.value : 'viral';
        const model = el.genModelSelect ? el.genModelSelect.value : 'base';

        if (el.genProgressPanel) el.genProgressPanel.style.display = 'flex';
        if (el.genReadyPanel) el.genReadyPanel.style.display = 'none';
        if (el.genProgressStatus) {
            el.genProgressStatus.textContent = language === 'hinglish' ?
                'Transcribing audio with Whisper AI & transliterating to Hinglish...' :
                'Transcribing audio with Whisper AI...';
        }
        if (el.genStartBtn) el.genStartBtn.disabled = true;

        fetch('/api/caption-studio/auto-caption', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                videoFileName: state.serverFilename,
                language: language,
                style: style,
                model: model,
                project_id: state.projectId || ''
            })
        })
        .then(r => r.json())
        .then(res => {
            if (res.success && res.captions && res.captions.length > 0) {
                pendingGeneratedCaptions = res.captions;
                if (el.genProgressPanel) el.genProgressPanel.style.display = 'none';
                if (el.genStartBtn) el.genStartBtn.style.display = 'none';
                if (el.genReadyPanel) el.genReadyPanel.style.display = 'flex';
                if (el.genReadyCountText) {
                    el.genReadyCountText.textContent = `✓ Generated ${res.captions.length} Captions!`;
                }
                if (el.genPreviewBox) {
                    const sampleLines = res.captions.slice(0, 4).map(c => `<b>[${c.start.toFixed(1)}s - ${c.end.toFixed(1)}s]</b> ${c.text}`).join('<br>');
                    el.genPreviewBox.innerHTML = sampleLines + (res.captions.length > 4 ? `<div style="margin-top:4px; opacity:0.75;"><i>+ ${res.captions.length - 4} more captions ready to apply</i></div>` : '');
                }
                if (el.genApplyBtn) el.genApplyBtn.style.display = 'inline-flex';
                if (window.lucide) window.lucide.createIcons();
                showToast(`${res.captions.length} captions generated! Click "Apply Captions".`, 'success', 3000);
            } else {
                showToast(res.error || 'Whisper transcription failed', 'error');
                if (el.genProgressPanel) el.genProgressPanel.style.display = 'none';
                if (el.genStartBtn) el.genStartBtn.disabled = false;
            }
        })
        .catch(err => {
            showToast(`Auto-caption error: ${err.message}`, 'error');
            if (el.genProgressPanel) el.genProgressPanel.style.display = 'none';
            if (el.genStartBtn) el.genStartBtn.disabled = false;
        });
    }

    function applyGeneratedCaptions() {
        if (!pendingGeneratedCaptions || pendingGeneratedCaptions.length === 0) return;
        pushHistory();
        state.captions = pendingGeneratedCaptions;
        closeGenerateModal();

        // Seek video or render first card so user immediately sees captions
        if (state.videoElement && state.captions[0]) {
            state.videoElement.currentTime = state.captions[0].start;
        }
        updateLiveCaptionOverlay();
        showToast(`✓ Applied ${state.captions.length} captions to video!`, 'success', 3500);
    }

    // =========================================================================
    // 12b. CUSTOM PRESETS ENGINE (SAVE PRESET / MY PRESETS / SELECT & DELETE)
    // =========================================================================
    let customPresets = [];
    const CUSTOM_PRESETS_STORAGE_KEY = 'upclip_custom_caption_presets';

    function initCustomPresetsSystem() {
        loadCustomPresets();

        if (el.savePresetBtn) {
            el.savePresetBtn.addEventListener('click', openSavePresetModal);
        }
        if (el.savePresetCloseBtn) {
            el.savePresetCloseBtn.addEventListener('click', closeSavePresetModal);
        }
        if (el.savePresetCancelBtn) {
            el.savePresetCancelBtn.addEventListener('click', closeSavePresetModal);
        }
        if (el.savePresetConfirmBtn) {
            el.savePresetConfirmBtn.addEventListener('click', handleConfirmSavePreset);
        }

        if (el.myPresetsBtn) {
            el.myPresetsBtn.addEventListener('click', openMyPresetsModal);
        }
        if (el.myPresetsCloseBtn) {
            el.myPresetsCloseBtn.addEventListener('click', closeMyPresetsModal);
        }
        if (el.myPresetsDismissBtn) {
            el.myPresetsDismissBtn.addEventListener('click', closeMyPresetsModal);
        }
    }

    function loadCustomPresets() {
        try {
            const raw = localStorage.getItem(CUSTOM_PRESETS_STORAGE_KEY);
            customPresets = raw ? JSON.parse(raw) : [];
        } catch (e) {
            customPresets = [];
        }

        // Also fetch from server to synchronize
        fetch('/api/caption-studio/presets/list')
            .then(r => r.json())
            .then(res => {
                if (res.success && Array.isArray(res.presets) && res.presets.length > 0) {
                    const map = new Map();
                    customPresets.forEach(p => map.set(p.id, p));
                    res.presets.forEach(p => map.set(p.id, p));
                    customPresets = Array.from(map.values());
                    saveCustomPresetsToLocalStorage();
                    renderPresets();
                }
            })
            .catch(() => {});
    }

    function saveCustomPresetsToLocalStorage() {
        try {
            localStorage.setItem(CUSTOM_PRESETS_STORAGE_KEY, JSON.stringify(customPresets));
        } catch (e) {}
    }

    function openSavePresetModal() {
        if (!el.savePresetModal) return;
        if (el.presetNameInput) {
            el.presetNameInput.value = `Custom Style ${customPresets.length + 1}`;
        }
        if (el.presetSaveSummary) {
            const boxModeText = activeStyle.bgMode === 'none' ? 'Transparent' : activeStyle.bgMode;
            el.presetSaveSummary.innerHTML = `
                <div><b>Font:</b> ${activeStyle.fontFamily} (${activeStyle.fontWeight}) • ${activeStyle.fontSize}px</div>
                <div><b>Colors:</b> Base <span style="display:inline-block; width:10px; height:10px; border-radius:2px; background:${activeStyle.textColor}; vertical-align:middle;"></span> ${activeStyle.textColor} • Active <span style="display:inline-block; width:10px; height:10px; border-radius:2px; background:${activeStyle.activeWordColor}; vertical-align:middle;"></span> ${activeStyle.activeWordColor}</div>
                <div><b>Box / Backdrop:</b> ${boxModeText} • Casing: ${activeStyle.textCase} • Animation: ${activeStyle.animation}</div>
            `;
        }
        el.savePresetModal.style.display = 'flex';
        if (el.presetNameInput) el.presetNameInput.focus();
        if (window.lucide) window.lucide.createIcons();
    }

    function closeSavePresetModal() {
        if (el.savePresetModal) el.savePresetModal.style.display = 'none';
    }

    function handleConfirmSavePreset() {
        const name = (el.presetNameInput ? el.presetNameInput.value.trim() : '') || `Custom Style ${customPresets.length + 1}`;
        const newId = `custom_${Date.now()}`;
        const newPreset = {
            id: newId,
            name: name,
            category: 'custom',
            platform: 'My Presets',
            tagClass: 'tag-custom',
            previewWord1: name.split(' ')[0].toUpperCase() || 'CUSTOM',
            previewWord2: 'STYLE',
            style: JSON.parse(JSON.stringify(activeStyle)),
            created_at: Date.now()
        };

        customPresets.unshift(newPreset);
        saveCustomPresetsToLocalStorage();

        // Also post to server
        fetch('/api/caption-studio/presets/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, style: activeStyle })
        }).catch(() => {});

        closeSavePresetModal();
        renderPresets();
        showToast(`Preset "${name}" saved! View it in My Presets.`, 'success', 3000);
    }

    function openMyPresetsModal() {
        if (!el.myPresetsModal) return;
        renderMyPresetsList();
        el.myPresetsModal.style.display = 'flex';
        if (window.lucide) window.lucide.createIcons();
    }

    function closeMyPresetsModal() {
        if (el.myPresetsModal) el.myPresetsModal.style.display = 'none';
    }

    function renderMyPresetsList() {
        if (!el.myPresetsList) return;
        if (customPresets.length === 0) {
            el.myPresetsList.innerHTML = `
                <div style="text-align:center; padding:32px 16px; color:var(--text-muted, #94A3B8);">
                    <div style="font-size:28px; margin-bottom:8px;">🔖</div>
                    <div style="font-weight:600; font-size:14px; margin-bottom:4px; color:var(--text-primary, #FFF);">No Custom Presets Saved Yet</div>
                    <div style="font-size:12px;">Customize your styling settings and click <b>Save Preset</b> to create your first reusable preset.</div>
                </div>
            `;
            return;
        }

        el.myPresetsList.innerHTML = customPresets.map(p => {
            const st = p.style || {};
            const font = st.fontFamily || 'Montserrat';
            const textColor = st.textColor || '#FFFFFF';
            const activeColor = st.activeWordColor || '#22C55E';
            return `
                <div class="my-preset-card" data-preset-id="${p.id}" style="display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px 14px; background:var(--surface-2, #1E293B); border:1px solid var(--border, #334155); border-radius:8px;">
                    <div style="flex:1; min-width:0;">
                        <div style="font-weight:700; font-size:13px; color:var(--text-primary, #FFF); margin-bottom:4px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${p.name}</div>
                        <div style="display:flex; align-items:center; gap:8px; font-size:11px; color:var(--text-secondary, #94A3B8);">
                            <span>${font} • ${st.fontSize || 38}px</span>
                            <span style="display:inline-flex; align-items:center; gap:3px;">
                                <span style="width:8px; height:8px; border-radius:50%; background:${textColor}; display:inline-block;"></span>
                                <span style="width:8px; height:8px; border-radius:50%; background:${activeColor}; display:inline-block;"></span>
                            </span>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px; flex-shrink:0;">
                        <button type="button" class="btn btn-primary btn-sm btn-select-preset" data-id="${p.id}" style="padding:5px 12px; font-size:11px;">
                            Select
                        </button>
                        <button type="button" class="btn btn-secondary btn-sm btn-delete-preset" data-id="${p.id}" style="padding:5px 10px; font-size:11px; color:var(--error, #EF4444);" title="Delete Preset">
                            Delete
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        // Wire Select and Delete buttons
        el.myPresetsList.querySelectorAll('.btn-select-preset').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                const preset = customPresets.find(p => p.id === id);
                if (preset && preset.style) {
                    pushHistory();
                    Object.assign(activeStyle, preset.style);
                    state.activePresetId = preset.id;
                    applyStyleToControls(activeStyle);
                    updatePresetCardActiveUI();
                    updateLiveCaptionOverlay();
                    closeMyPresetsModal();
                    showToast(`Preset "${preset.name}" selected!`, 'success', 2500);
                }
            });
        });

        el.myPresetsList.querySelectorAll('.btn-delete-preset').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.getAttribute('data-id');
                const p = customPresets.find(item => item.id === id);
                const name = p ? p.name : 'preset';
                if (!confirm(`Are you sure you want to delete preset "${name}"?`)) return;

                customPresets = customPresets.filter(item => item.id !== id);
                saveCustomPresetsToLocalStorage();

                // Delete from server
                fetch('/api/caption-studio/presets/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id })
                }).catch(() => {});

                renderMyPresetsList();
                renderPresets();
                showToast(`Preset "${name}" deleted`, 'info', 2000);
            });
        });

        if (window.lucide) window.lucide.createIcons();
    }

    // =========================================================================
    // 13. EXPORT VIDEO MODAL & FFMPEG RENDER
    // =========================================================================
    function initExportModal() {
        if (!el.exportVideoModal) return;

        if (el.exportModalCloseBtn) {
            el.exportModalCloseBtn.addEventListener('click', closeExportModal);
        }
        if (el.exportCancelBtn) {
            el.exportCancelBtn.addEventListener('click', closeExportModal);
        }

        if (el.exportStartRenderBtn) {
            el.exportStartRenderBtn.addEventListener('click', () => {
                triggerExportRender();
            });
        }

        // Quick Subtitles Only Downloads
        if (el.exportSrtOnlyBtn) {
            el.exportSrtOnlyBtn.addEventListener('click', () => exportSubtitlesOnly('srt'));
        }
        if (el.exportVttOnlyBtn) {
            el.exportVttOnlyBtn.addEventListener('click', () => exportSubtitlesOnly('vtt'));
        }
        if (el.exportJsonOnlyBtn) {
            el.exportJsonOnlyBtn.addEventListener('click', () => exportSubtitlesOnly('json'));
        }
    }

    function openExportModal() {
        if (!el.exportVideoModal) return;
        el.exportVideoModal.style.display = 'flex';
        if (el.exportProgressPanel) el.exportProgressPanel.style.display = 'none';
        if (el.exportDownloadLinkBtn) el.exportDownloadLinkBtn.style.display = 'none';
        if (el.exportStartRenderBtn) {
            el.exportStartRenderBtn.style.display = 'inline-flex';
            el.exportStartRenderBtn.disabled = false;
        }
    }

    function closeExportModal() {
        if (el.exportVideoModal) {
            el.exportVideoModal.style.display = 'none';
        }
    }

    function triggerExportRender() {
        if (!state.serverFilename) {
            showToast('Video source is not ready for export.', 'warning');
            return;
        }

        // If no captions generated yet, create sample burned captions so user gets a captioned video
        const captionsToExport = (state.captions && state.captions.length > 0) ? state.captions : getFallbackDemoCaptions();

        if (el.exportProgressPanel) el.exportProgressPanel.style.display = 'flex';
        if (el.exportProgressSpinner) el.exportProgressSpinner.style.display = 'block';
        if (el.exportStatusText) el.exportStatusText.textContent = 'Rendering video with burned captions via FFmpeg...';
        if (el.exportStartRenderBtn) el.exportStartRenderBtn.disabled = true;

        const payload = {
            videoFileName: state.serverFilename,
            captions: captionsToExport,
            style: activeStyle,
            project_id: state.projectId || '',
            resolution: el.exportResolutionSelect ? el.exportResolutionSelect.value : '9:16_1080p',
            fps: el.exportFpsSelect ? parseInt(el.exportFpsSelect.value, 10) : 30,
            format: el.exportFormatSelect ? el.exportFormatSelect.value : 'mp4'
        };

        fetch('/api/caption-studio/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(r => r.json())
        .then(res => {
            if (res.success && res.download_url) {
                if (el.exportProgressSpinner) el.exportProgressSpinner.style.display = 'none';
                if (el.exportStatusText) el.exportStatusText.textContent = '✓ Render Complete! Click below to save your video.';
                if (el.exportStartRenderBtn) el.exportStartRenderBtn.style.display = 'none';
                if (el.exportDownloadLinkBtn) {
                    el.exportDownloadLinkBtn.href = res.download_url;
                    el.exportDownloadLinkBtn.download = res.filename || 'captioned_video.mp4';
                    el.exportDownloadLinkBtn.style.display = 'inline-flex';
                }
                showToast('Render Complete! Click Download to save.', 'success', 4000);
            } else {
                if (el.exportProgressPanel) el.exportProgressPanel.style.display = 'none';
                if (el.exportStartRenderBtn) el.exportStartRenderBtn.disabled = false;
                showToast(res.error || 'Video rendering failed', 'error');
            }
        })
        .catch(err => {
            if (el.exportProgressPanel) el.exportProgressPanel.style.display = 'none';
            if (el.exportStartRenderBtn) el.exportStartRenderBtn.disabled = false;
            showToast(`Render error: ${err.message}`, 'error');
        });
    }

    function exportSubtitlesOnly(format) {
        const captionsToExport = (state.captions && state.captions.length > 0) ? state.captions : getFallbackDemoCaptions();
        fetch('/api/caption-studio/export-captions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                captions: captionsToExport,
                format: format,
                project_id: state.projectId || ''
            })
        })
        .then(r => r.json())
        .then(res => {
            if (res.success && res.files && res.files[format]) {
                const url = res.files[format].url;
                const link = document.createElement('a');
                link.href = url;
                link.download = res.files[format].filename;
                document.body.appendChild(link);
                link.click();
                link.remove();
                showToast(`Downloaded .${format.toUpperCase()} subtitles`, 'success');
            } else {
                showToast(res.error || 'Failed to export subtitles', 'error');
            }
        })
        .catch(err => {
            showToast(`Subtitle export error: ${err.message}`, 'error');
        });
    }

    function getFallbackDemoCaptions() {
        return [
            {
                id: 'demo_1',
                text: 'CREATING VIRAL SHORTS',
                start: 0.0,
                end: 3.0,
                words: [
                    { text: 'CREATING', start: 0.0, end: 1.0 },
                    { text: 'VIRAL', start: 1.0, end: 2.0 },
                    { text: 'SHORTS', start: 2.0, end: 3.0 },
                ]
            }
        ];
    }

    // =========================================================================
    // 14. LIVE CAPTION OVERLAY RENDERING & KARAOKE SYNC
    // =========================================================================
    function syncCaptionsToTime(currentTime) {
        if (!state.captions || state.captions.length === 0) {
            // Keep default preview tokens visible so user can adjust styles
            return;
        }

        const curCap = state.captions.find(c => currentTime >= c.start && currentTime <= c.end);
        const box = el.captionDragBox;
        if (!box) return;

        if (!curCap) {
            // No spoken caption at this moment
            box.style.opacity = '0';
            return;
        }

        box.style.opacity = '1';
        renderCaptionWords(curCap, currentTime);
    }

    function renderCaptionWords(cap, currentTime) {
        const box = el.captionDragBox;
        if (!box) return;

        const words = cap.words && cap.words.length > 0 ? cap.words : cap.text.split(' ').map(w => ({ text: w, start: cap.start, end: cap.end }));

        // Rebuild tokens if text changed
        const currentText = words.map(w => w.text).join(' ');
        if (box.getAttribute('data-current-text') !== currentText) {
            box.setAttribute('data-current-text', currentText);
            box.innerHTML = '';
            words.forEach((w, idx) => {
                const span = document.createElement('span');
                span.className = 'caption-word-token';
                span.id = `capWord_${idx}`;
                span.textContent = w.text;
                box.appendChild(span);
            });
        }

        // Highlight active word
        const tokens = box.querySelectorAll('.caption-word-token');
        words.forEach((w, idx) => {
            const span = tokens[idx];
            if (!span) return;
            const isWordActive = (currentTime >= w.start && currentTime <= w.end) || (idx === 0 && words.length === 1);
            if (isWordActive) {
                span.classList.add('active-karaoke-word');
            } else {
                span.classList.remove('active-karaoke-word');
            }
        });

        applyActiveStyleToDOM();
    }

    function updateLiveCaptionOverlay() {
        const overlay = el.captionOverlayContainer;
        const box = el.captionDragBox;
        if (!overlay || !box) return;

        // Position
        overlay.style.top = `${activeStyle.posYPercent}%`;
        const scaleVal = (activeStyle.scale || 100) / 100;

        // Box & Alignment
        box.style.transform = `scale(${scaleVal})`;
        box.style.justifyContent = activeStyle.textAlign === 'left' ? 'flex-start' :
                                   activeStyle.textAlign === 'right' ? 'flex-end' : 'center';

        // Background
        if (activeStyle.bgMode === 'semi') {
            box.style.background = `rgba(15, 23, 42, ${(activeStyle.bgOpacity || 65) / 100})`;
            box.style.borderRadius = `${activeStyle.bgRadius || 8}px`;
            box.style.padding = `${activeStyle.bgPadding || 8}px 14px`;
        } else if (activeStyle.bgMode === 'solid') {
            const hex = activeStyle.bgColor || '#000000';
            box.style.background = hex;
            box.style.borderRadius = `${activeStyle.bgRadius || 6}px`;
            box.style.padding = `${activeStyle.bgPadding || 6}px 12px`;
        } else if (activeStyle.bgMode === 'highlight') {
            box.style.background = 'transparent';
            box.style.padding = '4px';
        } else {
            box.style.background = 'transparent';
            box.style.padding = '0';
        }

        applyActiveStyleToDOM();
    }

    function applyActiveStyleToDOM() {
        const box = el.captionDragBox;
        if (!box) return;

        // Text Stroke
        const textStroke = (activeStyle.strokeEnabled && activeStyle.strokeWidth > 0) ?
                           `${activeStyle.strokeWidth}px ${activeStyle.strokeColor || '#000000'}` : 'none';

        // Text Shadow / Glow
        let textShadow = 'none';
        if (activeStyle.glowEnabled) {
            textShadow = `0 0 ${activeStyle.glowIntensity || 14}px ${activeStyle.glowColor || '#10B981'}`;
        } else if (activeStyle.shadowEnabled) {
            textShadow = `0 ${activeStyle.shadowY || 2}px ${activeStyle.shadowBlur || 6}px ${activeStyle.shadowColor || '#000000'}`;
        }

        // Casing
        const textTransform = activeStyle.textCase === 'uppercase' ? 'uppercase' :
                              activeStyle.textCase === 'capitalize' ? 'capitalize' : 'none';

        // Opacity
        const alpha = (activeStyle.textOpacity !== undefined ? activeStyle.textOpacity : 100) / 100;

        // Typography styling for all word tokens
        const words = box.querySelectorAll('.caption-word-token');
        words.forEach(w => {
            w.style.fontFamily = `'${activeStyle.fontFamily}', sans-serif`;
            w.style.fontWeight = activeStyle.fontWeight;
            w.style.fontSize = `${activeStyle.fontSize}px`;
            w.style.letterSpacing = `${activeStyle.letterSpacing || 0}px`;
            w.style.lineHeight = activeStyle.lineHeight || 1.2;
            w.style.textTransform = textTransform;
            w.style.webkitTextStroke = textStroke;
            w.style.textShadow = textShadow;
            w.style.opacity = alpha;

            if (w.classList.contains('active-karaoke-word')) {
                w.style.color = activeStyle.activeWordColor || '#22C55E';
                if (activeStyle.bgMode === 'highlight') {
                    w.style.background = 'rgba(0,0,0,0.85)';
                    w.style.padding = '2px 8px';
                    w.style.borderRadius = '6px';
                } else {
                    w.style.background = 'transparent';
                    w.style.padding = '0';
                }
            } else {
                w.style.color = activeStyle.textColor || '#FFFFFF';
                w.style.background = 'transparent';
                w.style.padding = '0';
            }
        });
    }

    // =========================================================================
    // 15. PRELOAD BACKEND DATA
    // =========================================================================
    function initPreloadData() {
        if (!el.captionContextData) return;

        try {
            const rawPreload = el.captionContextData.getAttribute('data-preload');
            const sourceFile = el.captionContextData.getAttribute('data-source-file');

            if (sourceFile) {
                state.serverFilename = sourceFile;
            }

            if (rawPreload && rawPreload !== 'null') {
                const preload = JSON.parse(rawPreload);
                if (preload && preload.video_url) {
                    state.serverFilename = preload.filename || sourceFile || '';
                    loadVideoSource(preload.video_url, preload.filename || 'Preloaded Video');
                }
            }
        } catch (err) {
            console.warn('Caption Studio: Preload parse error', err);
        }
    }

    // =========================================================================
    // 16. TOAST NOTIFICATIONS
    // =========================================================================
    function showToast(message, type = 'info', duration = 2500) {
        let container = el.toastContainer;
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container';
            document.body.appendChild(container);
            el.toastContainer = container;
        }

        const toast = document.createElement('div');
        toast.className = `upclip-toast toast-${type}`;
        toast.style.cssText = `
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            margin-bottom: 8px;
            background: var(--surface-2, #323232);
            color: var(--text-primary, #FFF7E8);
            border: 1px solid var(--border, #3A3A3A);
            border-left: 3px solid ${type === 'success' ? '#10B981' : type === 'warning' ? '#F59E0B' : '#3B82F6'};
            border-radius: 6px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.5);
            font-size: 11px;
            font-weight: 500;
            opacity: 0;
            transform: translateY(8px);
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            pointer-events: auto;
        `;

        toast.textContent = message;
        container.appendChild(toast);

        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        });

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-8px)';
            setTimeout(() => toast.remove(), 200);
        }, duration);
    }
})();
