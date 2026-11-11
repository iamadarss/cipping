import { create } from "zustand";
import { v4 as uuidv4 } from "uuid";
import type { CaptionSegment, CaptionStyle, ProjectState, DragState } from "../types";

export const CANONICAL_PRESET_STYLES: CaptionStyle[] = [
  // =========================================================================
  // 1. CARD & AESTHETIC (Image 1)
  // =========================================================================
  {
    id: "boxed",
    name: "Boxed",
    category: "Card & Aesthetic",
    description: "White words on a rounded black card. Reads on any background.",
    fontFamily: "Inter",
    fontWeight: 700,
    fontSize: 36,
    letterSpacing: 0.2,
    lineHeight: 1.25,
    textColor: "#FFFFFF",
    activeWordColor: "#FACC15",
    backgroundColor: "#000000",
    backgroundOpacity: 0.88,
    bgMode: "solid",
    outlineColor: "#000000",
    outlineWidth: 0,
    outlineEnabled: false,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 2,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "smooth_fade",
    animationSpeed: 0.2,
    maxLines: 2,
    maxWordsPerLine: 4,
    isSystem: true,
  },
  {
    id: "subtitle",
    name: "Subtitle",
    category: "Card & Aesthetic",
    description: "Classic subtitles on a dark box. Calm, and easy to read for long videos.",
    fontFamily: "Inter",
    fontWeight: 600,
    fontSize: 34,
    letterSpacing: 0.0,
    lineHeight: 1.30,
    textColor: "#FFFFFF",
    activeWordColor: "#FEF08A",
    backgroundColor: "#000000",
    backgroundOpacity: 0.75,
    bgMode: "semi",
    outlineColor: "#000000",
    outlineWidth: 0,
    outlineEnabled: false,
    shadowColor: "#000000",
    shadowBlur: 2,
    shadowOffsetY: 1.5,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "smooth_fade",
    animationSpeed: 0.22,
    maxLines: 2,
    maxWordsPerLine: 5,
    isSystem: true,
  },
  {
    id: "highlight",
    name: "Highlight",
    category: "Card & Aesthetic",
    description: "The spoken word sits on a tilted colour pill.",
    fontFamily: "Montserrat",
    fontWeight: 800,
    fontSize: 38,
    letterSpacing: 0.5,
    lineHeight: 1.20,
    uppercase: true,
    textColor: "#FFFFFF",
    activeWordColor: "#FFFFFF",
    wordBox: true,
    wordBoxColor: "#7C3AED",
    wordBoxRadius: 8,
    isTilted: true,
    tiltAngle: -2.0,
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    bgMode: "none",
    outlineColor: "#000000",
    outlineWidth: 1.5,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 2,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "active_word_pill",
    animationSpeed: 0.18,
    maxLines: 2,
    maxWordsPerLine: 3,
    isSystem: true,
  },
  {
    id: "comic",
    name: "Comic",
    category: "Card & Aesthetic",
    description: "Black on a tilted yellow panel with a hard shadow.",
    fontFamily: "Arial Black",
    fontWeight: 900,
    fontSize: 36,
    letterSpacing: 0.5,
    lineHeight: 1.15,
    uppercase: true,
    textColor: "#000000",
    activeWordColor: "#E11D48",
    backgroundColor: "#FDE047",
    backgroundOpacity: 1.0,
    bgMode: "solid",
    isTilted: true,
    tiltAngle: -1.5,
    outlineColor: "#000000",
    outlineWidth: 2.5,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 0,
    shadowOffsetY: 4,
    shadowEnabled: true,
    threeDShadow: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "soft_pop",
    animationSpeed: 0.18,
    maxLines: 2,
    maxWordsPerLine: 3,
    isSystem: true,
  },
  {
    id: "terminal",
    name: "Terminal",
    category: "Card & Aesthetic",
    description: "Mono on a dark strip, typed on. Tech.",
    fontFamily: "JetBrains Mono",
    fontWeight: 600,
    fontSize: 32,
    letterSpacing: 0.0,
    lineHeight: 1.25,
    textColor: "#E2E8F0",
    activeWordColor: "#4ADE80",
    backgroundColor: "#0F172A",
    backgroundOpacity: 0.95,
    bgMode: "solid",
    outlineColor: "#000000",
    outlineWidth: 0,
    outlineEnabled: false,
    shadowColor: "#000000",
    shadowBlur: 2,
    shadowOffsetY: 1.5,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "typewriter",
    animationSpeed: 0.15,
    maxLines: 2,
    maxWordsPerLine: 4,
    isSystem: true,
  },
  {
    id: "soft_glass",
    name: "Soft glass",
    category: "Card & Aesthetic",
    description: "Sans on a see-through pill. Clean, modern.",
    fontFamily: "Inter",
    fontWeight: 600,
    fontSize: 34,
    letterSpacing: 0.2,
    lineHeight: 1.25,
    textColor: "#FFFFFF",
    activeWordColor: "#FFFFFF",
    backgroundColor: "#FFFFFF",
    backgroundOpacity: 0.18,
    bgMode: "glass",
    outlineColor: "#000000",
    outlineWidth: 0,
    outlineEnabled: false,
    shadowColor: "#000000",
    shadowBlur: 4,
    shadowOffsetY: 2,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "smooth_fade",
    animationSpeed: 0.20,
    maxLines: 2,
    maxWordsPerLine: 4,
    isSystem: true,
  },
  {
    id: "magazine",
    name: "Magazine",
    category: "Card & Aesthetic",
    description: "Fashion caps on a black band, italic.",
    fontFamily: "Playfair Display",
    fontWeight: 700,
    fontSize: 35,
    letterSpacing: 0.8,
    lineHeight: 1.25,
    isItalic: true,
    textColor: "#F8FAFC",
    activeWordColor: "#FFFFFF",
    backgroundColor: "#000000",
    backgroundOpacity: 0.95,
    bgMode: "solid",
    outlineColor: "#000000",
    outlineWidth: 0,
    outlineEnabled: false,
    shadowColor: "#000000",
    shadowBlur: 2,
    shadowOffsetY: 1,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "sentence_fade",
    animationSpeed: 0.20,
    maxLines: 2,
    maxWordsPerLine: 3,
    isSystem: true,
  },
  {
    id: "highlighter",
    name: "Highlighter",
    category: "Card & Aesthetic",
    description: "A highlighter swipes the key word. Tips, explainers.",
    fontFamily: "Inter",
    fontWeight: 700,
    fontSize: 36,
    letterSpacing: 0.0,
    lineHeight: 1.25,
    textColor: "#FFFFFF",
    activeWordColor: "#000000",
    wordBox: true,
    wordBoxColor: "#FACC15",
    wordBoxRadius: 4,
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    bgMode: "none",
    outlineColor: "#000000",
    outlineWidth: 1.5,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 2.5,
    shadowOffsetY: 1.5,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "word_highlight",
    animationSpeed: 0.18,
    maxLines: 2,
    maxWordsPerLine: 4,
    isSystem: true,
  },
  {
    id: "paper",
    name: "Paper",
    category: "Card & Aesthetic",
    description: "Typewriter on torn paper, typed on. Stories, journals.",
    fontFamily: "Courier New",
    fontWeight: 700,
    fontSize: 33,
    letterSpacing: 0.2,
    lineHeight: 1.25,
    textColor: "#1F2937",
    activeWordColor: "#111827",
    backgroundColor: "#F3EDE2",
    backgroundOpacity: 0.98,
    bgMode: "solid",
    isTilted: true,
    tiltAngle: -1.0,
    outlineColor: "#000000",
    outlineWidth: 0,
    outlineEnabled: false,
    shadowColor: "#000000",
    shadowBlur: 4,
    shadowOffsetY: 2.5,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "typewriter",
    animationSpeed: 0.15,
    maxLines: 2,
    maxWordsPerLine: 4,
    isSystem: true,
  },
  {
    id: "label",
    name: "Label",
    category: "Card & Aesthetic",
    description: "Mono caps on a white label. Minimal, polished.",
    fontFamily: "JetBrains Mono",
    fontWeight: 800,
    fontSize: 34,
    letterSpacing: 0.5,
    lineHeight: 1.20,
    uppercase: true,
    textColor: "#000000",
    activeWordColor: "#000000",
    backgroundColor: "#FFFFFF",
    backgroundOpacity: 1.0,
    bgMode: "solid",
    outlineColor: "#000000",
    outlineWidth: 0,
    outlineEnabled: false,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 2,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "color_karaoke",
    animationSpeed: 0.18,
    maxLines: 2,
    maxWordsPerLine: 3,
    isSystem: true,
  },
  {
    id: "sticker",
    name: "Sticker",
    category: "Card & Aesthetic",
    description: "Rounded words on a white sticker, the key word on colour.",
    fontFamily: "Poppins",
    fontWeight: 700,
    fontSize: 34,
    letterSpacing: 0.0,
    lineHeight: 1.25,
    textColor: "#0F172A",
    activeWordColor: "#FFFFFF",
    wordBox: true,
    wordBoxColor: "#FB7185",
    wordBoxRadius: 14,
    backgroundColor: "#FFFFFF",
    backgroundOpacity: 1.0,
    bgMode: "solid",
    outlineColor: "#000000",
    outlineWidth: 0,
    outlineEnabled: false,
    shadowColor: "#000000",
    shadowBlur: 4,
    shadowOffsetY: 2.5,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "active_word_pill",
    animationSpeed: 0.18,
    maxLines: 2,
    maxWordsPerLine: 4,
    isSystem: true,
  },

  // =========================================================================
  // 2. LOUD CAPTIONS (Image 2)
  // =========================================================================
  {
    id: "bold_pop",
    name: "Bold pop",
    category: "Loud Captions",
    description: "Heavy white caps, black outline, the spoken word pops in yellow.",
    fontFamily: "Arial Black",
    fontWeight: 900,
    fontSize: 40,
    letterSpacing: 0.5,
    lineHeight: 1.15,
    uppercase: true,
    textColor: "#FFFFFF",
    activeWordColor: "#FACC15",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    bgMode: "none",
    outlineColor: "#000000",
    outlineWidth: 3.5,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 2,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "soft_pop",
    animationSpeed: 0.18,
    maxLines: 2,
    maxWordsPerLine: 3,
    isSystem: true,
  },
  {
    id: "karaoke",
    name: "Karaoke",
    category: "Loud Captions",
    description: "The whole line shows; words fill with colour as they're said.",
    fontFamily: "Montserrat",
    fontWeight: 800,
    fontSize: 38,
    letterSpacing: 0.0,
    lineHeight: 1.20,
    textColor: "#FFFFFF",
    activeWordColor: "#FACC15",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    bgMode: "none",
    outlineColor: "#000000",
    outlineWidth: 2.5,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 2.5,
    shadowOffsetY: 2,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "color_karaoke",
    animationSpeed: 0.18,
    maxLines: 2,
    maxWordsPerLine: 4,
    isSystem: true,
  },
  {
    id: "typewriter",
    name: "Typewriter",
    category: "Loud Captions",
    description: "Words appear one by one, as they're said.",
    fontFamily: "Montserrat",
    fontWeight: 800,
    fontSize: 38,
    letterSpacing: 0.5,
    lineHeight: 1.15,
    uppercase: true,
    textColor: "#FFFFFF",
    activeWordColor: "#FACC15",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    bgMode: "none",
    outlineColor: "#000000",
    outlineWidth: 3.0,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 2.5,
    shadowOffsetY: 2,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "typewriter",
    animationSpeed: 0.15,
    maxLines: 2,
    maxWordsPerLine: 3,
    isSystem: true,
  },
  {
    id: "one_word",
    name: "One word",
    category: "Loud Captions",
    description: "One huge word at a time, punched in. High energy.",
    fontFamily: "Anton",
    fontWeight: 900,
    fontSize: 58,
    letterSpacing: 1.0,
    lineHeight: 1.10,
    uppercase: true,
    textColor: "#FFFFFF",
    activeWordColor: "#FFFFFF",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    bgMode: "none",
    outlineColor: "#000000",
    outlineWidth: 4.0,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 4,
    shadowOffsetY: 3,
    shadowEnabled: true,
    position: "center",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "emphasis_scale",
    animationSpeed: 0.15,
    maxLines: 1,
    maxWordsPerLine: 1,
    isSystem: true,
  },
  {
    id: "neon",
    name: "Neon",
    category: "Loud Captions",
    description: "Geometric caps with a coloured glow on the spoken word.",
    fontFamily: "Montserrat",
    fontWeight: 800,
    fontSize: 38,
    letterSpacing: 0.8,
    lineHeight: 1.15,
    uppercase: true,
    textColor: "#FFFFFF",
    activeWordColor: "#00F5FF",
    glow: true,
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    bgMode: "none",
    outlineColor: "#000000",
    outlineWidth: 2.0,
    outlineEnabled: true,
    shadowColor: "#00F5FF",
    shadowBlur: 16,
    shadowOffsetY: 0,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "color_karaoke",
    animationSpeed: 0.18,
    maxLines: 2,
    maxWordsPerLine: 3,
    isSystem: true,
  },
  {
    id: "pop_3d",
    name: "3D pop",
    category: "Loud Captions",
    description: "Chunky caps with a stacked 3D shadow; the spoken word jumps.",
    fontFamily: "Arial Black",
    fontWeight: 900,
    fontSize: 38,
    letterSpacing: 0.5,
    lineHeight: 1.15,
    uppercase: true,
    textColor: "#FFFFFF",
    activeWordColor: "#FACC15",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    bgMode: "none",
    outlineColor: "#000000",
    outlineWidth: 3.0,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 0,
    shadowOffsetY: 5,
    shadowEnabled: true,
    threeDShadow: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "emphasis_scale",
    animationSpeed: 0.18,
    maxLines: 2,
    maxWordsPerLine: 3,
    isSystem: true,
  },
  {
    id: "gradient",
    name: "Gradient",
    category: "Loud Captions",
    description: "Bold caps; the spoken word glows in a sunset gradient.",
    fontFamily: "Montserrat",
    fontWeight: 800,
    fontSize: 38,
    letterSpacing: 0.5,
    lineHeight: 1.15,
    uppercase: true,
    textColor: "#FFFFFF",
    activeWordColor: "#FB923C",
    glow: true,
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    bgMode: "none",
    outlineColor: "#000000",
    outlineWidth: 2.8,
    outlineEnabled: true,
    shadowColor: "#F43F5E",
    shadowBlur: 10,
    shadowOffsetY: 2,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "soft_pop",
    animationSpeed: 0.18,
    maxLines: 2,
    maxWordsPerLine: 3,
    isSystem: true,
  },
  {
    id: "beast",
    name: "Beast",
    category: "Loud Captions",
    description: "Huge condensed caps in three colours, punched in. Maximum energy.",
    fontFamily: "Anton",
    fontWeight: 900,
    fontSize: 48,
    letterSpacing: 1.0,
    lineHeight: 1.10,
    uppercase: true,
    textColor: "#FFFFFF",
    activeWordColor: "#FDE047",
    emphasisColor: "#38BDF8",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    bgMode: "none",
    outlineColor: "#000000",
    outlineWidth: 4.0,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 4,
    shadowOffsetY: 3,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "emphasis_scale",
    animationSpeed: 0.15,
    maxLines: 2,
    maxWordsPerLine: 3,
    isSystem: true,
  },
];

