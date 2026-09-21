# UP CLIP STUDIO — CAPTION STUDIO
## Antigravity Coding Agent Master Prompt
### Pixel-Accurate UI Reconstruction + Fully Functional Caption Workflow

> **Role:** You are an expert senior product engineer, UI/UX architect, frontend engineer, media-processing engineer, and QA engineer.
>
> **Mission:** Build and integrate a production-quality **Caption Studio** module inside the existing **Up Clip Studio** project. The result must closely follow the supplied reference screenshot and the user's existing Up Clip Studio design system. Do not create a different generic SaaS dashboard. Reuse the existing project architecture, navigation, icons, colors, fonts, typography, routes, theme, components, media-processing utilities, settings, and local-first behavior wherever they already exist.

---

# 1. NON-NEGOTIABLE OBJECTIVE

Create a complete, functional **Up Clip Studio → Caption Studio** workspace with:

- Existing Up Clip Studio branding.
- Existing left navigation/sidebar icons.
- Existing project theme, colors, typography, fonts, spacing, and visual language.
- A video import area with playback controls.
- Caption import.
- Offline/local caption generation.
- Caption preset library.
- Typography and Style settings.
- Transcript Caption Lines panel.
- Timeline with caption blocks and waveform.
- Caption editing tools.
- Undo and Redo.
- Export functionality.
- Fully functional interactions, not static mockups.
- Responsive behavior for desktop and smaller screens.
- Performance suitable for a low-resource Windows laptop with approximately 8 GB RAM and 256 GB storage.
- Local-first behavior; the application must continue to work without a mandatory cloud LLM or paid API.

The implementation must be integrated into the existing application rather than replacing the entire project or redesigning unrelated modules.

---

# 2. REFERENCE AND DESIGN MATCHING

Use the supplied screenshot as the primary visual reference.

The UI should preserve the following visual structure:

1. Top navigation/header.
2. Narrow vertical left sidebar.
3. Left video preview/player area.
4. Middle preset library area.
5. Middle-right Typography & Style area.
6. Right Transcript Caption Lines area.
7. Horizontal caption editing toolbar.
8. Bottom timeline with caption blocks and waveform.

The screenshot is a visual reference for layout, hierarchy, proportions, spacing, and interaction patterns. Do not copy any copyrighted branding or third-party proprietary assets. Use the existing Up Clip Studio branding and project assets.

The final result must feel like the same product and the same design system.

---

# 3. IMPORTANT UI CHANGES REQUIRED

Implement the following exact changes:

## 3.1 Remove New Project

Remove the **New Project** button from the Caption Studio header.

Do not show a New Project button in this screen.

If project creation already exists elsewhere in the application, preserve that existing functionality outside this Caption Studio header.

## 3.2 Header Actions

The top header must contain these primary actions in this order:

1. Import Video
2. Import Caption
3. Generate Caption
4. Export

The buttons must be functional.

Use the existing project button styles, icons, hover states, focus states, loading states, and theme.

## 3.3 Saved, Undo, and Redo

Keep the existing:

- Up Clip Studio logo/brand.
- Caption Studio title.
- Saved status.

Immediately after Saved, add or preserve:

- Undo
- Redo

Undo and Redo must be functional and state-aware:

- Disabled when no action is available.
- Enabled when an undoable/redoable action exists.
- Keyboard shortcuts:
  - Ctrl + Z = Undo
  - Ctrl + Shift + Z = Redo
  - Ctrl + Y = Redo where appropriate
- Show a subtle saved/unsaved state.
- Avoid losing undo history when changing tabs or scrolling.

## 3.4 Remove Skip Silence in Preview

Remove the **Skip Silence in Preview** toggle completely from the visible Caption Studio player UI.

Do not show it as a hidden duplicate, placeholder, or disabled control.

If silence detection exists in the application, keep its internal capability only if it is used by another module. It must not appear in this Caption Studio preview controls area.

## 3.5 Preset Library Header

Make the text **Preset Library** smaller and more compact.

Reduce unnecessary vertical space above and below the title.

The preset library should have:

- Compact heading.
- Compact cards.
- Consistent spacing.
- Scrollable preset list.
- All available presets accessible through vertical scrolling.
- No fixed limit of only three visible presets.

