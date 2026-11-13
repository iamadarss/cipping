export type CaptionWord = {
  text: string;
  start: number;
  end: number;
};

export type CaptionSegment = {
  id: string;
  text: string;
  start: number;
  end: number;
  words?: CaptionWord[];
};

export type CaptionStyle = {
  id: string;
  name: string;
  category?: string;
  description?: string;
  fontFamily: string;
  fontWeight: number;
  fontSize: number;
  letterSpacing: number;
  lineHeight: number;
  textColor: string;
  activeWordColor: string;
  emphasisColor?: string;
  backgroundColor: string;
  backgroundOpacity: number;
  bgMode?: "none" | "semi" | "solid" | "glass";
  wordBox?: boolean;
  wordBoxColor?: string;
  wordBoxRadius?: number;
  outlineColor: string;
  outlineWidth: number;
  outlineEnabled?: boolean;
  shadowColor: string;
  shadowBlur: number;
  shadowOffsetY: number;
  shadowEnabled?: boolean;
  position: "top" | "center" | "bottom" | "lower_third" | "upper_center";
  x: number;
  y: number;
  maxWidth: number;
  padding: number;
  animation:
    | "pop_in"
    | "bounce_in"
    | "smooth_fade"
    | "slide_up"
    | "slide_down"
    | "zoom_in"
    | "zoom_out"
    | "typewriter"
    | "word_reveal"
    | "karaoke_highlight"
    | "glow_pulse"
    | "glitch"
    | "elastic_scale"
    | "blur_reveal"
    | "split_reveal"
    | "tracking_reveal"
    | "color_karaoke"
    | "soft_pop"
    | "active_word_pill"
    | "emphasis_scale"
    | "word_highlight"
    | "sentence_fade"
    | "pop"
    | "fade"
    | "bounce"
    | "slide"
    | "zoom"
    | "glow"
    | "none"
    | "float"
    | "wave"
    | "neon-flicker"
    | "retro";
  animationSpeed: number;
  maxLines: number;
  maxWordsPerLine?: number;
  uppercase?: boolean;
  isItalic?: boolean;
  isTilted?: boolean;
  tiltAngle?: number;
  threeDShadow?: boolean;
  wordPop?: boolean;
  glow?: boolean;
  glowColor?: string;
  glowBlur?: number;
  secondaryFontFamily?: string;
  secondaryFontSize?: number;
  twoLineHierarchy?: boolean;
  keywordScale?: number;
  emoji?: boolean;
  isSystem?: boolean;
  isCustom?: boolean;
  favorite?: boolean;
};

export type ProjectState = {
  id: string;
  name: string;
  videoFileName: string | null;
  videoUrl: string | null;
  duration: number;
  currentTime: number;
  isPlaying: boolean;
  captions: CaptionSegment[];
  selectedCaptionId: string | null;
  timelineZoom: number;
  selectedStyleId: string;
  styles: CaptionStyle[];
  canvasSettings: {
    aspectRatio: "9:16" | "16:9" | "1:1" | "4:5";
    width: number;
    height: number;
  };
  exportSettings: {
    quality: "social" | "landscape" | "square";
    format: "mp4" | "webm";
  };
  history: { captions: CaptionSegment[] }[];
  historyIndex: number;
  autosaveStatus: "saved" | "saving" | "unsaved";
};

export type DragState = {
  type: "move" | "resize-start" | "resize-end" | null;
  captionId: string | null;
  startX: number;
  originalStart: number;
  originalEnd: number;
};