const LEGACY_ID_MAP: Record<string, string> = {
  "pure_white": "boxed",
  "soft_highlight": "highlighter",
  "luxury_editorial": "magazine",
  "modern_creator": "soft_glass",
  "podcast_gold": "karaoke",
  "podcast_teal": "neon",
  "glass_caption": "soft_glass",
  "speaker_focus": "highlight",
  "karaoke_clean": "karaoke",
  "word_pill": "highlight",
  "punch_orange": "comic",
  "creator_pink": "sticker",
  "cinema_classic": "subtitle",
  "documentary": "paper",
  "editorial_gold": "magazine",
  "top_clean": "label",
  "fresh_green": "terminal",
  "lavender": "highlight",
  "focus_red": "comic",
  "monochrome": "label",
  "tiktok-pop": "bold_pop",
  "default": "boxed",
  "hormozi": "bold_pop",
  "mrbeast": "beast",
  "minimal": "subtitle",
  "tiktok": "bold_pop",
  "podcast": "karaoke",
  "3d_pop": "pop_3d",
  "three_d_pop": "pop_3d",
};

export const DEFAULT_STYLE = CANONICAL_PRESET_STYLES[0];

const getInitialState = (inheritedStyle?: CaptionStyle | null): ProjectState => {
  let initialId = inheritedStyle ? inheritedStyle.id : DEFAULT_STYLE.id;
  if (LEGACY_ID_MAP[initialId]) {
    initialId = LEGACY_ID_MAP[initialId];
  }
  return {
    id: uuidv4(),
    name: "Untitled Project",
    videoFileName: null,
    videoUrl: null,
    duration: 0,
    currentTime: 0,
    isPlaying: false,
    captions: [],
    selectedCaptionId: null,
    timelineZoom: 1,
    selectedStyleId: initialId,
    styles: inheritedStyle ? [inheritedStyle, ...CANONICAL_PRESET_STYLES.filter(s => s.id !== inheritedStyle.id)] : CANONICAL_PRESET_STYLES,
    canvasSettings: {
      aspectRatio: "9:16",
      width: 1080,
      height: 1920,
    },
    exportSettings: {
      quality: "social",
      format: "mp4",
    },
    history: [],
    historyIndex: -1,
    autosaveStatus: "saved",
  };
};