As the user scrolls, more presets must appear.

## 3.6 Typography & Style Header

Keep the exact title:

**Typography & Style**

Make its heading compact and reduce unused vertical space.

The Typography & Style area must use a narrow, efficient column layout. Settings should not consume excessive horizontal space.

All settings must be vertically scrollable. The user should be able to scroll through the complete settings list without the entire page becoming unusable.

## 3.7 Font Settings Expansion

Remove the current Expand/Collapse toggle behavior from the Font Settings section.

The Font Settings section must remain permanently expanded.

Do not show a collapse chevron or a collapse action.

The settings inside it must always remain visible when the Typography & Style panel is open.

Other settings groups may be expandable/collapsible only if this does not conflict with the existing project behavior. Font Settings specifically must be permanently expanded.

## 3.8 Transcript Caption Lines

Keep the **Transcript Caption Lines** panel on the right side.

The panel must appear and become populated after captions are generated or imported.

It must support:

- Caption line groups.
- Time ranges.
- Individual word chips.
- Active word highlighting.
- Selecting a word.
- Editing caption text.
- Selecting a line.
- Jumping the video playhead to a line.
- Synchronizing the selected line with the timeline and preview.
- Scrollable content.
- Empty state before captions are imported/generated.
- Loading state during generation.
- Error state when caption processing fails.

Example structure:

- Time range: `2:38 - 3:19`
- Word chips: `mish`, `ge`, `duniya`, `ka`, `mum`

Do not hardcode the sample words. Use real transcript data.

---

# 4. REQUIRED PAGE LAYOUT

Build the Caption Studio page using a stable application shell.

## 4.1 High-Level Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ UpClipStudio | Caption Studio | Saved | Undo | Redo | Import Video | ...    │
├──────┬──────────────────────┬─────────────────────┬─────────────────────────┤
│      │                      │                     │                         │
│      │                      │                     │ Transcript Caption      │
│ Side │   Video Preview      │   Preset Library    │ Lines                   │
│ bar  │   + Player Controls  │   + Typography      │                         │
│      │                      │   & Style           │                         │
│      │                      │                     │                         │
├──────┴──────────────────────┴─────────────────────┴─────────────────────────┤
│ Add Caption | Split | Merge | Delete                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ Caption Timeline + Time Ruler + Waveform + Playhead                           │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 4.2 Use Resizable/Adaptive Panels

Use a robust layout system such as CSS Grid, Flexbox, or the existing layout system.

Recommended desktop proportions:

- Left sidebar: 64–92 px depending on existing project layout.
- Video preview: approximately 25–32%.
- Preset Library: approximately 20–25%.
- Typography & Style: approximately 22–28%.
- Transcript Caption Lines: approximately 18–24%.

Do not force exact percentages if the existing application already has a better layout system. Preserve the reference's visual balance.

The panel layout must not cause horizontal overflow at normal desktop widths.

At smaller widths:

- Preserve the sidebar.
- Convert secondary panels into tabs, drawers, or horizontally scrollable panels.
- Keep the video preview usable.
- Never hide core controls without providing an accessible alternative.

---

# 5. TOP HEADER SPECIFICATION

## 5.1 Left Side

Preserve existing project elements:

- Up Clip Studio logo/wordmark.
- Caption Studio icon.
- Caption Studio title.
- Saved state indicator.
- Undo button.
- Redo button.

Use existing assets and components whenever possible.

## 5.2 Right Side

Display buttons in this order:

### Import Video

Functionality:

- Open local video file picker.
- Support common formats such as MP4, MOV, WebM, and MKV if the existing media stack supports them.
- Validate file type and size.
- Show loading/import progress where possible.
- Load the video into the preview.
- Update duration and timeline.
- Generate or load waveform data.
- Preserve the current project state if the user imports a new file after edits, using a confirmation dialog when needed.

### Import Caption

Support:

- SRT
- VTT
- ASS/SSA where supported
- JSON caption format if already supported by the project

Functionality:

- Parse captions.
- Validate timestamps.
- Normalize text.
- Detect invalid or overlapping time ranges.
- Display imported captions in the transcript panel.
- Display captions in the timeline.
- Render captions in the video preview.
- Allow editing after import.

