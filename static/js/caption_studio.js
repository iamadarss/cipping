/**
 * ==============================================================================
 * FLIP STUDIO — CAPTION STUDIO 3.0 DESKTOP ENGINE
 * ==============================================================================
 * Comprehensive modern video caption editor engine:
 * - Large 16:9 default horizontal editing canvas + aspect ratio switching
 * - Frame-accurate transport controls & synchronized timeline
 * - Direct on-video drag & drop caption positioning with magnetic snap & guidelines
 * - 20 curated visual preset styles with 1-click apply
 * - 25+ font library with live search filter & dynamic typography
 * - Full styling: stroke/outline, drop shadow, glow, background box, animations
 * - Word-by-word synchronized karaoke highlight during playback
 * - Timeline with time ruler, playhead scrubbing, trim handles, split/merge/duplicate
 * - Native video file picker & drag-and-drop loading with 0-latency playback
 * - AI Speech-to-text generation via Whisper
 * - Subtitle import & export (.srt, .vtt, .json)
 * - Burned-in caption video export via FFmpeg
 * - History stack (Undo/Redo) & Autosave
 * ==============================================================================
 */

(function () {
    'use strict';

    // ==========================================================================
    // 1. FONT REGISTRY (25+ Professional Fonts)
    // ==========================================================================
    const FONT_REGISTRY = [
        { id: "Inter", name: "Inter", category: "Sans-Serif", defaultWeight: 700 },
        { id: "Poppins", name: "Poppins", category: "Geometric", defaultWeight: 800 },
        { id: "Roboto", name: "Roboto", category: "Standard", defaultWeight: 700 },
        { id: "Montserrat", name: "Montserrat", category: "Modern Bold", defaultWeight: 800 },
        { id: "Open Sans", name: "Open Sans", category: "Neutral", defaultWeight: 700 },
        { id: "Lato", name: "Lato", category: "Warm Sans", defaultWeight: 700 },
        { id: "Nunito", name: "Nunito", category: "Rounded", defaultWeight: 800 },
        { id: "Oswald", name: "Oswald", category: "Condensed", defaultWeight: 700 },
        { id: "Bebas Neue", name: "Bebas Neue", category: "Tall Display", defaultWeight: 800 },
        { id: "Anton", name: "Anton", category: "High Impact", defaultWeight: 900 },
        { id: "Raleway", name: "Raleway", category: "Elegant", defaultWeight: 800 },
        { id: "Playfair Display", name: "Playfair Display", category: "Luxury Serif", defaultWeight: 800 },
        { id: "Merriweather", name: "Merriweather", category: "Editorial Serif", defaultWeight: 700 },
        { id: "DM Sans", name: "DM Sans", category: "Editorial", defaultWeight: 700 },
        { id: "Space Grotesk", name: "Space Grotesk", category: "Tech", defaultWeight: 700 },
        { id: "Manrope", name: "Manrope", category: "Modern Clean", defaultWeight: 700 },
        { id: "Plus Jakarta Sans", name: "Plus Jakarta Sans", category: "Premium Sans", defaultWeight: 800 },
        { id: "Archivo", name: "Archivo", category: "Geometric Heavy", defaultWeight: 800 },
        { id: "Outfit", name: "Outfit", category: "Social Clean", defaultWeight: 700 },
        { id: "Ubuntu", name: "Ubuntu", category: "Contemporary", defaultWeight: 700 },
        { id: "Rubik", name: "Rubik", category: "Sturdy", defaultWeight: 800 },
        { id: "Work Sans", name: "Work Sans", category: "Optimized UI", defaultWeight: 800 },
        { id: "Fira Sans", name: "Fira Sans", category: "Humanist", defaultWeight: 700 },
        { id: "Fira Code", name: "Fira Code", category: "Monospace", defaultWeight: 700 },
        { id: "Bricolage Grotesque", name: "Bricolage Grotesque", category: "Expressive", defaultWeight: 800 },
        { id: "Arial Black", name: "Arial Black", category: "System Heavy", defaultWeight: 900 }
    ];

    // ==========================================================================
    // 2. PRESETS REGISTRY (20 Curated Styles)
    // ==========================================================================
    const PRESETS_REGISTRY = [
        {
            id: "minimal_word_by_word",
            name: "Minimal Word-by-Word",
            category: "Clean",
            style: {
                font_family: "Inter",
                font_weight: 700,
                font_size: 40,
                text_color: "#FFFFFF",
                active_word_color: "#10B981",
                stroke_enabled: false,
                stroke_width: 0,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 4,
                shadow_y: 2,
                glow_enabled: false,
                bg_mode: "none",
                bg_opacity: 0,
                animation: "pop",
                text_case: "normal"
            }
        },
        {
            id: "vlog_clean_pop",
            name: "Vlog Clean Pop",
            category: "Vlog",
            style: {
                font_family: "Poppins",
                font_weight: 800,
                font_size: 42,
                text_color: "#FFFFFF",
                active_word_color: "#38BDF8",
                stroke_enabled: true,
                stroke_color: "#000000",
                stroke_width: 2.5,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 5,
                shadow_y: 2,
                bg_mode: "semi",
                bg_color: "#0F172A",
                bg_opacity: 60,
                bg_radius: 12,
                bg_padding: 10,
                animation: "pop",
                text_case: "normal"
            }
        },
        {
            id: "action_pop_hormozi",
            name: "Action Pop / Hormozi",
            category: "High-Energy",
            style: {
                font_family: "Montserrat",
                font_weight: 900,
                font_size: 46,
                text_color: "#FFFFFF",
                active_word_color: "#22C55E",
                stroke_enabled: true,
                stroke_color: "#000000",
                stroke_width: 4,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 8,
                shadow_y: 4,
                bg_mode: "none",
                animation: "bounce",
                text_case: "uppercase"
            }
        },
        {
            id: "neon_pulse",
            name: "Neon Pulse",
            category: "Vibrant",
            style: {
                font_family: "Bebas Neue",
                font_weight: 800,
                font_size: 48,
                text_color: "#00FFCC",
                active_word_color: "#FF007F",
                stroke_enabled: true,
                stroke_color: "#000000",
                stroke_width: 2,
                shadow_enabled: true,
                shadow_color: "#00FFCC",
                shadow_blur: 14,
                shadow_y: 0,
                glow_enabled: true,
                glow_color: "#00FFCC",
                glow_intensity: 16,
                bg_mode: "none",
                animation: "pop",
                text_case: "uppercase"
            }
        },
        {
            id: "cyber_red",
            name: "Cyber Red",
            category: "Cyber",
            style: {
                font_family: "Oswald",
                font_weight: 800,
                font_size: 46,
                text_color: "#FFFFFF",
                active_word_color: "#EF4444",
                stroke_enabled: true,
                stroke_color: "#7F1D1D",
                stroke_width: 3,
                shadow_enabled: true,
                shadow_color: "#EF4444",
                shadow_blur: 10,
                shadow_y: 2,
                glow_enabled: true,
                glow_color: "#EF4444",
                glow_intensity: 12,
                bg_mode: "none",
                animation: "pop",
                text_case: "uppercase"
            }
        },
        {
            id: "minimal_trendy",
            name: "Minimal Trendy",
            category: "Clean",
            style: {
                font_family: "DM Sans",
                font_weight: 700,
                font_size: 36,
                text_color: "#F8FAFC",
                active_word_color: "#F59E0B",
                stroke_enabled: false,
                stroke_width: 0,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 4,
                shadow_y: 2,
                bg_mode: "none",
                animation: "fade_in",
                text_case: "normal"
            }
        },
        {
            id: "typewriter_retro",
            name: "Typewriter Retro",
            category: "Retro",
            style: {
                font_family: "Fira Code",
                font_weight: 700,
                font_size: 34,
                text_color: "#E2E8F0",
                active_word_color: "#10B981",
                stroke_enabled: false,
                stroke_width: 0,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 4,
                shadow_y: 1,
                bg_mode: "semi",
                bg_color: "#0F172A",
                bg_opacity: 85,
                bg_radius: 6,
                bg_padding: 8,
                animation: "typewriter",
                text_case: "normal"
            }
        },
        {
            id: "impact_yellow_punch",
            name: "Impact Yellow Punch",
            category: "High-Energy",
            style: {
                font_family: "Anton",
                font_weight: 900,
                font_size: 48,
                text_color: "#FFFFFF",
                active_word_color: "#FACC15",
                stroke_enabled: true,
                stroke_color: "#000000",
                stroke_width: 4,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 8,
                shadow_y: 3,
                bg_mode: "none",
                animation: "bounce",
                text_case: "uppercase"
            }
        },
        {
            id: "gradient_dream",
            name: "Gradient Dream",
            category: "Creative",
            style: {
                font_family: "Plus Jakarta Sans",
                font_weight: 800,
                font_size: 42,
                text_color: "#FFFFFF",
                active_word_color: "#EC4899",
                stroke_enabled: true,
                stroke_color: "#1E1B4B",
                stroke_width: 2.5,
                shadow_enabled: true,
                shadow_color: "#8B5CF6",
                shadow_blur: 10,
                shadow_y: 2,
                glow_enabled: true,
                glow_color: "#A855F7",
                glow_intensity: 10,
                bg_mode: "none",
                animation: "pop",
                text_case: "normal"
            }
        },
        {
            id: "underline_slide",
            name: "Underline Slide",
            category: "Modern",
            style: {
                font_family: "Outfit",
                font_weight: 700,
                font_size: 38,
                text_color: "#FFFFFF",
                active_word_color: "#3B82F6",
                stroke_enabled: true,
                stroke_color: "#000000",
                stroke_width: 1.5,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 4,
                shadow_y: 2,
                bg_mode: "none",
                animation: "slide_up",
                text_case: "normal"
            }
        },
        {
            id: "beast_high_energy",
            name: "Beast High-Energy",
            category: "High-Energy",
            style: {
                font_family: "Arial Black",
                font_weight: 900,
                font_size: 50,
                text_color: "#FFE600",
                active_word_color: "#FF0055",
                stroke_enabled: true,
                stroke_color: "#000000",
                stroke_width: 5,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 10,
                shadow_y: 4,
                bg_mode: "none",
                animation: "bounce",
                text_case: "uppercase"
            }
        },
        {
            id: "karaoke_smooth_fill",
            name: "Karaoke Smooth Fill",
            category: "Karaoke",
            style: {
                font_family: "Inter",
                font_weight: 800,
                font_size: 42,
                text_color: "#94A3B8",
                active_word_color: "#FFFFFF",
                stroke_enabled: true,
                stroke_color: "#0F172A",
                stroke_width: 2.5,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 6,
                shadow_y: 2,
                bg_mode: "none",
                animation: "karaoke",
                text_case: "normal"
            }
        },
        {
            id: "boxed_highlight",
            name: "Boxed Highlight",
            category: "Highlight",
            style: {
                font_family: "Work Sans",
                font_weight: 800,
                font_size: 38,
                text_color: "#000000",
                active_word_color: "#DC2626",
                stroke_enabled: false,
                stroke_width: 0,
                shadow_enabled: false,
                bg_mode: "solid",
                bg_color: "#FDE047",
                bg_opacity: 100,
                bg_radius: 6,
                bg_padding: 10,
                animation: "pop",
                text_case: "uppercase"
            }
        },
        {
            id: "subtle_luxury",
            name: "Subtle Luxury",
            category: "Luxury",
            style: {
                font_family: "Playfair Display",
                font_weight: 800,
                font_size: 38,
                text_color: "#FFFDF7",
                active_word_color: "#D97706",
                stroke_enabled: true,
                stroke_color: "#18181B",
                stroke_width: 1.5,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 4,
                shadow_y: 2,
                letter_spacing: 2,
                bg_mode: "none",
                animation: "fade_in",
                text_case: "normal"
            }
        },
        {
            id: "tiktok_classic",
            name: "TikTok Classic",
            category: "Social",
            style: {
                font_family: "Poppins",
                font_weight: 800,
                font_size: 44,
                text_color: "#FFFFFF",
                active_word_color: "#25F4EE",
                stroke_enabled: true,
                stroke_color: "#000000",
                stroke_width: 3,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 6,
                shadow_y: 3,
                bg_mode: "none",
                animation: "pop",
                text_case: "normal"
            }
        },
        {
            id: "comic_stomp",
            name: "Comic Stomp",
            category: "Fun",
            style: {
                font_family: "Bricolage Grotesque",
                font_weight: 800,
                font_size: 46,
                text_color: "#FFFFFF",
                active_word_color: "#FEF08A",
                stroke_enabled: true,
                stroke_color: "#18181B",
                stroke_width: 3.5,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 6,
                shadow_y: 3,
                bg_mode: "none",
                animation: "bounce",
                text_case: "normal"
            }
        },
        {
            id: "glitch_active",
            name: "Glitch Active",
            category: "Cyber",
            style: {
                font_family: "Rubik",
                font_weight: 900,
                font_size: 44,
                text_color: "#00FFFF",
                active_word_color: "#FF0055",
                stroke_enabled: true,
                stroke_color: "#000000",
                stroke_width: 3,
                shadow_enabled: true,
                shadow_color: "#FF0055",
                shadow_blur: 8,
                shadow_y: 2,
                glow_enabled: true,
                glow_color: "#00FFFF",
                glow_intensity: 12,
                bg_mode: "none",
                animation: "pop",
                text_case: "uppercase"
            }
        },
        {
            id: "clean_corporate",
            name: "Clean Corporate",
            category: "Corporate",
            style: {
                font_family: "Manrope",
                font_weight: 700,
                font_size: 34,
                text_color: "#FFFFFF",
                active_word_color: "#10B981",
                stroke_enabled: false,
                stroke_width: 0,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 3,
                shadow_y: 1,
                bg_mode: "semi",
                bg_color: "#1F2937",
                bg_opacity: 75,
                bg_radius: 8,
                bg_padding: 10,
                animation: "fade_in",
                text_case: "normal"
            }
        },
        {
            id: "dual_tone",
            name: "Dual Tone",
            category: "Modern",
            style: {
                font_family: "Space Grotesk",
                font_weight: 700,
                font_size: 40,
                text_color: "#E0E7FF",
                active_word_color: "#F43F5E",
                stroke_enabled: true,
                stroke_color: "#1E1B4B",
                stroke_width: 2,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 5,
                shadow_y: 2,
                bg_mode: "none",
                animation: "pop",
                text_case: "normal"
            }
        },
        {
            id: "cinematic_fade",
            name: "Cinematic Fade",
            category: "Cinematic",
            style: {
                font_family: "Merriweather",
                font_weight: 700,
                font_size: 34,
                text_color: "#FFF7E8",
                active_word_color: "#FDE68A",
                stroke_enabled: true,
                stroke_color: "#000000",
                stroke_width: 1.5,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 4,
                shadow_y: 2,
                bg_mode: "none",
                animation: "fade_in",
                text_case: "normal"
            }
        }
    ];

    // ==========================================================================
    // 3. CAPTION STUDIO STATE ENGINE
    // ==========================================================================
    class CaptionStudioEngine {
        constructor() {
            // Core project data
            this.projectId = "";
            this.project = null;
            this.videoFile = null;
            this.videoFileName = "";
            this.videoUrl = "";
            this.videoDuration = 0.0;
            this.videoWidth = 1080;
            this.videoHeight = 1920;

            // Canvas & aspect ratio settings (Default 9:16 Vertical Shorts)
            this.aspectRatio = "9:16";
            this.safeGuidesVisible = true;

            // Transform Modes & Video Pan/Zoom
            this.transformMode = "caption"; // "caption" | "video"
            this.videoZoom = 1.0;
            this.panX = 0;
            this.panY = 0;
            this.captionScale = 1.0; // Separate caption scale (0.50 to 2.50)

            // Three-column inspector tab mode
            this.activeColumnTab = "all";
            this.customPresets = [];

            // Caption Collection
            this.captions = [];
            this.selectedCaptionId = null;

            // Playback state
            this.currentTime = 0.0;
            this.isPlaying = false;
            this.volume = 1.0;
            this.isMuted = false;
            this.playbackRate = 1.0;

            // Timeline settings
            this.zoomPxPerSec = 40; // Pixels per second
            this.isDraggingPlayhead = false;
            this.activeTrimming = null;
            this.activeDraggingBlock = null;
            this.timelineDisplayMode = "line"; // "word" | "line"
            this.audioBuffer = null;

            // Canvas caption positioning drag state
            this.isDraggingCaption = false;
            this.dragStartX = 0;
            this.dragStartY = 0;
            this.initialPosX = 0;
            this.initialPosY = 0;

            // Active Style
            this.activeStyle = {
                font_family: "Inter",
                font_weight: 700,
                font_size: 42,
                letter_spacing: 0,
                line_height: 1.2,
                text_color: "#FFFFFF",
                text_opacity: 100,
                text_case: "normal",
                text_align: "center",
                is_bold: true,
                is_italic: false,
                is_underline: false,
                stroke_enabled: false,
                stroke_color: "#000000",
                stroke_width: 0,
                shadow_enabled: true,
                shadow_color: "#000000",
                shadow_blur: 4,
                shadow_y: 2,
                glow_enabled: false,
                glow_color: "#10B981",
                glow_intensity: 12,
                bg_mode: "none",
                bg_color: "#000000",
                bg_opacity: 0,
                bg_radius: 8,
                bg_padding: 12,
                pos_x: 0,
                pos_y: 240,
                animation: "pop",
                anim_duration: 250,
                karaoke_mode: "karaoke",
                active_word_color: "#10B981"
            };

            // History Stack (Undo/Redo)
            this.history = [];
            this.historyIndex = -1;
            this.isDirty = false;
            this.transcriptionTimer = null;

            // DOM Element References
            this.dom = {};

            this.init();
        }

        // ======================================================================
        // Initialization
        // ======================================================================
        init() {
            this.cacheDom();
            this.bindEvents();
            this.setupFontRegistry();
            this.setupPresetsCards();
            this.setupCustomPresets();
            this.setupVideoPanning();
            this.setupSidebar();
            this.setupCommandPalette();
            this.loadInitialContext();
            this.setAspectRatio("9:16");
            this.pushHistory("Initial State");
            this.renderCanvas();
            this.renderMiniTimelineList();
        }

        cacheDom() {
            this.dom.videoPlayer = document.getElementById("captionVideo") || document.getElementById("captionVideoPlayer");
            this.dom.previewBox = document.getElementById("previewCanvasBox");
            this.dom.canvasViewportLayer = document.getElementById("canvasViewportLayer");
            this.dom.videoPanZoomContainer = document.getElementById("videoPanZoomContainer");
            this.dom.captionDragBox = document.getElementById("captionDragBox");
            this.dom.captionTextDisplay = document.getElementById("captionOverlayText") || document.getElementById("captionTextDisplay");
            this.dom.canvasSafeGuides = document.getElementById("canvasSafeGuides");
            this.dom.guideCenterV = document.getElementById("guideCenterV");
            this.dom.guideCenterH = document.getElementById("guideCenterH");
            this.dom.emptyState = document.getElementById("captionEmptyState");

            // Transform mode & video zoom
            this.dom.modeCaptionBtn = document.getElementById("modeCaptionBtn");
            this.dom.modeVideoBtn = document.getElementById("modeVideoBtn");
            this.dom.videoZoomSelect = document.getElementById("videoZoomSelect");
            this.dom.resetPanBtn = document.getElementById("resetPanBtn");

            // Header controls
            this.dom.projectNameText = document.getElementById("projectNameText");
            this.dom.saveStatus = document.getElementById("saveStatus");
            this.dom.dirtyIndicator = document.getElementById("dirtyIndicator");
            this.dom.undoBtn = document.getElementById("undoBtn");
            this.dom.redoBtn = document.getElementById("redoBtn");
            this.dom.importVideoTopBtn = document.getElementById("importVideoTopBtn");
            this.dom.importCaptionsTopBtn = document.getElementById("importCaptionsTopBtn");
            this.dom.generateCaptionsTopBtn = document.getElementById("generateCaptionsTopBtn");
            this.dom.generateBtnText = document.getElementById("generateBtnText");
            this.dom.exportVideoTopBtn = document.getElementById("exportVideoTopBtn");

            // Canvas tools
            this.dom.canvasAspectSelect = document.getElementById("canvasAspectSelect");
            this.dom.canvasResolutionBadge = document.getElementById("canvasResolutionBadge");
            this.dom.toggleSafeGuidesBtn = document.getElementById("toggleSafeGuidesBtn");
            this.dom.centerCaptionBtn = document.getElementById("centerCaptionBtn");

            // Transport controls
            this.dom.playPauseBtn = document.getElementById("playPauseBtn");
            this.dom.playIcon = document.getElementById("playIcon");
            this.dom.pauseIcon = document.getElementById("pauseIcon");
            this.dom.playPauseIcon = document.getElementById("playPauseIcon");
            this.dom.prevFrameBtn = document.getElementById("skipBackBtn") || document.getElementById("prevFrameBtn");
            this.dom.nextFrameBtn = document.getElementById("skipFwdBtn") || document.getElementById("nextFrameBtn");
            this.dom.currentTimeReadout = document.getElementById("currentTimeDisplay") || document.getElementById("currentTimeReadout");
            this.dom.totalDurationReadout = document.getElementById("totalTimeDisplay") || document.getElementById("totalDurationReadout");
            this.dom.muteBtn = document.getElementById("muteBtn");
            this.dom.volIcon = document.getElementById("volIcon");
            this.dom.muteIcon = document.getElementById("muteIcon");
            this.dom.volumeSlider = document.getElementById("volumeSlider");
            this.dom.playbackSpeedSelect = document.getElementById("playbackSpeedSelect");
            this.dom.fullscreenBtn = document.getElementById("fullscreenBtn");

            // Timeline
            this.dom.timelineScrollArea = document.getElementById("timelineScrollArea");
            this.dom.timelineTracksContent = document.getElementById("timelineTracksContent");
            this.dom.timelineRulerCanvas = document.getElementById("timelineRulerCanvas");
            this.dom.timelinePlayheadLine = document.getElementById("timelinePlayheadLine");
            this.dom.playheadScrubberHandle = document.getElementById("playheadScrubberHandle");
            this.dom.captionTrackLane = document.getElementById("captionTrackLane");
            this.dom.timelineZoomSlider = document.getElementById("timelineZoomSlider");
            this.dom.addCaptionBtn = document.getElementById("addCaptionBtn");
            this.dom.splitCaptionBtn = document.getElementById("splitCaptionBtn");
            this.dom.mergeCaptionBtn = document.getElementById("mergeCaptionBtn");
            this.dom.duplicateCaptionBtn = document.getElementById("duplicateCaptionBtn");
            this.dom.deleteCaptionBtn = document.getElementById("deleteCaptionBtn");
            this.dom.autoSplitCaptionsBtn = document.getElementById("autoSplitCaptionsBtn");

            // Three Column Inspector container & Tab Switcher
            this.dom.captionInspectorContainer = document.getElementById("captionInspectorContainer");
            this.dom.colTabBtns = document.querySelectorAll(".col-tab-btn");

            // Column 1: Presets
            this.dom.presetsCardsGrid = document.getElementById("presetsCardsGrid");
            this.dom.presetSearchInput = document.getElementById("presetSearchInput");
            this.dom.customPresetsList = document.getElementById("customPresetsList");
            this.dom.openCustomPresetModalBtn = document.getElementById("openCustomPresetModalBtn");

            // Column 2: Accordions & Settings
            this.dom.expandAllAccordionsBtn = document.getElementById("expandAllAccordionsBtn");
            this.dom.collapseAllAccordionsBtn = document.getElementById("collapseAllAccordionsBtn");
            this.dom.captionTextareaInput = document.getElementById("captionTextareaInput");
            this.dom.captionStartInput = document.getElementById("captionStartInput");
            this.dom.captionEndInput = document.getElementById("captionEndInput");
            this.dom.alignLeftBtn = document.getElementById("alignLeftBtn");
            this.dom.alignCenterBtn = document.getElementById("alignCenterBtn");
            this.dom.alignRightBtn = document.getElementById("alignRightBtn");
            this.dom.textCaseSelect = document.getElementById("textCaseSelect");
            this.dom.fontSearchInput = document.getElementById("fontSearchInput");
            this.dom.fontFamilySelect = document.getElementById("fontFamilySelect");
            this.dom.fontWeightSelect = document.getElementById("fontWeightSelect");
            this.dom.fontSizeRange = document.getElementById("fontSizeRange");
            this.dom.fontSizeNum = document.getElementById("fontSizeNum");
            this.dom.fontSizeDisplay = document.getElementById("fontSizeDisplay");
            this.dom.fontSizeDecBtn = document.getElementById("fontSizeDecBtn");
            this.dom.fontSizeIncBtn = document.getElementById("fontSizeIncBtn");
            this.dom.letterSpacingRange = document.getElementById("letterSpacingRange");
            this.dom.letterSpacingDisplay = document.getElementById("letterSpacingDisplay");
            this.dom.lineHeightRange = document.getElementById("lineHeightRange");
            this.dom.lineHeightDisplay = document.getElementById("lineHeightDisplay");
            this.dom.textColorPicker = document.getElementById("textColorPicker");
            this.dom.textColorHex = document.getElementById("textColorHex");
            this.dom.textOpacityRange = document.getElementById("textOpacityRange");
            this.dom.toggleBoldBtn = document.getElementById("toggleBoldBtn");
            this.dom.toggleItalicBtn = document.getElementById("toggleItalicBtn");
            this.dom.toggleUnderlineBtn = document.getElementById("toggleUnderlineBtn");
            this.dom.strokeToggle = document.getElementById("strokeToggle");
            this.dom.strokeColorPicker = document.getElementById("strokeColorPicker");
            this.dom.strokeWidthRange = document.getElementById("strokeWidthRange");
            this.dom.strokeWidthDisplay = document.getElementById("strokeWidthDisplay");
            this.dom.shadowToggle = document.getElementById("shadowToggle");
            this.dom.shadowColorPicker = document.getElementById("shadowColorPicker");
            this.dom.shadowBlurRange = document.getElementById("shadowBlurRange");
            this.dom.shadowBlurDisplay = document.getElementById("shadowBlurDisplay");
            this.dom.shadowYRange = document.getElementById("shadowYRange");
            this.dom.shadowYDisplay = document.getElementById("shadowYDisplay");
            this.dom.glowToggle = document.getElementById("glowToggle");
            this.dom.glowColorPicker = document.getElementById("glowColorPicker");
            this.dom.glowIntensityRange = document.getElementById("glowIntensityRange");
            this.dom.glowIntensityDisplay = document.getElementById("glowIntensityDisplay");
            this.dom.bgModeSelect = document.getElementById("bgModeSelect");
            this.dom.bgColorPicker = document.getElementById("bgColorPicker");
            this.dom.bgOpacityRange = document.getElementById("bgOpacityRange");
            this.dom.bgOpacityDisplay = document.getElementById("bgOpacityDisplay");
            this.dom.bgRadiusRange = document.getElementById("bgRadiusRange");
            this.dom.bgRadiusDisplay = document.getElementById("bgRadiusDisplay");
            this.dom.bgPaddingRange = document.getElementById("bgPaddingRange");
            this.dom.bgPaddingDisplay = document.getElementById("bgPaddingDisplay");
            this.dom.posXRange = document.getElementById("posXRange");
            this.dom.posXDisplay = document.getElementById("posXDisplay");
            this.dom.posYRange = document.getElementById("posYRange");
            this.dom.posYDisplay = document.getElementById("posYDisplay");
            this.dom.animationTypeSelect = document.getElementById("animationTypeSelect");
            this.dom.animDurationRange = document.getElementById("animDurationRange");
            this.dom.animDurationDisplay = document.getElementById("animDurationDisplay");
            this.dom.karaokeModeSelect = document.getElementById("karaokeModeSelect");
            this.dom.activeWordColorPicker = document.getElementById("activeWordColorPicker");
            this.dom.applyAllCaptionsBtn = document.getElementById("applyAllCaptionsBtn");

            // Column 3: Quick Inspector & Mini Timeline List
            this.dom.quickCaptionTextPreview = document.getElementById("quickCaptionTextPreview");
            this.dom.quickDurationBadge = document.getElementById("quickDurationBadge");
            this.dom.quickStartBadge = document.getElementById("quickStartBadge");
            this.dom.quickEndBadge = document.getElementById("quickEndBadge");
            this.dom.quickSplitBtn = document.getElementById("quickSplitBtn");
            this.dom.quickMergeBtn = document.getElementById("quickMergeBtn");
            this.dom.quickDuplicateBtn = document.getElementById("quickDuplicateBtn");
            this.dom.quickDeleteBtn = document.getElementById("quickDeleteBtn");
            this.dom.captionScaleSlider = document.getElementById("captionScaleSlider");
            this.dom.captionScaleDisplay = document.getElementById("captionScaleDisplay");
            this.dom.scaleChipBtns = document.querySelectorAll(".scale-chip-btn");
            this.dom.quickFontFamilySelect = document.getElementById("quickFontFamilySelect");
            this.dom.quickFontSizeNum = document.getElementById("quickFontSizeNum");
            this.dom.quickTextColorPicker = document.getElementById("quickTextColorPicker");
            this.dom.miniCaptionList = document.getElementById("miniCaptionList");
            this.dom.miniCaptionSearchInput = document.getElementById("miniCaptionSearchInput");
            this.dom.captionCountBadge = document.getElementById("captionCountBadge");

            // Hidden file pickers
            this.dom.videoFileInput = document.getElementById("videoFileInput");
            this.dom.captionFileInput = document.getElementById("captionFileInput");
            this.dom.emptyStateImportBtn = document.getElementById("emptyStateImportBtn");

            // Generate Modal (Whisper AI - Hinglish / Hindi / English)
            this.dom.generateCaptionsModal = document.getElementById("generateCaptionsModal");
            this.dom.generateModalCloseBtn = document.getElementById("generateModalCloseBtn");
            this.dom.genCancelBtn = document.getElementById("genCancelBtn");
            this.dom.genExecuteBtn = document.getElementById("genExecuteBtn");
            this.dom.genLoadingStatus = document.getElementById("genLoadingStatus");
            this.dom.genStatusText = document.getElementById("genStatusText");

            // Modals: Export
            this.dom.exportVideoModal = document.getElementById("exportVideoModal");
            this.dom.exportModalCloseBtn = document.getElementById("exportModalCloseBtn");
            this.dom.exportCancelBtn = document.getElementById("exportCancelBtn");
            this.dom.exportStartRenderBtn = document.getElementById("exportStartRenderBtn");
            this.dom.exportDownloadLinkBtn = document.getElementById("exportDownloadLinkBtn");
            this.dom.exportStatusPanel = document.getElementById("exportStatusPanel");
            this.dom.exportStatusText = document.getElementById("exportStatusText");
            this.dom.exportPercentText = document.getElementById("exportPercentText");
            this.dom.exportProgressBar = document.getElementById("exportProgressBar");
            this.dom.exportResolutionSelect = document.getElementById("exportResolutionSelect");
            this.dom.exportFpsSelect = document.getElementById("exportFpsSelect");
            this.dom.exportFormatSelect = document.getElementById("exportFormatSelect");
            this.dom.exportSrtOnlyBtn = document.getElementById("exportSrtOnlyBtn");
            this.dom.exportVttOnlyBtn = document.getElementById("exportVttOnlyBtn");
            this.dom.exportJsonOnlyBtn = document.getElementById("exportJsonOnlyBtn");

            // Search & Replace
            this.dom.searchReplaceModal = document.getElementById("searchReplaceModal");
            this.dom.searchReplaceCloseBtn = document.getElementById("searchReplaceCloseBtn");
            this.dom.openSearchReplaceBtn = document.getElementById("openSearchReplaceBtn");
            this.dom.srFindInput = document.getElementById("srFindInput");
            this.dom.srReplaceInput = document.getElementById("srReplaceInput");
            this.dom.srCaseCheck = document.getElementById("srCaseCheck");
            this.dom.srExecuteBtn = document.getElementById("srExecuteBtn");
            this.dom.srCancelBtn = document.getElementById("srCancelBtn");
            this.dom.srMatchesCount = document.getElementById("srMatchesCount");

            // Custom Preset
            this.dom.customPresetNameInput = document.getElementById("customPresetNameInput");
            this.dom.saveCustomPresetBtn = document.getElementById("saveCustomPresetBtn");
            this.dom.toastContainer = document.getElementById("toastContainer");

            // Command Palette (Ctrl + K) - Section 3.B
            this.dom.commandPaletteModal = document.getElementById("commandPaletteModal");
            this.dom.commandPaletteBtn = document.getElementById("commandPaletteBtn");
            this.dom.commandPaletteSearchInput = document.getElementById("commandPaletteSearchInput");
            this.dom.commandPaletteResultsList = document.getElementById("commandPaletteResultsList");

            // Transcription Waiting Animation Modal - Section 8
            this.dom.transcriptionWaitingModal = document.getElementById("transcriptionWaitingModal");
            this.dom.waitingStatusText = document.getElementById("waitingStatusText");
            this.dom.waitingProgressBar = document.getElementById("waitingProgressBar");
            this.dom.waitingPercentageText = document.getElementById("waitingPercentageText");
            this.dom.workflowLangSelect = document.getElementById("workflowLangSelect");

            // Reference-matched Workspace controls
            this.dom.timelineWaveformCanvas = document.getElementById("timelineWaveformCanvas");
            this.dom.modeWordBtn = document.getElementById("modeWordBtn");
            this.dom.modeLineBtn = document.getElementById("modeLineBtn");
            this.dom.tabBuiltInTemplates = document.getElementById("tabBuiltInTemplates");
            this.dom.tabMyPresets = document.getElementById("tabMyPresets");
            this.dom.myPresetsSection = document.getElementById("myPresetsSection");
            this.dom.fillSolidBtn = document.getElementById("fillSolidBtn");
            this.dom.fillGradientBtn = document.getElementById("fillGradientBtn");
            this.dom.styleTitleCaseBtn = document.getElementById("styleTitleCaseBtn");
            this.dom.styleUpperCaseBtn = document.getElementById("styleUpperCaseBtn");
            this.dom.styleLowerCaseBtn = document.getElementById("styleLowerCaseBtn");
            this.dom.posXPercentNum = document.getElementById("posXPercentNum");
            this.dom.posYPercentNum = document.getElementById("posYPercentNum");
            this.dom.startOfflineGenerateBtn = document.getElementById("startOfflineGenerateBtn");
            this.dom.panelAiSettings = document.getElementById("panelAiSettings");
            this.dom.offlineAiModelSelect = document.getElementById("offlineAiModelSelect");
            this.dom.offlineLanguageSelect = document.getElementById("offlineLanguageSelect");
        }

        // ======================================================================
        // Left Sidebar Collapse & Navigation
        // ======================================================================
        setupSidebar() {
            const toggle = document.getElementById("sidebarToggle");
            const sidebar = document.getElementById("appSidebar");
            if (toggle && sidebar) {
                toggle.addEventListener("click", () => {
                    sidebar.classList.toggle("collapsed");
                    const isCollapsed = sidebar.classList.contains("collapsed");
                    localStorage.setItem("flip_sidebar_collapsed", isCollapsed ? "1" : "0");
                });

                if (localStorage.getItem("flip_sidebar_collapsed") === "1") {
                    sidebar.classList.add("collapsed");
                }
            }

            const settingsBtn = document.getElementById("sidebarSettingsBtn");
            if (settingsBtn) {
                settingsBtn.addEventListener("click", (e) => {
                    e.preventDefault();
                    // Scroll to settings accordion or open search & replace
                    const settingsGroup = document.getElementById("accordionSettings");
                    if (settingsGroup) {
                        settingsGroup.classList.add("open");
                        settingsGroup.scrollIntoView({ behavior: "smooth", block: "center" });
                    }
                    this.showToast("Settings & Tools panel opened", "info");
                });
            }
        }

        // ======================================================================
        // Initial Context from Flask Template
        // ======================================================================
        loadInitialContext() {
            const contextEl = document.getElementById("captionContextData");
            if (!contextEl) return;

            let preload = null;
            let project = null;
            let sourceFile = contextEl.getAttribute("data-source-file") || "";

            try {
                preload = JSON.parse(contextEl.getAttribute("data-preload") || "null");
                project = JSON.parse(contextEl.getAttribute("data-project") || "null");
            } catch (e) {
                console.warn("Context parse error:", e);
            }

            if (project) {
                this.project = project;
                this.projectId = project.id || "";
                if (project.name && this.dom.projectNameText) {
                    this.dom.projectNameText.textContent = project.name;
                }
            }

            if (preload && preload.video_url) {
                this.loadVideoSource(preload.video_url, preload.filename || sourceFile, preload.metadata);
            } else if (sourceFile) {
                const url = `/download/input/${encodeURIComponent(sourceFile)}`;
                this.loadVideoSource(url, sourceFile);
            }

            // Restore from localStorage if available
            this.restoreLocalAutosave();
        }

        // ======================================================================
        // Video Source Handling (Real Playback)
        // ======================================================================
        loadVideoSource(url, filename = "video.mp4", metadata = null) {
            this.videoUrl = url;
            this.videoFileName = filename;

            if (this.dom.videoPlayer) {
                this.dom.videoPlayer.src = url;
                this.dom.videoPlayer.load();
            }

            if (this.dom.emptyState) {
                this.dom.emptyState.style.display = "none";
            }

            if (this.dom.projectNameText && filename) {
                this.dom.projectNameText.textContent = filename.replace(/\.[^/.]+$/, "");
            }

            this.showToast(`Video loaded: ${filename}`, "success");
            this.extractAudioWaveform(url, null);
        }

        handleNativeVideoFile(file) {
            if (!file) return;

            const objectUrl = URL.createObjectURL(file);
            this.videoFile = file;
            this.videoFileName = file.name;
            this.loadVideoSource(objectUrl, file.name);
            this.extractAudioWaveform(objectUrl, file);

            // Upload in background to Flask server for AI processing & rendering
            const formData = new FormData();
            formData.append("video", file);
            if (this.projectId) formData.append("project_id", this.projectId);

            fetch("/upload/video", {
                method: "POST",
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.filename) {
                    this.videoFileName = data.filename;
                    if (data.project_id) this.projectId = data.project_id;
                    this.showToast("Video synchronized with server", "success");
                }
            })
            .catch(err => {
                console.warn("Background upload notice:", err);
            });
        }

        // ======================================================================
        // Audio Waveform Extraction & Canvas 2D Rendering
        // ======================================================================
        extractAudioWaveform(url, file = null) {
            try {
                const AudioCtx = window.AudioContext || window.webkitAudioContext;
                if (!AudioCtx) {
                    this.renderWaveform();
                    return;
                }
                const actx = new AudioCtx();
                const getBuf = file ? file.arrayBuffer() : fetch(url).then(r => r.arrayBuffer());
                getBuf.then(arrayBuf => {
                    actx.decodeAudioData(arrayBuf, (audioBuf) => {
                        this.audioBuffer = audioBuf;
                        this.renderWaveform();
                    }, (err) => {
                        console.warn("Waveform decode note:", err);
                        this.renderWaveform();
                    });
                }).catch(err => {
                    console.warn("Waveform buffer fetch error:", err);
                    this.renderWaveform();
                });
            } catch (e) {
                console.warn("AudioContext error:", e);
                this.renderWaveform();
            }
        }

        renderWaveform() {
            const canvas = this.dom.timelineWaveformCanvas;
            if (!canvas) return;

            const totalWidth = Math.max(1200, (this.videoDuration || 60) * this.zoomPxPerSec + 200);
            canvas.width = totalWidth;
            canvas.height = 52;

            const ctx = canvas.getContext("2d");
            if (!ctx) return;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const midY = canvas.height / 2;
            const barWidth = 3;
            const barGap = 2;
            const step = barWidth + barGap;
            const totalBars = Math.ceil(canvas.width / step);

            if (this.audioBuffer) {
                const channelData = this.audioBuffer.getChannelData(0);
                const sampleRate = this.audioBuffer.sampleRate;
                const duration = this.audioBuffer.duration || this.videoDuration || 60;
                const totalSamples = channelData.length;

                ctx.fillStyle = "#20E890";

                for (let i = 0; i < totalBars; i++) {
                    const x = i * step;
                    const timeAtX = x / this.zoomPxPerSec;
                    if (timeAtX > duration) break;

                    const sampleIdx = Math.floor((timeAtX / duration) * totalSamples);
                    const windowSize = Math.max(1, Math.floor((step / this.zoomPxPerSec) * (sampleRate / 2)));
                    let peak = 0;
                    for (let j = 0; j < windowSize && sampleIdx + j < totalSamples; j += 4) {
                        const val = Math.abs(channelData[sampleIdx + j]);
                        if (val > peak) peak = val;
                    }

                    const amp = Math.min(1.0, peak * 1.8);
                    const h = Math.max(4, amp * (canvas.height - 8));
                    const y = midY - h / 2;

                    ctx.beginPath();
                    if (ctx.roundRect) {
                        ctx.roundRect(x, y, barWidth, h, 2);
                    } else {
                        ctx.rect(x, y, barWidth, h);
                    }
                    ctx.fill();
                }
            } else {
                // Synthesize active waveform based on caption intervals & voice modulation
                ctx.fillStyle = "#20E890";
                for (let i = 0; i < totalBars; i++) {
                    const x = i * step;
                    const timeAtX = x / this.zoomPxPerSec;
                    if (this.videoDuration && timeAtX > this.videoDuration) break;

                    const inCaption = this.captions.some(c => timeAtX >= c.start && timeAtX <= c.end);
                    let amp = 0.12 + 0.08 * Math.sin(i * 0.3) + 0.05 * Math.cos(i * 0.7);

                    if (inCaption) {
                        const speechBurst = Math.abs(Math.sin(i * 0.8) * Math.cos(i * 0.4));
                        amp = 0.45 + speechBurst * 0.5;
                    }

                    const h = Math.max(4, amp * (canvas.height - 8));
                    const y = midY - h / 2;

                    ctx.beginPath();
                    if (ctx.roundRect) {
                        ctx.roundRect(x, y, barWidth, h, 2);
                    } else {
                        ctx.rect(x, y, barWidth, h);
                    }
                    ctx.fill();
                }
            }
        }

        // ======================================================================
        // Font Registry & Search
        // ======================================================================
        setupFontRegistry() {
            const selects = [this.dom.fontFamilySelect, this.dom.quickFontFamilySelect].filter(Boolean);
            if (!selects.length) return;

            const populateFonts = (query = "") => {
                const lower = query.toLowerCase().trim();
                const filtered = FONT_REGISTRY.filter(f => !lower || f.name.toLowerCase().includes(lower) || f.category.toLowerCase().includes(lower));

                selects.forEach(sel => {
                    sel.innerHTML = "";
                    filtered.forEach(font => {
                        const opt = document.createElement("option");
                        opt.value = font.id;
                        opt.textContent = `${font.name} (${font.category})`;
                        opt.style.fontFamily = `'${font.name}', sans-serif`;
                        if (font.id === this.activeStyle.font_family) {
                            opt.selected = true;
                        }
                        sel.appendChild(opt);
                    });
                });
            };

            populateFonts();

            if (this.dom.fontSearchInput) {
                this.dom.fontSearchInput.addEventListener("input", (e) => {
                    populateFonts(e.target.value);
                });
            }
        }

        // ======================================================================
        // 20 Preset Cards Rendering
        // ======================================================================
        // ======================================================================
        setupPresetsCards() {
            if (!this.dom.presetsCardsGrid) return;

            this.dom.presetsCardsGrid.innerHTML = "";

            PRESETS_REGISTRY.forEach(preset => {
                const card = document.createElement("div");
                const isDefaultActive = (preset.id === "action_pop_hormozi" || preset.id === "minimal_word_by_word");
                card.className = `preset-selector-card preset-visual-card ${isDefaultActive ? "active selected" : ""}`;
                card.setAttribute("data-preset-id", preset.id);

                const s = preset.style;
                const textStyle = `
                    font-family: '${s.font_family}', sans-serif;
                    font-weight: ${s.font_weight || 800};
                    color: ${s.text_color || '#FFFFFF'};
                    text-transform: ${s.text_case || 'normal'};
                    letter-spacing: ${s.letter_spacing || 0}px;
                    ${s.stroke_enabled ? `-webkit-text-stroke: 1.2px ${s.stroke_color || '#000'};` : ''}
                    ${s.shadow_enabled ? `text-shadow: 0 2px ${s.shadow_blur || 4}px ${s.shadow_color || '#000'};` : ''}
                `;

                let badgeClass = "badge-creator";
                const catLower = (preset.category || "").toLowerCase();
                if (catLower.includes("high") || catLower.includes("energy") || catLower.includes("viral")) {
                    badgeClass = "badge-viral";
                } else if (catLower.includes("clean") || catLower.includes("vlog")) {
                    badgeClass = "badge-clean";
                } else if (catLower.includes("cyber") || catLower.includes("neon")) {
                    badgeClass = "badge-cyber";
                } else if (catLower.includes("vibrant") || catLower.includes("pop")) {
                    badgeClass = "badge-pop";
                }

                card.innerHTML = `
                    <div class="preset-card-top-row">
                        <span class="preset-card-label">${preset.name}</span>
                        <span class="preset-card-badge ${badgeClass}">${preset.category || 'Preset'}</span>
                    </div>
                    <div class="preset-card-preview">
                        <div style="${textStyle}">
                            <span>UP</span> <span style="color:${s.active_word_color || '#10B981'}; font-weight:900;">CLIP</span>
                        </div>
                    </div>
                    <div class="preset-card-desc">${s.font_family || 'Inter'} • ${s.animation || 'Pop'}</div>
                `;

                card.addEventListener("click", () => {
                    this.applyPreset(preset);
                });

                this.dom.presetsCardsGrid.appendChild(card);
            });
        }

        applyPreset(preset) {
            document.querySelectorAll(".preset-selector-card, .preset-visual-card").forEach(c => {
                c.classList.remove("active");
                c.classList.remove("selected");
            });
            const card = document.querySelector(`[data-preset-id="${preset.id}"]`);
            if (card) {
                card.classList.add("active");
                card.classList.add("selected");
            }

            Object.assign(this.activeStyle, preset.style);
            this.syncInspectorInputs();
            this.renderCanvas();
            this.pushHistory(`Applied Preset: ${preset.name}`);
            this.showToast(`Applied preset: ${preset.name}`, "info");
        }

        // ======================================================================
        // Event Binding
        // ======================================================================
        bindEvents() {
            // Video element metadata & timeupdate
            if (this.dom.videoPlayer) {
                this.dom.videoPlayer.addEventListener("loadedmetadata", () => {
                    this.videoDuration = this.dom.videoPlayer.duration || 0;
                    this.videoWidth = this.dom.videoPlayer.videoWidth || 1920;
                    this.videoHeight = this.dom.videoPlayer.videoHeight || 1080;
                    this.updateResolutionBadge();
                    this.renderTimeline();
                    this.updateTimeReadouts();
                });

                this.dom.videoPlayer.addEventListener("timeupdate", () => {
                    if (!this.isDraggingPlayhead) {
                        this.currentTime = this.dom.videoPlayer.currentTime;
                        this.updatePlayheadPosition();
                        this.updateTimeReadouts();
                        this.renderActiveCaption();
                    }
                });

                this.dom.videoPlayer.addEventListener("play", () => {
                    this.isPlaying = true;
                    this.updatePlayPauseBtn(true);
                });

                this.dom.videoPlayer.addEventListener("pause", () => {
                    this.isPlaying = false;
                    this.updatePlayPauseBtn(false);
                });

                this.dom.videoPlayer.addEventListener("ended", () => {
                    this.isPlaying = false;
                    this.updatePlayPauseBtn(false);
                });
            }

            // Transport Buttons
            if (this.dom.playPauseBtn) {
                this.dom.playPauseBtn.addEventListener("click", () => this.togglePlayPause());
            }
            if (this.dom.prevFrameBtn) {
                this.dom.prevFrameBtn.addEventListener("click", () => this.seekBy(-5.0));
            }
            if (this.dom.nextFrameBtn) {
                this.dom.nextFrameBtn.addEventListener("click", () => this.seekBy(5.0));
            }

            // Close Column 3 Button (Cut Button)
            const closeCol3Btn = document.getElementById("closeCol3Btn");
            if (closeCol3Btn) {
                closeCol3Btn.addEventListener("click", () => this.closeColumn3());
            }

            // Setup real-time Manual Cue Editor listeners
            this.setupManualCueEditorListeners();
            if (this.dom.muteBtn) {
                this.dom.muteBtn.addEventListener("click", () => this.toggleMute());
            }
            if (this.dom.volumeSlider) {
                this.dom.volumeSlider.addEventListener("input", (e) => {
                    this.setVolume(parseFloat(e.target.value) / 100);
                });
            }
            if (this.dom.playbackSpeedSelect) {
                this.dom.playbackSpeedSelect.addEventListener("change", (e) => {
                    this.setPlaybackSpeed(parseFloat(e.target.value));
                });
            }
            if (this.dom.fullscreenBtn) {
                this.dom.fullscreenBtn.addEventListener("click", () => this.toggleFullscreen());
            }

            // Canvas Tools (Aspect ratio & Safe Guides)
            if (this.dom.canvasAspectSelect) {
                this.dom.canvasAspectSelect.addEventListener("change", (e) => {
                    this.setAspectRatio(e.target.value);
                });
            }
            if (this.dom.toggleSafeGuidesBtn) {
                this.dom.toggleSafeGuidesBtn.addEventListener("click", () => {
                    this.safeGuidesVisible = !this.safeGuidesVisible;
                    if (this.dom.canvasSafeGuides) {
                        this.dom.canvasSafeGuides.classList.toggle("active", this.safeGuidesVisible);
                    }
                });
            }
            if (this.dom.centerCaptionBtn) {
                this.dom.centerCaptionBtn.addEventListener("click", () => {
                    this.activeStyle.pos_x = 0;
                    this.activeStyle.pos_y = 240;
                    this.syncInspectorInputs();
                    this.renderCanvas();
                    this.pushHistory("Center Caption");
                });
            }

            // Transform Mode Switcher (Caption Mode vs Video Mode)
            if (this.dom.modeCaptionBtn) {
                this.dom.modeCaptionBtn.addEventListener("click", () => this.setTransformMode("caption"));
            }
            if (this.dom.modeVideoBtn) {
                this.dom.modeVideoBtn.addEventListener("click", () => this.setTransformMode("video"));
            }

            // Video Zoom & Pan Controls
            if (this.dom.videoZoomSelect) {
                this.dom.videoZoomSelect.addEventListener("change", (e) => {
                    const val = e.target.value;
                    if (val === "fit") {
                        this.videoZoom = 1.0;
                        this.panX = 0;
                        this.panY = 0;
                    } else if (val === "fill") {
                        this.videoZoom = 1.35;
                    } else {
                        this.videoZoom = parseFloat(val) || 1.0;
                    }
                    this.updateVideoTransform();
                });
            }
            if (this.dom.resetPanBtn) {
                this.dom.resetPanBtn.addEventListener("click", () => {
                    this.videoZoom = 1.0;
                    this.panX = 0;
                    this.panY = 0;
                    if (this.dom.videoZoomSelect) this.dom.videoZoomSelect.value = "fit";
                    this.updateVideoTransform();
                    this.showToast("Zoom & pan reset", "info");
                });
            }

            // Canvas Caption Dragging
            if (this.dom.captionDragBox) {
                this.setupCaptionCanvasDragging();
            }

            // Native File Pickers
            if (this.dom.importVideoTopBtn) {
                this.dom.importVideoTopBtn.addEventListener("click", () => this.dom.videoFileInput.click());
            }
            if (this.dom.emptyStateImportBtn) {
                this.dom.emptyStateImportBtn.addEventListener("click", () => this.dom.videoFileInput.click());
            }
            if (this.dom.videoFileInput) {
                this.dom.videoFileInput.addEventListener("change", (e) => {
                    const file = e.target.files && e.target.files[0];
                    if (file) this.handleNativeVideoFile(file);
                });
            }

            // Drag & Drop Video onto Empty State / Canvas
            const dropArea = document.getElementById("captionCanvasArea");
            if (dropArea) {
                ["dragenter", "dragover"].forEach(evt => {
                    dropArea.addEventListener(evt, (e) => {
                        e.preventDefault();
                        if (this.dom.emptyState) this.dom.emptyState.classList.add("dragover");
                    });
                });
                ["dragleave", "drop"].forEach(evt => {
                    dropArea.addEventListener(evt, (e) => {
                        e.preventDefault();
                        if (this.dom.emptyState) this.dom.emptyState.classList.remove("dragover");
                    });
                });
                dropArea.addEventListener("drop", (e) => {
                    const file = e.dataTransfer && e.dataTransfer.files[0];
                    if (file && file.type.startsWith("video/")) {
                        this.handleNativeVideoFile(file);
                    } else if (file && (file.name.endsWith(".srt") || file.name.endsWith(".vtt") || file.name.endsWith(".json"))) {
                        this.handleSubtitleFile(file);
                    }
                });
            }

            // Subtitle Import
            if (this.dom.importCaptionsTopBtn) {
                this.dom.importCaptionsTopBtn.addEventListener("click", () => this.dom.captionFileInput.click());
            }
            if (this.dom.captionFileInput) {
                this.dom.captionFileInput.addEventListener("change", (e) => {
                    const file = e.target.files && e.target.files[0];
                    if (file) this.handleSubtitleFile(file);
                });
            }

            // AI Caption Generation Trigger
            if (this.dom.generateCaptionsTopBtn) {
                this.dom.generateCaptionsTopBtn.addEventListener("click", () => {
                    this.openColumn3("ai");
                    const panelCol3 = document.getElementById("panelAiSettings") || this.dom.panelAiSettings;
                    if (panelCol3) {
                        panelCol3.scrollIntoView({ behavior: "smooth", block: "nearest" });
                        panelCol3.classList.add("highlight-panel");
                        setTimeout(() => panelCol3.classList.remove("highlight-panel"), 1200);
                    }
                });
            }
            if (this.dom.generateModalCloseBtn) {
                this.dom.generateModalCloseBtn.addEventListener("click", () => {
                    if (this.dom.generateCaptionsModal) this.dom.generateCaptionsModal.style.display = "none";
                });
            }
            if (this.dom.genCancelBtn) {
                this.dom.genCancelBtn.addEventListener("click", () => {
                    if (this.dom.generateCaptionsModal) this.dom.generateCaptionsModal.style.display = "none";
                });
            }
            if (this.dom.genExecuteBtn) {
                this.dom.genExecuteBtn.addEventListener("click", () => this.executeGenerateModalCaptions());
            }

            // Undo / Redo
            if (this.dom.undoBtn) {
                this.dom.undoBtn.addEventListener("click", () => this.undo());
            }
            if (this.dom.redoBtn) {
                this.dom.redoBtn.addEventListener("click", () => this.redo());
            }

            // Export Video Modal Trigger
            if (this.dom.exportVideoTopBtn) {
                this.dom.exportVideoTopBtn.addEventListener("click", () => this.openExportModal());
            }
            if (this.dom.exportModalCloseBtn) {
                this.dom.exportModalCloseBtn.addEventListener("click", () => this.closeExportModal());
            }
            if (this.dom.exportCancelBtn) {
                this.dom.exportCancelBtn.addEventListener("click", () => this.closeExportModal());
            }
            if (this.dom.exportStartRenderBtn) {
                this.dom.exportStartRenderBtn.addEventListener("click", () => this.startExportVideoRender());
            }

            // Subtitle raw exports
            if (this.dom.exportSrtOnlyBtn) {
                this.dom.exportSrtOnlyBtn.addEventListener("click", () => this.exportCaptionsOnly("srt"));
            }
            if (this.dom.exportVttOnlyBtn) {
                this.dom.exportVttOnlyBtn.addEventListener("click", () => this.exportCaptionsOnly("vtt"));
            }
            if (this.dom.exportJsonOnlyBtn) {
                this.dom.exportJsonOnlyBtn.addEventListener("click", () => this.exportCaptionsOnly("json"));
            }

            // Timeline Controls
            if (this.dom.addCaptionBtn) {
                this.dom.addCaptionBtn.addEventListener("click", () => this.addCaptionAtPlayhead());
            }
            if (this.dom.splitCaptionBtn) {
                this.dom.splitCaptionBtn.addEventListener("click", () => this.splitSelectedCaption());
            }
            if (this.dom.mergeCaptionBtn) {
                this.dom.mergeCaptionBtn.addEventListener("click", () => this.mergeSelectedCaption());
            }
            if (this.dom.duplicateCaptionBtn) {
                this.dom.duplicateCaptionBtn.addEventListener("click", () => this.duplicateSelectedCaption());
            }
            if (this.dom.deleteCaptionBtn) {
                this.dom.deleteCaptionBtn.addEventListener("click", () => this.deleteSelectedCaption());
            }
            if (this.dom.autoSplitCaptionsBtn) {
                this.dom.autoSplitCaptionsBtn.addEventListener("click", () => this.autoSplitCaptions());
            }
            if (this.dom.timelineZoomSlider) {
                this.dom.timelineZoomSlider.addEventListener("input", (e) => {
                    this.zoomPxPerSec = parseInt(e.target.value, 10);
                    this.renderTimeline();
                });
            }

            // Three Column Switcher (Presets | Settings | Inspector | All 3)
            if (this.dom.colTabBtns) {
                this.dom.colTabBtns.forEach(btn => {
                    btn.addEventListener("click", () => {
                        this.dom.colTabBtns.forEach(b => b.classList.remove("active"));
                        btn.classList.add("active");
                        const col = btn.getAttribute("data-col") || "all";
                        this.activeColumnTab = col;
                        if (this.dom.captionInspectorContainer) {
                            this.dom.captionInspectorContainer.setAttribute("data-active-tab", col);
                        }
                    });
                });
            }

            // Column 1: Preset Search Filter
            if (this.dom.presetSearchInput) {
                this.dom.presetSearchInput.addEventListener("input", (e) => {
                    const q = e.target.value.toLowerCase().trim();
                    document.querySelectorAll(".preset-selector-card").forEach(card => {
                        const title = card.querySelector(".preset-card-title")?.textContent.toLowerCase() || "";
                        card.style.display = (!q || title.includes(q)) ? "flex" : "none";
                    });
                });
            }

            // Column 1: Custom Preset Add Button
            if (this.dom.openCustomPresetModalBtn) {
                this.dom.openCustomPresetModalBtn.addEventListener("click", () => {
                    const name = prompt("Name your custom preset:", `Preset ${this.customPresets.length + 1}`);
                    if (name && name.trim()) {
                        this.saveCustomPresetByName(name.trim());
                    }
                });
            }

            // Column 2: Expand / Collapse All Accordions
            if (this.dom.expandAllAccordionsBtn) {
                this.dom.expandAllAccordionsBtn.addEventListener("click", () => {
                    document.querySelectorAll("#colSettings .accordion-group").forEach(g => g.classList.add("open"));
                    this.showToast("Expanded all settings panels", "info");
                });
            }
            if (this.dom.collapseAllAccordionsBtn) {
                this.dom.collapseAllAccordionsBtn.addEventListener("click", () => {
                    document.querySelectorAll("#colSettings .accordion-group").forEach(g => g.classList.remove("open"));
                    this.showToast("Collapsed all settings panels", "info");
                });
            }

            // Column 3: Quick Actions
            if (this.dom.quickSplitBtn) {
                this.dom.quickSplitBtn.addEventListener("click", () => this.splitSelectedCaption());
            }
            if (this.dom.quickMergeBtn) {
                this.dom.quickMergeBtn.addEventListener("click", () => this.mergeSelectedCaption());
            }
            if (this.dom.quickDuplicateBtn) {
                this.dom.quickDuplicateBtn.addEventListener("click", () => this.duplicateSelectedCaption());
            }
            if (this.dom.quickDeleteBtn) {
                this.dom.quickDeleteBtn.addEventListener("click", () => this.deleteSelectedCaption());
            }

            // Column 3: Caption Scale Slider & Chips
            if (this.dom.captionScaleSlider) {
                this.dom.captionScaleSlider.addEventListener("input", (e) => {
                    const scale = parseInt(e.target.value, 10) / 100;
                    this.setCaptionScale(scale);
                });
            }
            if (this.dom.scaleChipBtns) {
                this.dom.scaleChipBtns.forEach(btn => {
                    btn.addEventListener("click", () => {
                        const scale = parseFloat(btn.getAttribute("data-scale")) || 1.0;
                        this.setCaptionScale(scale);
                        if (this.dom.captionScaleSlider) {
                            this.dom.captionScaleSlider.value = Math.round(scale * 100);
                        }
                    });
                });
            }

            // Column 3: Quick Style Controls
            if (this.dom.quickFontFamilySelect) {
                this.dom.quickFontFamilySelect.addEventListener("change", (e) => {
                    this.activeStyle.font_family = e.target.value;
                    if (this.dom.fontFamilySelect) this.dom.fontFamilySelect.value = e.target.value;
                    this.renderCanvas();
                    this.pushHistory("Quick Font Family");
                });
            }
            if (this.dom.quickFontSizeNum) {
                this.dom.quickFontSizeNum.addEventListener("change", (e) => {
                    const sz = Math.max(12, Math.min(120, parseInt(e.target.value, 10) || 42));
                    this.activeStyle.font_size = sz;
                    if (this.dom.fontSizeRange) this.dom.fontSizeRange.value = sz;
                    if (this.dom.fontSizeNum) this.dom.fontSizeNum.value = sz;
                    if (this.dom.fontSizeDisplay) this.dom.fontSizeDisplay.textContent = sz;
                    this.renderCanvas();
                    this.pushHistory("Quick Font Size");
                });
            }
            if (this.dom.quickTextColorPicker) {
                this.dom.quickTextColorPicker.addEventListener("input", (e) => {
                    this.activeStyle.text_color = e.target.value;
                    if (this.dom.textColorPicker) this.dom.textColorPicker.value = e.target.value;
                    if (this.dom.textColorHex) this.dom.textColorHex.value = e.target.value.toUpperCase();
                    this.renderCanvas();
                });
                this.dom.quickTextColorPicker.addEventListener("change", () => this.pushHistory("Quick Text Color"));
            }

            // Column 3: Mini Timeline Filter
            if (this.dom.miniCaptionSearchInput) {
                this.dom.miniCaptionSearchInput.addEventListener("input", (e) => {
                    this.renderMiniTimelineList(e.target.value);
                });
            }

            // Timeline Scrubbing
            this.setupTimelineScrubbing();

            // Inspector Form Inputs
            this.bindInspectorFormInputs();

            // Accordion Toggles
            document.querySelectorAll(".accordion-header").forEach(header => {
                header.addEventListener("click", () => {
                    const group = header.closest(".accordion-group");
                    if (group) group.classList.toggle("open");
                });
            });

            // Search & Replace Modal
            if (this.dom.openSearchReplaceBtn) {
                this.dom.openSearchReplaceBtn.addEventListener("click", () => {
                    if (this.dom.searchReplaceModal) this.dom.searchReplaceModal.style.display = "flex";
                });
            }
            if (this.dom.searchReplaceCloseBtn) {
                this.dom.searchReplaceCloseBtn.addEventListener("click", () => {
                    if (this.dom.searchReplaceModal) this.dom.searchReplaceModal.style.display = "none";
                });
            }
            if (this.dom.srCancelBtn) {
                this.dom.srCancelBtn.addEventListener("click", () => {
                    if (this.dom.searchReplaceModal) this.dom.searchReplaceModal.style.display = "none";
                });
            }
            if (this.dom.srExecuteBtn) {
                this.dom.srExecuteBtn.addEventListener("click", () => this.executeSearchReplace());
            }

            // Custom Preset Save
            if (this.dom.saveCustomPresetBtn) {
                this.dom.saveCustomPresetBtn.addEventListener("click", () => this.saveCustomPreset());
            }

            // WORD / LINE Toggle Mode
            if (this.dom.modeWordBtn) {
                this.dom.modeWordBtn.addEventListener("click", () => {
                    this.timelineDisplayMode = "word";
                    this.dom.modeWordBtn.classList.add("active");
                    if (this.dom.modeLineBtn) this.dom.modeLineBtn.classList.remove("active");
                    this.renderTimeline();
                    this.showToast("Timeline mode: WORD", "info");
                });
            }
            if (this.dom.modeLineBtn) {
                this.dom.modeLineBtn.addEventListener("click", () => {
                    this.timelineDisplayMode = "line";
                    this.dom.modeLineBtn.classList.add("active");
                    if (this.dom.modeWordBtn) this.dom.modeWordBtn.classList.remove("active");
                    this.renderTimeline();
                    this.showToast("Timeline mode: LINE", "info");
                });
            }

            // Templates & Presets Tab Switcher (Built-in vs My Presets)
            if (this.dom.tabBuiltInTemplates) {
                this.dom.tabBuiltInTemplates.addEventListener("click", () => {
                    this.dom.tabBuiltInTemplates.classList.add("active");
                    if (this.dom.tabMyPresets) this.dom.tabMyPresets.classList.remove("active");
                    if (this.dom.presetsCardsGrid) this.dom.presetsCardsGrid.style.display = "grid";
                    if (this.dom.myPresetsSection) this.dom.myPresetsSection.style.display = "none";
                });
            }
            if (this.dom.tabMyPresets) {
                this.dom.tabMyPresets.addEventListener("click", () => {
                    this.dom.tabMyPresets.classList.add("active");
                    if (this.dom.tabBuiltInTemplates) this.dom.tabBuiltInTemplates.classList.remove("active");
                    if (this.dom.presetsCardsGrid) this.dom.presetsCardsGrid.style.display = "none";
                    if (this.dom.myPresetsSection) this.dom.myPresetsSection.style.display = "flex";
                    this.renderCustomPresetsList();
                });
            }

            // Text Fill: Solid vs Gradient
            if (this.dom.fillSolidBtn) {
                this.dom.fillSolidBtn.addEventListener("click", () => {
                    this.dom.fillSolidBtn.classList.add("active");
                    if (this.dom.fillGradientBtn) this.dom.fillGradientBtn.classList.remove("active");
                    this.activeStyle.bg_mode = "none";
                    this.renderCanvas();
                    this.pushHistory("Solid Fill Mode");
                });
            }
            if (this.dom.fillGradientBtn) {
                this.dom.fillGradientBtn.addEventListener("click", () => {
                    this.dom.fillGradientBtn.classList.add("active");
                    if (this.dom.fillSolidBtn) this.dom.fillSolidBtn.classList.remove("active");
                    this.activeStyle.bg_mode = "gradient";
                    this.renderCanvas();
                    this.pushHistory("Gradient Fill Mode");
                });
            }

            // Text Styles (Tt: TitleCase, T: UpperCase, t: LowerCase)
            if (this.dom.styleTitleCaseBtn) {
                this.dom.styleTitleCaseBtn.addEventListener("click", () => {
                    [this.dom.styleTitleCaseBtn, this.dom.styleUpperCaseBtn, this.dom.styleLowerCaseBtn].forEach(b => b && b.classList.remove("active"));
                    this.dom.styleTitleCaseBtn.classList.add("active");
                    this.activeStyle.text_case = "capitalize";
                    if (this.dom.textCaseSelect) this.dom.textCaseSelect.value = "capitalize";
                    this.renderCanvas();
                    this.pushHistory("Set Title Case");
                });
            }
            if (this.dom.styleUpperCaseBtn) {
                this.dom.styleUpperCaseBtn.addEventListener("click", () => {
                    [this.dom.styleTitleCaseBtn, this.dom.styleUpperCaseBtn, this.dom.styleLowerCaseBtn].forEach(b => b && b.classList.remove("active"));
                    this.dom.styleUpperCaseBtn.classList.add("active");
                    this.activeStyle.text_case = "uppercase";
                    if (this.dom.textCaseSelect) this.dom.textCaseSelect.value = "uppercase";
                    this.renderCanvas();
                    this.pushHistory("Set Upper Case");
                });
            }
            if (this.dom.styleLowerCaseBtn) {
                this.dom.styleLowerCaseBtn.addEventListener("click", () => {
                    [this.dom.styleTitleCaseBtn, this.dom.styleUpperCaseBtn, this.dom.styleLowerCaseBtn].forEach(b => b && b.classList.remove("active"));
                    this.dom.styleLowerCaseBtn.classList.add("active");
                    this.activeStyle.text_case = "lowercase";
                    if (this.dom.textCaseSelect) this.dom.textCaseSelect.value = "lowercase";
                    this.renderCanvas();
                    this.pushHistory("Set Lower Case");
                });
            }

            // Position Percentage inputs X: 50%, Y: 85%
            if (this.dom.posXPercentNum) {
                this.dom.posXPercentNum.addEventListener("input", (e) => {
                    const pct = parseFloat(e.target.value) || 50;
                    const posX = Math.round(((pct - 50) / 50) * 300);
                    this.activeStyle.pos_x = posX;
                    if (this.dom.posXRange) this.dom.posXRange.value = posX;
                    if (this.dom.posXDisplay) this.dom.posXDisplay.textContent = posX;
                    this.renderCanvas();
                });
                this.dom.posXPercentNum.addEventListener("change", () => this.pushHistory("Set X Position %"));
            }
            if (this.dom.posYPercentNum) {
                this.dom.posYPercentNum.addEventListener("input", (e) => {
                    const pct = parseFloat(e.target.value) || 85;
                    const posY = Math.round(((pct - 50) / 35) * 320);
                    this.activeStyle.pos_y = posY;
                    if (this.dom.posYRange) this.dom.posYRange.value = posY;
                    if (this.dom.posYDisplay) this.dom.posYDisplay.textContent = posY;
                    this.renderCanvas();
                });
                this.dom.posYPercentNum.addEventListener("change", () => this.pushHistory("Set Y Position %"));
            }

            // Offline AI Settings Generate Button
            if (this.dom.startOfflineGenerateBtn) {
                this.dom.startOfflineGenerateBtn.addEventListener("click", () => {
                    if (!this.videoFileName) {
                        this.showToast("Import a video first", "error");
                        return;
                    }
                    const lang = this.dom.offlineLanguageSelect ? this.dom.offlineLanguageSelect.value : "english";
                    this.generateAICaptions(lang);
                });
            }

            // Global Keyboard Shortcuts
            window.addEventListener("keydown", (e) => this.handleKeyboardShortcuts(e));
        }

        // ======================================================================
        // Transform Modes & Video Pan/Zoom
        // ======================================================================
        setTransformMode(mode) {
            this.transformMode = mode === "video" ? "video" : "caption";
            if (this.dom.modeCaptionBtn) {
                this.dom.modeCaptionBtn.classList.toggle("active", this.transformMode === "caption");
            }
            if (this.dom.modeVideoBtn) {
                this.dom.modeVideoBtn.classList.toggle("active", this.transformMode === "video");
            }
            if (this.dom.canvasViewportLayer) {
                this.dom.canvasViewportLayer.classList.toggle("mode-video", this.transformMode === "video");
                this.dom.canvasViewportLayer.classList.toggle("mode-caption", this.transformMode === "caption");
            }
            this.showToast(`Mode: ${this.transformMode === "video" ? "Video Pan & Zoom" : "Caption Transform"}`, "info");
        }

        setupVideoPanning() {
            const viewport = this.dom.canvasViewportLayer || this.dom.previewBox;
            if (!viewport) return;

            let isPanning = false;
            let startX = 0;
            let startY = 0;
            let initPanX = 0;
            let initPanY = 0;

            viewport.addEventListener("pointerdown", (e) => {
                if (this.transformMode !== "video") return;
                isPanning = true;
                viewport.classList.add("is-panning");
                startX = e.clientX;
                startY = e.clientY;
                initPanX = this.panX;
                initPanY = this.panY;

                const onMove = (me) => {
                    if (!isPanning) return;
                    this.panX = initPanX + (me.clientX - startX);
                    this.panY = initPanY + (me.clientY - startY);
                    this.updateVideoTransform();
                };

                const onUp = () => {
                    isPanning = false;
                    viewport.classList.remove("is-panning");
                    window.removeEventListener("pointermove", onMove);
                    window.removeEventListener("pointerup", onUp);
                };

                window.addEventListener("pointermove", onMove);
                window.addEventListener("pointerup", onUp);
            });
        }

        updateVideoTransform() {
            if (this.dom.videoPanZoomContainer) {
                this.dom.videoPanZoomContainer.style.transform = `translate(${this.panX}px, ${this.panY}px) scale(${this.videoZoom})`;
            }
        }

        setCaptionScale(scale) {
            this.captionScale = Math.max(0.5, Math.min(2.5, scale));
            if (this.dom.captionScaleDisplay) {
                this.dom.captionScaleDisplay.textContent = Math.round(this.captionScale * 100);
            }
            this.renderCanvas();
        }

        // ======================================================================
        // Custom Presets Management
        // ======================================================================
        setupCustomPresets() {
            try {
                const saved = localStorage.getItem("upclip_custom_caption_presets");
                if (saved) {
                    this.customPresets = JSON.parse(saved);
                }
            } catch (e) {
                this.customPresets = [];
            }
            this.renderCustomPresetsList();
        }

        renderCustomPresetsList() {
            if (!this.dom.customPresetsList) return;
            this.dom.customPresetsList.innerHTML = "";

            if (!this.customPresets || !this.customPresets.length) {
                this.dom.customPresetsList.innerHTML = `<div style="font-size:10px; color:var(--text-muted); font-style:italic;">No custom presets saved</div>`;
                return;
            }

            this.customPresets.forEach((p, idx) => {
                const item = document.createElement("div");
                item.style.display = "flex";
                item.style.alignItems = "center";
                item.style.justifyContent = "space-between";
                item.style.background = "var(--surface-2)";
                item.style.border = "1px solid var(--border)";
                item.style.borderRadius = "var(--radius-xs)";
                item.style.padding = "4px 8px";
                item.style.fontSize = "11px";
                item.style.cursor = "pointer";

                const left = document.createElement("div");
                left.style.display = "flex";
                left.style.alignItems = "center";
                left.style.gap = "6px";
                left.innerHTML = `
                    <span style="width:8px; height:8px; border-radius:50%; background:${p.style?.text_color || '#10B981'}; display:inline-block;"></span>
                    <span style="font-weight:600; color:var(--text-primary);">${this.escapeHtml(p.name)}</span>
                `;
                left.addEventListener("click", () => {
                    this.applyPreset(p);
                });

                const delBtn = document.createElement("button");
                delBtn.className = "btn btn-icon btn-xs";
                delBtn.style.color = "var(--text-muted)";
                delBtn.style.width = "18px";
                delBtn.style.height = "18px";
                delBtn.style.fontSize = "10px";
                delBtn.innerHTML = "✕";
                delBtn.title = "Delete custom preset";
                delBtn.addEventListener("click", (e) => {
                    e.stopPropagation();
                    this.customPresets.splice(idx, 1);
                    localStorage.setItem("upclip_custom_caption_presets", JSON.stringify(this.customPresets));
                    this.renderCustomPresetsList();
                    this.showToast(`Deleted preset: ${p.name}`, "info");
                });

                item.appendChild(left);
                item.appendChild(delBtn);
                this.dom.customPresetsList.appendChild(item);
            });
        }

        saveCustomPresetByName(name) {
            const newPreset = {
                id: `custom_${Date.now()}`,
                name: name,
                category: "Custom",
                style: JSON.parse(JSON.stringify(this.activeStyle))
            };

            this.customPresets.push(newPreset);
            localStorage.setItem("upclip_custom_caption_presets", JSON.stringify(this.customPresets));
            this.renderCustomPresetsList();
            this.showToast(`Saved custom preset: ${name}`, "success");
        }

        // ======================================================================
        // Column 3 Inspector & Mini Timeline List
        // ======================================================================
        updateColumn3Inspector(selected) {
            if (!selected) return;
            if (this.dom.quickCaptionTextPreview) {
                this.dom.quickCaptionTextPreview.textContent = selected.text || "(Empty caption)";
            }
            if (this.dom.quickDurationBadge) {
                this.dom.quickDurationBadge.textContent = `${(selected.end - selected.start).toFixed(2)}s`;
            }
            if (this.dom.quickStartBadge) {
                this.dom.quickStartBadge.textContent = this.formatTimecode(selected.start);
            }
            if (this.dom.quickEndBadge) {
                this.dom.quickEndBadge.textContent = this.formatTimecode(selected.end);
            }
            if (this.dom.quickFontFamilySelect && this.activeStyle.font_family) {
                this.dom.quickFontFamilySelect.value = this.activeStyle.font_family;
            }
            if (this.dom.quickFontSizeNum && this.activeStyle.font_size) {
                this.dom.quickFontSizeNum.value = this.activeStyle.font_size;
            }
            if (this.dom.quickTextColorPicker && this.activeStyle.text_color) {
                this.dom.quickTextColorPicker.value = this.activeStyle.text_color;
            }
        }

        formatTimecodeMs(seconds) {
            const totalMs = Math.max(0, Math.floor((seconds || 0) * 1000));
            const ms = String(totalMs % 1000).padStart(3, "0");
            const totalSec = Math.floor(totalMs / 1000);
            const s = String(totalSec % 60).padStart(2, "0");
            const m = String(Math.floor(totalSec / 60)).padStart(2, "0");
            return `${m}:${s}:${ms}`;
        }

        rebuildCaptionWords(cap) {
            if (!cap) return;
            const wordsList = (cap.text || "").split(/\s+/).filter(Boolean);
            if (wordsList.length === 0) {
                cap.words = [];
                return;
            }
            const totalDur = Math.max(0.1, (cap.end || 1) - (cap.start || 0));
            const durPerWord = totalDur / wordsList.length;
            cap.words = wordsList.map((w, idx) => ({
                text: w,
                word: w,
                start: parseFloat((cap.start + idx * durPerWord).toFixed(3)),
                end: parseFloat((cap.start + (idx + 1) * durPerWord).toFixed(3))
            }));
        }

        // ======================================================================
        // Word-Level Caption Editing Matrix (Section 7)
        // ======================================================================
        renderMiniTimelineList(query = "") {
            if (!this.dom.miniCaptionList) return;
            const container = this.dom.miniCaptionList;
            container.innerHTML = "";

            if (this.dom.captionCountBadge) {
                this.dom.captionCountBadge.textContent = `${this.captions.length} cues`;
            }

            const lower = query.toLowerCase().trim();
            const filtered = this.captions.filter(c => !lower || c.text.toLowerCase().includes(lower));

            if (filtered.length === 0) {
                container.innerHTML = `<div style="font-size:11px; color:var(--text-muted); text-align:center; padding:16px;">${this.captions.length === 0 ? "No captions added yet" : "No matching captions"}</div>`;
                return;
            }

            filtered.forEach((cap) => {
                const item = document.createElement("div");
                const isSelected = cap.id === this.selectedCaptionId;
                const isPlaying = this.currentTime >= cap.start && this.currentTime <= cap.end;

                item.className = `matrix-caption-row mini-caption-item ${isSelected ? "selected" : ""} ${isPlaying ? "is-active-playing" : ""}`;
                item.setAttribute("data-caption-id", cap.id);

                const timeBadgeText = `${this.formatTimecodeMs(cap.start)} → ${this.formatTimecodeMs(cap.end)}`;

                item.innerHTML = `
                    <button class="matrix-time-badge" type="button" title="Seek to ${this.formatTimecode(cap.start)}">
                        ${timeBadgeText}
                    </button>
                    <div class="matrix-inline-text" contenteditable="true" spellcheck="false" title="Click to edit caption text inline">
                        ${this.escapeHtml(cap.text)}
                    </div>
                    <div class="matrix-row-actions">
                        <button class="matrix-row-btn btn-split" type="button" title="Split Caption">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><line x1="20" y1="4" x2="8.12" y2="15.88"/></svg>
                        </button>
                        <button class="matrix-row-btn btn-duplicate" type="button" title="Duplicate Caption">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="14" x="8" y="8" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
                        </button>
                        <button class="matrix-row-btn btn-delete danger" type="button" title="Delete Caption">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                        </button>
                    </div>
                `;

                // Click badge to seek and select
                const timeBadge = item.querySelector(".matrix-time-badge");
                if (timeBadge) {
                    timeBadge.addEventListener("click", (e) => {
                        e.stopPropagation();
                        this.selectCaption(cap.id);
                        this.seekTo(cap.start);
                    });
                }

                // Inline editable text area
                const inlineText = item.querySelector(".matrix-inline-text");
                if (inlineText) {
                    inlineText.addEventListener("focus", () => {
                        this.selectCaption(cap.id);
                    });
                    inlineText.addEventListener("input", () => {
                        const newText = inlineText.innerText.trim();
                        cap.text = newText;
                        if (this.dom.captionTextareaInput && this.selectedCaptionId === cap.id) {
                            this.dom.captionTextareaInput.value = newText;
                        }
                        this.rebuildCaptionWords(cap);
                        this.renderCanvas();
                        this.debouncedServerSave();
                    });
                    inlineText.addEventListener("keydown", (e) => {
                        e.stopPropagation(); // stop player shortcuts
                        if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            inlineText.blur();
                        }
                    });
                }

                // Inline row actions
                const splitBtn = item.querySelector(".btn-split");
                if (splitBtn) {
                    splitBtn.addEventListener("click", (e) => {
                        e.stopPropagation();
                        this.selectCaption(cap.id);
                        this.splitSelectedCaption();
                    });
                }

                const dupBtn = item.querySelector(".btn-duplicate");
                if (dupBtn) {
                    dupBtn.addEventListener("click", (e) => {
                        e.stopPropagation();
                        this.selectCaption(cap.id);
                        this.duplicateSelectedCaption();
                    });
                }

                const delBtn = item.querySelector(".btn-delete");
                if (delBtn) {
                    delBtn.addEventListener("click", (e) => {
                        e.stopPropagation();
                        this.selectCaption(cap.id);
                        this.deleteSelectedCaption();
                    });
                }

                // Row click selects caption
                item.addEventListener("click", (e) => {
                    if (e.target.closest(".matrix-row-actions") || e.target.closest(".matrix-time-badge") || e.target.closest(".matrix-inline-text")) {
                        return;
                    }
                    this.selectCaption(cap.id);
                });

                container.appendChild(item);
            });
        }

        // ======================================================================
        // Draggable Caption Positioning on Video Canvas
        // ======================================================================
        setupCaptionCanvasDragging() {
            const dragBox = this.dom.captionDragBox;

            const onPointerDown = (e) => {
                if (this.transformMode !== "caption") return;
                if (e.target.tagName === "INPUT" || e.target.tagName === "BUTTON") return;
                this.isDraggingCaption = true;
                dragBox.classList.add("dragging");

                this.dragStartX = e.clientX;
                this.dragStartY = e.clientY;
                this.initialPosX = this.activeStyle.pos_x || 0;
                this.initialPosY = this.activeStyle.pos_y !== undefined ? this.activeStyle.pos_y : 240;

                window.addEventListener("pointermove", onPointerMove);
                window.addEventListener("pointerup", onPointerUp);
            };

            const onPointerMove = (e) => {
                if (!this.isDraggingCaption) return;

                const dx = e.clientX - this.dragStartX;
                const dy = e.clientY - this.dragStartY;

                let nextX = Math.round(this.initialPosX + dx);
                let nextY = Math.round(this.initialPosY + dy);

                // Magnetic snap to center (±16px threshold)
                let snapX = false;
                let snapY = false;

                if (Math.abs(nextX) < 16) {
                    nextX = 0;
                    snapX = true;
                }
                if (Math.abs(nextY) < 16) {
                    nextY = 0;
                    snapY = true;
                }

                // Show guidelines on snap
                if (this.dom.guideCenterV) {
                    this.dom.guideCenterV.classList.toggle("visible", snapX);
                }
                if (this.dom.guideCenterH) {
                    this.dom.guideCenterH.classList.toggle("visible", snapY);
                }

                this.activeStyle.pos_x = nextX;
                this.activeStyle.pos_y = nextY;

                // Sync X/Y in Inspector
                if (this.dom.posXRange) this.dom.posXRange.value = nextX;
                if (this.dom.posXDisplay) this.dom.posXDisplay.textContent = nextX;
                if (this.dom.posYRange) this.dom.posYRange.value = nextY;
                if (this.dom.posYDisplay) this.dom.posYDisplay.textContent = nextY;
                if (this.dom.posXPercentNum) {
                    const pctX = Math.max(0, Math.min(100, Math.round(50 + (nextX / 300) * 50)));
                    this.dom.posXPercentNum.value = pctX;
                }
                if (this.dom.posYPercentNum) {
                    const pctY = Math.max(0, Math.min(100, Math.round(50 + (nextY / 320) * 35)));
                    this.dom.posYPercentNum.value = pctY;
                }

                this.renderCanvas();
            };

            const onPointerUp = () => {
                if (!this.isDraggingCaption) return;
                this.isDraggingCaption = false;
                dragBox.classList.remove("dragging");

                if (this.dom.guideCenterV) this.dom.guideCenterV.classList.remove("visible");
                if (this.dom.guideCenterH) this.dom.guideCenterH.classList.remove("visible");

                window.removeEventListener("pointermove", onPointerMove);
                window.removeEventListener("pointerup", onPointerUp);

                this.pushHistory("Moved Caption Position");
            };

            dragBox.addEventListener("pointerdown", onPointerDown);
        }

        // ======================================================================
        // Inspector Form Input Bindings
        // ======================================================================
        bindInspectorFormInputs() {
            // Text Direct Edit
            if (this.dom.captionTextareaInput) {
                this.dom.captionTextareaInput.addEventListener("input", (e) => {
                    const selected = this.getSelectedCaption();
                    if (selected) {
                        selected.text = e.target.value;
                        this.recomputeWordsForCaption(selected);
                        this.renderCanvas();
                        this.renderTimeline();
                        this.markDirty();
                    }
                });
            }

            // Start & End Times
            if (this.dom.captionStartInput) {
                this.dom.captionStartInput.addEventListener("change", (e) => {
                    const selected = this.getSelectedCaption();
                    if (selected) {
                        const val = Math.max(0, parseFloat(e.target.value) || 0);
                        selected.start = val;
                        if (selected.end <= selected.start) selected.end = selected.start + 1.0;
                        this.captions.sort((a, b) => a.start - b.start);
                        this.renderTimeline();
                        this.pushHistory("Adjusted Caption Start Time");
                    }
                });
            }
            if (this.dom.captionEndInput) {
                this.dom.captionEndInput.addEventListener("change", (e) => {
                    const selected = this.getSelectedCaption();
                    if (selected) {
                        const val = Math.max(selected.start + 0.2, parseFloat(e.target.value) || selected.start + 1);
                        selected.end = val;
                        this.renderTimeline();
                        this.pushHistory("Adjusted Caption End Time");
                    }
                });
            }

            // Alignment buttons
            [this.dom.alignLeftBtn, this.dom.alignCenterBtn, this.dom.alignRightBtn].forEach(btn => {
                if (btn) {
                    btn.addEventListener("click", () => {
                        const align = btn.getAttribute("data-align");
                        [this.dom.alignLeftBtn, this.dom.alignCenterBtn, this.dom.alignRightBtn].forEach(b => b.classList.remove("active"));
                        btn.classList.add("active");
                        this.activeStyle.text_align = align;
                        this.renderCanvas();
                        this.pushHistory(`Set Alignment: ${align}`);
                    });
                }
            });

            // Text Case
            if (this.dom.textCaseSelect) {
                this.dom.textCaseSelect.addEventListener("change", (e) => {
                    this.activeStyle.text_case = e.target.value;
                    this.renderCanvas();
                    this.pushHistory("Set Text Case");
                });
            }

            // Font Family
            if (this.dom.fontFamilySelect) {
                this.dom.fontFamilySelect.addEventListener("change", (e) => {
                    this.activeStyle.font_family = e.target.value;
                    this.renderCanvas();
                    this.pushHistory(`Set Font: ${e.target.value}`);
                });
            }

            // Font Weight
            if (this.dom.fontWeightSelect) {
                this.dom.fontWeightSelect.addEventListener("change", (e) => {
                    this.activeStyle.font_weight = parseInt(e.target.value, 10);
                    this.renderCanvas();
                    this.pushHistory("Set Font Weight");
                });
            }

            // Font Size
            const updateFontSize = (val) => {
                const size = Math.max(12, Math.min(120, parseInt(val, 10) || 42));
                this.activeStyle.font_size = size;
                if (this.dom.fontSizeRange) this.dom.fontSizeRange.value = size;
                if (this.dom.fontSizeNum) this.dom.fontSizeNum.value = size;
                if (this.dom.fontSizeDisplay) this.dom.fontSizeDisplay.textContent = size;
                this.renderCanvas();
            };

            if (this.dom.fontSizeRange) {
                this.dom.fontSizeRange.addEventListener("input", (e) => updateFontSize(e.target.value));
                this.dom.fontSizeRange.addEventListener("change", () => this.pushHistory("Set Font Size"));
            }
            if (this.dom.fontSizeNum) {
                this.dom.fontSizeNum.addEventListener("change", (e) => {
                    updateFontSize(e.target.value);
                    this.pushHistory("Set Font Size");
                });
            }
            if (this.dom.fontSizeDecBtn) {
                this.dom.fontSizeDecBtn.addEventListener("click", () => {
                    updateFontSize(this.activeStyle.font_size - 2);
                    this.pushHistory("Decreased Font Size");
                });
            }
            if (this.dom.fontSizeIncBtn) {
                this.dom.fontSizeIncBtn.addEventListener("click", () => {
                    updateFontSize(this.activeStyle.font_size + 2);
                    this.pushHistory("Increased Font Size");
                });
            }

            // Tracking / Letter Spacing
            if (this.dom.letterSpacingRange) {
                this.dom.letterSpacingRange.addEventListener("input", (e) => {
                    this.activeStyle.letter_spacing = parseInt(e.target.value, 10);
                    if (this.dom.letterSpacingDisplay) this.dom.letterSpacingDisplay.textContent = e.target.value;
                    this.renderCanvas();
                });
                this.dom.letterSpacingRange.addEventListener("change", () => this.pushHistory("Set Letter Spacing"));
            }

            // Line Height
            if (this.dom.lineHeightRange) {
                this.dom.lineHeightRange.addEventListener("input", (e) => {
                    this.activeStyle.line_height = parseFloat(e.target.value);
                    if (this.dom.lineHeightDisplay) this.dom.lineHeightDisplay.textContent = e.target.value;
                    this.renderCanvas();
                });
                this.dom.lineHeightRange.addEventListener("change", () => this.pushHistory("Set Line Height"));
            }

            // Text Color & Hex & Opacity
            if (this.dom.textColorPicker) {
                this.dom.textColorPicker.addEventListener("input", (e) => {
                    this.activeStyle.text_color = e.target.value;
                    if (this.dom.textColorHex) this.dom.textColorHex.value = e.target.value.toUpperCase();
                    this.renderCanvas();
                });
                this.dom.textColorPicker.addEventListener("change", () => this.pushHistory("Set Text Color"));
            }
            if (this.dom.textColorHex) {
                this.dom.textColorHex.addEventListener("change", (e) => {
                    let val = e.target.value.trim();
                    if (!val.startsWith("#")) val = "#" + val;
                    if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
                        this.activeStyle.text_color = val;
                        if (this.dom.textColorPicker) this.dom.textColorPicker.value = val;
                        this.renderCanvas();
                        this.pushHistory("Set Text Color Hex");
                    }
                });
            }
            if (this.dom.textOpacityRange) {
                this.dom.textOpacityRange.addEventListener("input", (e) => {
                    this.activeStyle.text_opacity = parseInt(e.target.value, 10);
                    this.renderCanvas();
                });
            }

            // Quick color swatches
            document.querySelectorAll(".color-dot-swatch").forEach(swatch => {
                swatch.addEventListener("click", () => {
                    const color = swatch.getAttribute("data-color");
                    if (color) {
                        this.activeStyle.text_color = color;
                        if (this.dom.textColorPicker) this.dom.textColorPicker.value = color;
                        if (this.dom.textColorHex) this.dom.textColorHex.value = color.toUpperCase();
                        this.renderCanvas();
                        this.pushHistory("Applied Color Swatch");
                    }
                });
            });

            // Decorators (Bold, Italic, Underline)
            if (this.dom.toggleBoldBtn) {
                this.dom.toggleBoldBtn.addEventListener("click", () => {
                    this.activeStyle.is_bold = !this.activeStyle.is_bold;
                    this.dom.toggleBoldBtn.classList.toggle("active", this.activeStyle.is_bold);
                    this.renderCanvas();
                    this.pushHistory("Toggle Bold");
                });
            }
            if (this.dom.toggleItalicBtn) {
                this.dom.toggleItalicBtn.addEventListener("click", () => {
                    this.activeStyle.is_italic = !this.activeStyle.is_italic;
                    this.dom.toggleItalicBtn.classList.toggle("active", this.activeStyle.is_italic);
                    this.renderCanvas();
                    this.pushHistory("Toggle Italic");
                });
            }
            if (this.dom.toggleUnderlineBtn) {
                this.dom.toggleUnderlineBtn.addEventListener("click", () => {
                    this.activeStyle.is_underline = !this.activeStyle.is_underline;
                    this.dom.toggleUnderlineBtn.classList.toggle("active", this.activeStyle.is_underline);
                    this.renderCanvas();
                    this.pushHistory("Toggle Underline");
                });
            }

            // Stroke / Outline
            if (this.dom.strokeToggle) {
                this.dom.strokeToggle.addEventListener("change", (e) => {
                    this.activeStyle.stroke_enabled = e.target.checked;
                    this.renderCanvas();
                    this.pushHistory("Toggle Stroke");
                });
            }
            if (this.dom.strokeColorPicker) {
                this.dom.strokeColorPicker.addEventListener("input", (e) => {
                    this.activeStyle.stroke_color = e.target.value;
                    this.renderCanvas();
                });
            }
            if (this.dom.strokeWidthRange) {
                this.dom.strokeWidthRange.addEventListener("input", (e) => {
                    this.activeStyle.stroke_width = parseInt(e.target.value, 10);
                    if (this.dom.strokeWidthDisplay) this.dom.strokeWidthDisplay.textContent = e.target.value;
                    this.renderCanvas();
                });
                this.dom.strokeWidthRange.addEventListener("change", () => this.pushHistory("Set Stroke Width"));
            }

            // Shadow
            if (this.dom.shadowToggle) {
                this.dom.shadowToggle.addEventListener("change", (e) => {
                    this.activeStyle.shadow_enabled = e.target.checked;
                    this.renderCanvas();
                    this.pushHistory("Toggle Shadow");
                });
            }
            if (this.dom.shadowColorPicker) {
                this.dom.shadowColorPicker.addEventListener("input", (e) => {
                    this.activeStyle.shadow_color = e.target.value;
                    this.renderCanvas();
                });
            }
            if (this.dom.shadowBlurRange) {
                this.dom.shadowBlurRange.addEventListener("input", (e) => {
                    this.activeStyle.shadow_blur = parseInt(e.target.value, 10);
                    if (this.dom.shadowBlurDisplay) this.dom.shadowBlurDisplay.textContent = e.target.value;
                    this.renderCanvas();
                });
            }
            if (this.dom.shadowYRange) {
                this.dom.shadowYRange.addEventListener("input", (e) => {
                    this.activeStyle.shadow_y = parseInt(e.target.value, 10);
                    if (this.dom.shadowYDisplay) this.dom.shadowYDisplay.textContent = e.target.value;
                    this.renderCanvas();
                });
            }

            // Glow
            if (this.dom.glowToggle) {
                this.dom.glowToggle.addEventListener("change", (e) => {
                    this.activeStyle.glow_enabled = e.target.checked;
                    this.renderCanvas();
                    this.pushHistory("Toggle Glow");
                });
            }
            if (this.dom.glowColorPicker) {
                this.dom.glowColorPicker.addEventListener("input", (e) => {
                    this.activeStyle.glow_color = e.target.value;
                    this.renderCanvas();
                });
            }
            if (this.dom.glowIntensityRange) {
                this.dom.glowIntensityRange.addEventListener("input", (e) => {
                    this.activeStyle.glow_intensity = parseInt(e.target.value, 10);
                    if (this.dom.glowIntensityDisplay) this.dom.glowIntensityDisplay.textContent = e.target.value;
                    this.renderCanvas();
                });
            }

            // Background Mode & Box
            if (this.dom.bgModeSelect) {
                this.dom.bgModeSelect.addEventListener("change", (e) => {
                    this.activeStyle.bg_mode = e.target.value;
                    if (e.target.value === "none") {
                        this.activeStyle.bg_opacity = 0;
                    } else if (this.activeStyle.bg_opacity === 0) {
                        this.activeStyle.bg_opacity = 75;
                    }
                    if (this.dom.bgOpacityRange) this.dom.bgOpacityRange.value = this.activeStyle.bg_opacity;
                    if (this.dom.bgOpacityDisplay) this.dom.bgOpacityDisplay.textContent = `${this.activeStyle.bg_opacity}%`;
                    this.renderCanvas();
                    this.pushHistory("Set Background Style");
                });
            }
            if (this.dom.bgColorPicker) {
                this.dom.bgColorPicker.addEventListener("input", (e) => {
                    this.activeStyle.bg_color = e.target.value;
                    this.renderCanvas();
                });
            }
            if (this.dom.bgOpacityRange) {
                this.dom.bgOpacityRange.addEventListener("input", (e) => {
                    this.activeStyle.bg_opacity = parseInt(e.target.value, 10);
                    if (this.dom.bgOpacityDisplay) this.dom.bgOpacityDisplay.textContent = `${e.target.value}%`;
                    this.renderCanvas();
                });
            }
            if (this.dom.bgRadiusRange) {
                this.dom.bgRadiusRange.addEventListener("input", (e) => {
                    this.activeStyle.bg_radius = parseInt(e.target.value, 10);
                    if (this.dom.bgRadiusDisplay) this.dom.bgRadiusDisplay.textContent = e.target.value;
                    this.renderCanvas();
                });
            }
            if (this.dom.bgPaddingRange) {
                this.dom.bgPaddingRange.addEventListener("input", (e) => {
                    this.activeStyle.bg_padding = parseInt(e.target.value, 10);
                    if (this.dom.bgPaddingDisplay) this.dom.bgPaddingDisplay.textContent = e.target.value;
                    this.renderCanvas();
                });
            }

            // Position Presets Grid (9-point)
            document.querySelectorAll(".pos-grid-btn").forEach(btn => {
                btn.addEventListener("click", () => {
                    const pos = btn.getAttribute("data-pos");
                    document.querySelectorAll(".pos-grid-btn").forEach(b => b.classList.remove("active"));
                    btn.classList.add("active");

                    let targetX = 0;
                    let targetY = 0;

                    if (pos === "top-left") { targetX = -280; targetY = -180; }
                    else if (pos === "top-center") { targetX = 0; targetY = -180; }
                    else if (pos === "top-right") { targetX = 280; targetY = -180; }
                    else if (pos === "center-left") { targetX = -280; targetY = 0; }
                    else if (pos === "center") { targetX = 0; targetY = 0; }
                    else if (pos === "center-right") { targetX = 280; targetY = 0; }
                    else if (pos === "bottom-left") { targetX = -280; targetY = 160; }
                    else if (pos === "bottom-center") { targetX = 0; targetY = 160; }
                    else if (pos === "bottom-right") { targetX = 280; targetY = 160; }

                    this.activeStyle.pos_x = targetX;
                    this.activeStyle.pos_y = targetY;

                    if (this.dom.posXRange) this.dom.posXRange.value = targetX;
                    if (this.dom.posXDisplay) this.dom.posXDisplay.textContent = targetX;
                    if (this.dom.posYRange) this.dom.posYRange.value = targetY;
                    if (this.dom.posYDisplay) this.dom.posYDisplay.textContent = targetY;

                    this.renderCanvas();
                    this.pushHistory(`Set Position Preset: ${pos}`);
                });
            });

            // X and Y Slider Sliders
            if (this.dom.posXRange) {
                this.dom.posXRange.addEventListener("input", (e) => {
                    this.activeStyle.pos_x = parseInt(e.target.value, 10);
                    if (this.dom.posXDisplay) this.dom.posXDisplay.textContent = e.target.value;
                    this.renderCanvas();
                });
                this.dom.posXRange.addEventListener("change", () => this.pushHistory("Set X Position"));
            }
            if (this.dom.posYRange) {
                this.dom.posYRange.addEventListener("input", (e) => {
                    this.activeStyle.pos_y = parseInt(e.target.value, 10);
                    if (this.dom.posYDisplay) this.dom.posYDisplay.textContent = e.target.value;
                    this.renderCanvas();
                });
                this.dom.posYRange.addEventListener("change", () => this.pushHistory("Set Y Position"));
            }

            // Animation
            if (this.dom.animationTypeSelect) {
                this.dom.animationTypeSelect.addEventListener("change", (e) => {
                    this.activeStyle.animation = e.target.value;
                    this.renderCanvas();
                    this.pushHistory("Set Caption Animation");
                });
            }
            if (this.dom.animDurationRange) {
                this.dom.animDurationRange.addEventListener("input", (e) => {
                    this.activeStyle.anim_duration = parseInt(e.target.value, 10);
                    if (this.dom.animDurationDisplay) this.dom.animDurationDisplay.textContent = e.target.value;
                });
            }

            // Word-by-Word & Karaoke
            if (this.dom.karaokeModeSelect) {
                this.dom.karaokeModeSelect.addEventListener("change", (e) => {
                    this.activeStyle.karaoke_mode = e.target.value;
                    this.renderCanvas();
                    this.pushHistory("Set Karaoke Mode");
                });
            }
            if (this.dom.activeWordColorPicker) {
                this.dom.activeWordColorPicker.addEventListener("input", (e) => {
                    this.activeStyle.active_word_color = e.target.value;
                    this.renderCanvas();
                });
            }

            // Apply to All Captions
            if (this.dom.applyAllCaptionsBtn) {
                this.dom.applyAllCaptionsBtn.addEventListener("click", () => {
                    this.captions.forEach(c => {
                        c.style = JSON.parse(JSON.stringify(this.activeStyle));
                    });
                    this.pushHistory("Applied Style to All Captions");
                    this.showToast("Current style applied to all captions", "success");
                });
            }
        }

        // ======================================================================
        // Inspector Sync with State
        // ======================================================================
        syncInspectorInputs() {
            const s = this.activeStyle;
            if (this.dom.fontFamilySelect) this.dom.fontFamilySelect.value = s.font_family;
            if (this.dom.fontWeightSelect) this.dom.fontWeightSelect.value = String(s.font_weight || 700);
            if (this.dom.fontSizeRange) this.dom.fontSizeRange.value = s.font_size;
            if (this.dom.fontSizeNum) this.dom.fontSizeNum.value = s.font_size;
            if (this.dom.fontSizeDisplay) this.dom.fontSizeDisplay.textContent = s.font_size;
            if (this.dom.letterSpacingRange) this.dom.letterSpacingRange.value = s.letter_spacing || 0;
            if (this.dom.letterSpacingDisplay) this.dom.letterSpacingDisplay.textContent = s.letter_spacing || 0;
            if (this.dom.lineHeightRange) this.dom.lineHeightRange.value = s.line_height || 1.2;
            if (this.dom.lineHeightDisplay) this.dom.lineHeightDisplay.textContent = s.line_height || 1.2;
            if (this.dom.textColorPicker) this.dom.textColorPicker.value = s.text_color || "#FFFFFF";
            if (this.dom.textColorHex) this.dom.textColorHex.value = (s.text_color || "#FFFFFF").toUpperCase();
            if (this.dom.textOpacityRange) this.dom.textOpacityRange.value = s.text_opacity ?? 100;
            if (this.dom.textCaseSelect) this.dom.textCaseSelect.value = s.text_case || "normal";
            if (this.dom.strokeToggle) this.dom.strokeToggle.checked = !!s.stroke_enabled;
            if (this.dom.strokeColorPicker) this.dom.strokeColorPicker.value = s.stroke_color || "#000000";
            if (this.dom.strokeWidthRange) this.dom.strokeWidthRange.value = s.stroke_width || 0;
            if (this.dom.strokeWidthDisplay) this.dom.strokeWidthDisplay.textContent = s.stroke_width || 0;
            if (this.dom.shadowToggle) this.dom.shadowToggle.checked = !!s.shadow_enabled;
            if (this.dom.shadowColorPicker) this.dom.shadowColorPicker.value = s.shadow_color || "#000000";
            if (this.dom.shadowBlurRange) this.dom.shadowBlurRange.value = s.shadow_blur || 0;
            if (this.dom.shadowBlurDisplay) this.dom.shadowBlurDisplay.textContent = s.shadow_blur || 0;
            if (this.dom.shadowYRange) this.dom.shadowYRange.value = s.shadow_y || 0;
            if (this.dom.shadowYDisplay) this.dom.shadowYDisplay.textContent = s.shadow_y || 0;
            if (this.dom.glowToggle) this.dom.glowToggle.checked = !!s.glow_enabled;
            if (this.dom.glowColorPicker) this.dom.glowColorPicker.value = s.glow_color || "#10B981";
            if (this.dom.glowIntensityRange) this.dom.glowIntensityRange.value = s.glow_intensity || 12;
            if (this.dom.glowIntensityDisplay) this.dom.glowIntensityDisplay.textContent = s.glow_intensity || 12;
            if (this.dom.bgModeSelect) this.dom.bgModeSelect.value = s.bg_mode || "none";
            if (this.dom.bgColorPicker) this.dom.bgColorPicker.value = s.bg_color || "#000000";
            if (this.dom.bgOpacityRange) this.dom.bgOpacityRange.value = s.bg_opacity ?? 0;
            if (this.dom.bgOpacityDisplay) this.dom.bgOpacityDisplay.textContent = `${s.bg_opacity ?? 0}%`;
            if (this.dom.bgRadiusRange) this.dom.bgRadiusRange.value = s.bg_radius || 8;
            if (this.dom.bgRadiusDisplay) this.dom.bgRadiusDisplay.textContent = s.bg_radius || 8;
            if (this.dom.bgPaddingRange) this.dom.bgPaddingRange.value = s.bg_padding || 12;
            if (this.dom.bgPaddingDisplay) this.dom.bgPaddingDisplay.textContent = s.bg_padding || 12;
            if (this.dom.posXRange) this.dom.posXRange.value = s.pos_x || 0;
            if (this.dom.posXDisplay) this.dom.posXDisplay.textContent = s.pos_x || 0;
            if (this.dom.posYRange) this.dom.posYRange.value = s.pos_y || 160;
            if (this.dom.posYDisplay) this.dom.posYDisplay.textContent = s.pos_y || 160;
            if (this.dom.posXPercentNum) {
                const pctX = Math.max(0, Math.min(100, Math.round(50 + ((s.pos_x || 0) / 300) * 50)));
                this.dom.posXPercentNum.value = pctX;
            }
            if (this.dom.posYPercentNum) {
                const pctY = Math.max(0, Math.min(100, Math.round(50 + ((s.pos_y !== undefined ? s.pos_y : 240) / 320) * 35)));
                this.dom.posYPercentNum.value = pctY;
            }
            if (this.dom.animationTypeSelect) this.dom.animationTypeSelect.value = s.animation || "pop";
            if (this.dom.karaokeModeSelect) this.dom.karaokeModeSelect.value = s.karaoke_mode || "karaoke";
            if (this.dom.activeWordColorPicker) this.dom.activeWordColorPicker.value = s.active_word_color || "#FBBF24";

            const selected = this.getSelectedCaption();
            if (selected) {
                if (this.dom.captionTextareaInput) this.dom.captionTextareaInput.value = selected.text;
                if (this.dom.captionStartInput) this.dom.captionStartInput.value = selected.start.toFixed(2);
                if (this.dom.captionEndInput) this.dom.captionEndInput.value = selected.end.toFixed(2);
            }
        }

        // ======================================================================
        // Aspect Ratio & Canvas Rendering
        // ======================================================================
        setAspectRatio(ratio) {
            this.aspectRatio = ratio;
            if (this.dom.previewBox) {
                const cls = ratio === "custom" ? "aspect-9-16" : `aspect-${ratio.replace(":", "-")}`;
                this.dom.previewBox.className = `preview-canvas-box ${cls}`;
            }
            if (this.dom.canvasAspectSelect && this.dom.canvasAspectSelect.value !== ratio) {
                this.dom.canvasAspectSelect.value = ratio;
            }
            this.updateResolutionBadge();
            this.renderCanvas();
        }

        updateResolutionBadge() {
            if (!this.dom.canvasResolutionBadge) return;
            const resMap = {
                "9:16": "9:16 • 1080 × 1920",
                "16:9": "16:9 • 1920 × 1080",
                "1:1": "1:1 • 1080 × 1080",
                "4:5": "4:5 • 1080 × 1350",
                "custom": "Custom • Freeform"
            };
            this.dom.canvasResolutionBadge.textContent = resMap[this.aspectRatio] || "9:16 • 1080 × 1920";
        }

        renderCanvas() {
            const dragBox = this.dom.captionDragBox;
            if (!dragBox) return;

            const s = this.activeStyle;

            // Positioning & Independent Caption Scaling via CSS transform
            const posX = s.pos_x || 0;
            const posY = s.pos_y !== undefined ? s.pos_y : 240;
            const scale = this.captionScale || 1.0;
            dragBox.style.setProperty("--box-x", `${posX}px`);
            dragBox.style.setProperty("--box-y", `${posY}px`);
            dragBox.style.transform = `translate(${posX}px, ${posY}px) scale(${scale})`;

            // Typography styles
            dragBox.style.fontFamily = `'${s.font_family}', sans-serif`;
            dragBox.style.fontWeight = s.font_weight || 700;
            dragBox.style.fontSize = `${s.font_size || 42}px`;
            dragBox.style.letterSpacing = `${s.letter_spacing || 0}px`;
            dragBox.style.lineHeight = s.line_height || 1.2;
            dragBox.style.textAlign = s.text_align || "center";
            dragBox.style.textTransform = s.text_case || "normal";
            dragBox.style.color = s.text_color || "#FFFFFF";
            dragBox.style.opacity = (s.text_opacity ?? 100) / 100;
            dragBox.style.fontStyle = s.is_italic ? "italic" : "normal";
            dragBox.style.textDecoration = s.is_underline ? "underline" : "none";

            // Stroke / Outline
            if (s.stroke_enabled && s.stroke_width > 0) {
                dragBox.style.webkitTextStroke = `${s.stroke_width}px ${s.stroke_color || '#000000'}`;
            } else {
                dragBox.style.webkitTextStroke = "0px transparent";
            }

            // Shadow / Glow
            const shadows = [];
            if (s.shadow_enabled && s.shadow_blur > 0) {
                shadows.push(`0 ${s.shadow_y || 2}px ${s.shadow_blur}px ${s.shadow_color || '#000000'}`);
            }
            if (s.glow_enabled && s.glow_intensity > 0) {
                shadows.push(`0 0 ${s.glow_intensity}px ${s.glow_color || '#10B981'}`);
            }
            dragBox.style.textShadow = shadows.length ? shadows.join(", ") : "none";

            // Background Box
            if (s.bg_mode && s.bg_mode !== "none" && s.bg_opacity > 0) {
                const alpha = (s.bg_opacity / 100).toFixed(2);
                if (s.bg_mode === "solid") {
                    dragBox.style.backgroundColor = s.bg_color || "#000000";
                } else if (s.bg_mode === "semi") {
                    const hex = (s.bg_color || "#000000").replace("#", "");
                    const r = parseInt(hex.substring(0, 2), 16) || 0;
                    const g = parseInt(hex.substring(2, 4), 16) || 0;
                    const b = parseInt(hex.substring(4, 6), 16) || 0;
                    dragBox.style.backgroundColor = `rgba(${r}, ${g}, ${b}, ${alpha})`;
                } else if (s.bg_mode === "gradient") {
                    dragBox.style.background = `radial-gradient(ellipse at center, ${s.bg_color || '#10B981'} 0%, transparent 80%)`;
                }
                dragBox.style.borderRadius = `${s.bg_radius || 8}px`;
                dragBox.style.padding = `${s.bg_padding || 12}px ${s.bg_padding || 12}px`;
            } else {
                dragBox.style.background = "transparent";
                dragBox.style.padding = "6px 12px";
            }

            // Animation class
            dragBox.className = `caption-drag-box anim-${s.animation || 'pop'}`;
            if (this.selectedCaptionId) dragBox.classList.add("selected");

            this.renderActiveCaption();
        }

        // ======================================================================
        // Active Caption & Word-by-Word Karaoke Rendering
        // ======================================================================
        renderActiveCaption() {
            if (!this.dom.captionTextDisplay) return;

            const activeCap = this.captions.find(c => this.currentTime >= c.start && this.currentTime <= c.end);

            if (!activeCap) {
                if (this.captions.length === 0) {
                    this.dom.captionTextDisplay.innerHTML = `<span class="placeholder-caption-text">Your Caption Appears Here</span>`;
                } else {
                    const selected = this.getSelectedCaption();
                    if (selected) {
                        this.dom.captionTextDisplay.innerHTML = `<span style="opacity:0.6;">${this.escapeHtml(selected.text)}</span>`;
                    } else {
                        this.dom.captionTextDisplay.innerHTML = "";
                    }
                }
                // Clear active playhead highlights
                document.querySelectorAll(".timeline-caption-card").forEach(el => el.classList.remove("active-playhead"));
                if (this.dom.miniCaptionList) {
                    this.dom.miniCaptionList.querySelectorAll(".mini-caption-item").forEach(item => item.classList.remove("is-active-playing"));
                }
                return;
            }

            // Highlight active caption on timeline
            document.querySelectorAll(".timeline-caption-card").forEach(el => {
                const id = el.getAttribute("data-caption-id");
                el.classList.toggle("active-playhead", id === activeCap.id);
            });

            // Highlight active caption on mini timeline list & auto-scroll (Section 7)
            if (this.dom.miniCaptionList) {
                let newlyActive = null;
                this.dom.miniCaptionList.querySelectorAll(".mini-caption-item").forEach(item => {
                    const id = item.getAttribute("data-caption-id");
                    const isActive = !!(activeCap && id === activeCap.id);
                    if (isActive && !item.classList.contains("is-active-playing")) {
                        newlyActive = item;
                    }
                    item.classList.toggle("is-active-playing", isActive);
                });
                if (newlyActive && this.isPlaying) {
                    newlyActive.scrollIntoView({ block: "nearest", behavior: "smooth" });
                }
            }

            // Word-by-word karaoke rendering
            const mode = this.activeStyle.karaoke_mode || "karaoke";
            const words = activeCap.words || [];

            if (mode === "sentence" || words.length === 0) {
                this.dom.captionTextDisplay.textContent = activeCap.text;
                return;
            }

            let html = "";
            const activeWordColor = this.activeStyle.active_word_color || "#FBBF24";

            words.forEach((w, idx) => {
                const isCurrentWord = this.currentTime >= w.start && this.currentTime <= w.end;
                const isPastWord = this.currentTime > w.end;

                if (mode === "word_by_word" && !isCurrentWord && !isPastWord) {
                    return;
                }

                let spanClass = "caption-word-span";
                let styleAttr = "";

                if (isCurrentWord) {
                    spanClass += " active-karaoke-word";
                    styleAttr = `style="--active-word-color:${activeWordColor};"`;
                }

                html += `<span class="${spanClass}" ${styleAttr}>${this.escapeHtml(w.text)}</span> `;
            });

            this.dom.captionTextDisplay.innerHTML = html.trim() || this.escapeHtml(activeCap.text);
        }

        // ======================================================================
        // Bottom Caption Timeline Rendering
        // ======================================================================
        renderTimeline() {
            this.renderTimeRuler();
            this.renderWaveform();

            if (!this.dom.captionTrackLane) return;

            const totalWidth = Math.max(1200, (this.videoDuration || 60) * this.zoomPxPerSec + 200);
            if (this.dom.timelineTracksContent) {
                this.dom.timelineTracksContent.style.width = `${totalWidth}px`;
            }

            this.dom.captionTrackLane.innerHTML = "";

            if (this.timelineDisplayMode === "word") {
                // WORD Mode: Display individual word-level caption blocks
                this.captions.forEach(cap => {
                    const words = (cap.words && cap.words.length) ? cap.words : [{
                        text: cap.text,
                        start: cap.start,
                        end: cap.end
                    }];

                    words.forEach((w, wIdx) => {
                        const left = w.start * this.zoomPxPerSec;
                        const width = Math.max(26, (w.end - w.start) * this.zoomPxPerSec);

                        const card = document.createElement("div");
                        card.className = `timeline-caption-card word-mode-card ${cap.id === this.selectedCaptionId ? "selected" : ""}`;
                        card.style.left = `${left}px`;
                        card.style.width = `${width}px`;
                        card.setAttribute("data-caption-id", cap.id);
                        card.setAttribute("data-word-index", wIdx);

                        card.innerHTML = `
                            <div class="caption-block-text">${this.escapeHtml(w.text)}</div>
                            <div class="caption-block-sub">/ Word</div>
                        `;

                        card.addEventListener("mousedown", (e) => {
                            this.selectCaption(cap.id);
                            this.seekTo(w.start);
                        });

                        this.dom.captionTrackLane.appendChild(card);
                    });
                });
            } else {
                // LINE Mode: Display caption line segments
                this.captions.forEach(cap => {
                    const left = cap.start * this.zoomPxPerSec;
                    const width = Math.max(30, (cap.end - cap.start) * this.zoomPxPerSec);

                    const card = document.createElement("div");
                    card.className = `timeline-caption-card ${cap.id === this.selectedCaptionId ? "selected" : ""}`;
                    card.style.left = `${left}px`;
                    card.style.width = `${width}px`;
                    card.setAttribute("data-caption-id", cap.id);

                    card.innerHTML = `
                        <div class="caption-trim-handle trim-left" data-edge="start"></div>
                        <div class="caption-block-text">${this.escapeHtml(cap.text)}</div>
                        <div class="caption-block-sub">/ Text</div>
                        <div class="caption-trim-handle trim-right" data-edge="end"></div>
                    `;

                    // Drag block along timeline
                    let isDraggingBlock = false;
                    let dragStartX = 0;
                    let origStart = cap.start;
                    let origEnd = cap.end;

                    card.addEventListener("mousedown", (e) => {
                        if (e.target.classList.contains("caption-trim-handle")) {
                            this.startTrimming(e, cap.id, e.target.getAttribute("data-edge"));
                            return;
                        }
                        this.selectCaption(cap.id);
                        this.seekTo(cap.start);

                        isDraggingBlock = true;
                        dragStartX = e.clientX;
                        origStart = cap.start;
                        origEnd = cap.end;

                        const onBlockMove = (moveEvt) => {
                            if (!isDraggingBlock) return;
                            const deltaX = moveEvt.clientX - dragStartX;
                            const deltaTime = deltaX / this.zoomPxPerSec;
                            const dur = origEnd - origStart;
                            const newStart = Math.max(0, origStart + deltaTime);
                            const newEnd = newStart + dur;
                            cap.start = Math.round(newStart * 100) / 100;
                            cap.end = Math.round(newEnd * 100) / 100;
                            card.style.left = `${cap.start * this.zoomPxPerSec}px`;
                            this.syncInspectorInputs();
                        };

                        const onBlockUp = () => {
                            if (isDraggingBlock) {
                                isDraggingBlock = false;
                                this.captions.sort((a, b) => a.start - b.start);
                                this.renderTimeline();
                                this.pushHistory("Moved Caption on Timeline");
                            }
                            window.removeEventListener("mousemove", onBlockMove);
                            window.removeEventListener("mouseup", onBlockUp);
                        };

                        window.addEventListener("mousemove", onBlockMove);
                        window.addEventListener("mouseup", onBlockUp);
                    });

                    this.dom.captionTrackLane.appendChild(card);
                });
            }

            this.updatePlayheadPosition();
            this.renderMiniTimelineList(this.dom.miniCaptionSearchInput ? this.dom.miniCaptionSearchInput.value : "");
            const sel = this.getSelectedCaption();
            if (sel) this.updateColumn3Inspector(sel);
        }

        renderTimeRuler() {
            const canvas = this.dom.timelineRulerCanvas;
            if (!canvas) return;

            const totalWidth = Math.max(1200, (this.videoDuration || 60) * this.zoomPxPerSec + 200);
            canvas.width = totalWidth;
            canvas.height = 26;

            const ctx = canvas.getContext("2d");
            if (!ctx) return;

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "#071C16";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.strokeStyle = "#164B3B";
            ctx.fillStyle = "#8FA8A0";
            ctx.font = "10px Inter, monospace";

            const stepSec = this.zoomPxPerSec >= 60 ? 1 : (this.zoomPxPerSec >= 30 ? 2 : 5);

            for (let s = 0; s <= (this.videoDuration || 60) + 10; s += stepSec) {
                const x = s * this.zoomPxPerSec;
                ctx.beginPath();
                ctx.moveTo(x, 16);
                ctx.lineTo(x, 26);
                ctx.stroke();

                // Text timestamp
                const timeStr = this.formatSeconds(s);
                ctx.fillText(timeStr, x + 3, 14);

                // Sub-ticks
                if (this.zoomPxPerSec >= 40) {
                    const halfX = (s + stepSec / 2) * this.zoomPxPerSec;
                    ctx.beginPath();
                    ctx.moveTo(halfX, 20);
                    ctx.lineTo(halfX, 26);
                    ctx.stroke();
                }
            }
        }

        setupTimelineScrubbing() {
            const ruler = this.dom.timelineRulerCanvas;
            const scrollArea = this.dom.timelineScrollArea;

            const onScrub = (e) => {
                const rect = scrollArea.getBoundingClientRect();
                const scrollLeft = scrollArea.scrollLeft;
                const clickX = e.clientX - rect.left + scrollLeft;
                const time = Math.max(0, Math.min(this.videoDuration || 1000, clickX / this.zoomPxPerSec));
                this.seekTo(time);
            };

            if (ruler) {
                ruler.addEventListener("mousedown", (e) => {
                    this.isDraggingPlayhead = true;
                    onScrub(e);

                    const onMove = (mv) => {
                        if (this.isDraggingPlayhead) onScrub(mv);
                    };
                    const onUp = () => {
                        this.isDraggingPlayhead = false;
                        window.removeEventListener("mousemove", onMove);
                        window.removeEventListener("mouseup", onUp);
                    };
                    window.addEventListener("mousemove", onMove);
                    window.addEventListener("mouseup", onUp);
                });
            }

            if (this.dom.playheadScrubberHandle) {
                this.dom.playheadScrubberHandle.addEventListener("mousedown", (e) => {
                    e.stopPropagation();
                    this.isDraggingPlayhead = true;

                    const onMove = (mv) => {
                        if (this.isDraggingPlayhead) onScrub(mv);
                    };
                    const onUp = () => {
                        this.isDraggingPlayhead = false;
                        window.removeEventListener("mousemove", onMove);
                        window.removeEventListener("mouseup", onUp);
                    };
                    window.addEventListener("mousemove", onMove);
                    window.addEventListener("mouseup", onUp);
                });
            }
        }

        startTrimming(e, captionId, edge) {
            e.stopPropagation();
            const cap = this.captions.find(c => c.id === captionId);
            if (!cap) return;

            this.activeTrimming = {
                captionId,
                edge,
                startX: e.clientX,
                originalStart: cap.start,
                originalEnd: cap.end
            };

            const onTrimMove = (moveEvt) => {
                if (!this.activeTrimming) return;
                const deltaX = moveEvt.clientX - this.activeTrimming.startX;
                const deltaTime = deltaX / this.zoomPxPerSec;

                if (this.activeTrimming.edge === "start") {
                    const newStart = Math.max(0, Math.min(this.activeTrimming.originalEnd - 0.2, this.activeTrimming.originalStart + deltaTime));
                    cap.start = Math.round(newStart * 100) / 100;
                } else if (this.activeTrimming.edge === "end") {
                    const newEnd = Math.max(this.activeTrimming.originalStart + 0.2, this.activeTrimming.originalEnd + deltaTime);
                    cap.end = Math.round(newEnd * 100) / 100;
                }

                this.renderTimeline();
                this.syncInspectorInputs();
            };

            const onTrimUp = () => {
                if (this.activeTrimming) {
                    this.activeTrimming = null;
                    this.pushHistory("Trimmed Caption Duration");
                }
                window.removeEventListener("mousemove", onTrimMove);
                window.removeEventListener("mouseup", onTrimUp);
            };

            window.addEventListener("mousemove", onTrimMove);
            window.addEventListener("mouseup", onTrimUp);
        }

        updatePlayheadPosition() {
            if (!this.dom.timelinePlayheadLine) return;
            const x = this.currentTime * this.zoomPxPerSec;
            this.dom.timelinePlayheadLine.style.transform = `translateX(${x}px)`;
        }

        updateTimeReadouts() {
            if (this.dom.currentTimeReadout) {
                this.dom.currentTimeReadout.textContent = this.formatTimecode(this.currentTime);
            }
            if (this.dom.totalDurationReadout) {
                this.dom.totalDurationReadout.textContent = this.formatTimecode(this.videoDuration);
            }
        }

        // ======================================================================
        // Caption Operations (Select, Add, Split, Merge, Duplicate, Delete)
        // ======================================================================
        selectCaption(id) {
            this.selectedCaptionId = id;
            document.querySelectorAll(".timeline-caption-card").forEach(card => {
                card.classList.toggle("selected", card.getAttribute("data-caption-id") === id);
            });
            this.syncInspectorInputs();
            this.renderCanvas();

            const cap = this.getSelectedCaption();
            if (cap) {
                this.openColumn3("edit");
                this.populateManualCueEditor(cap);
            }
        }

        getSelectedCaption() {
            return this.captions.find(c => c.id === this.selectedCaptionId) || null;
        }

        addCaptionAtPlayhead() {
            const start = Math.max(0, this.currentTime);
            const end = start + 2.5;
            const newCap = {
                id: `cap_${Date.now()}`,
                start: Math.round(start * 100) / 100,
                end: Math.round(end * 100) / 100,
                text: "New Caption Text",
                words: [
                    { text: "New", start: start, end: start + 0.8 },
                    { text: "Caption", start: start + 0.8, end: start + 1.6 },
                    { text: "Text", start: start + 1.6, end: end }
                ],
                style: JSON.parse(JSON.stringify(this.activeStyle))
            };

            this.captions.push(newCap);
            this.captions.sort((a, b) => a.start - b.start);
            this.selectCaption(newCap.id);
            this.renderTimeline();
            this.pushHistory("Added New Caption");
            this.showToast("Added caption segment at playhead", "success");
        }

        splitSelectedCaption() {
            const cap = this.getSelectedCaption();
            if (!cap) {
                this.showToast("Select a caption to split", "error");
                return;
            }

            const splitTime = this.currentTime;
            if (splitTime <= cap.start + 0.2 || splitTime >= cap.end - 0.2) {
                this.showToast("Playhead must be inside the caption to split", "error");
                return;
            }

            const words = cap.words || cap.text.split(" ").map((w, idx) => ({
                text: w,
                start: cap.start + (idx * (cap.end - cap.start) / Math.max(1, cap.text.split(" ").length)),
                end: cap.start + ((idx + 1) * (cap.end - cap.start) / Math.max(1, cap.text.split(" ").length))
            }));

            const leftWords = words.filter(w => w.end <= splitTime);
            const rightWords = words.filter(w => w.start >= splitTime);

            const leftText = leftWords.map(w => w.text).join(" ") || cap.text.substring(0, Math.floor(cap.text.length / 2));
            const rightText = rightWords.map(w => w.text).join(" ") || cap.text.substring(Math.floor(cap.text.length / 2));

            const originalEnd = cap.end;
            cap.text = leftText;
            cap.end = splitTime;
            cap.words = leftWords;

            const newCap = {
                id: `cap_${Date.now()}`,
                start: splitTime,
                end: originalEnd,
                text: rightText,
                words: rightWords,
                style: JSON.parse(JSON.stringify(this.activeStyle))
            };

            this.captions.push(newCap);
            this.captions.sort((a, b) => a.start - b.start);
            this.selectCaption(newCap.id);
            this.renderTimeline();
            this.pushHistory("Split Caption at Playhead");
            this.showToast("Split caption into two segments", "success");
        }

        mergeSelectedCaption() {
            const cap = this.getSelectedCaption();
            if (!cap) {
                this.showToast("Select a caption to merge", "error");
                return;
            }

            const idx = this.captions.findIndex(c => c.id === cap.id);
            if (idx === -1 || idx >= this.captions.length - 1) {
                this.showToast("No adjacent next caption to merge with", "error");
                return;
            }

            const nextCap = this.captions[idx + 1];
            cap.text = `${cap.text.trim()} ${nextCap.text.trim()}`;
            cap.end = nextCap.end;
            cap.words = (cap.words || []).concat(nextCap.words || []);

            this.captions.splice(idx + 1, 1);
            this.renderTimeline();
            this.pushHistory("Merged with Next Caption");
            this.showToast("Merged captions successfully", "success");
        }

        duplicateSelectedCaption() {
            const cap = this.getSelectedCaption();
            if (!cap) {
                this.showToast("Select a caption to duplicate", "error");
                return;
            }

            const duration = cap.end - cap.start;
            const newStart = cap.end + 0.1;
            const newEnd = newStart + duration;

            const dupCap = {
                id: `cap_${Date.now()}`,
                start: Math.round(newStart * 100) / 100,
                end: Math.round(newEnd * 100) / 100,
                text: cap.text,
                words: (cap.words || []).map(w => ({
                    text: w.text,
                    start: w.start + duration + 0.1,
                    end: w.end + duration + 0.1
                })),
                style: JSON.parse(JSON.stringify(cap.style || this.activeStyle))
            };

            this.captions.push(dupCap);
            this.captions.sort((a, b) => a.start - b.start);
            this.selectCaption(dupCap.id);
            this.renderTimeline();
            this.pushHistory("Duplicated Caption");
            this.showToast("Caption duplicated", "success");
        }

        deleteSelectedCaption() {
            if (!this.selectedCaptionId) {
                this.showToast("No caption selected to delete", "error");
                return;
            }

            this.captions = this.captions.filter(c => c.id !== this.selectedCaptionId);
            this.selectedCaptionId = this.captions.length > 0 ? this.captions[0].id : null;
            this.renderTimeline();
            this.renderCanvas();
            this.pushHistory("Deleted Caption");
            this.showToast("Caption deleted", "info");
        }

        autoSplitCaptions() {
            if (!this.captions.length) {
                this.showToast("No captions to auto-split", "error");
                return;
            }

            fetch("/api/caption-studio/auto-split", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    captions: this.captions,
                    max_words: 5,
                    max_chars: 30
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.captions) {
                    this.captions = data.captions;
                    this.selectedCaptionId = this.captions[0]?.id || null;
                    this.renderTimeline();
                    this.renderCanvas();
                    this.pushHistory("Auto-Split Captions");
                    this.showToast(`Auto-split generated ${data.captions.length} short-form segments`, "success");
                } else {
                    this.showToast(data.error || "Auto-split failed", "error");
                }
            })
            .catch(err => {
                this.showToast(`Error: ${err.message}`, "error");
            });
        }

        recomputeWordsForCaption(cap) {
            const words = cap.text.trim().split(/\s+/);
            const totalDur = Math.max(0.1, cap.end - cap.start);
            const wordDur = totalDur / Math.max(1, words.length);

            cap.words = words.map((w, idx) => ({
                text: w,
                start: Math.round((cap.start + idx * wordDur) * 100) / 100,
                end: Math.round((cap.start + (idx + 1) * wordDur) * 100) / 100
            }));
        }

        // ======================================================================
        // Subtitle File Import (.srt, .vtt, .json)
        // ======================================================================
        handleSubtitleFile(file) {
            const formData = new FormData();
            formData.append("file", file);
            if (this.projectId) formData.append("project_id", this.projectId);

            fetch("/api/caption-studio/import", {
                method: "POST",
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.captions && data.captions.length) {
                    this.captions = data.captions;
                    this.selectedCaptionId = this.captions[0].id;
                    this.renderTimeline();
                    this.renderCanvas();
                    this.pushHistory(`Imported Subtitles: ${file.name}`);
                    this.showToast(`Imported ${data.captions.length} captions from ${file.name}`, "success");
                } else {
                    this.showToast(data.error || "Failed to parse subtitle file", "error");
                }
            })
            .catch(err => {
                this.showToast(`Import error: ${err.message}`, "error");
            });
        }

        // ======================================================================
        // Loading & Transcription Waiting Animation (Section 8)
        // ======================================================================
        showTranscriptionWaitingModal() {
            if (!this.dom.transcriptionWaitingModal) return;
            this.dom.transcriptionWaitingModal.style.display = "flex";

            const stages = [
                { text: "Extracting audio stream...", progress: 20 },
                { text: "Transcribing with Whisper AI...", progress: 55 },
                { text: "Generating word-level timestamps & karaoke alignments...", progress: 80 },
                { text: "Applying selected visual presets...", progress: 95 }
            ];

            let stageIdx = 0;
            this.updateWaitingModal(stages[0].text, stages[0].progress);

            if (this.transcriptionTimer) clearInterval(this.transcriptionTimer);
            this.transcriptionTimer = setInterval(() => {
                stageIdx++;
                if (stageIdx < stages.length) {
                    this.updateWaitingModal(stages[stageIdx].text, stages[stageIdx].progress);
                }
            }, 1800);
        }

        updateWaitingModal(statusText, percent) {
            if (this.dom.waitingStatusText) {
                this.dom.waitingStatusText.textContent = statusText;
            }
            if (this.dom.waitingProgressBar) {
                this.dom.waitingProgressBar.style.width = `${percent}%`;
            }
            if (this.dom.waitingPercentageText) {
                this.dom.waitingPercentageText.textContent = `${percent}%`;
            }
        }

        finishTranscriptionWaitingModal(success = true) {
            if (this.transcriptionTimer) {
                clearInterval(this.transcriptionTimer);
                this.transcriptionTimer = null;
            }
            if (!this.dom.transcriptionWaitingModal) return;

            if (success) {
                this.updateWaitingModal("Done! Captions Loaded", 100);
                setTimeout(() => {
                    this.dom.transcriptionWaitingModal.style.display = "none";
                }, 400);
            } else {
                this.dom.transcriptionWaitingModal.style.display = "none";
            }
        }

        executeGenerateModalCaptions() {
            if (this.dom.generateCaptionsModal) {
                this.dom.generateCaptionsModal.style.display = "none";
            }
            const selectedRadio = document.querySelector('input[name="genLanguageRadio"]:checked');
            const lang = selectedRadio ? selectedRadio.value : (this.dom.workflowLangSelect ? this.dom.workflowLangSelect.value : "hinglish");
            this.generateAICaptions(lang);
        }

        startAutoCaption(language) {
            return this.generateAICaptions(language);
        }

        generateAICaptions(language = "hinglish") {
            if (!this.videoFileName) {
                this.showToast("Please import a video first", "error");
                return;
            }

            if (this.dom.generateCaptionsTopBtn) {
                this.dom.generateCaptionsTopBtn.disabled = true;
                this.dom.generateCaptionsTopBtn.classList.add("is-generating");
            }
            if (this.dom.generateBtnText) {
                this.dom.generateBtnText.textContent = "Transcribing...";
            }

            const activeLang = language || (this.dom.workflowLangSelect ? this.dom.workflowLangSelect.value : "hinglish");

            this.showTranscriptionWaitingModal();
            this.showToast("Analyzing video audio with Whisper AI...", "info");

            fetch("/api/caption-studio/auto-caption", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    videoFileName: this.videoFileName,
                    project_id: this.projectId,
                    language: activeLang
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.captions && data.captions.length) {
                    this.captions = data.captions;
                    this.selectedCaptionId = this.captions[0].id;
                    this.renderTimeline();
                    this.renderCanvas();
                    this.pushHistory("AI Auto-Caption Generated");
                    this.finishTranscriptionWaitingModal(true);
                    this.showToast(`Captions generated successfully (${data.captions.length} segments)`, "success");
                } else {
                    this.finishTranscriptionWaitingModal(false);
                    this.showToast(data.error || "Speech-to-text transcription failed", "error");
                }
            })
            .catch(err => {
                this.finishTranscriptionWaitingModal(false);
                this.showToast(`Transcription error: ${err.message}`, "error");
            })
            .finally(() => {
                if (this.dom.generateCaptionsTopBtn) {
                    this.dom.generateCaptionsTopBtn.disabled = false;
                    this.dom.generateCaptionsTopBtn.classList.remove("is-generating");
                }
                if (this.dom.generateBtnText) this.dom.generateBtnText.textContent = "Generate";
            });
        }

        // ======================================================================
        // Video Export Dialog & FFmpeg Burn-In Render
        // ======================================================================
        openExportModal() {
            if (!this.dom.exportVideoModal) return;
            this.dom.exportVideoModal.style.display = "flex";
            if (this.dom.exportStatusPanel) this.dom.exportStatusPanel.style.display = "none";
            if (this.dom.exportStartRenderBtn) this.dom.exportStartRenderBtn.style.display = "inline-flex";
            if (this.dom.exportDownloadLinkBtn) this.dom.exportDownloadLinkBtn.style.display = "none";
        }

        closeExportModal() {
            if (this.dom.exportVideoModal) this.dom.exportVideoModal.style.display = "none";
        }

        startExportVideoRender() {
            if (!this.videoFileName) {
                this.showToast("No video loaded for export", "error");
                return;
            }

            if (this.dom.exportStartRenderBtn) this.dom.exportStartRenderBtn.disabled = true;
            if (this.dom.exportStatusPanel) this.dom.exportStatusPanel.style.display = "block";
            if (this.dom.exportDownloadLinkBtn) this.dom.exportDownloadLinkBtn.style.display = "none";

            this.updateExportProgress(10, "Preparing video & style assets...");

            const payload = {
                videoFileName: this.videoFileName,
                project_id: this.projectId,
                captions: this.captions,
                style: Object.assign({}, this.activeStyle, {
                    caption_scale: this.captionScale || this.activeStyle.caption_scale || 1.0
                }),
                resolution: this.dom.exportResolutionSelect ? this.dom.exportResolutionSelect.value : "9:16_1080p",
                fps: this.dom.exportFpsSelect ? parseInt(this.dom.exportFpsSelect.value, 10) : 30,
                format: this.dom.exportFormatSelect ? this.dom.exportFormatSelect.value : "mp4"
            };

            // Simulate realistic progress steps while server encodes with FFmpeg
            let progress = 15;
            const progressTimer = setInterval(() => {
                if (progress < 90) {
                    progress += Math.floor(Math.random() * 8) + 4;
                    const msg = progress < 40 ? "Encoding video frames..." :
                                (progress < 70 ? "Burning animated karaoke subtitles..." : "Finalizing export...");
                    this.updateExportProgress(progress, msg);
                }
            }, 700);

            fetch("/api/caption-studio/export", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                clearInterval(progressTimer);
                if (data.success && data.download_url) {
                    this.updateExportProgress(100, "Rendering complete!");
                    if (this.dom.exportStartRenderBtn) this.dom.exportStartRenderBtn.style.display = "none";
                    if (this.dom.exportDownloadLinkBtn) {
                        this.dom.exportDownloadLinkBtn.style.display = "inline-flex";
                        this.dom.exportDownloadLinkBtn.href = data.download_url;
                        this.dom.exportDownloadLinkBtn.download = data.filename || "captioned_video.mp4";
                    }
                    this.showToast("Video export completed successfully!", "success");
                } else {
                    this.updateExportProgress(0, "Rendering failed");
                    this.showToast(data.error || "FFmpeg export failed", "error");
                    if (this.dom.exportStartRenderBtn) this.dom.exportStartRenderBtn.disabled = false;
                }
            })
            .catch(err => {
                clearInterval(progressTimer);
                this.updateExportProgress(0, "Error");
                this.showToast(`Export error: ${err.message}`, "error");
                if (this.dom.exportStartRenderBtn) this.dom.exportStartRenderBtn.disabled = false;
            });
        }

        updateExportProgress(percent, msg) {
            if (this.dom.exportProgressBar) this.dom.exportProgressBar.style.width = `${percent}%`;
            if (this.dom.exportPercentText) this.dom.exportPercentText.textContent = `${percent}%`;
            if (this.dom.exportStatusText) this.dom.exportStatusText.textContent = msg;
        }

        exportCaptionsOnly(format = "srt") {
            if (!this.captions.length) {
                this.showToast("No captions to export", "error");
                return;
            }

            fetch("/api/caption-studio/export-captions", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    captions: this.captions,
                    project_id: this.projectId,
                    format: format
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.files && data.files[format]) {
                    const fileInfo = data.files[format];
                    const link = document.createElement("a");
                    link.href = fileInfo.url;
                    link.download = fileInfo.filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    this.showToast(`Exported ${format.toUpperCase()} successfully`, "success");
                } else {
                    this.showToast(data.error || `Failed to export ${format.toUpperCase()}`, "error");
                }
            })
            .catch(err => {
                this.showToast(`Error: ${err.message}`, "error");
            });
        }

        // ======================================================================
        // Search & Replace
        // ======================================================================
        executeSearchReplace() {
            const findText = this.dom.srFindInput ? this.dom.srFindInput.value : "";
            const replaceText = this.dom.srReplaceInput ? this.dom.srReplaceInput.value : "";
            const isCase = this.dom.srCaseCheck ? this.dom.srCaseCheck.checked : false;

            if (!findText) {
                this.showToast("Enter text to find", "error");
                return;
            }

            fetch("/api/caption-studio/search-replace", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    captions: this.captions,
                    search: findText,
                    replace: replaceText,
                    case_sensitive: isCase
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.captions) {
                    this.captions = data.captions;
                    this.renderTimeline();
                    this.renderCanvas();
                    this.syncInspectorInputs();
                    this.pushHistory(`Replaced "${findText}" with "${replaceText}"`);
                    if (this.dom.srMatchesCount) {
                        this.dom.srMatchesCount.textContent = `Replaced ${data.replaceCount} match(es)`;
                    }
                    this.showToast(`Replaced ${data.replaceCount} caption segment(s)`, "success");
                    setTimeout(() => {
                        if (this.dom.searchReplaceModal) this.dom.searchReplaceModal.style.display = "none";
                    }, 800);
                } else {
                    this.showToast(data.error || "Search and replace failed", "error");
                }
            })
            .catch(err => {
                this.showToast(`Error: ${err.message}`, "error");
            });
        }

        // ======================================================================
        // Custom Presets
        // ======================================================================
        saveCustomPreset() {
            const name = (this.dom.customPresetNameInput && this.dom.customPresetNameInput.value.trim()) || "My Custom Style";
            const newPreset = {
                id: `custom_${Date.now()}`,
                name: name,
                category: "Custom",
                style: JSON.parse(JSON.stringify(this.activeStyle))
            };

            PRESETS_REGISTRY.push(newPreset);
            this.setupPresetsCards();
            if (this.dom.customPresetNameInput) this.dom.customPresetNameInput.value = "";
            this.showToast(`Saved custom preset: ${name}`, "success");
        }

        // ======================================================================
        // Undo / Redo & Autosave
        // ======================================================================
        pushHistory(action = "Change") {
            // Truncate forward history if at intermediate index
            if (this.historyIndex < this.history.length - 1) {
                this.history = this.history.slice(0, this.historyIndex + 1);
            }

            const snapshot = {
                action,
                captions: JSON.parse(JSON.stringify(this.captions)),
                style: JSON.parse(JSON.stringify(this.activeStyle)),
                selectedCaptionId: this.selectedCaptionId
            };

            this.history.push(snapshot);
            if (this.history.length > 50) this.history.shift();
            this.historyIndex = this.history.length - 1;

            this.updateUndoRedoButtons();
            this.markDirty();
            this.saveToLocalStorage();
        }

        undo() {
            if (this.historyIndex > 0) {
                this.historyIndex--;
                const state = this.history[this.historyIndex];
                this.captions = JSON.parse(JSON.stringify(state.captions));
                this.activeStyle = JSON.parse(JSON.stringify(state.style));
                this.selectedCaptionId = state.selectedCaptionId;

                this.syncInspectorInputs();
                this.renderCanvas();
                this.renderTimeline();
                this.updateUndoRedoButtons();
                this.showToast(`Undo: ${state.action}`, "info");
            }
        }

        redo() {
            if (this.historyIndex < this.history.length - 1) {
                this.historyIndex++;
                const state = this.history[this.historyIndex];
                this.captions = JSON.parse(JSON.stringify(state.captions));
                this.activeStyle = JSON.parse(JSON.stringify(state.style));
                this.selectedCaptionId = state.selectedCaptionId;

                this.syncInspectorInputs();
                this.renderCanvas();
                this.renderTimeline();
                this.updateUndoRedoButtons();
                this.showToast(`Redo: ${state.action}`, "info");
            }
        }

        updateUndoRedoButtons() {
            if (this.dom.undoBtn) {
                this.dom.undoBtn.disabled = this.historyIndex <= 0;
                this.dom.undoBtn.style.opacity = this.historyIndex <= 0 ? "0.4" : "1";
            }
            if (this.dom.redoBtn) {
                this.dom.redoBtn.disabled = this.historyIndex >= this.history.length - 1;
                this.dom.redoBtn.style.opacity = this.historyIndex >= this.history.length - 1 ? "0.4" : "1";
            }
        }

        markDirty() {
            this.isDirty = true;
            if (this.dom.dirtyIndicator) this.dom.dirtyIndicator.style.display = "inline";
            if (this.dom.saveStatus) this.dom.saveStatus.textContent = "Saving...";
            this.debouncedServerSave();
        }

        markClean() {
            this.isDirty = false;
            if (this.dom.dirtyIndicator) this.dom.dirtyIndicator.style.display = "none";
            if (this.dom.saveStatus) this.dom.saveStatus.textContent = "Saved";
        }

        debouncedServerSave() {
            clearTimeout(this._saveTimer);
            this._saveTimer = setTimeout(() => {
                if (this.projectId) {
                    fetch("/api/caption-studio/save-state", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            project_id: this.projectId,
                            captions: this.captions,
                            style: this.activeStyle
                        })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) this.markClean();
                    })
                    .catch(() => {});
                } else {
                    this.markClean();
                }
            }, 1200);
        }

        saveToLocalStorage() {
            try {
                const key = `flip_caption_state_${this.projectId || this.videoFileName || 'default'}`;
                const payload = {
                    videoFileName: this.videoFileName,
                    captions: this.captions,
                    style: this.activeStyle,
                    aspectRatio: this.aspectRatio
                };
                localStorage.setItem(key, JSON.stringify(payload));
            } catch (e) {}
        }

        restoreLocalAutosave() {
            try {
                const key = `flip_caption_state_${this.projectId || this.videoFileName || 'default'}`;
                const saved = localStorage.getItem(key);
                if (saved) {
                    const data = JSON.parse(saved);
                    if (data.captions && data.captions.length && !this.captions.length) {
                        this.captions = data.captions;
                        this.selectedCaptionId = this.captions[0]?.id || null;
                    }
                    if (data.style) {
                        Object.assign(this.activeStyle, data.style);
                    }
                    if (data.aspectRatio) {
                        this.setAspectRatio(data.aspectRatio);
                    }
                    this.syncInspectorInputs();
                    this.renderTimeline();
                    this.renderCanvas();
                }
            } catch (e) {}
        }

        // ======================================================================
        // Playback Transport Controls
        // ======================================================================
        togglePlayPause() {
            if (!this.dom.videoPlayer) return;
            if (this.dom.videoPlayer.paused) {
                this.dom.videoPlayer.play().catch(e => console.warn("Playback interrupted", e));
                this.updatePlayPauseBtn(true);
            } else {
                this.dom.videoPlayer.pause();
                this.updatePlayPauseBtn(false);
            }
        }

        updatePlayPauseBtn(isPlaying) {
            this.isPlaying = isPlaying;
            const playIcon = document.getElementById("playIcon") || this.dom.playIcon;
            const pauseIcon = document.getElementById("pauseIcon") || this.dom.pauseIcon;
            if (playIcon) playIcon.style.display = isPlaying ? "none" : "block";
            if (pauseIcon) pauseIcon.style.display = isPlaying ? "block" : "none";
            if (this.dom.playPauseBtn) {
                this.dom.playPauseBtn.setAttribute("title", isPlaying ? "Pause (Space)" : "Play (Space)");
            }
        }

        // ======================================================================
        // Dynamic Column 3 (Offline AI & Manual Cue Text Editor)
        // ======================================================================
        openColumn3(mode = "ai") {
            const upperRow = document.getElementById("captionUpperThreeCols") || this.dom.captionUpperThreeCols;
            if (upperRow) {
                upperRow.classList.remove("cols-two");
                upperRow.classList.add("cols-three");
            }
            const panelCol3 = document.getElementById("panelAiSettings") || this.dom.panelAiSettings;
            if (panelCol3) {
                panelCol3.style.display = "flex";
            }
            const viewAi = document.getElementById("viewOfflineAi");
            const viewEdit = document.getElementById("viewManualEdit");
            const col3Title = document.getElementById("col3Title");
            const col3Tag = document.getElementById("col3Tag");

            if (mode === "ai") {
                if (viewAi) viewAi.style.display = "flex";
                if (viewEdit) viewEdit.style.display = "none";
                if (col3Title) col3Title.textContent = "Offline AI Settings";
                if (col3Tag) col3Tag.textContent = "Whisper AI";
            } else if (mode === "edit") {
                if (viewAi) viewAi.style.display = "none";
                if (viewEdit) viewEdit.style.display = "flex";
                if (col3Title) col3Title.textContent = "Edit Caption Text";
                if (col3Tag) col3Tag.textContent = "Spelling & Words";
            }
        }

        closeColumn3() {
            const upperRow = document.getElementById("captionUpperThreeCols") || this.dom.captionUpperThreeCols;
            if (upperRow) {
                upperRow.classList.remove("cols-three");
                upperRow.classList.add("cols-two");
            }
            const panelCol3 = document.getElementById("panelAiSettings") || this.dom.panelAiSettings;
            if (panelCol3) {
                panelCol3.style.display = "none";
            }
        }

        populateManualCueEditor(cap) {
            if (!cap) return;
            const textarea = document.getElementById("captionTextareaInput");
            if (textarea) {
                textarea.value = cap.text || "";
            }
            const badge = document.getElementById("manualCueBadge");
            if (badge) {
                badge.textContent = `Cue ${cap.id ? cap.id.replace("cap_", "") : ""}`;
            }
            const startInput = document.getElementById("captionStartInput");
            if (startInput) {
                startInput.value = this.formatTimecode(cap.start);
            }
            const endInput = document.getElementById("captionEndInput");
            if (endInput) {
                endInput.value = this.formatTimecode(cap.end);
            }

            this.renderWordChips(cap);
        }

        renderWordChips(cap) {
            const chipsContainer = document.getElementById("manualWordChipsContainer");
            if (!chipsContainer) return;
            chipsContainer.innerHTML = "";

            const words = (cap.words && cap.words.length > 0)
                ? cap.words
                : (cap.text || "").trim().split(/\s+/).filter(Boolean).map(w => ({ text: w, start: cap.start, end: cap.end }));

            words.forEach((wObj) => {
                const wordText = typeof wObj === "string" ? wObj : (wObj.text || "");
                if (!wordText) return;
                const chip = document.createElement("button");
                chip.type = "button";
                chip.className = "word-chip-pill";
                chip.textContent = wordText;
                chip.title = "Click to focus & edit this word in text area";
                chip.addEventListener("click", () => {
                    const textarea = document.getElementById("captionTextareaInput");
                    if (textarea) {
                        textarea.focus();
                        const pos = textarea.value.indexOf(wordText);
                        if (pos !== -1) {
                            textarea.setSelectionRange(pos, pos + wordText.length);
                        }
                    }
                });
                chipsContainer.appendChild(chip);
            });
        }

        setupManualCueEditorListeners() {
            const textarea = document.getElementById("captionTextareaInput");
            if (textarea) {
                textarea.addEventListener("input", (e) => {
                    const cap = this.getSelectedCaption();
                    if (!cap) return;
                    const newText = e.target.value;
                    cap.text = newText;

                    const rawWords = newText.trim().split(/\s+/).filter(Boolean);
                    if (rawWords.length > 0) {
                        const totalDur = Math.max(0.1, (cap.end || 1) - (cap.start || 0));
                        const wordDur = totalDur / rawWords.length;
                        cap.words = rawWords.map((w, idx) => ({
                            text: w,
                            word: w,
                            start: parseFloat((cap.start + idx * wordDur).toFixed(3)),
                            end: parseFloat((cap.start + (idx + 1) * wordDur).toFixed(3))
                        }));
                    } else {
                        cap.words = [];
                    }

                    const overlayText = document.getElementById("captionOverlayText");
                    if (overlayText) overlayText.textContent = newText;

                    const card = document.querySelector(`.timeline-caption-card[data-caption-id="${cap.id}"] .caption-block-text`);
                    if (card) card.textContent = newText;

                    this.renderWordChips(cap);
                    this.renderActiveCaption();
                    this.isDirty = true;
                });
            }

            const startInput = document.getElementById("captionStartInput");
            if (startInput) {
                startInput.addEventListener("change", (e) => {
                    const cap = this.getSelectedCaption();
                    if (!cap) return;
                    const parsed = this.parseTimecode(e.target.value);
                    if (parsed !== null && parsed < cap.end) {
                        cap.start = parsed;
                        this.rebuildCaptionWords(cap);
                        this.renderTimeline();
                        this.renderActiveCaption();
                    }
                });
            }

            const endInput = document.getElementById("captionEndInput");
            if (endInput) {
                endInput.addEventListener("change", (e) => {
                    const cap = this.getSelectedCaption();
                    if (!cap) return;
                    const parsed = this.parseTimecode(e.target.value);
                    if (parsed !== null && parsed > cap.start) {
                        cap.end = parsed;
                        this.rebuildCaptionWords(cap);
                        this.renderTimeline();
                        this.renderActiveCaption();
                    }
                });
            }
        }

        parseTimecode(str) {
            if (!str) return null;
            const parts = str.trim().split(":");
            if (parts.length === 1) {
                const s = parseFloat(parts[0]);
                return isNaN(s) ? null : s;
            } else if (parts.length === 2) {
                const m = parseFloat(parts[0]);
                const s = parseFloat(parts[1]);
                return (isNaN(m) || isNaN(s)) ? null : (m * 60 + s);
            } else if (parts.length === 3) {
                const h = parseFloat(parts[0]);
                const m = parseFloat(parts[1]);
                const s = parseFloat(parts[2]);
                return (isNaN(h) || isNaN(m) || isNaN(s)) ? null : (h * 3600 + m * 60 + s);
            }
            return null;
        }

        seekTo(seconds) {
            if (!this.dom.videoPlayer) return;
            this.currentTime = Math.max(0, Math.min(this.videoDuration || 1000, seconds));
            this.dom.videoPlayer.currentTime = this.currentTime;
            this.updatePlayheadPosition();
            this.updateTimeReadouts();
            this.renderActiveCaption();
        }

        seekBy(deltaSeconds) {
            this.seekTo(this.currentTime + deltaSeconds);
        }

        toggleMute() {
            if (!this.dom.videoPlayer) return;
            this.isMuted = !this.isMuted;
            this.dom.videoPlayer.muted = this.isMuted;
            if (this.dom.volIcon) this.dom.volIcon.style.display = this.isMuted ? "none" : "block";
            if (this.dom.muteIcon) this.dom.muteIcon.style.display = this.isMuted ? "block" : "none";
        }

        setVolume(vol) {
            if (!this.dom.videoPlayer) return;
            this.volume = Math.max(0, Math.min(1, vol));
            this.dom.videoPlayer.volume = this.volume;
            if (this.volume === 0 && !this.isMuted) this.toggleMute();
            else if (this.volume > 0 && this.isMuted) this.toggleMute();
        }

        setPlaybackSpeed(rate) {
            if (!this.dom.videoPlayer) return;
            this.playbackRate = rate;
            this.dom.videoPlayer.playbackRate = rate;
            this.showToast(`Speed: ${rate}x`, "info");
        }

        toggleFullscreen() {
            const el = document.getElementById("captionCanvasArea");
            if (!el) return;
            if (!document.fullscreenElement) {
                el.requestFullscreen().catch(() => {});
            } else {
                document.exitFullscreen().catch(() => {});
            }
        }

        // ======================================================================
        // Command Palette (Ctrl + K) - Section 3.B
        // ======================================================================
        setupCommandPalette() {
            if (!this.dom.commandPaletteModal) return;

            if (this.dom.commandPaletteBtn) {
                this.dom.commandPaletteBtn.addEventListener("click", () => this.openCommandPalette());
            }

            if (this.dom.commandPaletteSearchInput) {
                this.dom.commandPaletteSearchInput.addEventListener("input", (e) => {
                    this.filterCommandPalette(e.target.value);
                });
                this.dom.commandPaletteSearchInput.addEventListener("keydown", (e) => {
                    if (e.key === "Escape") {
                        this.closeCommandPalette();
                    } else if (e.key === "Enter") {
                        if (this.dom.commandPaletteResultsList) {
                            const firstVisible = this.dom.commandPaletteResultsList.querySelector(".cp-item:not([style*='display: none'])");
                            if (firstVisible) {
                                firstVisible.click();
                            }
                        }
                    }
                });
            }

            // Click outside modal overlay to close
            this.dom.commandPaletteModal.addEventListener("click", (e) => {
                if (e.target === this.dom.commandPaletteModal) {
                    this.closeCommandPalette();
                }
            });

            // Quick actions inside Command Palette
            if (this.dom.commandPaletteResultsList) {
                this.dom.commandPaletteResultsList.querySelectorAll(".cp-item[data-action]").forEach(item => {
                    item.addEventListener("click", () => {
                        const action = item.getAttribute("data-action");
                        this.closeCommandPalette();
                        this.executeCommandPaletteAction(action);
                    });
                });
            }
        }

        openCommandPalette() {
            if (!this.dom.commandPaletteModal) return;
            this.dom.commandPaletteModal.style.display = "flex";
            if (this.dom.commandPaletteSearchInput) {
                this.dom.commandPaletteSearchInput.value = "";
                this.filterCommandPalette("");
                setTimeout(() => this.dom.commandPaletteSearchInput.focus(), 60);
            }
        }

        closeCommandPalette() {
            if (!this.dom.commandPaletteModal) return;
            this.dom.commandPaletteModal.style.display = "none";
        }

        filterCommandPalette(query) {
            if (!this.dom.commandPaletteResultsList) return;
            const q = query.toLowerCase().trim();
            this.dom.commandPaletteResultsList.querySelectorAll(".cp-item").forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = (!q || text.includes(q)) ? "flex" : "none";
            });
        }

        executeCommandPaletteAction(action) {
            switch (action) {
                case "import_video":
                    if (this.dom.videoFileInput) this.dom.videoFileInput.click();
                    break;
                case "generate_captions":
                    this.generateAICaptions();
                    break;
                case "auto_split":
                    this.autoSplitCaptions();
                    break;
                case "export_video":
                    this.openExportModal();
                    break;
                default:
                    console.log("Command palette action:", action);
            }
        }

        // ======================================================================
        // Keyboard Shortcuts (Space, Seek, Undo, Delete, Export, Command Palette)
        // ======================================================================
        handleKeyboardShortcuts(e) {
            const isInput = e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || e.target.isContentEditable;

            // Command Palette (Ctrl + K / Cmd + K) - Section 3.B
            if ((e.ctrlKey || e.metaKey) && (e.code === "KeyK" || e.key === "k" || e.key === "K")) {
                e.preventDefault();
                this.openCommandPalette();
                return;
            }

            if (e.code === "Escape") {
                this.closeCommandPalette();
                this.closeExportModal();
                if (this.dom.generateCaptionsModal) this.dom.generateCaptionsModal.style.display = "none";
                if (this.dom.searchReplaceModal) this.dom.searchReplaceModal.style.display = "none";
                return;
            }

            if (e.code === "Space" && !isInput) {
                e.preventDefault();
                this.togglePlayPause();
            } else if (e.code === "ArrowLeft" && !isInput) {
                e.preventDefault();
                this.seekBy(e.shiftKey ? -5.0 : -1.0);
            } else if (e.code === "ArrowRight" && !isInput) {
                e.preventDefault();
                this.seekBy(e.shiftKey ? 5.0 : 1.0);
            } else if ((e.ctrlKey || e.metaKey) && e.code === "KeyZ") {
                e.preventDefault();
                if (e.shiftKey) this.redo();
                else this.undo();
            } else if ((e.ctrlKey || e.metaKey) && e.code === "KeyS") {
                e.preventDefault();
                this.debouncedServerSave();
                this.showToast("Project saved", "success");
            } else if ((e.ctrlKey || e.metaKey) && e.code === "KeyE") {
                e.preventDefault();
                this.openExportModal();
            } else if ((e.code === "Delete" || e.code === "Backspace") && !isInput) {
                if (this.selectedCaptionId) {
                    this.deleteSelectedCaption();
                }
            } else if (e.code === "Enter" && !isInput) {
                if (this.selectedCaptionId && this.dom.captionTextareaInput) {
                    this.dom.captionTextareaInput.focus();
                }
            }
        }

        // ======================================================================
        // Toast Notifications
        // ======================================================================
        showToast(message, type = "info") {
            if (!this.dom.toastContainer) return;

            const toast = document.createElement("div");
            toast.className = `toast-item ${type === 'error' ? 'error' : ''}`;
            toast.innerHTML = `
                <span>${type === 'error' ? '✕' : (type === 'success' ? '✓' : '✦')}</span>
                <span>${this.escapeHtml(message)}</span>
            `;

            this.dom.toastContainer.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = "0";
                toast.style.transform = "translateY(10px)";
                toast.style.transition = "all 0.3s";
                setTimeout(() => toast.remove(), 300);
            }, 3200);
        }

        // ======================================================================
        // Utility Helpers
        // ======================================================================
        formatTimecode(sec) {
            const m = Math.floor(sec / 60);
            const s = Math.floor(sec % 60);
            const ms = Math.floor((sec % 1) * 100);
            return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${String(ms).padStart(2, '0')}`;
        }

        formatSeconds(sec) {
            const m = Math.floor(sec / 60);
            const s = Math.floor(sec % 60);
            return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
        }

        escapeHtml(str) {
            if (!str) return "";
            return str
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }
    }

    // Initialize application when DOM is ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => {
            window.CaptionStudioApp = new CaptionStudioEngine();
        });
    } else {
        window.CaptionStudioApp = new CaptionStudioEngine();
    }
})();
