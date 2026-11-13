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
        viralEnhancements: {
            watermark: {
                enabled: false,
                image_path: '',
                image_url: '',
                text: '',
                position: 'top_right',
                scale_pct: 16,
                opacity: 80
            },
            outro_cta: {
                enabled: false,
                channel_name: 'UpClip Creator',
                handle: '@creator',
                avatar_path: '',
                avatar_url: '',
                duration: 4
            },
            sfx: {
                enabled: false,
                sound_type: 'whoosh',
                trigger_cue: 'major',
                volume: 70
            },
            b_rolls: [
                {
                    enabled: false,
                    file_path: '',
                    file_url: '',
                    file_name: '',
                    mode: 'cutaway',
                    start_time: 2.0,
                    duration: 3.0
                }
            ]
        }
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
        if (typeof debouncedSaveCaptionState === 'function') {
            debouncedSaveCaptionState();
        }
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
        if (typeof debouncedSaveCaptionState === 'function') {
            debouncedSaveCaptionState();
        }
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
        if (typeof debouncedSaveCaptionState === 'function') {
            debouncedSaveCaptionState();
        }
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
    // 3. ULTRA HIGH-QUALITY CINEMATIC MASTER & CREATOR GRADE PRESETS
    // =========================================================================
    const PRESETS = [
        {
                "id": "cinematic_creator",
                "name": "Cinematic Creator",
                "category": "cinematic master",
                "description": "Bold condensed uppercase with Ice Blue glow and 2-line visual hierarchy.",
                "platform": "Cinematic Master",
                "tagClass": "tag-cinematic",
                "previewWord1": "BHAI SCOUT KIA",
                "previewWord2": "ROYA HOGA",
                "style": {
                        "fontFamily": "Anton",
                        "fontWeight": "900",
                        "fontSize": 42,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#80D8FF",
                        "textCase": "uppercase",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": true,
                        "strokeColor": "#001830",
                        "strokeWidth": 2.5,
                        "shadowEnabled": true,
                        "shadowColor": "#001428",
                        "shadowBlur": 8.0,
                        "shadowY": 3.0,
                        "glowEnabled": true,
                        "glowColor": "#0088FF",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "pop_in",
                        "position": "center",
                        "twoLineHierarchy": true
                }
        },
        {
                "id": "cinematic_minimal_hindi",
                "name": "Cinematic Minimal (Devanagari)",
                "category": "cinematic master",
                "description": "Elegant Hindi Devanagari typography, pure white, center-aligned, minimal soft shadow.",
                "platform": "Cinematic Master",
                "tagClass": "tag-minimal",
                "previewWord1": "\u0909\u0938\u0915\u0947 \u0906\u0938\u092a\u093e\u0938",
                "previewWord2": "\u0915\u0947 \u0932\u094b\u0917",
                "style": {
                        "fontFamily": "Noto Sans Devanagari",
                        "fontWeight": "600",
                        "fontSize": 34,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FFFFFF",
                        "textCase": "normal",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": false,
                        "strokeColor": "#000000",
                        "strokeWidth": 0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 2.0,
                        "shadowY": 1.5,
                        "glowEnabled": false,
                        "glowColor": "#FFFFFF",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "smooth_fade",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "bold_keyword_yellow",
                "name": "Bold Keyword Highlight",
                "category": "cinematic master",
                "description": "Main keyword in bright yellow with white supporting text, large bold condensed font.",
                "platform": "Cinematic Master",
                "tagClass": "tag-viral",
                "previewWord1": "AGAR",
                "previewWord2": "US DIN",
                "style": {
                        "fontFamily": "Anton",
                        "fontWeight": "900",
                        "fontSize": 46,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FFEA00",
                        "textCase": "uppercase",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": true,
                        "strokeColor": "#000000",
                        "strokeWidth": 3.0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 4.0,
                        "shadowY": 3.0,
                        "glowEnabled": true,
                        "glowColor": "#FFEA00",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "zoom_in",
                        "position": "bottom",
                        "twoLineHierarchy": true
                }
        },
        {
                "id": "modern_kinetic_cyan",
                "name": "Modern Kinetic Typography",
                "category": "cinematic master",
                "description": "White + electric cyan/turquoise, modern bold sans-serif, dynamic composition.",
                "platform": "Cinematic Master",
                "tagClass": "tag-podcast",
                "previewWord1": "with something",
                "previewWord2": "predictable",
                "style": {
                        "fontFamily": "Montserrat",
                        "fontWeight": "800",
                        "fontSize": 38,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#00F0FF",
                        "textCase": "normal",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": false,
                        "strokeColor": "#000000",
                        "strokeWidth": 0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 4.0,
                        "shadowY": 2.0,
                        "glowEnabled": true,
                        "glowColor": "#00E5FF",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "word_reveal",
                        "position": "center",
                        "twoLineHierarchy": true
                }
        },
        {
                "id": "editorial_layered",
                "name": "Editorial Layered Typography",
                "category": "cinematic master",
                "description": "Cream lowercase typography with combination of bold sans and elegant serif italic.",
                "platform": "Cinematic Master",
                "tagClass": "tag-minimal",
                "previewWord1": "paaji ch dekho",
                "previewWord2": "is",
                "style": {
                        "fontFamily": "Playfair Display",
                        "fontWeight": "700",
                        "fontSize": 42,
                        "textColor": "#FDF6E9",
                        "activeWordColor": "#FFFFFF",
                        "textCase": "normal",
                        "isItalic": true,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": false,
                        "strokeColor": "#000000",
                        "strokeWidth": 0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 5.0,
                        "shadowY": 2.5,
                        "glowEnabled": false,
                        "glowColor": "#FFFFFF",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "slide_up",
                        "position": "center",
                        "twoLineHierarchy": true
                }
        },
        {
                "id": "boxed",
                "name": "Boxed",
                "category": "card & aesthetic",
                "description": "White words on a rounded black card. Reads on any background.",
                "platform": "Card & Aesthetic",
                "tagClass": "tag-aesthetic",
                "previewWord1": "morning",
                "previewWord2": "matcha routine.",
                "style": {
                        "fontFamily": "Inter",
                        "fontWeight": "700",
                        "fontSize": 36,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FACC15",
                        "textCase": "normal",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": false,
                        "strokeColor": "#000000",
                        "strokeWidth": 0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 3.0,
                        "shadowY": 2.0,
                        "glowEnabled": false,
                        "glowColor": "#FACC15",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "solid",
                        "bgColor": "#000000",
                        "animation": "smooth_fade",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "subtitle",
                "name": "Subtitle",
                "category": "card & aesthetic",
                "description": "Classic subtitles on a dark box. Calm, and easy to read for long videos.",
                "platform": "Card & Aesthetic",
                "tagClass": "tag-aesthetic",
                "previewWord1": "morning",
                "previewWord2": "matcha routine.",
                "style": {
                        "fontFamily": "Inter",
                        "fontWeight": "600",
                        "fontSize": 34,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FEF08A",
                        "textCase": "normal",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": false,
                        "strokeColor": "#000000",
                        "strokeWidth": 0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 2.0,
                        "shadowY": 1.5,
                        "glowEnabled": false,
                        "glowColor": "#FEF08A",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "semi",
                        "bgColor": "#000000",
                        "animation": "smooth_fade",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "highlight",
                "name": "Highlight",
                "category": "card & aesthetic",
                "description": "The spoken word sits on a tilted colour pill.",
                "platform": "Card & Aesthetic",
                "tagClass": "tag-aesthetic",
                "previewWord1": "MORNING",
                "previewWord2": "MATCHA",
                "style": {
                        "fontFamily": "Montserrat",
                        "fontWeight": "800",
                        "fontSize": 38,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FFFFFF",
                        "textCase": "uppercase",
                        "isItalic": false,
                        "isTilted": true,
                        "tiltAngle": -2.0,
                        "threeDShadow": false,
                        "strokeEnabled": true,
                        "strokeColor": "#000000",
                        "strokeWidth": 1.5,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 3.0,
                        "shadowY": 2.0,
                        "glowEnabled": false,
                        "glowColor": "#FFFFFF",
                        "wordBox": true,
                        "wordBoxColor": "#7C3AED",
                        "wordBoxRadius": 8,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "active_word_pill",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "comic",
                "name": "Comic",
                "category": "card & aesthetic",
                "description": "Black on a tilted yellow panel with a hard shadow.",
                "platform": "Card & Aesthetic",
                "tagClass": "tag-aesthetic",
                "previewWord1": "MORNING",
                "previewWord2": "MATCHA",
                "style": {
                        "fontFamily": "Arial Black",
                        "fontWeight": "900",
                        "fontSize": 36,
                        "textColor": "#000000",
                        "activeWordColor": "#000000",
                        "textCase": "uppercase",
                        "isItalic": false,
                        "isTilted": true,
                        "tiltAngle": -1.5,
                        "threeDShadow": true,
                        "strokeEnabled": true,
                        "strokeColor": "#000000",
                        "strokeWidth": 2.5,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 2,
                        "shadowY": 4.0,
                        "glowEnabled": false,
                        "glowColor": "#000000",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "solid",
                        "bgColor": "#FDE047",
                        "animation": "soft_pop",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "terminal",
                "name": "Terminal",
                "category": "card & aesthetic",
                "description": "Mono on a dark strip, typed on. Tech.",
                "platform": "Card & Aesthetic",
                "tagClass": "tag-tech",
                "previewWord1": "> morning",
                "previewWord2": "match",
                "style": {
                        "fontFamily": "JetBrains Mono",
                        "fontWeight": "600",
                        "fontSize": 32,
                        "textColor": "#E2E8F0",
                        "activeWordColor": "#4ADE80",
                        "textCase": "normal",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": false,
                        "strokeColor": "#000000",
                        "strokeWidth": 0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 2.0,
                        "shadowY": 1.5,
                        "glowEnabled": false,
                        "glowColor": "#4ADE80",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "solid",
                        "bgColor": "#0F172A",
                        "animation": "typewriter",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "soft_glass",
                "name": "Soft glass",
                "category": "card & aesthetic",
                "description": "Sans on a see-through pill. Clean, modern.",
                "platform": "Card & Aesthetic",
                "tagClass": "tag-aesthetic",
                "previewWord1": "morning",
                "previewWord2": "matcha routine.",
                "style": {
                        "fontFamily": "Inter",
                        "fontWeight": "600",
                        "fontSize": 34,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FFFFFF",
                        "textCase": "normal",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": false,
                        "strokeColor": "#000000",
                        "strokeWidth": 0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 4.0,
                        "shadowY": 2.0,
                        "glowEnabled": false,
                        "glowColor": "#FFFFFF",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "glass",
                        "bgColor": "#FFFFFF",
                        "animation": "smooth_fade",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "magazine",
                "name": "Magazine",
                "category": "card & aesthetic",
                "description": "Fashion caps on a black band, italic.",
                "platform": "Card & Aesthetic",
                "tagClass": "tag-minimal",
                "previewWord1": "morning",
                "previewWord2": "MATCHA",
                "style": {
                        "fontFamily": "Playfair Display",
                        "fontWeight": "700",
                        "fontSize": 35,
                        "textColor": "#F8FAFC",
                        "activeWordColor": "#FFFFFF",
                        "textCase": "normal",
                        "isItalic": true,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": false,
                        "strokeColor": "#000000",
                        "strokeWidth": 0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 2.0,
                        "shadowY": 1.0,
                        "glowEnabled": false,
                        "glowColor": "#FFFFFF",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "solid",
                        "bgColor": "#000000",
                        "animation": "sentence_fade",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "highlighter",
                "name": "Highlighter",
                "category": "card & aesthetic",
                "description": "A highlighter swipes the key word. Tips, explainers.",
                "platform": "Card & Aesthetic",
                "tagClass": "tag-aesthetic",
                "previewWord1": "morning",
                "previewWord2": "matcha routine.",
                "style": {
                        "fontFamily": "Inter",
                        "fontWeight": "700",
                        "fontSize": 36,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#000000",
                        "textCase": "normal",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": true,
                        "strokeColor": "#000000",
                        "strokeWidth": 1.5,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 2.5,
                        "shadowY": 1.5,
                        "glowEnabled": false,
                        "glowColor": "#000000",
                        "wordBox": true,
                        "wordBoxColor": "#FACC15",
                        "wordBoxRadius": 4,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "word_highlight",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "paper",
                "name": "Paper",
                "category": "card & aesthetic",
                "description": "Typewriter on torn paper, typed on. Stories, journals.",
                "platform": "Card & Aesthetic",
                "tagClass": "tag-minimal",
                "previewWord1": "morning",
                "previewWord2": "matc",
                "style": {
                        "fontFamily": "Courier New",
                        "fontWeight": "700",
                        "fontSize": 33,
                        "textColor": "#1F2937",
                        "activeWordColor": "#111827",
                        "textCase": "normal",
                        "isItalic": false,
                        "isTilted": true,
                        "tiltAngle": -1.0,
                        "threeDShadow": false,
                        "strokeEnabled": false,
                        "strokeColor": "#000000",
                        "strokeWidth": 0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 4.0,
                        "shadowY": 2.5,
                        "glowEnabled": false,
                        "glowColor": "#111827",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "solid",
                        "bgColor": "#F3EDE2",
                        "animation": "typewriter",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "label",
                "name": "Label",
                "category": "card & aesthetic",
                "description": "Mono caps on a white label. Minimal, polished.",
                "platform": "Card & Aesthetic",
                "tagClass": "tag-aesthetic",
                "previewWord1": "MORNING",
                "previewWord2": "MATCHA",
                "style": {
                        "fontFamily": "JetBrains Mono",
                        "fontWeight": "800",
                        "fontSize": 34,
                        "textColor": "#000000",
                        "activeWordColor": "#000000",
                        "textCase": "uppercase",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": false,
                        "strokeColor": "#000000",
                        "strokeWidth": 0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 3.0,
                        "shadowY": 2.0,
                        "glowEnabled": false,
                        "glowColor": "#000000",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "solid",
                        "bgColor": "#FFFFFF",
                        "animation": "color_karaoke",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "sticker",
                "name": "Sticker",
                "category": "card & aesthetic",
                "description": "Rounded words on a white sticker, the key word on colour.",
                "platform": "Card & Aesthetic",
                "tagClass": "tag-aesthetic",
                "previewWord1": "morning",
                "previewWord2": "matcha routine.",
                "style": {
                        "fontFamily": "Poppins",
                        "fontWeight": "700",
                        "fontSize": 34,
                        "textColor": "#0F172A",
                        "activeWordColor": "#FFFFFF",
                        "textCase": "normal",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": false,
                        "strokeColor": "#000000",
                        "strokeWidth": 0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 4.0,
                        "shadowY": 2.5,
                        "glowEnabled": false,
                        "glowColor": "#FFFFFF",
                        "wordBox": true,
                        "wordBoxColor": "#FB7185",
                        "wordBoxRadius": 14,
                        "bgMode": "solid",
                        "bgColor": "#FFFFFF",
                        "animation": "active_word_pill",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "bold_pop",
                "name": "Bold pop",
                "category": "loud captions",
                "description": "Heavy white caps, black outline, the spoken word pops in yellow.",
                "platform": "Loud Captions",
                "tagClass": "tag-viral",
                "previewWord1": "MORNING",
                "previewWord2": "MATCHA",
                "style": {
                        "fontFamily": "Arial Black",
                        "fontWeight": "900",
                        "fontSize": 40,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FACC15",
                        "textCase": "uppercase",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": true,
                        "strokeColor": "#000000",
                        "strokeWidth": 3.5,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 3.0,
                        "shadowY": 2.0,
                        "glowEnabled": false,
                        "glowColor": "#FACC15",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "soft_pop",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "karaoke",
                "name": "Karaoke",
                "category": "loud captions",
                "description": "The whole line shows; words fill with colour as they're said.",
                "platform": "Loud Captions",
                "tagClass": "tag-viral",
                "previewWord1": "MORNING",
                "previewWord2": "MATCHA",
                "style": {
                        "fontFamily": "Montserrat",
                        "fontWeight": "800",
                        "fontSize": 38,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FACC15",
                        "textCase": "normal",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": true,
                        "strokeColor": "#000000",
                        "strokeWidth": 2.5,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 2.5,
                        "shadowY": 2.0,
                        "glowEnabled": false,
                        "glowColor": "#FACC15",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "color_karaoke",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "typewriter",
                "name": "Typewriter",
                "category": "loud captions",
                "description": "Words appear one by one, as they're said.",
                "platform": "Loud Captions",
                "tagClass": "tag-viral",
                "previewWord1": "MORNING",
                "previewWord2": "MATCHA",
                "style": {
                        "fontFamily": "Montserrat",
                        "fontWeight": "800",
                        "fontSize": 38,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FACC15",
                        "textCase": "uppercase",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": true,
                        "strokeColor": "#000000",
                        "strokeWidth": 3.0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 2.5,
                        "shadowY": 2.0,
                        "glowEnabled": false,
                        "glowColor": "#FACC15",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "typewriter",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "one_word",
                "name": "One word",
                "category": "loud captions",
                "description": "One huge word at a time, punched in. High energy.",
                "platform": "Loud Captions",
                "tagClass": "tag-viral",
                "previewWord1": "MATCHA",
                "previewWord2": "",
                "style": {
                        "fontFamily": "Anton",
                        "fontWeight": "900",
                        "fontSize": 58,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FFFFFF",
                        "textCase": "uppercase",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": true,
                        "strokeColor": "#000000",
                        "strokeWidth": 4.0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 4.0,
                        "shadowY": 3.0,
                        "glowEnabled": false,
                        "glowColor": "#FFFFFF",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "emphasis_scale",
                        "position": "center",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "neon",
                "name": "Neon",
                "category": "loud captions",
                "description": "Geometric caps with a coloured glow on the spoken word.",
                "platform": "Loud Captions",
                "tagClass": "tag-viral",
                "previewWord1": "MORNING",
                "previewWord2": "MATCHA",
                "style": {
                        "fontFamily": "Montserrat",
                        "fontWeight": "800",
                        "fontSize": 38,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#00F5FF",
                        "textCase": "uppercase",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": true,
                        "strokeColor": "#000000",
                        "strokeWidth": 2.0,
                        "shadowEnabled": true,
                        "shadowColor": "#00F5FF",
                        "shadowBlur": 16.0,
                        "shadowY": 1,
                        "glowEnabled": true,
                        "glowColor": "#00F5FF",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "color_karaoke",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "pop_3d",
                "name": "3D pop",
                "category": "loud captions",
                "description": "Chunky caps with a stacked 3D shadow; the spoken word jumps.",
                "platform": "Loud Captions",
                "tagClass": "tag-viral",
                "previewWord1": "MORNING",
                "previewWord2": "MATCHA",
                "style": {
                        "fontFamily": "Arial Black",
                        "fontWeight": "900",
                        "fontSize": 38,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FACC15",
                        "textCase": "uppercase",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": true,
                        "strokeEnabled": true,
                        "strokeColor": "#000000",
                        "strokeWidth": 3.0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 2,
                        "shadowY": 5.0,
                        "glowEnabled": false,
                        "glowColor": "#FACC15",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "emphasis_scale",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "gradient",
                "name": "Gradient",
                "category": "loud captions",
                "description": "Bold caps; the spoken word glows in a sunset gradient.",
                "platform": "Loud Captions",
                "tagClass": "tag-viral",
                "previewWord1": "MORNING",
                "previewWord2": "MATCHA",
                "style": {
                        "fontFamily": "Montserrat",
                        "fontWeight": "800",
                        "fontSize": 38,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FB923C",
                        "textCase": "uppercase",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": true,
                        "strokeColor": "#000000",
                        "strokeWidth": 2.8,
                        "shadowEnabled": true,
                        "shadowColor": "#F43F5E",
                        "shadowBlur": 10.0,
                        "shadowY": 2.0,
                        "glowEnabled": true,
                        "glowColor": "#FB923C",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "soft_pop",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        },
        {
                "id": "beast",
                "name": "Beast",
                "category": "loud captions",
                "description": "Huge condensed caps in three colours, punched in. Maximum energy.",
                "platform": "Loud Captions",
                "tagClass": "tag-viral",
                "previewWord1": "MORNING",
                "previewWord2": "MATCHA",
                "style": {
                        "fontFamily": "Anton",
                        "fontWeight": "900",
                        "fontSize": 48,
                        "textColor": "#FFFFFF",
                        "activeWordColor": "#FDE047",
                        "textCase": "uppercase",
                        "isItalic": false,
                        "isTilted": false,
                        "tiltAngle": 0,
                        "threeDShadow": false,
                        "strokeEnabled": true,
                        "strokeColor": "#000000",
                        "strokeWidth": 4.0,
                        "shadowEnabled": true,
                        "shadowColor": "#000000",
                        "shadowBlur": 4.0,
                        "shadowY": 3.0,
                        "glowEnabled": false,
                        "glowColor": "#FDE047",
                        "wordBox": false,
                        "wordBoxColor": "#4F46E5",
                        "wordBoxRadius": 6,
                        "bgMode": "none",
                        "bgColor": "#000000",
                        "animation": "emphasis_scale",
                        "position": "bottom",
                        "twoLineHierarchy": false
                }
        }
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
        initViralEnhancements();
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
            wordBoxColorPicker: document.getElementById('wordBoxColorPicker'),
            wordBoxColorHex: document.getElementById('wordBoxColorHex'),
            animationTypeSelect: document.getElementById('animationTypeSelect'),
            animationSpeedRange: document.getElementById('animationSpeedRange'),
            animationSpeedDisplay: document.getElementById('animationSpeedDisplay'),
            caseUpperBtn: document.getElementById('caseUpperBtn'),
            caseTitleBtn: document.getElementById('caseTitleBtn'),
            caseNormalBtn: document.getElementById('caseNormalBtn'),

            // Viral Enhancements
            watermarkPreview: document.getElementById('watermarkPreview'),
            watermarkPreviewImg: document.getElementById('watermarkPreviewImg'),
            watermarkPreviewText: document.getElementById('watermarkPreviewText'),
            watermarkToggle: document.getElementById('watermarkToggle'),
            watermarkFileInput: document.getElementById('watermarkFileInput'),
            watermarkUploadBtn: document.getElementById('watermarkUploadBtn'),
            watermarkPreviewRow: document.getElementById('watermarkPreviewRow'),
            watermarkThumbImg: document.getElementById('watermarkThumbImg'),
            watermarkRemoveBtn: document.getElementById('watermarkRemoveBtn'),
            watermarkTextInput: document.getElementById('watermarkTextInput'),
            watermarkPositionSelect: document.getElementById('watermarkPositionSelect'),
            watermarkScaleRange: document.getElementById('watermarkScaleRange'),
            watermarkScaleDisplay: document.getElementById('watermarkScaleDisplay'),
            watermarkOpacityRange: document.getElementById('watermarkOpacityRange'),
            watermarkOpacityDisplay: document.getElementById('watermarkOpacityDisplay'),

            outroCtaPreview: document.getElementById('outroCtaPreview'),
            outroAvatarLetter: document.getElementById('outroAvatarLetter'),
            outroAvatarImg: document.getElementById('outroAvatarImg'),
            outroChannelNameDisplay: document.getElementById('outroChannelNameDisplay'),
            outroHandleDisplay: document.getElementById('outroHandleDisplay'),
            outroToggle: document.getElementById('outroToggle'),
            outroChannelNameInput: document.getElementById('outroChannelNameInput'),
            outroHandleInput: document.getElementById('outroHandleInput'),
            outroDurationRange: document.getElementById('outroDurationRange'),
            outroDurationDisplay: document.getElementById('outroDurationDisplay'),

            sfxToggle: document.getElementById('sfxToggle'),
            sfxTypeSelect: document.getElementById('sfxTypeSelect'),
            sfxFreqSelect: document.getElementById('sfxFreqSelect'),
            sfxVolumeRange: document.getElementById('sfxVolumeRange'),
            sfxVolumeDisplay: document.getElementById('sfxVolumeDisplay'),
            sfxPreviewPlayBtn: document.getElementById('sfxPreviewPlayBtn'),

            brollToggle: document.getElementById('brollToggle'),
            brollFileInput: document.getElementById('brollFileInput'),
            brollUploadBtn: document.getElementById('brollUploadBtn'),
            brollPreviewRow: document.getElementById('brollPreviewRow'),
            brollNameBadge: document.getElementById('brollNameBadge'),
            brollRemoveBtn: document.getElementById('brollRemoveBtn'),
            brollModeSelect: document.getElementById('brollModeSelect'),
            brollStartInput: document.getElementById('brollStartInput'),
            brollDurationInput: document.getElementById('brollDurationInput'),
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
                state.projectId = res.project_id || state.projectId || '';
                showToast(`Video ready for AI captioning: ${res.filename}`, 'success', 2500);
                if (typeof debouncedSaveCaptionState === 'function') {
                    debouncedSaveCaptionState(400);
                }
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
            syncOutroPreviewToTime(current, duration);
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
    // 9. COLUMN 1: CANONICAL PRESETS IMPLEMENTATION
    // =========================================================================
    let canonicalApiPresets = [];

    async function loadCanonicalPresets() {
        try {
            const res = await fetch('/api/caption-studio/presets/canonical');
            const data = await res.json();
            if (data.success && Array.isArray(data.presets)) {
                canonicalApiPresets = data.presets.map(p => {
                    let pw1 = 'morning';
                    let pw2 = 'matcha';
                    let tagCls = 'tag-aesthetic';
                    const cat = p.category || 'Card & Aesthetic';
                    const catLower = cat.toLowerCase();

                    if (p.id === 'cinematic_creator') {
                        pw1 = 'BHAI SCOUT KIA';
                        pw2 = 'ROYA HOGA';
                        tagCls = 'tag-cinematic';
                    } else if (p.id === 'cinematic_minimal_hindi') {
                        pw1 = 'उसके आसपास';
                        pw2 = 'के लोग';
                        tagCls = 'tag-minimal';
                    } else if (p.id === 'bold_keyword_yellow') {
                        pw1 = 'AGAR';
                        pw2 = 'US DIN';
                        tagCls = 'tag-viral';
                    } else if (p.id === 'modern_kinetic_cyan') {
                        pw1 = 'with something';
                        pw2 = 'predictable';
                        tagCls = 'tag-podcast';
                    } else if (p.id === 'editorial_layered') {
                        pw1 = 'paaji ch dekho';
                        pw2 = 'is';
                        tagCls = 'tag-minimal';
                    } else if (p.id === 'terminal') {
                        pw1 = '> morning';
                        pw2 = 'match';
                        tagCls = 'tag-tech';
                    } else if (p.id === 'one_word') {
                        pw1 = 'MATCHA';
                        pw2 = '';
                        tagCls = 'tag-viral';
                    } else if (p.id === 'paper') {
                        pw1 = 'morning';
                        pw2 = 'matc';
                        tagCls = 'tag-minimal';
                    } else if (p.id === 'magazine') {
                        pw1 = 'morning';
                        pw2 = 'MATCHA';
                        tagCls = 'tag-minimal';
                    } else if (p.id === 'highlight' || p.id === 'comic' || p.id === 'label' || cat === 'Loud Captions') {
                        pw1 = 'MORNING';
                        pw2 = 'MATCHA';
                        tagCls = cat === 'Loud Captions' ? 'tag-viral' : 'tag-aesthetic';
                    } else if (['boxed', 'subtitle', 'soft_glass', 'highlighter', 'sticker'].includes(p.id)) {
                        pw1 = 'morning';
                        pw2 = 'matcha routine.';
                        tagCls = 'tag-aesthetic';
                    }

                    return {
                        id: p.id,
                        name: p.name,
                        category: catLower,
                        description: p.description || '',
                        platform: p.category || 'Creator Style',
                        tagClass: tagCls,
                        previewWord1: pw1,
                        previewWord2: pw2,
                        style: {
                            fontFamily: p.fontFamily || p.font_family || 'Inter',
                            fontWeight: String(p.fontWeight || p.font_weight || 700),
                            fontSize: p.fontSize || p.font_size || 36,
                            textColor: p.textColor || p.text_color || '#FFFFFF',
                            activeWordColor: p.activeWordColor || p.active_word_color || '#FFE000',
                            textCase: p.uppercase ? 'uppercase' : (p.textCase || 'normal'),
                            isItalic: Boolean(p.isItalic || p.is_italic || p.id === 'magazine' || p.id === 'editorial_layered'),
                            isTilted: Boolean(p.isTilted || p.is_tilted || p.id === 'comic' || p.id === 'highlight'),
                            tiltAngle: p.tiltAngle || p.tilt_angle || (p.id === 'comic' ? -2 : p.id === 'highlight' ? -1.5 : 0),
                            threeDShadow: Boolean(p.threeDShadow || p.three_d_shadow || p.id === 'pop_3d'),
                            strokeEnabled: Boolean(p.outlineEnabled || (p.outlineWidth && p.outlineWidth > 0)),
                            strokeColor: p.outlineColor || '#000000',
                            strokeWidth: p.outlineWidth || 0,
                            shadowEnabled: p.shadowEnabled !== false,
                            shadowColor: p.shadowColor || '#000000',
                            shadowBlur: p.shadowBlur || 2,
                            shadowY: p.shadowOffsetY || 1,
                            glowEnabled: Boolean(p.glow || p.glowEnabled),
                            glowColor: p.glowColor || p.glow_color || p.activeWordColor || '#FFE000',
                            wordBox: Boolean(p.wordBox),
                            wordBoxColor: p.wordBoxColor || '#4F46E5',
                            wordBoxRadius: p.wordBoxRadius || 6,
                            bgMode: p.bgMode || (p.backgroundOpacity > 0 ? 'semi' : (p.background ? 'solid' : 'none')),
                            bgColor: p.backgroundColor || '#000000',
                            animation: p.animation || 'color_karaoke',
                            position: p.position || 'bottom',
                            twoLineHierarchy: Boolean(p.twoLineHierarchy || p.two_line_hierarchy),
                        }
                    };
                });
                renderPresets();
            }
        } catch (e) {
            console.warn('Could not load canonical presets from API, using defaults:', e);
        }
    }

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

        loadCanonicalPresets();
        renderPresets();
    }

    function renderPresets() {
        if (!el.presetsGrid) return;
        el.presetsGrid.innerHTML = '';

        const allPresets = (canonicalApiPresets.length > 0 ? canonicalApiPresets : PRESETS).concat(customPresets);
        const filtered = allPresets.filter(p => {
            if (state.activeCategory === 'all') return true;
            return (p.category || '').toLowerCase() === state.activeCategory.toLowerCase();
        });

        filtered.forEach(preset => {
            const card = document.createElement('div');
            card.className = `preset-card ${preset.id === state.activePresetId ? 'active' : ''}`;
            card.setAttribute('data-preset-id', preset.id);

            const st = preset.style;
            const animLabelMap = {
                'color_karaoke': '✨ Karaoke',
                'smooth_fade': '🌊 Fade',
                'soft_pop': '💥 Pop',
                'active_word_pill': '💊 Pill',
                'slide_up': '⬆️ Slide',
                'slide_down': '⬇️ Drop',
                'typewriter': '⌨️ Type',
                'emphasis_scale': '🎯 Punch',
                'word_highlight': '🖍️ Highlight',
                'sentence_fade': '🌫️ Flow',
                'none': '⏹️ Static'
            };
            const animBadgeText = animLabelMap[st.animation] || (st.animation ? st.animation.replace('_', ' ') : '✨ Karaoke');

            // Generate specialized preview matching reference screenshots exactly
            let previewInnerHtml = '';
            let tiltStyle = '';

            if (preset.id === 'cinematic_creator') {
                previewInnerHtml = `
                    <div style="font-family:'Anton', sans-serif; text-transform:uppercase; text-align:center; line-height:1.15;">
                        <div style="font-size:11.5px; color:#FFFFFF; letter-spacing:0.5px; text-shadow:0 2px 4px rgba(0,0,0,0.8);">BHAI SCOUT KIA</div>
                        <div style="font-size:16px; color:#80D8FF; letter-spacing:0.5px; text-shadow:0 0 10px #0088FF, 0 0 16px rgba(0,136,255,0.7); font-weight:900;">ROYA HOGA</div>
                    </div>`;
            } else if (preset.id === 'cinematic_minimal_hindi') {
                previewInnerHtml = `
                    <div style="font-family:'Noto Sans Devanagari', sans-serif; font-size:13px; font-weight:600; color:#FFFFFF; text-shadow:0 1px 3px rgba(0,0,0,0.85); text-align:center;">
                        उसके आसपास के लोग
                    </div>`;
            } else if (preset.id === 'bold_keyword_yellow') {
                previewInnerHtml = `
                    <div style="font-family:'Anton', sans-serif; text-transform:uppercase; text-align:center; line-height:1.15;">
                        <div style="font-size:15px; font-weight:900; -webkit-text-stroke:0.8px #000; text-shadow:0 2px 4px #000;">
                            <span style="color:#FFEA00; text-shadow:0 0 8px rgba(255,234,0,0.6);">AGAR</span> <span style="color:#FFFFFF;">US DIN</span>
                        </div>
                        <div style="font-size:12px; color:#E2E8F0; -webkit-text-stroke:0.6px #000; text-shadow:0 2px 4px #000;">KD KE GHAR PE</div>
                    </div>`;
            } else if (preset.id === 'modern_kinetic_cyan') {
                previewInnerHtml = `
                    <div style="font-family:'Montserrat', sans-serif; font-weight:800; text-align:center; line-height:1.2;">
                        <span style="font-size:11px; color:#FFFFFF; text-shadow:0 2px 4px #000;">with</span>
                        <div style="font-size:16px; color:#00F0FF; text-shadow:0 0 10px #00E5FF, 0 0 18px rgba(0,229,255,0.6);">something</div>
                        <span style="font-size:11px; color:#FFFFFF; text-shadow:0 2px 4px #000;">predictable</span>
                    </div>`;
            } else if (preset.id === 'editorial_layered') {
                previewInnerHtml = `
                    <div style="text-align:center; line-height:1.2;">
                        <div style="font-family:'Playfair Display', serif; font-style:italic; font-weight:700; font-size:15px; color:#FDF6E9; text-shadow:0 2px 5px rgba(0,0,0,0.85);">paaji ch dekho</div>
                        <div style="font-family:'Inter', sans-serif; font-size:13px; font-weight:600; color:#FFFFFF; text-shadow:0 2px 4px rgba(0,0,0,0.85);">is</div>
                    </div>`;
            } else if (preset.id === 'boxed') {
                previewInnerHtml = `<span style="background:#000000; color:#FFFFFF; font-family:'Inter', sans-serif; font-size:11.5px; font-weight:700; border-radius:12px; padding:3px 9px; box-shadow:0 2px 6px rgba(0,0,0,0.6);">morning matcha routine.</span>`;
            } else if (preset.id === 'subtitle') {
                previewInnerHtml = `<span style="background:rgba(0,0,0,0.85); color:#FFFFFF; font-family:'Inter', sans-serif; font-size:11.5px; font-weight:600; border-radius:4px; padding:3px 8px;">morning matcha routine.</span>`;
            } else if (preset.id === 'highlight') {
                tiltStyle = 'transform: rotate(-1.5deg);';
                previewInnerHtml = `<span style="font-family:'Montserrat', sans-serif; font-weight:800; font-size:12.5px; color:#FFFFFF; text-shadow:0 2px 4px rgba(0,0,0,0.8);">MORNING <span style="background:#8B5CF6; color:#FFFFFF; border-radius:4px; padding:2px 6px;">MATCHA</span></span>`;
            } else if (preset.id === 'comic') {
                tiltStyle = 'transform: rotate(-2deg);';
                previewInnerHtml = `<span style="background:#FDE047; color:#000000; border:2px solid #000000; box-shadow:3px 3px 0 #000000; border-radius:3px; padding:2px 7px; font-weight:900; font-size:12.5px; font-family:'Arial Black', sans-serif;">MORNING MATCHA</span>`;
            } else if (preset.id === 'terminal') {
                previewInnerHtml = `<span style="background:#0A0E17; color:#22C55E; border-radius:3px; padding:3px 7px; font-family:'JetBrains Mono', monospace; font-size:10.5px; border:1px solid rgba(34,197,94,0.3);">&gt; morning match</span>`;
            } else if (preset.id === 'soft_glass') {
                previewInnerHtml = `<span style="background:rgba(255,255,255,0.18); backdrop-filter:blur(6px); border:1px solid rgba(255,255,255,0.25); color:#FFFFFF; border-radius:12px; padding:3px 9px; font-size:11.5px; font-weight:600; font-family:'Plus Jakarta Sans', sans-serif;">morning matcha routine.</span>`;
            } else if (preset.id === 'magazine') {
                previewInnerHtml = `<span style="background:#000000; color:#FFFFFF; padding:2px 8px; font-family:'Playfair Display', serif; font-size:12px; font-style:italic; border-radius:2px;">morning <strong style="font-style:normal; font-family:'Montserrat', sans-serif; font-weight:800;">MATCHA</strong></span>`;
            } else if (preset.id === 'highlighter') {
                previewInnerHtml = `<span style="font-family:'Inter', sans-serif; font-size:11.5px; font-weight:600; color:#FFFFFF; text-shadow:0 1px 3px #000;">morning <span style="background:#FDE047; color:#000000; padding:1px 4px; border-radius:2px; font-weight:700;">matcha</span> routine.</span>`;
            } else if (preset.id === 'paper') {
                previewInnerHtml = `<span style="background:#F5F5F0; color:#1C1917; border-radius:2px; padding:2px 7px; font-family:'JetBrains Mono', monospace; font-size:10.5px; box-shadow:1px 2px 4px rgba(0,0,0,0.3);">morning matc</span>`;
            } else if (preset.id === 'label') {
                previewInnerHtml = `<span style="background:#FFFFFF; color:#18181B; border-radius:2px; padding:2px 7px; font-family:'JetBrains Mono', monospace; font-weight:800; font-size:10.5px;">MORNING MATCHA</span>`;
            } else if (preset.id === 'sticker') {
                previewInnerHtml = `<span style="background:#FFFFFF; color:#18181B; border-radius:12px; padding:2px 7px; font-size:11px; font-weight:700; font-family:'Poppins', sans-serif;"><span style="background:#EC4899; color:#FFFFFF; border-radius:6px; padding:1px 5px;">morning</span> matcha routine.</span>`;
            } else if (preset.id === 'bold_pop') {
                previewInnerHtml = `<span style="font-family:'Anton', sans-serif; font-size:15px; color:#FFFFFF; -webkit-text-stroke:0.8px #000; text-shadow:0 2px 4px #000;">MORNING <span style="color:#FACC15;">MATCHA</span></span>`;
            } else if (preset.id === 'karaoke') {
                previewInnerHtml = `<span style="font-family:'Montserrat', sans-serif; font-weight:800; font-size:13px; color:#FFFFFF; -webkit-text-stroke:0.6px #000; text-shadow:0 2px 4px #000;">morning <span style="color:#FACC15;">matcha</span></span>`;
            } else if (preset.id === 'typewriter') {
                previewInnerHtml = `<span style="font-family:'Montserrat', sans-serif; font-weight:800; font-size:13px; color:#FFFFFF; -webkit-text-stroke:0.6px #000; text-shadow:0 2px 4px #000;">MORNING <span style="color:#FACC15;">MATCHA</span></span>`;
            } else if (preset.id === 'one_word') {
                previewInnerHtml = `<span style="font-family:'Anton', sans-serif; font-size:20px; color:#FFFFFF; -webkit-text-stroke:1px #000; text-shadow:0 3px 6px #000; letter-spacing:0.5px;">MATCHA</span>`;
            } else if (preset.id === 'neon') {
                previewInnerHtml = `<span style="font-family:'Montserrat', sans-serif; font-weight:800; font-size:13px; color:#FFFFFF; -webkit-text-stroke:0.6px #000; text-shadow:0 2px 4px #000;">MORNING <span style="color:#00F5FF; text-shadow:0 0 10px #00F5FF, 0 0 16px rgba(0,245,255,0.7);">MATCHA</span></span>`;
            } else if (preset.id === 'pop_3d') {
                previewInnerHtml = `<span style="font-family:'Arial Black', sans-serif; font-size:12.5px; color:#FFFFFF; text-shadow:2px 2px 0 #000, 3.5px 3.5px 0 #000;">MORNING <span style="color:#FACC15;">MATCHA</span></span>`;
            } else if (preset.id === 'gradient') {
                previewInnerHtml = `<span style="font-family:'Montserrat', sans-serif; font-weight:800; font-size:13px; color:#FFFFFF; -webkit-text-stroke:0.6px #000; text-shadow:0 2px 4px #000;">MORNING <span style="color:#FB923C; text-shadow:0 0 8px #EA580C;">MATCHA</span></span>`;
            } else if (preset.id === 'beast') {
                previewInnerHtml = `<span style="font-family:'Anton', sans-serif; font-size:16px; color:#FFFFFF; -webkit-text-stroke:1px #000; text-shadow:0 2px 4px #000;">MORNING <span style="color:#FDE047;">MATCHA</span></span>`;
            } else {
                // Generic Custom Preset fallback
                let textShadow = st.glowEnabled ? `0 0 10px ${st.glowColor || '#00FFCC'}` : st.shadowEnabled ? `0 ${st.shadowY || 2}px ${st.shadowBlur || 4}px ${st.shadowColor || '#000'}` : 'none';
                let textStroke = st.strokeEnabled ? `${st.strokeWidth || 1}px ${st.strokeColor || '#000'}` : 'none';
                let bgCss = st.bgMode === 'semi' ? 'background:rgba(15,23,42,0.7); border-radius:6px; padding:3px 7px;' : st.bgMode === 'solid' ? `background:${st.bgColor || '#000'}; border-radius:4px; padding:3px 7px;` : '';
                previewInnerHtml = `<span style="font-family:'${st.fontFamily}', sans-serif; font-weight:${st.fontWeight}; font-size:13px; color:${st.textColor}; text-transform:${st.textCase || 'normal'}; -webkit-text-stroke:${textStroke}; text-shadow:${textShadow}; ${bgCss}">${preset.previewWord1 || 'Custom'} <span style="color:${st.activeWordColor || '#FACC15'};">${preset.previewWord2 || 'Preset'}</span></span>`;
            }

            card.innerHTML = `
                <div class="preset-preview-box" style="${tiltStyle}">
                    ${previewInnerHtml}
                </div>
                <div class="preset-card-meta">
                    <div class="preset-card-header">
                        <span class="preset-card-title">${preset.name}</span>
                        <span class="preset-anim-tag" style="font-size:9.5px; font-weight:600; padding:1px 5px; border-radius:4px; background:rgba(255,255,255,0.08); color:var(--text-secondary);">${animBadgeText}</span>
                    </div>
                    ${preset.description ? `<p class="preset-card-desc" style="font-size:10.5px; color:var(--text-muted); margin:3px 0 0 0; line-height:1.35;">${preset.description}</p>` : ''}
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

        // Word Pill Accent Color
        if (el.wordBoxColorPicker) {
            el.wordBoxColorPicker.addEventListener('input', (e) => {
                activeStyle.wordBoxColor = e.target.value;
                if (el.wordBoxColorHex) {
                    el.wordBoxColorHex.textContent = e.target.value.toUpperCase();
                    el.wordBoxColorHex.style.color = e.target.value;
                }
                updateLiveCaptionOverlay();
            });
            el.wordBoxColorPicker.addEventListener('change', () => pushHistory());
        }

        // Animation
        if (el.animationTypeSelect) {
            el.animationTypeSelect.addEventListener('change', (e) => {
                pushHistory();
                activeStyle.animation = e.target.value;
                updateLiveCaptionOverlay();
                showToast(`Animation: ${e.target.options[e.target.selectedIndex].text}`, 'info', 1200);
            });
        }

        // Animation Speed
        if (el.animationSpeedRange) {
            el.animationSpeedRange.addEventListener('input', (e) => {
                const spd = parseFloat(e.target.value) || 1.0;
                activeStyle.animationSpeed = spd;
                if (el.animationSpeedDisplay) el.animationSpeedDisplay.textContent = spd.toFixed(1);
                updateLiveCaptionOverlay();
            });
            el.animationSpeedRange.addEventListener('change', () => pushHistory());
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
        if (el.wordBoxColorPicker) el.wordBoxColorPicker.value = st.wordBoxColor || '#10B981';
        if (el.wordBoxColorHex) {
            el.wordBoxColorHex.textContent = (st.wordBoxColor || '#10B981').toUpperCase();
            el.wordBoxColorHex.style.color = st.wordBoxColor || '#10B981';
        }
        if (el.textOpacityRange) el.textOpacityRange.value = st.textOpacity !== undefined ? st.textOpacity : 100;
        if (el.textOpacityDisplay) el.textOpacityDisplay.textContent = st.textOpacity !== undefined ? st.textOpacity : 100;

        // Animation selection mapping
        if (el.animationTypeSelect) {
            const rawAnim = (st.animation || 'color_karaoke').toLowerCase().replace('-', '_');
            const animAliases = {
                'pop': 'soft_pop',
                'fade_in': 'smooth_fade',
                'fade': 'smooth_fade',
                'bounce': 'soft_pop',
                'karaoke': 'color_karaoke',
                'word_pill': 'active_word_pill',
                'zoom': 'emphasis_scale',
                'scale': 'emphasis_scale'
            };
            const targetVal = animAliases[rawAnim] || rawAnim;
            let matched = false;
            for (let i = 0; i < el.animationTypeSelect.options.length; i++) {
                if (el.animationTypeSelect.options[i].value === targetVal) {
                    el.animationTypeSelect.selectedIndex = i;
                    matched = true;
                    break;
                }
            }
            if (!matched && el.animationTypeSelect.options.length > 0) {
                el.animationTypeSelect.value = 'color_karaoke';
            }
        }

        if (el.animationSpeedRange) {
            const spd = st.animationSpeed || st.animation_speed || 1.0;
            el.animationSpeedRange.value = spd;
            if (el.animationSpeedDisplay) el.animationSpeedDisplay.textContent = Number(spd).toFixed(1);
        }

        // Casing buttons
        const currentCase = (st.textCase || 'uppercase').toLowerCase();
        if (el.caseUpperBtn) el.caseUpperBtn.classList.toggle('active', currentCase === 'uppercase');
        if (el.caseTitleBtn) el.caseTitleBtn.classList.toggle('active', currentCase === 'capitalize' || currentCase === 'title');
        if (el.caseNormalBtn) el.caseNormalBtn.classList.toggle('active', currentCase === 'normal' || currentCase === 'lowercase');

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
        if (typeof debouncedSaveCaptionState === 'function') {
            debouncedSaveCaptionState(300);
        }
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
            format: el.exportFormatSelect ? el.exportFormatSelect.value : 'mp4',
            watermark: state.viralEnhancements.watermark.enabled ? state.viralEnhancements.watermark : null,
            outro_cta: state.viralEnhancements.outro_cta.enabled ? state.viralEnhancements.outro_cta : null,
            sfx: state.viralEnhancements.sfx.enabled ? state.viralEnhancements.sfx : null,
            b_rolls: (state.viralEnhancements.b_rolls[0] && state.viralEnhancements.b_rolls[0].enabled) ? state.viralEnhancements.b_rolls : null,
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
        const rotateStr = activeStyle.isTilted ? ` rotate(${activeStyle.tiltAngle || -1.5}deg)` : '';
        box.style.transform = `scale(${scaleVal})${rotateStr}`;
        box.style.justifyContent = activeStyle.textAlign === 'left' ? 'flex-start' :
                                   activeStyle.textAlign === 'right' ? 'flex-end' : 'center';

        // Background
        if (activeStyle.bgMode === 'semi') {
            box.style.background = `rgba(15, 23, 42, ${(activeStyle.bgOpacity || 65) / 100})`;
            box.style.borderRadius = `${activeStyle.bgRadius || 8}px`;
            box.style.padding = `${activeStyle.bgPadding || 8}px 14px`;
        } else if (activeStyle.bgMode === 'glass') {
            box.style.background = 'rgba(255, 255, 255, 0.18)';
            box.style.backdropFilter = 'blur(10px)';
            box.style.borderRadius = '24px';
            box.style.padding = '8px 18px';
            box.style.border = '1px solid rgba(255, 255, 255, 0.25)';
            box.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.37)';
        } else if (activeStyle.bgMode === 'solid') {
            const hex = activeStyle.bgColor || '#000000';
            box.style.background = hex;
            box.style.borderRadius = `${activeStyle.bgRadius || 6}px`;
            box.style.padding = `${activeStyle.bgPadding || 6}px 12px`;
            if (activeStyle.id === 'comic') {
                box.style.border = '2.5px solid #000000';
                box.style.boxShadow = '4px 4px 0px #000000';
            } else {
                box.style.border = 'none';
                box.style.boxShadow = 'none';
            }
        } else if (activeStyle.bgMode === 'highlight') {
            box.style.background = 'transparent';
            box.style.padding = '4px';
            box.style.border = 'none';
            box.style.boxShadow = 'none';
        } else {
            box.style.background = 'transparent';
            box.style.padding = '0';
            box.style.border = 'none';
            box.style.boxShadow = 'none';
        }

        applyActiveStyleToDOM();
    }

    function applyActiveStyleToDOM() {
        const box = el.captionDragBox;
        if (!box) return;

        // Text Stroke
        const textStroke = (activeStyle.strokeEnabled && activeStyle.strokeWidth > 0) ?
                           `${activeStyle.strokeWidth}px ${activeStyle.strokeColor || '#000000'}` : 'none';

        // Text Shadow / Glow / 3D Shadow
        let textShadow = 'none';
        if (activeStyle.threeDShadow) {
            textShadow = '2px 2px 0px #000000, 4px 4px 0px #000000';
        } else if (activeStyle.glowEnabled) {
            textShadow = `0 0 ${activeStyle.glowIntensity || 14}px ${activeStyle.glowColor || '#10B981'}`;
        } else if (activeStyle.shadowEnabled) {
            textShadow = `0 ${activeStyle.shadowY || 2}px ${activeStyle.shadowBlur || 6}px ${activeStyle.shadowColor || '#000000'}`;
        }

        // Casing
        const textTransform = activeStyle.textCase === 'uppercase' ? 'uppercase' :
                              activeStyle.textCase === 'capitalize' ? 'capitalize' : 'none';

        // Opacity
        const alpha = (activeStyle.textOpacity !== undefined ? activeStyle.textOpacity : 100) / 100;

        // Animation name normalization
        const anim = (activeStyle.animation || 'color_karaoke').toLowerCase().replace('-', '_');

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
            w.style.display = 'inline-block';
            w.style.margin = '0 3px';
            w.style.transition = 'all 0.16s cubic-bezier(0.16, 1, 0.3, 1)';

            const isActive = w.classList.contains('active-karaoke-word');
            if (isActive) {
                if (anim === 'active_word_pill' || activeStyle.wordBox) {
                    const pillBg = activeStyle.wordBoxColor || activeStyle.activeWordColor || '#10B981';
                    w.style.color = '#FFFFFF';
                    w.style.background = pillBg;
                    w.style.padding = '3px 12px';
                    w.style.borderRadius = `${activeStyle.wordBoxRadius || 8}px`;
                    w.style.boxShadow = '0 4px 14px rgba(0,0,0,0.38)';
                    w.style.transform = 'scale(1.04)';
                    w.style.opacity = '1';
                } else if (anim === 'soft_pop' || anim === 'pop') {
                    w.style.color = activeStyle.activeWordColor || '#22C55E';
                    w.style.background = 'transparent';
                    w.style.padding = '0';
                    w.style.borderRadius = '0';
                    w.style.boxShadow = 'none';
                    w.style.transform = 'scale(1.10)';
                    w.style.opacity = '1';
                } else if (anim === 'emphasis_scale') {
                    w.style.color = activeStyle.activeWordColor || '#22C55E';
                    w.style.background = 'transparent';
                    w.style.padding = '0';
                    w.style.borderRadius = '0';
                    w.style.boxShadow = 'none';
                    w.style.transform = 'scale(1.18)';
                    w.style.fontWeight = '800';
                    w.style.opacity = '1';
                } else if (anim === 'slide_up') {
                    w.style.color = activeStyle.activeWordColor || '#22C55E';
                    w.style.background = 'transparent';
                    w.style.padding = '0';
                    w.style.borderRadius = '0';
                    w.style.boxShadow = 'none';
                    w.style.transform = 'translateY(-5px)';
                    w.style.opacity = '1';
                } else if (anim === 'slide_down') {
                    w.style.color = activeStyle.activeWordColor || '#22C55E';
                    w.style.background = 'transparent';
                    w.style.padding = '0';
                    w.style.borderRadius = '0';
                    w.style.boxShadow = 'none';
                    w.style.transform = 'translateY(5px)';
                    w.style.opacity = '1';
                } else if (anim === 'word_highlight') {
                    w.style.color = activeStyle.activeWordColor || '#22C55E';
                    w.style.background = 'rgba(255, 230, 0, 0.28)';
                    w.style.padding = '2px 8px';
                    w.style.borderRadius = '4px';
                    w.style.boxShadow = 'none';
                    w.style.transform = 'none';
                    w.style.opacity = '1';
                } else if (anim === 'smooth_fade') {
                    w.style.color = activeStyle.activeWordColor || '#22C55E';
                    w.style.background = 'transparent';
                    w.style.padding = '0';
                    w.style.borderRadius = '0';
                    w.style.boxShadow = 'none';
                    w.style.transform = 'none';
                    w.style.opacity = '1';
                } else {
                    // Default color_karaoke / typewriter / sentence_fade / none
                    w.style.color = activeStyle.activeWordColor || '#22C55E';
                    w.style.borderRadius = '0';
                    w.style.boxShadow = 'none';
                    if (activeStyle.bgMode === 'highlight') {
                        w.style.background = 'rgba(0,0,0,0.85)';
                        w.style.padding = '2px 8px';
                        w.style.borderRadius = '6px';
                    } else {
                        w.style.background = 'transparent';
                        w.style.padding = '0';
                    }
                    w.style.transform = 'none';
                    w.style.opacity = '1';
                }
            } else {
                w.style.color = activeStyle.textColor || '#FFFFFF';
                w.style.background = 'transparent';
                w.style.padding = '0';
                w.style.borderRadius = '0';
                w.style.transform = 'none';
                w.style.boxShadow = 'none';
                if (anim === 'smooth_fade') {
                    w.style.opacity = Math.max(0.40, alpha * 0.65);
                } else {
                    w.style.opacity = alpha;
                }
            }
        });
    }

    // =========================================================================
    // =========================================================================
    // 15. PRELOAD BACKEND DATA & AUTO-SAVE ENGINE
    // =========================================================================
    let _saveCaptionTimer = null;
    function debouncedSaveCaptionState(delay = 1200) {
        clearTimeout(_saveCaptionTimer);
        _saveCaptionTimer = setTimeout(() => {
            saveCaptionStateNow();
        }, delay);
    }

    async function saveCaptionStateNow(useBeacon = false) {
        if (!state.serverFilename && (!state.captions || !state.captions.length)) {
            return;
        }
        const payload = {
            project_id: state.projectId || '',
            filename: state.serverFilename || '',
            video_filename: state.serverFilename || '',
            captions: state.captions || [],
            style: activeStyle,
            state: {
                origin: 'caption_studio',
                activePresetId: state.activePresetId,
                viral_enhancements: state.viralEnhancements
            }
        };

        if (useBeacon && navigator.sendBeacon) {
            try {
                const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
                navigator.sendBeacon('/api/caption-studio/save-state', blob);
                return;
            } catch (e) {}
        }

        try {
            const res = await fetch('/api/caption-studio/save-state', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.success && data.project_id) {
                state.projectId = data.project_id;
                const url = new URL(window.location.href);
                if (!url.searchParams.get('project_id')) {
                    url.searchParams.set('project_id', data.project_id);
                    window.history.replaceState({}, '', url.toString());
                }
            }
        } catch (err) {
            console.warn('Caption Studio auto-save failed:', err);
        }
    }

    function initPreloadData() {
        const urlParams = new URLSearchParams(window.location.search);
        const pId = urlParams.get('project_id') || urlParams.get('projectId');
        if (pId) {
            state.projectId = pId;
        }

        if (el.captionContextData) {
            const ctxProjId = el.captionContextData.getAttribute('data-project-id');
            if (ctxProjId && !state.projectId) {
                state.projectId = ctxProjId;
            }

            const sourceFile = el.captionContextData.getAttribute('data-source-file');
            if (sourceFile && !state.serverFilename) {
                state.serverFilename = sourceFile;
            }

            const rawPreload = el.captionContextData.getAttribute('data-preload');
            if (rawPreload && rawPreload !== 'null') {
                try {
                    const preload = JSON.parse(rawPreload);
                    if (preload && preload.video_url) {
                        state.serverFilename = preload.filename || sourceFile || state.serverFilename || '';
                        loadVideoSource(preload.video_url, preload.filename || 'Preloaded Video');
                    }
                } catch (e) {
                    console.warn('Caption Studio: Preload video parse error', e);
                }
            }

            const rawSavedCaptions = el.captionContextData.getAttribute('data-saved-captions');
            if (rawSavedCaptions && rawSavedCaptions !== 'null') {
                try {
                    const savedCaps = JSON.parse(rawSavedCaptions);
                    if (Array.isArray(savedCaps) && savedCaps.length > 0) {
                        state.captions = savedCaps;
                        if (el.captionOverlayContainer) el.captionOverlayContainer.style.display = 'flex';
                        if (el.videoBottomTransport) el.videoBottomTransport.style.display = 'flex';
                        updateLiveCaptionOverlay();
                    }
                } catch (e) {
                    console.warn('Caption Studio: Saved captions parse error', e);
                }
            }

            const rawSavedStyle = el.captionContextData.getAttribute('data-saved-style');
            if (rawSavedStyle && rawSavedStyle !== 'null') {
                try {
                    const savedSt = JSON.parse(rawSavedStyle);
                    if (savedSt && typeof savedSt === 'object') {
                        Object.assign(activeStyle, savedSt);
                        applyStyleToControls(activeStyle);
                        updateLiveCaptionOverlay();
                    }
                } catch (e) {
                    console.warn('Caption Studio: Saved style parse error', e);
                }
            }
        }

        // If project_id exists but captions were not preloaded via HTML, fetch state from backend
        if (state.projectId && (!state.captions || !state.captions.length)) {
            fetch(`/api/caption-studio/load-state?project_id=${encodeURIComponent(state.projectId)}`)
                .then(r => r.json())
                .then(res => {
                    if (res.success && res.state) {
                        if (res.state.captions && res.state.captions.length) {
                            state.captions = res.state.captions;
                            if (el.captionOverlayContainer) el.captionOverlayContainer.style.display = 'flex';
                            if (el.videoBottomTransport) el.videoBottomTransport.style.display = 'flex';
                            updateLiveCaptionOverlay();
                        }
                        if (res.state.caption_style) {
                            Object.assign(activeStyle, res.state.caption_style);
                            applyStyleToControls(activeStyle);
                            updateLiveCaptionOverlay();
                        }
                        if (res.state.video_filename && !state.videoLoaded) {
                            state.serverFilename = res.state.video_filename;
                            loadVideoSource(`/download/input/${encodeURIComponent(res.state.video_filename)}`, res.state.video_filename);
                        }
                    }
                })
                .catch(err => console.warn('Caption Studio: Load state fetch error', err));
        }

        // Auto-save listeners on page departure / app switch
        window.addEventListener('beforeunload', () => {
            saveCaptionStateNow(true);
        });
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') {
                saveCaptionStateNow(true);
            }
        });
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

    // =========================================================================
    // 17. VIRAL ENHANCEMENTS ENGINE (WATERMARK, OUTRO CTA, SFX, B-ROLL)
    // =========================================================================
    function initViralEnhancements() {
        initWatermarkControls();
        initOutroCtaControls();
        initSfxControls();
        initBRollControls();
    }

    function initWatermarkControls() {
        const wm = state.viralEnhancements.watermark;

        if (el.watermarkToggle) {
            el.watermarkToggle.addEventListener('change', (e) => {
                wm.enabled = e.target.checked;
                updateWatermarkPreview();
            });
        }

        if (el.watermarkUploadBtn && el.watermarkFileInput) {
            el.watermarkUploadBtn.addEventListener('click', () => el.watermarkFileInput.click());
            el.watermarkFileInput.addEventListener('change', () => {
                const file = el.watermarkFileInput.files[0];
                if (!file) return;

                const formData = new FormData();
                formData.append('logo', file);

                showToast('Uploading channel logo...', 'info', 2000);
                fetch('/api/caption-studio/upload-logo', {
                    method: 'POST',
                    body: formData
                })
                .then(r => r.json())
                .then(res => {
                    if (res.success) {
                        wm.image_path = res.file_path;
                        wm.image_url = res.url;
                        if (el.watermarkThumbImg) el.watermarkThumbImg.src = res.url;
                        if (el.watermarkPreviewRow) el.watermarkPreviewRow.style.display = 'flex';
                        if (el.watermarkToggle && !el.watermarkToggle.checked) {
                            el.watermarkToggle.checked = true;
                            wm.enabled = true;
                        }
                        updateWatermarkPreview();
                        showToast('Channel logo attached successfully!', 'success');
                    } else {
                        showToast(res.error || 'Failed to upload logo', 'error');
                    }
                })
                .catch(err => showToast(`Upload error: ${err.message}`, 'error'));
            });
        }

        if (el.watermarkRemoveBtn) {
            el.watermarkRemoveBtn.addEventListener('click', () => {
                wm.image_path = '';
                wm.image_url = '';
                if (el.watermarkFileInput) el.watermarkFileInput.value = '';
                if (el.watermarkPreviewRow) el.watermarkPreviewRow.style.display = 'none';
                updateWatermarkPreview();
                showToast('Logo removed', 'info');
            });
        }

        if (el.watermarkTextInput) {
            el.watermarkTextInput.addEventListener('input', (e) => {
                wm.text = e.target.value.trim();
                updateWatermarkPreview();
            });
        }

        if (el.watermarkPositionSelect) {
            el.watermarkPositionSelect.addEventListener('change', (e) => {
                wm.position = e.target.value;
                updateWatermarkPreview();
            });
        }

        if (el.watermarkScaleRange) {
            el.watermarkScaleRange.addEventListener('input', (e) => {
                wm.scale_pct = parseInt(e.target.value, 10);
                if (el.watermarkScaleDisplay) el.watermarkScaleDisplay.textContent = wm.scale_pct;
                updateWatermarkPreview();
            });
        }

        if (el.watermarkOpacityRange) {
            el.watermarkOpacityRange.addEventListener('input', (e) => {
                wm.opacity = parseInt(e.target.value, 10);
                if (el.watermarkOpacityDisplay) el.watermarkOpacityDisplay.textContent = wm.opacity;
                updateWatermarkPreview();
            });
        }
    }

    function updateWatermarkPreview() {
        const wm = state.viralEnhancements.watermark;
        if (!el.watermarkPreview) return;

        if (!wm.enabled || (!wm.image_url && !wm.text)) {
            el.watermarkPreview.style.display = 'none';
            return;
        }

        el.watermarkPreview.style.display = 'flex';
        el.watermarkPreview.style.opacity = (wm.opacity / 100).toString();

        // Clear previous placement
        el.watermarkPreview.style.top = '';
        el.watermarkPreview.style.bottom = '';
        el.watermarkPreview.style.left = '';
        el.watermarkPreview.style.right = '';
        el.watermarkPreview.style.transform = '';

        const margin = '16px';
        switch (wm.position) {
            case 'top_right':
                el.watermarkPreview.style.top = margin;
                el.watermarkPreview.style.right = margin;
                break;
            case 'top_left':
                el.watermarkPreview.style.top = margin;
                el.watermarkPreview.style.left = margin;
                break;
            case 'bottom_right':
                el.watermarkPreview.style.bottom = '85px';
                el.watermarkPreview.style.right = margin;
                break;
            case 'bottom_left':
                el.watermarkPreview.style.bottom = '85px';
                el.watermarkPreview.style.left = margin;
                break;
            case 'top_center':
                el.watermarkPreview.style.top = margin;
                el.watermarkPreview.style.left = '50%';
                el.watermarkPreview.style.transform = 'translateX(-50%)';
                break;
            default:
                el.watermarkPreview.style.top = margin;
                el.watermarkPreview.style.right = margin;
        }

        if (wm.image_url) {
            if (el.watermarkPreviewImg) {
                el.watermarkPreviewImg.src = wm.image_url;
                el.watermarkPreviewImg.style.display = 'block';
                const px = Math.round(280 * (wm.scale_pct / 100));
                el.watermarkPreviewImg.style.maxWidth = `${px}px`;
                el.watermarkPreviewImg.style.maxHeight = `${px}px`;
            }
            if (el.watermarkPreviewText) el.watermarkPreviewText.style.display = 'none';
        } else if (wm.text) {
            if (el.watermarkPreviewText) {
                el.watermarkPreviewText.textContent = wm.text;
                el.watermarkPreviewText.style.display = 'block';
                const fontSize = Math.max(10, Math.round(18 * (wm.scale_pct / 16)));
                el.watermarkPreviewText.style.fontSize = `${fontSize}px`;
            }
            if (el.watermarkPreviewImg) el.watermarkPreviewImg.style.display = 'none';
        }
    }

    function initOutroCtaControls() {
        const outro = state.viralEnhancements.outro_cta;

        if (el.outroToggle) {
            el.outroToggle.addEventListener('change', (e) => {
                outro.enabled = e.target.checked;
                updateOutroPreview();
            });
        }

        if (el.outroChannelNameInput) {
            el.outroChannelNameInput.addEventListener('input', (e) => {
                outro.channel_name = e.target.value.trim() || 'UpClip Creator';
                updateOutroPreview();
            });
        }

        if (el.outroHandleInput) {
            el.outroHandleInput.addEventListener('input', (e) => {
                outro.handle = e.target.value.trim() || '@creator';
                updateOutroPreview();
            });
        }

        if (el.outroDurationRange) {
            el.outroDurationRange.addEventListener('input', (e) => {
                outro.duration = parseInt(e.target.value, 10);
                if (el.outroDurationDisplay) el.outroDurationDisplay.textContent = outro.duration;
            });
        }
    }

    function updateOutroPreview() {
        const outro = state.viralEnhancements.outro_cta;
        if (!el.outroCtaPreview) return;

        if (!outro.enabled) {
            el.outroCtaPreview.style.display = 'none';
            return;
        }

        el.outroCtaPreview.style.display = 'flex';
        if (el.outroChannelNameDisplay) {
            el.outroChannelNameDisplay.textContent = outro.channel_name || 'UpClip Creator';
        }
        if (el.outroHandleDisplay) {
            el.outroHandleDisplay.textContent = outro.handle || '@creator';
        }
        if (el.outroAvatarLetter) {
            const firstLetter = (outro.channel_name || 'U').charAt(0).toUpperCase();
            el.outroAvatarLetter.textContent = firstLetter;
        }
    }

    function syncOutroPreviewToTime(current, duration) {
        if (!el.outroCtaPreview) return;
        const outro = state.viralEnhancements.outro_cta;
        if (!outro.enabled) {
            el.outroCtaPreview.style.display = 'none';
            return;
        }
        const outroDur = outro.duration || 4;
        if (duration > 0 && current >= Math.max(0, duration - outroDur)) {
            el.outroCtaPreview.style.display = 'flex';
        } else {
            // Only hide during playback if video is actively playing
            if (state.videoElement && !state.videoElement.paused) {
                el.outroCtaPreview.style.display = 'none';
            }
        }
    }

    function initSfxControls() {
        const sfx = state.viralEnhancements.sfx;

        if (el.sfxToggle) {
            el.sfxToggle.addEventListener('change', (e) => {
                sfx.enabled = e.target.checked;
            });
        }

        if (el.sfxTypeSelect) {
            el.sfxTypeSelect.addEventListener('change', (e) => {
                sfx.sound_type = e.target.value;
            });
        }

        if (el.sfxFreqSelect) {
            el.sfxFreqSelect.addEventListener('change', (e) => {
                sfx.trigger_cue = e.target.value;
            });
        }

        if (el.sfxVolumeRange) {
            el.sfxVolumeRange.addEventListener('input', (e) => {
                sfx.volume = parseInt(e.target.value, 10);
                if (el.sfxVolumeDisplay) el.sfxVolumeDisplay.textContent = sfx.volume;
            });
        }

        if (el.sfxPreviewPlayBtn) {
            el.sfxPreviewPlayBtn.addEventListener('click', () => {
                const soundType = (el.sfxTypeSelect ? el.sfxTypeSelect.value : sfx.sound_type) || 'whoosh';
                const audioPath = `/static/audio/${soundType}.wav`;
                try {
                    const audio = new Audio(audioPath);
                    audio.volume = Math.max(0.05, Math.min(1.0, (sfx.volume || 70) / 100));
                    audio.play().catch(err => {
                        console.warn('[SFX Preview] audio play error:', err);
                    });
                } catch (err) {
                    console.warn('[SFX Preview] failed to instantiate Audio:', err);
                }
            });
        }
    }

    function initBRollControls() {
        const brolls = state.viralEnhancements.b_rolls;
        const broll = brolls[0];

        if (el.brollToggle) {
            el.brollToggle.addEventListener('change', (e) => {
                broll.enabled = e.target.checked;
            });
        }

        if (el.brollUploadBtn && el.brollFileInput) {
            el.brollUploadBtn.addEventListener('click', () => el.brollFileInput.click());
            el.brollFileInput.addEventListener('change', () => {
                const file = el.brollFileInput.files[0];
                if (!file) return;

                const formData = new FormData();
                formData.append('broll', file);

                showToast('Uploading B-roll clip...', 'info', 2000);
                fetch('/api/caption-studio/upload-broll', {
                    method: 'POST',
                    body: formData
                })
                .then(r => r.json())
                .then(res => {
                    if (res.success) {
                        broll.file_path = res.file_path;
                        broll.file_url = res.url;
                        broll.file_name = file.name;
                        if (el.brollNameBadge) el.brollNameBadge.textContent = file.name;
                        if (el.brollPreviewRow) el.brollPreviewRow.style.display = 'flex';
                        if (el.brollToggle && !el.brollToggle.checked) {
                            el.brollToggle.checked = true;
                            broll.enabled = true;
                        }
                        showToast('B-Roll clip attached successfully!', 'success');
                    } else {
                        showToast(res.error || 'Failed to upload B-roll', 'error');
                    }
                })
                .catch(err => showToast(`Upload error: ${err.message}`, 'error'));
            });
        }

        if (el.brollRemoveBtn) {
            el.brollRemoveBtn.addEventListener('click', () => {
                broll.file_path = '';
                broll.file_url = '';
                broll.file_name = '';
                if (el.brollFileInput) el.brollFileInput.value = '';
                if (el.brollPreviewRow) el.brollPreviewRow.style.display = 'none';
                showToast('B-Roll clip removed', 'info');
            });
        }

        if (el.brollModeSelect) {
            el.brollModeSelect.addEventListener('change', (e) => {
                broll.mode = e.target.value;
            });
        }

        if (el.brollStartInput) {
            el.brollStartInput.addEventListener('change', (e) => {
                broll.start_time = parseFloat(e.target.value) || 0.0;
            });
        }

        if (el.brollDurationInput) {
            el.brollDurationInput.addEventListener('change', (e) => {
                broll.duration = parseFloat(e.target.value) || 3.0;
            });
        }
    }
})();