### Generate Caption

The button must open the existing or newly integrated **Offline AI Settings** flow.

Preferred default engine:

- Local Whisper-compatible transcription.
- Use an existing local transcription implementation if present.
- Do not require a paid API.
- Do not require a cloud service for the core workflow.
- If local Whisper is not available in the current runtime, show a clear setup state and preserve manual/imported caption functionality.

Generation settings should support where practical:

- Language selection.
- Auto detect language.
- Hindi.
- English.
- Hinglish/mixed speech.
- Timestamp mode.
- Word-level timestamps if available.
- Line-level captions.
- Optional punctuation normalization.
- Optional profanity masking setting if already part of the existing project.
- Model selection based on device capability.
- Progress indicator.
- Cancel generation.
- Error handling.
- Retry.

The application must remain usable even if local AI generation is unavailable.

### Export

Add an **Export** button as the final header action.

Export should open a compact export menu or modal with supported formats:

- Rendered video with burned-in captions.
- SRT.
- VTT.
- ASS/SSA where supported.
- JSON caption project.
- Project package if supported by the existing architecture.

Include:

- Resolution selection where supported.
- Caption preset/style selection.
- Output folder selection or browser download behavior based on the platform.
- Progress indicator.
- Cancel behavior where technically possible.
- Success confirmation.
- Clear error messages.
- No fake export success.

---

# 6. VIDEO PREVIEW AND PLAYER

## 6.1 Preview Area

The preview area must be on the left side, similar to the screenshot.

Support:

- Vertical 9:16 video preview.
- Other aspect ratios when the imported video requires them.
- Fit-to-panel behavior.
- Contain mode.
- Crop mode if already supported.
- Caption overlay.
- Real-time style updates.
- Caption position preview.
- Safe-area guides where useful.
- Playhead synchronization.
- Current time and total duration.

## 6.2 Player Controls

Keep only useful player controls:

- Previous frame or previous segment where supported.
- Play.
- Pause.
- Next frame or next segment where supported.
- Seek bar.
- Current time.
- Total duration.
- Volume/mute if available.
- Fullscreen preview if supported.

Do not include:

- Skip Silence in Preview.
- New Project.
- Unrelated controls.

Player controls must be keyboard accessible.

Keyboard support:

- Space = Play/Pause.
- Left Arrow = Seek backward.
- Right Arrow = Seek forward.
- J/K/L shortcuts if consistent with the existing project.
- Home = Go to beginning.
- End = Go to end.

Do not use placeholder buttons. Every visible control must work or be clearly marked as unavailable.

---

# 7. PRESET LIBRARY

## 7.1 General Behavior

The Preset Library must be compact and scrollable.

All presets must be available through scrolling.

Do not show only three fixed cards.

Use a data-driven preset architecture:

```ts
type CaptionPreset = {
  id: string;
  name: string;
  description?: string;
  previewStyle: {
    fontFamily: string;
    fontSize: number;
    fontWeight: number;
    fillColor: string;
    outlineColor?: string;
    outlineWidth?: number;
    shadow?: string;
    alignment: "left" | "center" | "right";
    position: {
      x: number;
      y: number;
    };
    animation?: string;
  };
  supportedFormats?: string[];
  isBuiltIn: boolean;
};
```

## 7.2 Preset Requirements

At minimum, provide a scalable preset system with categories such as:

- Up Clip.
- Vlog Clip.
- Up Clip Bold.
- Clean White.
- High Contrast.
- News Style.
- Podcast Highlight.
- Minimal Subtitle.
- Bold Center.
- Kinetic Word.
- Hindi Friendly.
- Hinglish Friendly.
- Social Short.
- Creator Highlight.
- Documentary.
- Cinematic.
- Outline Heavy.
- Shadow Pop.
- Minimal Lower Third.
- Custom Presets.

The exact number can be increased, but the architecture must not be hardcoded to a small fixed list.

Each preset card must:

- Show a visual preview.
- Have a selected state.
- Apply immediately on click.
- Update the live preview.
- Update relevant Typography & Style settings.
- Support Apply to All when applicable.
- Avoid destroying custom changes unless the user explicitly chooses to overwrite them.
- Provide a way to save a custom preset if the existing project supports it.