export type EditorStore = ProjectState & {
  setVideo: (fileName: string, url: string, duration: number) => void;
  setCurrentTime: (time: number) => void;
  setIsPlaying: (playing: boolean) => void;
  addCaption: (caption?: CaptionSegment) => void;
  updateCaption: (id: string, updates: Partial<CaptionSegment>) => void;
  deleteCaption: (id: string) => void;
  duplicateCaption: (id: string) => void;
  splitCaption: (id: string, time: number) => void;
  mergeCaptions: (id1: string, id2: string) => void;
  selectCaption: (id: string | null) => void;
  setTimelineZoom: (zoom: number) => void;
  setSelectedStyle: (styleId: string) => void;
  updateStyle: (styleId: string, updates: Partial<CaptionStyle>) => void;
  addStyle: (style: CaptionStyle) => void;
  deleteStyle: (styleId: string) => void;
  saveCustomPreset: (name?: string) => Promise<CaptionStyle | null>;
  deleteCustomPreset: (presetId: string) => Promise<boolean>;
  resetPreset: (presetId: string) => Promise<CaptionStyle | null>;
  setCanvasSettings: (settings: Partial<ProjectState["canvasSettings"]>) => void;
  setExportSettings: (settings: Partial<ProjectState["exportSettings"]>) => void;
  pushHistory: () => void;
  undo: () => void;
  redo: () => void;
  setAutosaveStatus: (status: ProjectState["autosaveStatus"]) => void;
  loadProject: (state: Partial<ProjectState>) => void;
  reset: () => void;
  applyInheritedStyle: (style: CaptionStyle | null) => void;
  setProjectId: (projectId: string) => void;
};

