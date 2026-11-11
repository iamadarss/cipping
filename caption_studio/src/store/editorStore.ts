import { create } from "zustand";
import { v4 as uuidv4 } from "uuid";
import type { CaptionSegment, CaptionStyle, ProjectState, DragState } from "../types";

export const CANONICAL_PRESET_STYLES: CaptionStyle[] = [
  // -------------------------------------------------------------------------
  // 1. MINIMAL & LUXURY
  // -------------------------------------------------------------------------
  {
    id: "pure_white",
    name: "Pure White",
    category: "Minimal & Luxury",
    description: "Clean, understated white typography with zero stroke and soft ambient shadow.",
    fontFamily: "Inter",
    fontWeight: 700,
    fontSize: 36,
    letterSpacing: 0.2,
    lineHeight: 1.25,
    textColor: "#FFFFFF",
    activeWordColor: "#FFFFFF",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
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
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "soft_highlight",
    name: "Soft Highlight",
    category: "Minimal & Luxury",
    description: "Neutral ivory text with gentle butter-yellow word progression.",
    fontFamily: "Inter",
    fontWeight: 700,
    fontSize: 36,
    letterSpacing: 0.0,
    lineHeight: 1.25,
    textColor: "#F3F4F6",
    activeWordColor: "#FFE58F",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
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
    animation: "color_karaoke",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "luxury_editorial",
    name: "Luxury Editorial",
    category: "Minimal & Luxury",
    description: "Sophisticated serif typography with subtle muted champagne gold active words.",
    fontFamily: "Playfair Display",
    fontWeight: 700,
    fontSize: 38,
    letterSpacing: 0.5,
    lineHeight: 1.3,
    textColor: "#FAF9F6",
    activeWordColor: "#D4AF37",
    emphasisColor: "#D4AF37",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
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
    animation: "word_highlight",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "modern_creator",
    name: "Modern Creator",
    category: "Minimal & Luxury",
    description: "Sleek Manrope geometry with electric sky blue active keyword tracking.",
    fontFamily: "Manrope",
    fontWeight: 800,
    fontSize: 36,
    letterSpacing: 0.1,
    lineHeight: 1.22,
    textColor: "#FFFFFF",
    activeWordColor: "#38BDF8",
    emphasisColor: "#38BDF8",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    outlineColor: "#000000",
    outlineWidth: 0,
    outlineEnabled: false,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 1,
    shadowEnabled: true,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "soft_pop",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },

  // -------------------------------------------------------------------------
  // 2. PODCAST
  // -------------------------------------------------------------------------
  {
    id: "podcast_gold",
    name: "Podcast Gold",
    category: "Podcast",
    description: "Authoritative conversational captions with warm amber gold emphasis and subtle backing.",
    fontFamily: "Montserrat",
    fontWeight: 700,
    fontSize: 34,
    letterSpacing: 0.2,
    lineHeight: 1.25,
    textColor: "#FFFFFF",
    activeWordColor: "#F59E0B",
    emphasisColor: "#F59E0B",
    backgroundColor: "#000000",
    backgroundOpacity: 0.5,
    bgMode: "semi",
    outlineColor: "#000000",
    outlineWidth: 0,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 2,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "color_karaoke",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "podcast_teal",
    name: "Podcast Teal",
    category: "Podcast",
    description: "Modern studio podcast subtitle with deep cyan-teal active word pill accent.",
    fontFamily: "Inter",
    fontWeight: 700,
    fontSize: 33,
    letterSpacing: 0.0,
    lineHeight: 1.24,
    textColor: "#FFFFFF",
    activeWordColor: "#14B8A6",
    wordBox: true,
    wordBoxColor: "#0D9488",
    wordBoxRadius: 6,
    backgroundColor: "#0F172A",
    backgroundOpacity: 0.6,
    bgMode: "semi",
    outlineColor: "#000000",
    outlineWidth: 0,
    shadowColor: "#000000",
    shadowBlur: 2,
    shadowOffsetY: 1,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "active_word_pill",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "glass_caption",
    name: "Glass Caption",
    category: "Podcast",
    description: "Frosted dark glass backing card with crystal white typography and soft indigo glow.",
    fontFamily: "Manrope",
    fontWeight: 600,
    fontSize: 32,
    letterSpacing: 0.2,
    lineHeight: 1.26,
    textColor: "#FFFFFF",
    activeWordColor: "#E0E7FF",
    backgroundColor: "#111827",
    backgroundOpacity: 0.6,
    bgMode: "glass",
    outlineColor: "#000000",
    outlineWidth: 0,
    shadowColor: "#000000",
    shadowBlur: 0,
    shadowOffsetY: 0,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "smooth_fade",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "speaker_focus",
    name: "Speaker Focus",
    category: "Podcast",
    description: "Sharp DM Sans lettering with emerald green speaker highlight and crisp contrast.",
    fontFamily: "DM Sans",
    fontWeight: 700,
    fontSize: 34,
    letterSpacing: 0.0,
    lineHeight: 1.25,
    textColor: "#FFFFFF",
    activeWordColor: "#10B981",
    emphasisColor: "#10B981",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    outlineColor: "#000000",
    outlineWidth: 0,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 1,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "word_highlight",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },

  // -------------------------------------------------------------------------
  // 3. KINETIC
  // -------------------------------------------------------------------------
  {
    id: "karaoke_clean",
    name: "Karaoke Clean",
    category: "Kinetic",
    description: "Vibrant yellow karaoke progressive wipe with razor-sharp readability.",
    fontFamily: "Inter",
    fontWeight: 800,
    fontSize: 38,
    letterSpacing: 0.2,
    lineHeight: 1.22,
    textColor: "#FFFFFF",
    activeWordColor: "#FFE000",
    emphasisColor: "#FFE000",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    outlineColor: "#000000",
    outlineWidth: 2,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 2,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "color_karaoke",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "word_pill",
    name: "Word Pill",
    category: "Kinetic",
    description: "Dynamic rounded pill following each spoken word, inspired by top creator tools.",
    fontFamily: "Inter",
    fontWeight: 800,
    fontSize: 38,
    letterSpacing: 0.2,
    lineHeight: 1.22,
    textColor: "#FFFFFF",
    activeWordColor: "#FFFFFF",
    wordBox: true,
    wordBoxColor: "#4F46E5",
    wordBoxRadius: 8,
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    outlineColor: "#000000",
    outlineWidth: 0,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 1,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "active_word_pill",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "punch_orange",
    name: "Punch Orange",
    category: "Kinetic",
    description: "High-energy uppercase headline text with blazing neon orange active punch.",
    fontFamily: "Anton",
    fontWeight: 800,
    fontSize: 42,
    letterSpacing: 0.8,
    lineHeight: 1.18,
    uppercase: true,
    textColor: "#FFFFFF",
    activeWordColor: "#FF6B00",
    emphasisColor: "#FF6B00",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    outlineColor: "#000000",
    outlineWidth: 3,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 4,
    shadowOffsetY: 2,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "emphasis_scale",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "creator_pink",
    name: "Creator Pink",
    category: "Kinetic",
    description: "Vibrant Poppins kinetic subtitles with TikTok-signature crimson pink active pop.",
    fontFamily: "Poppins",
    fontWeight: 800,
    fontSize: 36,
    letterSpacing: 0.2,
    lineHeight: 1.2,
    textColor: "#FFFFFF",
    activeWordColor: "#FE2C55",
    emphasisColor: "#FE2C55",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    outlineColor: "#000000",
    outlineWidth: 2,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 1,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "soft_pop",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },

  // -------------------------------------------------------------------------
  // 4. CINEMATIC
  // -------------------------------------------------------------------------
  {
    id: "cinema_classic",
    name: "Cinema Classic",
    category: "Cinematic",
    description: "Warm theatrical cream typography placed with classic film lower-third spacing.",
    fontFamily: "Georgia",
    fontWeight: 600,
    fontSize: 34,
    letterSpacing: 1.0,
    lineHeight: 1.3,
    textColor: "#FFFDD0",
    activeWordColor: "#FFFDD0",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    outlineColor: "#000000",
    outlineWidth: 0,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 1,
    position: "lower_third",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "sentence_fade",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "documentary",
    name: "Documentary",
    category: "Cinematic",
    description: "Restrained factual documentary style with letterbox bar backing.",
    fontFamily: "Inter",
    fontWeight: 600,
    fontSize: 30,
    letterSpacing: 0.8,
    lineHeight: 1.28,
    uppercase: true,
    textColor: "#FFFFFF",
    activeWordColor: "#FFFFFF",
    backgroundColor: "#000000",
    backgroundOpacity: 0.75,
    bgMode: "semi",
    outlineColor: "#000000",
    outlineWidth: 0,
    shadowColor: "#000000",
    shadowBlur: 0,
    shadowOffsetY: 0,
    position: "lower_third",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "smooth_fade",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "editorial_gold",
    name: "Editorial Gold",
    category: "Cinematic",
    description: "Refined Playfair Display serif with radiant warm gold accents for premium storytelling.",
    fontFamily: "Playfair Display",
    fontWeight: 700,
    fontSize: 36,
    letterSpacing: 0.6,
    lineHeight: 1.3,
    textColor: "#FFFFFF",
    activeWordColor: "#E5C158",
    emphasisColor: "#E5C158",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    outlineColor: "#000000",
    outlineWidth: 0,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 2,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "word_highlight",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "top_clean",
    name: "Top Clean",
    category: "Cinematic",
    description: "Upper-third positioned subtitles keeping gameplay or subject face completely free.",
    fontFamily: "Manrope",
    fontWeight: 700,
    fontSize: 34,
    letterSpacing: 0.2,
    lineHeight: 1.24,
    textColor: "#FFFFFF",
    activeWordColor: "#FBBF24",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    outlineColor: "#000000",
    outlineWidth: 0,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 1,
    position: "upper_center",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "slide_down",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },

  // -------------------------------------------------------------------------
  // 5. SPECIAL
  // -------------------------------------------------------------------------
  {
    id: "fresh_green",
    name: "Fresh Green",
    category: "Special",
    description: "High-contrast Montserrat text with crisp electric lime highlighting.",
    fontFamily: "Montserrat",
    fontWeight: 800,
    fontSize: 36,
    letterSpacing: 0.2,
    lineHeight: 1.2,
    textColor: "#FFFFFF",
    activeWordColor: "#22C55E",
    emphasisColor: "#22C55E",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    outlineColor: "#000000",
    outlineWidth: 2,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 3,
    shadowOffsetY: 2,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "soft_pop",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "lavender",
    name: "Lavender",
    category: "Special",
    description: "Elegantly balanced Poppins lettering with soothing violet-lavender accents.",
    fontFamily: "Poppins",
    fontWeight: 700,
    fontSize: 35,
    letterSpacing: 0.2,
    lineHeight: 1.22,
    textColor: "#FFFFFF",
    activeWordColor: "#A855F7",
    emphasisColor: "#C084FC",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    outlineColor: "#000000",
    outlineWidth: 0,
    shadowColor: "#000000",
    shadowBlur: 2,
    shadowOffsetY: 1,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "color_karaoke",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "focus_red",
    name: "Focus Red",
    category: "Special",
    description: "Punchy Anton headline with crimson red focus words commanding maximum attention.",
    fontFamily: "Anton",
    fontWeight: 800,
    fontSize: 42,
    letterSpacing: 0.5,
    lineHeight: 1.18,
    uppercase: true,
    textColor: "#FFFFFF",
    activeWordColor: "#EF4444",
    emphasisColor: "#EF4444",
    backgroundColor: "#000000",
    backgroundOpacity: 0.0,
    outlineColor: "#000000",
    outlineWidth: 2.5,
    outlineEnabled: true,
    shadowColor: "#000000",
    shadowBlur: 4,
    shadowOffsetY: 2,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "soft_pop",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
  {
    id: "monochrome",
    name: "Monochrome",
    category: "Special",
    description: "High-contrast inverted black typography on crisp white pill badge.",
    fontFamily: "Inter",
    fontWeight: 800,
    fontSize: 34,
    letterSpacing: 0.2,
    lineHeight: 1.22,
    textColor: "#000000",
    activeWordColor: "#000000",
    backgroundColor: "#FFFFFF",
    backgroundOpacity: 0.95,
    bgMode: "solid",
    outlineColor: "#000000",
    outlineWidth: 0,
    shadowColor: "#00000040",
    shadowBlur: 4,
    shadowOffsetY: 2,
    position: "bottom",
    x: 0,
    y: 0,
    maxWidth: 800,
    padding: 12,
    animation: "smooth_fade",
    animationSpeed: 0.2,
    maxLines: 2,
    isSystem: true,
  },
];

const LEGACY_ID_MAP: Record<string, string> = {
  "tiktok-pop": "creator_pink",
  "karaoke": "karaoke_clean",
  "neon": "podcast_teal",
  "minimal": "pure_white",
  "typewriter": "pure_white",
  "bounce": "punch_orange",
  "pop": "soft_highlight",
  "default": "soft_highlight",
  "hormozi": "word_pill",
  "mrbeast": "focus_red",
  "tiktok": "creator_pink",
  "podcast": "podcast_gold",
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
            selectedStyleId: prev.selectedStyleId === presetId ? (filtered[0]?.id || "pure_white") : prev.selectedStyleId,
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