## 7.3 Preset Scrolling

Use:

- `overflow-y: auto`.
- Stable scrollbar behavior.
- Scrollbar styling consistent with the theme.
- Keyboard focus support.
- Lazy rendering only if necessary.
- No nested scroll traps.

---

# 8. TYPOGRAPHY & STYLE

## 8.1 Panel Behavior

The Typography & Style panel must be vertically scrollable.

The title must remain compact.

The settings must be grouped logically.

The Font Settings group must always be expanded and must not have a collapse option.

Use compact controls and reduce excessive empty space.

## 8.2 Required Settings

Integrate the settings already present in the existing project. Do not remove existing useful settings.

Include, where supported:

### Font Settings

- Font family.
- Font size.
- Font weight.
- Letter spacing.
- Line height.
- Text case.
- Alignment.
- Word spacing.
- Font fallback.
- Hindi/Devanagari-compatible font fallback.
- English-compatible font fallback.
- Hinglish-compatible font fallback.

Suggested font options should be loaded from the project's existing font system. Do not force a new font system if one already exists.

### Color

- Text/fill color.
- Highlight color.
- Active word color.
- Outline color.
- Background box color.
- Background opacity.
- Shadow color.
- Gradient support only if already compatible with the rendering system.

### Outline and Shadow

- Outline width.
- Shadow enable/disable.
- Shadow blur.
- Shadow offset X.
- Shadow offset Y.
- Shadow opacity.

### Position and Layout

- Horizontal position.
- Vertical position.
- Caption baseline.
- Safe-area positioning.
- Text alignment.
- Maximum line width.
- Maximum lines.
- Padding.
- Margin.
- Caption box width.
- Caption box height.
- Preview drag positioning.

### Word/Line Mode

Provide a clear mode selector:

- WORD
- LINE

WORD mode:

- Highlight words individually.
- Support active word color.
- Support word-level timing when available.

LINE mode:

- Display complete caption lines.
- Support line-level styling.
- Keep timing synchronized.

### Animation

If the existing project supports animation, integrate:

- None.
- Fade.
- Pop.
- Word highlight.
- Slide.
- Scale.
- Bounce only if performance remains acceptable.

Animation must not be mandatory for export.

### Apply Controls

Include:

- Apply to Current Caption.
- Apply to Selected Captions.
- Apply to All.
- Reset Current Style.
- Reset All Styles only with confirmation.

All controls must modify the actual caption model and live preview.

---

# 9. TRANSCRIPT CAPTION LINES PANEL

## 9.1 Panel Position

Keep the Transcript Caption Lines panel on the far right.

It must remain available after captions are generated or imported.

## 9.2 Data Structure

Use a normalized model similar to:

```ts
type CaptionWord = {
  id: string;
  text: string;
  start: number;
  end: number;
  confidence?: number;
};

type CaptionLine = {
  id: string;
  start: number;
  end: number;
  text: string;
  words: CaptionWord[];
  styleId?: string;
  position?: {
    x: number;
    y: number;
  };
};
```

## 9.3 Interactions

Support:

- Select line.
- Select word.
- Edit line text.
- Edit word text.
- Adjust start/end time.
- Split line.
- Merge selected lines.
- Delete line.
- Duplicate line if already part of the existing editor.
- Add new caption.
- Scroll to active line during playback.
- Click a line to move the playhead.
- Highlight active line and active word.
- Keep transcript, preview, and timeline synchronized.

## 9.4 Empty, Loading, and Error States

Before captions exist:

- Show a compact empty state.
- Provide Import Caption and Generate Caption actions.

During generation:

- Show progress.
- Show the current stage.
- Allow cancel if supported.

On error:

- Show a human-readable error.
- Provide Retry.
- Preserve imported video and existing edits.

---

# 10. CAPTION EDITING TOOLBAR

Keep only these required actions:

1. Add Caption
2. Split
3. Merge
4. Delete

Remove:

- Duplicate, unless it is required by the existing project and placed in a secondary menu.
- Any unnecessary toolbar action.
- Skip Silence.
- New Project.

## 10.1 Add Caption

- Add a caption at the current playhead.
- Use a sensible default duration.
- Focus the new caption for editing.
- Add it to the transcript panel and timeline.
- Make it visible in the preview.
- Support undo.