export const useEditorStore = create<EditorStore>((set, get) => ({
  ...getInitialState(),

  setVideo: (fileName, url, duration) =>
    set({
      videoFileName: fileName,
      videoUrl: url,
      duration,
      currentTime: 0,
      isPlaying: false,
    }),

  setCurrentTime: (currentTime) => set({ currentTime }),

  setIsPlaying: (isPlaying) => set({ isPlaying }),

  addCaption: (caption) =>
    set((state) => {
      const newCaption: CaptionSegment = caption || {
        id: uuidv4(),
        text: "New caption",
        start: state.currentTime,
        end: Math.min(state.currentTime + 3, state.duration || state.currentTime + 3),
      };
      return { captions: [...state.captions, newCaption].sort((a, b) => a.start - b.start) };
    }),

  updateCaption: (id, updates) =>
    set((state) => ({
      captions: state.captions.map((c) =>
        c.id === id ? { ...c, ...updates } : c
      ).sort((a, b) => a.start - b.start),
    })),

  deleteCaption: (id) =>
    set((state) => ({
      captions: state.captions.filter((c) => c.id !== id),
      selectedCaptionId: state.selectedCaptionId === id ? null : state.selectedCaptionId,
    })),

  duplicateCaption: (id) =>
    set((state) => {
      const caption = state.captions.find((c) => c.id === id);
      if (!caption) return state;
      const newCaption: CaptionSegment = {
        ...caption,
        id: uuidv4(),
        start: caption.end,
        end: Math.min(caption.end + (caption.end - caption.start), state.duration || caption.end + 3),
      };
      return { captions: [...state.captions, newCaption].sort((a, b) => a.start - b.start) };
    }),

  splitCaption: (id, time) =>
    set((state) => {
      const caption = state.captions.find((c) => c.id === id);
      if (!caption || time <= caption.start || time >= caption.end) return state;
      const first: CaptionSegment = { ...caption, end: time };
      const second: CaptionSegment = {
        id: uuidv4(),
        text: caption.text,
        start: time,
        end: caption.end,
        words: caption.words,
      };
      return { captions: state.captions.map((c) => c.id === id ? first : c).concat(second).sort((a, b) => a.start - b.start) };
    }),

  mergeCaptions: (id1, id2) =>
    set((state) => {
      const c1 = state.captions.find((c) => c.id === id1);
      const c2 = state.captions.find((c) => c.id === id2);
      if (!c1 || !c2) return state;
      const merged: CaptionSegment = {
        id: uuidv4(),
        text: `${c1.text} ${c2.text}`,
        start: Math.min(c1.start, c2.start),
        end: Math.max(c1.end, c2.end),
      };
      return { captions: state.captions.filter((c) => c.id !== id1 && c.id !== id2).concat(merged).sort((a, b) => a.start - b.start) };
    }),

  selectCaption: (selectedCaptionId) => set({ selectedCaptionId }),

  setTimelineZoom: (timelineZoom) => set({ timelineZoom }),

  setSelectedStyle: (styleId) => {
    const resolvedId = LEGACY_ID_MAP[styleId] || styleId;
    set({ selectedStyleId: resolvedId });
  },

  updateStyle: (styleId, updates) =>
    set((state) => ({
      styles: state.styles.map((s) => (s.id === styleId ? { ...s, ...updates } : s)),
    })),

  addStyle: (style) =>
    set((state) => ({
      styles: [...state.styles, style],
      selectedStyleId: style.id,
    })),

  deleteStyle: (styleId) =>
    set((state) => {
      if (state.styles.length <= 1) return state;
      const newStyles = state.styles.filter((s) => s.id !== styleId);
      return {
        styles: newStyles,
        selectedStyleId: state.selectedStyleId === styleId ? newStyles[0].id : state.selectedStyleId,
      };
    }),

  saveCustomPreset: async (name) => {
    const state = get();
    const currentStyle = state.styles.find((s) => s.id === state.selectedStyleId) || state.styles[0];
    const presetName = name || `${currentStyle.name} (Custom)`;
    try {
      const res = await fetch("/api/caption-studio/presets/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: presetName,
          style: { ...currentStyle, name: presetName, isCustom: true, isSystem: false },
        }),
      });
      const data = await res.json();
      if (data.success && data.preset) {
        const saved: CaptionStyle = data.preset.style || data.preset;
        set((prev) => ({
          styles: [saved, ...prev.styles.filter((s) => s.id !== saved.id)],
          selectedStyleId: saved.id,
        }));
        return saved;
      }
    } catch (e) {
      console.error("Failed to save custom preset:", e);
    }
    return null;
  },

  deleteCustomPreset: async (presetId) => {
    try {
      const res = await fetch("/api/caption-studio/presets/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: presetId }),
      });
      const data = await res.json();
      if (data.success) {
        set((prev) => {
          const filtered = prev.styles.filter((s) => s.id !== presetId);
          return {
            styles: filtered,
            selectedStyleId: prev.selectedStyleId === presetId ? (filtered[0]?.id || "boxed") : prev.selectedStyleId,
          };
        });
        return true;
      }
    } catch (e) {
      console.error("Failed to delete custom preset:", e);
    }
    return false;
  },

  resetPreset: async (presetId) => {
    try {
      const res = await fetch("/api/caption-studio/presets/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: presetId }),
      });
      const data = await res.json();
      if (data.success && data.preset) {
        const defaultStyle: CaptionStyle = data.preset;
        set((prev) => ({
          styles: prev.styles.map((s) => s.id === presetId ? defaultStyle : s),
          selectedStyleId: defaultStyle.id,
        }));
        return defaultStyle;
      }
    } catch (e) {
      console.error("Failed to reset preset:", e);
    }
    return null;
  },

  setCanvasSettings: (canvasSettings) =>
    set((state) => ({ canvasSettings: { ...state.canvasSettings, ...canvasSettings } })),

  setExportSettings: (exportSettings) =>
    set((state) => ({ exportSettings: { ...state.exportSettings, ...exportSettings } })),

  pushHistory: () =>
    set((state) => {
      const newHistory = state.history.slice(0, state.historyIndex + 1);
      newHistory.push({ captions: JSON.parse(JSON.stringify(state.captions)) });
      return { history: newHistory, historyIndex: newHistory.length - 1 };
    }),

  undo: () =>
    set((state) => {
      if (state.historyIndex <= 0) return state;
      const newIndex = state.historyIndex - 1;
      return {
        captions: JSON.parse(JSON.stringify(state.history[newIndex].captions)),
        historyIndex: newIndex,
      };
    }),

  redo: () =>
    set((state) => {
      if (state.historyIndex >= state.history.length - 1) return state;
      const newIndex = state.historyIndex + 1;
      return {
        captions: JSON.parse(JSON.stringify(state.history[newIndex].captions)),
        historyIndex: newIndex,
      };
    }),

  setAutosaveStatus: (autosaveStatus) => set({ autosaveStatus }),

  loadProject: (projectState) =>
    set((state) => ({
      ...state,
      ...projectState,
      captions: projectState.captions || state.captions,
      styles: projectState.styles || state.styles,
    })),

  reset: () => set(getInitialState()),

  applyInheritedStyle: (inheritedStyle) => {
    if (!inheritedStyle) return;
    set((state) => {
      const exists = state.styles.find((s) => s.id === inheritedStyle.id);
      if (exists) {
        return {
          styles: state.styles.map((s) => s.id === inheritedStyle.id ? { ...s, ...inheritedStyle } : s),
          selectedStyleId: inheritedStyle.id,
        };
      }
      return {
        styles: [inheritedStyle, ...state.styles],
        selectedStyleId: inheritedStyle.id,
      };
    });
  },

  setProjectId: (projectId) => set({ id: projectId }),
}));