## 10.2 Split

- Split the selected caption at the playhead or selected word boundary.
- Preserve text order.
- Calculate valid timestamps.
- Prevent zero-length captions.
- Preserve styling.
- Support undo.

## 10.3 Merge

- Merge selected adjacent captions.
- Preserve chronological order.
- Join text using the project's language-aware spacing rules.
- Use the earliest start and latest end.
- Preserve or intelligently combine styles.
- Support undo.

## 10.4 Delete

- Delete the selected caption(s).
- Support multi-selection if already available.
- Confirm only for destructive bulk operations, not every single deletion.
- Support undo.

---

# 11. TIMELINE AND WAVEFORM

## 11.1 Timeline

The timeline must remain at the bottom.

Include:

- Time ruler.
- Playhead.
- Caption blocks.
- Caption text preview.
- Caption start/end.
- Selection state.
- Horizontal scrolling.
- Zoom controls if supported.
- Snap-to-playhead behavior where useful.
- Waveform visualization.
- Playback synchronization.

## 11.2 Caption Blocks

Each block should:

- Be selectable.
- Show shortened caption text when space is limited.
- Show the number of words or metadata only if useful.
- Be draggable horizontally to change timing.
- Support resizing from left/right edges if supported.
- Update transcript and preview immediately.
- Prevent invalid timestamps.
- Show overlap warnings or resolve overlaps using a clear rule.

## 11.3 Waveform

- Generate waveform from the imported media where technically possible.
- Cache waveform data.
- Avoid blocking the main UI thread.
- Use a simplified waveform for low-resource devices.
- Synchronize waveform and playhead with the video.

---

# 12. CAPTION RENDERING ENGINE

The caption preview and exported captions must use the same style model as much as technically possible.

Do not create a preview-only style system that differs from export.

Support:

- Font family.
- Font size.
- Font weight.
- Fill color.
- Outline.
- Shadow.
- Background box.
- Position.
- Alignment.
- Word/line mode.
- Active word highlighting.
- Line wrapping.
- Hindi and Devanagari text.
- English and Hinglish text.
- Safe area.
- Aspect ratio adaptation.

Use the existing rendering engine if present.

If the project uses ASS/SSA, keep the ASS style mapping consistent and validate generated ASS syntax.

---

# 13. IMPORT AND EXPORT VALIDATION

## 13.1 Import Validation

Validate:

- Unsupported file types.
- Missing files.
- Corrupt media.
- Invalid caption timestamps.
- Negative timestamps.
- End time before start time.
- Empty caption text.
- Overlapping captions.
- Unsupported encoding.
- Very large files.

Provide clear messages such as:

- What went wrong.
- Why it happened.
- What the user can do next.

## 13.2 Export Validation

Before export:

- Confirm a video is loaded when video export is selected.
- Confirm at least one caption exists for caption export.
- Validate timestamps.
- Validate fonts and style values.
- Warn about unsupported effects.
- Do not claim completion before the output is actually created.

---

# 14. STATE MANAGEMENT

Use the existing state-management architecture if one exists.

Do not introduce a second competing state system without a strong reason.

Suggested state domains:

```ts
type CaptionStudioState = {
  projectId?: string;
  video?: {
    fileName: string;
    pathOrUrl: string;
    duration: number;
    width: number;
    height: number;
    fps?: number;
  };
  captions: CaptionLine[];
  selectedCaptionIds: string[];
  selectedWordId?: string;
  activePresetId?: string;
  styleSettings: StyleSettings;
  currentTime: number;
  isPlaying: boolean;
  zoom: number;
  generation: {
    status: "idle" | "loading" | "processing" | "complete" | "error";
    progress: number;
    message?: string;
  };
  dirty: boolean;
};
```

All major operations must update the shared state:

- Import video.
- Import caption.
- Generate caption.
- Edit text.
- Change timing.
- Add.
- Split.
- Merge.
- Delete.
- Apply preset.
- Change style.
- Export.
- Undo.
- Redo.

---

# 15. UNDO/REDO ARCHITECTURE

Implement command-based or snapshot-based history using the existing architecture.

History must cover:

- Caption creation.
- Caption deletion.
- Text changes.
- Timing changes.
- Split.
- Merge.
- Preset application.
- Style changes.
- Position changes.
- Bulk Apply to All.

Avoid storing huge video binaries in undo history.

Use immutable or safely cloned caption/style state.

Add debouncing for continuous slider changes so one drag does not create hundreds of undo entries.

---

# 16. PERFORMANCE REQUIREMENTS

The application must be optimized for:

- Windows laptop with approximately 8 GB RAM.
- Approximately 256 GB storage.
- Integrated graphics or modest hardware.
- Large videos and many caption lines.

Requirements:

- Do not load the complete video into memory.
- Use streaming/media element playback where possible.
- Use Web Workers or background processing for waveform/transcript parsing if supported.
- Virtualize long transcript lists if necessary.
- Avoid rendering every word as a heavy component when thousands of words exist.
- Debounce expensive style updates.
- Cache parsed captions and waveform data.
- Avoid unnecessary React re-renders.
- Keep scrolling smooth.
- Provide processing indicators for expensive operations.
- Never freeze the complete interface during import, parsing, generation, or export.

---

# 17. ACCESSIBILITY AND USABILITY

Implement:

- Keyboard navigation.
- Visible focus states.
- Accessible button labels.
- Tooltips for icon-only buttons.
- Sufficient color contrast.
- Screen-reader-friendly labels where practical.
- Error messages that are not color-only.
- Scrollable areas with clear focus behavior.
- No controls that can only be used by mouse.
- Responsive layout.

---

# 18. VISUAL DESIGN RULES

Use the existing Up Clip Studio theme.

The visual direction should be:

- Premium.
- Modern.
- Dark/deep-green primary palette as already used by the project.
- Teal/green accent where already present.
- Subtle purple highlight only where it already exists in the current design.
- Clean borders.
- Soft shadows.
- Controlled glow.
- High readability.
- Compact professional editor layout.
- No excessive glassmorphism.
- No unnecessary gradients.
- No random color changes.
- No purple-only redesign.
- No black-and-white-only redesign.
- No unrelated visual style.

Reuse:

- Existing fonts.
- Existing icon library.
- Existing button components.
- Existing sidebar.
- Existing cards.
- Existing modal system.
- Existing toast system.
- Existing theme tokens.
- Existing spacing tokens.
- Existing responsive breakpoints.

---

# 19. PROJECT INTEGRATION RULES

Before writing code:

1. Inspect the complete repository.
2. Identify the framework and build tool.
3. Identify routing.
4. Identify current Up Clip Studio layout.
5. Identify current sidebar implementation.
6. Identify theme and design tokens.
7. Identify fonts and icon library.
8. Identify media playback implementation.
9. Identify caption parser.
10. Identify existing local AI/Whisper integration.
11. Identify existing export pipeline.
12. Identify existing state management.
13. Identify existing persistence mechanism.
14. Identify existing tests.
15. Identify current Caption Studio implementation, if any.

Do not overwrite working modules without inspection.

Do not create duplicate components when an existing reusable component is available.

Do not break:

- Existing routes.
- Existing sidebar navigation.
- Existing projects.
- Existing video tools.
- Existing settings.
- Existing storage.
- Existing media utilities.
- Existing authentication or local session behavior, if present.

---

# 20. RECOMMENDED COMPONENT STRUCTURE

Adapt this structure to the existing project rather than blindly creating duplicate folders.

```text
src/
├── app/
│   ├── routes/
│   │   └── CaptionStudioRoute.*
│   └── providers/
├── components/
│   ├── layout/
│   │   ├── AppShell.*
│   │   ├── TopHeader.*
│   │   └── Sidebar.*
│   ├── caption-studio/
│   │   ├── CaptionStudioPage.*
│   │   ├── CaptionStudioHeader.*
│   │   ├── VideoPreviewPanel.*
│   │   ├── VideoPlayerControls.*
│   │   ├── PresetLibrary.*
│   │   ├── PresetCard.*
│   │   ├── TypographyStylePanel.*
│   │   ├── FontSettings.*
│   │   ├── ColorSettings.*
│   │   ├── PositionSettings.*
│   │   ├── AnimationSettings.*
│   │   ├── TranscriptCaptionLines.*
│   │   ├── TranscriptLine.*
│   │   ├── WordChip.*
│   │   ├── CaptionToolbar.*
│   │   ├── CaptionTimeline.*
│   │   ├── TimelineCaptionBlock.*
│   │   ├── Waveform.*
│   │   ├── ImportVideoDialog.*
│   │   ├── ImportCaptionDialog.*
│   │   ├── OfflineAISettings.*
│   │   └── ExportDialog.*
├── features/
│   ├── captions/
│   │   ├── captionTypes.*
│   │   ├── captionParser.*
│   │   ├── captionSerializer.*
│   │   ├── captionValidation.*
│   │   ├── captionHistory.*
│   │   └── captionSelectors.*
│   ├── media/
│   │   ├── mediaMetadata.*
│   │   ├── waveform.*
│   │   └── playback.*
│   └── transcription/
│       ├── whisperAdapter.*
│       ├── transcriptionQueue.*
│       └── transcriptionTypes.*
├── stores/
│   └── captionStudioStore.*
├── styles/
│   └── existing-theme-files
└── tests/
    ├── captionParser.test.*
    ├── captionEditing.test.*
    ├── captionHistory.test.*
    ├── captionExport.test.*
    └── captionStudioUI.test.*
```

Use the project's actual language and conventions. Do not force TypeScript if the project is JavaScript, but prefer typed models if the existing architecture supports them.

---

# 21. REQUIRED FUNCTIONAL FLOWS

## Flow A: Import Video

1. User clicks Import Video.
2. File picker opens.
3. User selects a supported video.
4. Application validates the file.
5. Video metadata loads.
6. Preview becomes visible.
7. Player controls become active.
8. Timeline updates.
9. Waveform generation begins.
10. User can play, pause, and seek.

## Flow B: Import Caption

1. User clicks Import Caption.
2. User selects SRT/VTT/ASS/JSON.
3. Parser validates the file.
4. Captions appear in transcript panel.
5. Caption blocks appear in timeline.
6. Captions render in preview.
7. User can edit captions.

## Flow C: Generate Caption

1. User clicks Generate Caption.
2. Offline AI Settings opens.
3. User selects language/model/settings.
4. User starts generation.
5. Progress is displayed.
6. Captions are created.
7. Transcript panel populates.
8. Timeline populates.
9. Preview displays captions.
10. User can edit and style them.

## Flow D: Apply Preset

1. User selects a preset.
2. Selected state updates.
3. Preview updates.
4. Typography & Style controls update.
5. User can fine-tune settings.
6. User can Apply to Current, Selected, or All.

## Flow E: Edit Caption

1. User selects a caption line or timeline block.
2. User edits text/timing/style.
3. Preview updates.
4. Transcript updates.
5. Timeline updates.
6. Undo becomes available.
7. Saved state becomes unsaved.

## Flow F: Export

1. User clicks Export.
2. Export options open.
3. User selects output type.
4. Application validates the project.
5. Export begins.
6. Progress is displayed.
7. Output is created.
8. Success state is shown only after completion.
9. User can open or locate the output where supported.

---

# 22. ERROR HANDLING

Handle and test:

- No video selected.
- Unsupported video format.
- Corrupt video.
- No caption selected for editing.
- Invalid caption file.
- Invalid timestamp.
- Caption overlaps.
- Local transcription unavailable.
- Insufficient storage.
- Export failure.
- Unsupported font.
- Missing font fallback.
- Browser permission failure.
- User cancels file picker.
- User closes a dialog while processing.
- Large file processing.
- Empty transcript.
- Unexpected renderer error.

Errors must be understandable and actionable.

---

# 23. TESTING REQUIREMENTS

Create or update tests for:

## UI Tests

- Header buttons appear in correct order.
- New Project is absent.
- Skip Silence is absent.
- Export exists.
- Undo and Redo appear after Saved.
- Font Settings is always expanded.
- Preset Library scrolls.
- Typography & Style scrolls.
- Transcript panel appears after caption generation/import.
- Add Caption, Split, Merge, and Delete are available.
- Duplicate is not shown as a primary toolbar action.

## Functional Tests

- Import video works.
- Import caption works.
- SRT parsing works.
- VTT parsing works.
- Caption generation state works.
- Add caption works.
- Split works.
- Merge works.
- Delete works.
- Text editing works.
- Timing editing works.
- Preset application works.
- Apply to All works.
- Undo/Redo works.
- Export validation works.
- Export output is actually created.

## Performance Tests

- Long transcript scrolling remains usable.
- Large caption lists do not cause severe lag.
- Style sliders do not create excessive history entries.
- Video playback remains responsive.
- Waveform processing does not freeze the UI.

---

# 24. ACCEPTANCE CRITERIA

The task is complete only when all of the following are true:

- [ ] The Caption Studio visually follows the supplied reference.
- [ ] Existing Up Clip Studio theme is reused.
- [ ] Existing sidebar icons are preserved.
- [ ] New Project is removed from this screen.
- [ ] Import Video is functional.
- [ ] Import Caption is functional.
- [ ] Generate Caption is functional or clearly connected to the local transcription setup.
- [ ] Export button exists at the end of the header and is functional.
- [ ] Saved is preserved.
- [ ] Undo and Redo are placed after Saved and work.
- [ ] Skip Silence in Preview is removed.
- [ ] Preset Library heading is compact.
- [ ] Presets are scrollable and data-driven.
- [ ] Typography & Style heading is compact.
- [ ] Typography & Style settings are scrollable.
- [ ] Font Settings remains permanently expanded.
- [ ] Collapse control is removed from Font Settings.
- [ ] Transcript Caption Lines remains available.
- [ ] Transcript panel populates after import/generation.
- [ ] Add Caption works.
- [ ] Split works.
- [ ] Merge works.
- [ ] Delete works.
- [ ] Timeline and waveform are synchronized.
- [ ] Preview updates when styles change.
- [ ] Captions can be moved/repositioned in preview where supported.
- [ ] WORD and LINE modes work.
- [ ] Hindi, English, and Hinglish text is supported.
- [ ] No fake buttons or fake success states remain.
- [ ] Existing unrelated modules continue working.
- [ ] Tests pass or failures are documented with causes and next steps.
- [ ] The app runs successfully using the project's existing start/build commands.

---

# 25. REQUIRED ANTIGRAVITY EXECUTION PROCESS

Follow this process in order.

## Phase 1 — Repository Audit

- Inspect the entire repository.
- Produce a short architecture report.
- Identify existing reusable components.
- Identify conflicts and risks.
- Do not modify files yet.

## Phase 2 — UI and State Plan

- Create a component map.
- Create a state-flow map.
- Create a data model.
- Identify required files to modify.
- Identify new files only where necessary.

## Phase 3 — Implementation

- Implement the header changes.
- Implement the panel layout.
- Implement scrollable presets.
- Implement scrollable Typography & Style settings.
- Make Font Settings permanently expanded.
- Implement transcript synchronization.
- Implement timeline synchronization.
- Integrate existing media and caption utilities.

## Phase 4 — Functional Integration

- Connect import.
- Connect caption parsing.
- Connect local generation.
- Connect editing actions.
- Connect undo/redo.
- Connect export.

## Phase 5 — QA and Refinement

- Run linting.
- Run type checking if available.
- Run unit tests.
- Run integration tests.
- Run build.
- Test manually in the browser.
- Test keyboard navigation.
- Test at multiple viewport widths.
- Fix visual overflow.
- Fix console errors.
- Fix broken interactions.

## Phase 6 — Final Report

Return:

1. Files changed.
2. Files added.
3. Existing components reused.
4. Features implemented.
5. Features that depend on optional local tools.
6. Commands used to run the app.
7. Test results.
8. Known limitations.
9. Recommended next steps only if genuinely necessary.

Do not claim that a feature is complete if it is only a visual placeholder.

---

# 26. FINAL IMPLEMENTATION RULE

Build the Caption Studio as a real editing tool, not a static screenshot.

The reference image defines the visual direction. The existing Up Clip Studio project defines the actual design system, architecture, settings, icons, fonts, colors, routes, and reusable functionality.

Preserve the product identity. Make every visible control meaningful and functional. Keep the UI compact, scrollable, synchronized, responsive, and optimized for local-first use.
