# MASTER PROMPT — UP CLIP STUDIO 2.0
## Caption Studio — Exact UI Reconstruction + Fully Functional Implementation

You are working on an existing desktop/local video software called:

UP CLIP STUDIO

Your task is to completely rebuild/refine ONLY the Caption Studio module according to the requirements below.

IMPORTANT:
DO NOT create a different UI concept.
DO NOT redesign the application into your own style.
DO NOT replace the existing Up Clip Studio visual language.
DO NOT invent a new navigation system.
DO NOT remove existing working functionality.

The attached reference images and the existing Up Clip Studio application are the primary source of truth.

The handwritten notebook sketch represents the intended layout.
The existing Up Clip Studio Home/Projects screenshot represents the existing application navigation, theme, icon style, spacing, and overall design language.

The final result must look like a professionally implemented version of the handwritten design — NOT like a generic video editor.

==================================================
1. CORE OBJECTIVE
==================================================

Build a professional Caption Studio for Up Clip Studio.

The user should be able to:

1. Import a video.
2. Preview the video.
3. Use vertical 9:16 video as the primary editing format.
4. Zoom the video preview.
5. Resize/scale captions.
6. Move captions freely.
7. Generate captions using speech-to-text.
8. Select generation language:
   - Hindi
   - English
   - Hinglish
9. Import existing:
   - SRT
   - VTT
   - JSON
10. Automatically display imported captions.
11. Edit caption text.
12. Edit caption timing.
13. Apply caption presets.
14. Create/edit custom presets.
15. Change fonts.
16. Change font size.
17. Change font weight.
18. Change text color.
19. Change stroke.
20. Change shadow.
21. Change glow.
22. Change background/box.
23. Change caption position.
24. Change animation.
25. Change transitions.
26. Enable word-by-word captions.
27. Enable karaoke-style highlighting.
28. Apply settings to all captions.
29. Preview everything in real time.
30. Export final rendered video with captions permanently burned into the video.
31. Export subtitle files when required.
32. Save/load custom presets.
33. Keep every existing Up Clip Studio navigation link functional.

EVERY visible control must either work or be intentionally disabled with a clear reason.
NO decorative fake buttons.

==================================================
2. MOST IMPORTANT DESIGN RULE
==================================================

RECREATE THE HANDWRITTEN NOTEBOOK STRUCTURE.

Do NOT use a different UI concept as the final structure.

The notebook layout is the design reference.

The final UI should feel like:

LEFT NAVIGATION
        +
VIDEO WORKSPACE
        +
CAPTION AREA
        +
RIGHT-SIDE THREE-COLUMN SETTINGS SYSTEM

The interface should be clean, premium, compact and professional.

Do not make the application look like Premiere Pro, DaVinci Resolve, CapCut or another existing editor.

It must remain visually recognizable as:

UP CLIP STUDIO

==================================================
3. EXISTING LEFT SIDEBAR
==================================================

Keep the existing Up Clip Studio left navigation.

Use the existing application's current sidebar structure.

Do not invent a new sidebar.

Existing navigation items should remain available according to the current project, including items such as:

- Home & Projects
- AI Clip Studio
- Caption Studio
- Studio Hub
- Downloader
- YouTube Desk
- Resources / How to Use
- other existing working modules

Use the exact existing icons wherever they already exist.

DO NOT replace existing icons unnecessarily.

Caption Studio must be highlighted when active.

The active Caption Studio item should have the same active-state visual language as the existing application.

==================================================
4. SIDEBAR COLLAPSE
==================================================

The bottom of the sidebar must contain:

Collapse

When clicked:

FULL SIDEBAR
↓
COLLAPSED SIDEBAR

Collapsed state should show icons only.

The main workspace must automatically expand into the freed space.

When expanded again:

icons + labels return.

The transition should be smooth.

The Collapse button itself must remain accessible.

Do not break the content layout when sidebar collapses.

No horizontal overflow.

No overlapping controls.

==================================================
5. TOP HEADER
==================================================

Top header:

[Up Clip Studio Logo]
|
Caption Studio

Use the existing Up Clip Studio logo and typography.

Do not create a random new logo.

On the right/top action area provide:

[Import Video]
[Import SRT/VTT/JSON]
[Generate]
[Export]

These are primary actions.

Buttons must be functional.

--------------------------------------------------
IMPORT VIDEO
--------------------------------------------------

"Import Video" must open the native file picker.

Support common formats:

MP4
MOV
MKV
WEBM
AVI
and other formats already supported by the application's FFmpeg pipeline.

After selecting the video:

- load it into Caption Studio
- display first frame
- detect duration
- initialize timeline
- initialize player
- enable playback
- enable caption workflow

Do not show a fake placeholder.

--------------------------------------------------
IMPORT SUBTITLES
--------------------------------------------------

"Import SRT/VTT/JSON"

Allow:

SRT
VTT
JSON

After import:

- parse the file
- validate timestamps
- load caption text
- load start/end time
- display captions in timeline/list
- display caption on video preview
- allow editing

If JSON uses a supported project/caption schema, preserve supported styling/timing data.

--------------------------------------------------
GENERATE
--------------------------------------------------

Generate button opens a compact generation control.

User must be able to select:

Language:

Hindi
English
Hinglish

Hinglish means:

Hindi speech converted into Roman/Latin characters.

Example:

Hindi:
"मुझे वीडियो बनाना है"

Hinglish:
"Mujhe video banana hai"

Do NOT simply return English translation when Hinglish is selected.

Generation flow:

VIDEO
↓
Audio extraction
↓
Speech-to-text
↓
Language selection
↓
Caption segmentation
↓
Timing generation
↓
Caption list
↓
Video overlay preview

Use the existing local Whisper/speech-to-text implementation if available.

Do not introduce a mandatory cloud API.

If the existing project already has a transcription engine, reuse it.

==================================================
6. EXPORT
==================================================

Export button must provide functional export options.

Primary:

Export Rendered Video

The final exported video must contain the captions visually burned into the video.

Also support subtitle export where existing project architecture allows:

Export SRT
Export VTT
Export JSON

Rendering must preserve:

- video resolution
- aspect ratio
- caption position
- font
- font size
- text color
- stroke
- shadow
- glow
- background
- opacity
- animation where technically supported
- karaoke effect where enabled

Do not export a video without the actual captions.

Do not merely save the preview screenshot.

==================================================
7. VIDEO WORKSPACE
==================================================

IMPORTANT:

The latest final requirement is:

VERTICAL VIDEO FIRST.

Primary canvas:

9:16

Example:

1080 × 1920

The video preview should appear vertically inside the main workspace.

Do NOT stretch the video.

Preserve aspect ratio.

Center the video inside the player.

The video player should be visually prominent.

==================================================
8. VIDEO PLAYER CONTROLS
==================================================

Below the video:

[Play/Pause]

[Current Time / Total Time]

[Timeline / Seek Bar]

[Volume]

[1x]

[2x]

[Fullscreen]

Playback speeds:

0.5x
1x
1.25x
1.5x
2x

Default:

1x

Volume control must work.

Fullscreen must work.

Seeking must work.

Playback controls must work.

The controls must not overlay the video unnecessarily.

==================================================
9. VIDEO ZOOM
==================================================

Add video preview zoom.

The user must be able to:

Zoom In
Zoom Out
Reset

Example:

50%
75%
100%
125%
150%
200%

Also provide:

Fit
Fill

The zoom should affect the preview/canvas positioning, NOT permanently modify the original video.

Do not destroy the original video.

Video position should be draggable when zoomed.

Support:

- pan left/right
- pan up/down
- reset position

This is preview/canvas manipulation.

==================================================
10. CAPTION ZOOM / SCALE
==================================================

Captions must also have their own scale control.

Example:

Caption Scale:
50%
75%
100%
125%
150%
200%

Or a slider.

The user must be able to resize caption visually.

IMPORTANT:

Caption scale must not change the video's zoom.

Video zoom and caption scale are separate controls.

==================================================
11. CAPTION POSITION
==================================================

The user must be able to move captions.

Provide preset positions:

Top Left
Top Center
Top Right

Middle Left
Middle Center
Middle Right

Bottom Left
Bottom Center
Bottom Right

Default:

Bottom Center

Also provide:

Custom Position

For Custom Position:

The caption can be dragged directly inside the video preview.

The user should visually see the caption moving.

Do not force the user to enter X/Y coordinates manually.

However, internally maintain normalized X/Y values so the position remains correct at different resolutions.

==================================================
12. MAIN RIGHT-SIDE STRUCTURE
==================================================

This is extremely important.

The right side should contain THREE logical columns/panels.

Do not make one giant uncontrolled settings panel.

COLUMN 1:
CAPTION PRESETS

COLUMN 2:
CAPTION SETTINGS

COLUMN 3:
CAPTION / TIMING / QUICK INSPECTOR

The three-column structure should be responsive and scrollable.

On smaller window widths, columns may stack or become tabs.

Do not cause horizontal overflow.

==================================================
13. COLUMN 1 — CAPTION PRESETS
==================================================

Title:

Caption Presets

Create at least 20 built-in presets.

Example preset names:

01 Default
02 Clean
03 Bold
04 Minimal
05 YouTube Classic
06 Podcast
07 Modern
08 Creator
09 Dynamic
10 Highlight
11 Strong
12 Soft
13 Cinema
14 News
15 Gaming
16 Educational
17 Viral
18 Karaoke
19 Word Focus
20 Neon

Each preset must actually change relevant caption styling.

Each preset card should show a mini visual preview.

Example:

Hello World

The user clicks a preset and it immediately applies.

Preset cards should support:

- hover preview
- click to apply
- selected state

==================================================
14. CUSTOM PRESETS
==================================================

Add:

+ Custom Preset

User can save current caption styling as a preset.

Custom preset should remember:

font
font size
font weight
text color
stroke
shadow
glow
background
background opacity
padding
corner radius
position
animation
transition
word highlighting
karaoke settings
caption scale

Allow:

Save
Rename
Delete
Duplicate

Persist custom presets locally.

==================================================
15. COLUMN 2 — SETTINGS
==================================================

Column 2 contains the detailed caption styling.

Settings MUST be scrollable.

This fixes the current problem where settings cannot scroll properly.

Use grouped accordion sections.

The user can expand/collapse individual sections.

Add:

Collapse All

and optionally:

Expand All

When Collapse All is clicked:

all accordion sections collapse.

When Expand All is clicked:

all sections expand.

The page itself must remain usable.

No nested-scroll bugs.

==================================================
16. SETTINGS ORDER
==================================================

Use this exact logical order:

1. Preset
2. Caption Text & Timings
3. Font & Typography
4. Stroke
5. Shadow
6. Glow
7. Background & Box
8. Caption Position
9. Animation & Transition
10. Word-by-Word & Karaoke
11. Settings Type
12. Tools & Custom Preset

This order should be preserved unless an existing working implementation requires a technically safer arrangement.

Do not randomly reorder controls.

==================================================
17. PRESET SETTINGS
==================================================

Preset section:

Current Preset
Apply Preset
Save as Custom Preset
Reset Preset

Provide quick controls for:

Font
Size
Color
Position

Advanced controls remain in the other sections.

==================================================
18. CAPTION TEXT & TIMINGS
==================================================

This section must allow editing:

Caption text

Start time

End time

Duration

Example:

00:00.000 → 00:03.200

Allow:

- edit
- split
- merge
- duplicate
- delete

The caption list should be synchronized with the video timeline.

Clicking a caption should:

1. select it
2. seek video to its start time
3. highlight it
4. show it on preview
5. load its settings

==================================================
19. FONT & TYPOGRAPHY
==================================================

Provide a large font library.

At minimum include:

Inter
Roboto
Poppins
Montserrat
Open Sans
Lato
Nunito
Nunito Sans
Manrope
Plus Jakarta Sans
DM Sans
Outfit
Space Grotesk
Oswald
Bebas Neue
Anton
Archivo
Raleway
Source Sans 3
Merriweather

Also support system fonts.

If the project supports local font files:

Add:

Import Font

Allow user to select:

.TTF
.OTF
.WOFF
.WOFF2 where supported

Imported fonts should appear in the font dropdown.

Store imported font metadata locally.

Font settings:

Font Family
Font Size
Font Weight
Line Height
Letter Spacing
Text Alignment
Text Transform

==================================================
20. FONT LOCATION / POSITION
==================================================

The user specifically wants to move the caption.

Therefore:

Font/Caption position is not fixed.

Allow:

drag inside preview
position presets
X/Y normalized position
scale

When dragging:

show subtle alignment guides.

Examples:

center guide
safe-area guide
vertical center
horizontal center

Do not make guides permanently visible.

==================================================
21. TEXT COLOR
==================================================

Provide:

Text Color
Opacity

Color picker must work.

Support:

HEX
RGB
RGBA where applicable

Also provide a small preset color palette.

Do not force only black/white.

Use the existing Up Clip Studio theme for UI colors.

==================================================
22. STROKE
==================================================

Settings:

Enable Stroke
Stroke Width
Stroke Color
Stroke Opacity

Example:

0px → 20px

Real-time preview.

==================================================
23. SHADOW
==================================================

Settings:

Enable Shadow
Shadow Color
Opacity
Blur
Offset X
Offset Y

Real-time preview.

==================================================
24. GLOW
==================================================

Settings:

Enable Glow
Glow Color
Opacity
Blur
Intensity

Real-time preview.

==================================================
25. BACKGROUND & BOX
==================================================

Settings:

Background Enable/Disable

Background Color

Opacity

Padding X

Padding Y

Corner Radius

Box Width Mode:

Auto
Full
Custom

Optional:

Border
Border Width
Border Color

All changes must update preview immediately.

==================================================
26. CAPTION POSITION
==================================================

Include:

Top
Middle
Bottom

Horizontal:

Left
Center
Right

Custom

Also:

Safe Area

Enable/Disable

The user can drag the caption.

==================================================
27. ANIMATION & TRANSITION
==================================================

Add caption entrance/exit animation.

Examples:

None
Fade
Fade Up
Fade Down
Slide Up
Slide Down
Slide Left
Slide Right
Scale
Pop
Bounce
Typewriter

Controls:

Entrance Duration
Exit Duration
Delay

Do not make animation excessively complicated.

Preview must work.

==================================================
28. WORD-BY-WORD & KARAOKE
==================================================

Add:

Enable Word-by-Word

Enable Karaoke

Karaoke settings:

Base Text Color
Highlight Color
Highlight Weight
Highlight Background optional
Timing Mode

Timing must follow caption word timestamps where available.

If word timestamps are unavailable:

fallback gracefully.

Do not crash.

==================================================
29. SETTINGS TYPE
==================================================

Settings Type should control how settings are applied.

Provide:

Current Caption
Selected Captions
All Captions

If:

Current Caption

only current caption changes.

If:

Selected Captions

apply to selected captions.

If:

All Captions

apply globally.

==================================================
30. APPLY TO ALL
==================================================

"Apply to All" must always be available in an obvious location.

When clicked:

Current style configuration
↓
Apply to all captions

This includes:

font
size
weight
color
stroke
shadow
glow
background
position
animation
word-by-word
karaoke
etc.

Show a small confirmation state.

Do not silently fail.

==================================================
31. TOOLS & CUSTOM PRESET
==================================================

Last settings group:

Tools & Custom Preset

Include useful actions:

Save Preset
Duplicate Preset
Reset Style
Copy Style
Paste Style
Import Preset
Export Preset

If preset files are supported, use a stable local JSON schema.

Do not overwrite user presets accidentally.

==================================================
32. THIRD COLUMN — CAPTION INSPECTOR / TIMELINE
==================================================

The third column should NOT be another random settings column.

Use it for:

CAPTION INSPECTOR

and

TIMING / QUICK CONTROLS

This solves the purpose of the third column without changing the requested settings.

Top:

Selected Caption

Then:

Caption text preview

Start
End
Duration

Quick actions:

Edit
Split
Merge
Duplicate
Delete

Then:

Quick Style

Font
Size
Color
Position
Scale

Then:

Caption list / mini timeline.

Clicking a caption in this column must select it in the main timeline and video.

==================================================
33. BOTTOM CAPTION TIMELINE
==================================================

Below the video player, create the caption timeline/list.

Example:

------------------------------------------------
CAPTIONS

00:00 – 00:03   Welcome to Up Clip Studio
00:03 – 00:07   Create captions automatically
00:07 – 00:11   Customize every word
00:11 – 00:15   Export your final video
------------------------------------------------

Each caption item must be clickable.

Click:

- seek video
- select caption
- show caption in preview
- load style settings

The timeline should support scrolling.

==================================================
34. VIDEO + CAPTION SYNCHRONIZATION
==================================================

This is mandatory.

Video time must control caption visibility.

Example:

Video time = 00:05

Only the caption whose timing contains 00:05 should appear.

As video plays:

caption changes automatically.

When user seeks:

caption updates automatically.

When user edits timing:

caption timing updates immediately.

==================================================
35. LIVE PREVIEW
==================================================

Every style setting must update the preview without requiring export.

Examples:

Change font
→ preview changes.

Change size
→ preview changes.

Change color
→ preview changes.

Change stroke
→ preview changes.

Move caption
→ preview changes.

Change animation
→ preview changes.

Change karaoke
→ preview changes.

Do not require page reload.

==================================================
36. VERTICAL VIDEO CANVAS
==================================================

Primary:

9:16

Recommended preview:

1080 × 1920 logical canvas.

But render according to original/project resolution.

Do NOT permanently resize the source video unless export settings require it.

Provide aspect ratio selector only where the existing project architecture supports it:

9:16
16:9
1:1
Custom

BUT:

DEFAULT MUST BE:

9:16 Vertical.

==================================================
37. CAPTION RESIZE
==================================================

The caption itself must be visually resizable.

Support:

drag handles where practical

OR

Scale slider.

Recommended:

Scale slider + direct drag positioning.

Do not make the user accidentally resize the video when trying to resize caption.

Use separate interaction modes:

Video Transform
Caption Transform

==================================================
38. INTERACTION MODES
==================================================

Provide a small transform mode:

[Video]

[Caption]

When Video selected:

drag/zoom controls video.

When Caption selected:

drag/scale controls caption.

This prevents accidental movement.

==================================================
39. SAFE AREA
==================================================

Add:

Safe Guides

Optional.

When enabled:

show safe title area
show safe caption area

These guides must NOT appear in exported video.

==================================================
40. THEME
==================================================

IMPORTANT:

DO NOT use the old black-and-white-only theme.

Use the EXISTING UP CLIP STUDIO THEME.

Read the existing project's design tokens/theme system.

Reuse:

existing background colors
existing surface colors
existing accent color
existing typography
existing border radius
existing shadows
existing icons
existing active states
existing button styles

Do NOT invent an unrelated color palette.

The UI should feel like the same product as Home & Projects.

If the existing project already has:

Dark Theme
Light Theme

preserve both.

Theme switching must continue to work.

Any existing theme-management system must be reused.

==================================================
41. USER PREFERENCES
==================================================

Reuse the existing project's preference architecture.

Do not create a separate incompatible settings system.

Preferences should remember:

theme
sidebar state
last selected font
last selected preset
default caption position
default caption size
default generation language
playback speed
video zoom
caption scale
safe guides state

Use local persistence.

==================================================
42. ICON SYSTEM
==================================================

Use the existing icon library already present in the project.

Do NOT mix multiple icon styles.

Icons must have:

consistent stroke width
consistent size
consistent alignment

Use icons for:

Import
Generate
Export
Play
Pause
Volume
Fullscreen
Zoom
Settings
Presets
Caption
Timeline
Delete
Duplicate
Reset
Save
Collapse

==================================================
43. NAVIGATION LINKS
==================================================

THIS IS MANDATORY.

Every existing Up Clip Studio navigation item must continue working.

Specifically:

When user clicks:

Caption Studio

it must navigate directly to:

Caption Studio

No broken route.

No blank page.

No console navigation errors.

When user leaves Caption Studio and returns:

the module should restore state where practical.

Also verify every existing "Caption Studio" link/button across the application.

Any button labeled:

Caption Studio

must open the actual Caption Studio route.

Do not create duplicate Caption Studio routes.

==================================================
44. ROUTING CHECK
==================================================

Test:

Home
↓
Caption Studio

Home
↓
AI Clip Studio
↓
Caption Studio

Sidebar
↓
Caption Studio

Any dashboard shortcut
↓
Caption Studio

All must resolve correctly.

==================================================
45. RESPONSIVE DESKTOP LAYOUT
==================================================

Target:

Windows desktop/laptop.

The user's laptop has:

8 GB RAM
256 GB storage

Therefore:

DO NOT create an unnecessarily heavy UI.

Avoid excessive animations.

Avoid continuously rendering expensive effects.

Use GPU acceleration only where appropriate.

The editor must remain usable on 8 GB RAM systems.

==================================================
46. PERFORMANCE
==================================================

Video preview should not repeatedly re-render the entire application.

Use:

debounced settings updates where necessary
memoized components
virtualized caption list if large
efficient timeline rendering
lazy-loaded panels
thumbnail caching

Do not load every font into memory at startup.

Load fonts on demand.

Do not decode the entire video into RAM.

Use FFmpeg/native video playback architecture already available.

==================================================
47. LOCAL-FIRST ARCHITECTURE
==================================================

The application must continue to work locally.

No mandatory:

cloud backend
paid API
subscription
online database

Speech-to-text should use the existing local implementation.

Internet must not be required for basic:

video import
subtitle import
caption editing
styling
preview
export

==================================================
48. ERROR HANDLING
==================================================

Handle:

unsupported video
corrupted video
invalid SRT
invalid VTT
invalid JSON
missing timestamps
overlapping captions
empty captions
missing font
missing audio
transcription failure
export failure
FFmpeg failure

Show user-friendly errors.

Never crash the application.

==================================================
49. UNSUPPORTED FONT FALLBACK
==================================================

If a custom font cannot be loaded:

Fallback automatically to a safe default font.

Show:

"Font unavailable — using fallback font."

Do not break caption rendering.

==================================================
50. CAPTION DATA MODEL
==================================================

Use a clean internal model:

Caption:

id
text
startTime
endTime
duration
style
position
scale
animation
wordTimings
karaokeEnabled

Style:

fontFamily
fontSize
fontWeight
lineHeight
letterSpacing
textColor
textOpacity
stroke
shadow
glow
background
backgroundOpacity
padding
borderRadius
alignment

Position:

x
y
anchor
scale

Animation:

in
out
duration
delay

==================================================
51. PRESET DATA MODEL
==================================================

Preset:

id
name
thumbnail/preview
font
fontSize
fontWeight
textColor
stroke
shadow
glow
background
backgroundOpacity
position
scale
animation
karaoke
wordByWord

Built-in presets must not be accidentally overwritten.

==================================================
52. GENERATION LANGUAGE
==================================================

Generate dialog:

--------------------------------
GENERATE CAPTIONS

Language

○ Hindi
○ English
○ Hinglish

[ Generate Captions ]
--------------------------------

Hindi:

Hindi script.

English:

English script.

Hinglish:

Hindi speech represented using Roman/Latin characters.

Example:

"Mujhe ye video banana hai"

NOT:

"I want to make this video"

==================================================
53. GENERATION OPTIONS
==================================================

Where technically supported, allow:

Language
Caption segmentation
Maximum words per caption
Minimum caption duration
Maximum caption duration
Punctuation
Speaker detection if supported

Keep advanced options collapsed by default.

Do not clutter the main interface.

==================================================
54. IMPORT JSON
==================================================

JSON import must support a documented internal schema.

Validate before loading.

If the JSON is not recognized:

show:

"Unsupported caption JSON format."

Do not crash.

==================================================
55. EXPORT SETTINGS
==================================================

Export dialog:

--------------------------------
EXPORT VIDEO

Resolution:
Original
1080p
720p

Format:
MP4

Quality:
High
Medium
Low

Burn Captions:
ON

[Export]
--------------------------------

For the main workflow:

Burn Captions = ON

The exported video must visibly contain the captions.

==================================================
56. SAVE PROJECT
==================================================

Use the existing project's save/project system where available.

Caption Studio project should remember:

video reference
caption data
preset
style
timings
language
settings

Do not duplicate the entire source video unnecessarily.

==================================================
57. UNDO / REDO
==================================================

Use the existing application's undo/redo architecture if available.

At minimum support:

caption text changes
timing changes
style changes
position changes
preset application
delete
split
merge

==================================================
58. RESET
==================================================

Provide:

Reset Current Caption

Reset Style

Reset All Caption Styles

Reset Workspace

Do not delete video or captions accidentally.

Dangerous operations require confirmation.

==================================================
59. VISUAL DESIGN
==================================================

The visual design should match Up Clip Studio.

Desired qualities:

premium
modern
clean
professional
compact
dark UI if existing theme is dark
accent-colored highlights
soft rounded panels
clear hierarchy
minimal clutter

Do NOT use:

huge cards
excessive gradients
random neon colors
unnecessary glassmorphism
giant empty spaces
oversized buttons
generic dashboard cards

The notebook sketch should remain visually recognizable.

==================================================
60. THREE-COLUMN RIGHT PANEL
==================================================

Final conceptual structure:

LEFT:
Caption Presets

CENTER:
Settings

RIGHT:
Caption Inspector + Timing

Example:

┌────────────────┬────────────────────┬─────────────────────┐
│ CAPTION        │ SETTINGS           │ INSPECTOR           │
│ PRESETS        │                    │                     │
│                │ Preset             │ Selected Caption    │
│ Default        │ Caption Text       │ Start / End         │
│ Bold           │ Font               │ Duration            │
│ Clean          │ Typography         │                     │
│ Podcast        │ Stroke             │ Quick Style         │
│ YouTube        │ Shadow              │ Font                │
│ Modern         │ Glow               │ Size                │
│ Dynamic        │ Background         │ Position            │
│ ...            │ Position           │ Scale               │
│                │ Animation          │                     │
│ + Custom       │ Karaoke            │ Caption List        │
│                │ Tools              │                     │
└────────────────┴────────────────────┴─────────────────────┘

All three areas must have independent scrolling where required.

Avoid nested-scroll bugs.

==================================================
61. SCROLL BEHAVIOR
==================================================

The settings panel MUST scroll.

The preset panel may scroll.

The caption list may scroll.

The main video workspace should not unexpectedly scroll when the mouse is over the settings.

Use independent scroll containers.

Mouse wheel should work naturally.

Keyboard scrolling should work.

==================================================
62. COLLAPSIBLE SETTINGS
==================================================

Every major settings group:

Preset
Caption Text & Timings
Font & Typography
Stroke
Shadow
Glow
Background & Box
Caption Position
Animation & Transition
Word-by-Word & Karaoke
Settings Type
Tools & Custom Preset

must support:

Expand
Collapse

Top controls:

Expand All
Collapse All

The collapsed state should persist locally if practical.

==================================================
63. KEYBOARD SHORTCUTS
==================================================

Use existing application shortcuts where available.

Recommended:

Space = Play/Pause
Ctrl+Z = Undo
Ctrl+Shift+Z = Redo
Ctrl+S = Save
Delete = Delete selected caption
Arrow Left/Right = timeline movement
Shift + Arrow = larger timeline movement

Do not override important existing application shortcuts.

==================================================
64. ACCESSIBILITY
==================================================

Every button needs:

tooltip
accessible label

Keyboard navigation should work.

Focus states must be visible.

Do not rely only on color to indicate selected state.

==================================================
65. IMPLEMENTATION RULE
==================================================

Before changing code:

1. Inspect existing project.
2. Identify framework.
3. Identify existing routing.
4. Identify existing theme.
5. Identify existing component library.
6. Identify existing icon library.
7. Identify existing video engine.
8. Identify existing FFmpeg integration.
9. Identify existing speech-to-text.
10. Identify existing storage/database.
11. Identify existing project state management.
12. Identify existing settings/preferences.

REUSE existing architecture.

Do NOT unnecessarily rewrite the entire application.

Do NOT introduce a second framework.

Do NOT duplicate functionality that already exists.

==================================================
66. IMPORTANT — EXISTING PROJECT PREFERENCES
==================================================

Take the established preferences from the existing Up Clip Studio project.

Preserve:

- current navigation
- current theme system
- current typography system
- current icons
- current button behavior
- current spacing system
- current sidebar
- current collapse behavior
- current project structure
- current local-first architecture
- current media processing architecture
- current settings persistence

The Caption Studio should feel like it belongs to the same application.

==================================================
67. DO NOT BREAK OTHER MODULES
==================================================

While implementing Caption Studio:

DO NOT break:

Home & Projects
AI Clip Studio
Studio Hub
Downloader
YouTube Desk
other existing modules

Run regression testing after implementation.

==================================================
68. ACCEPTANCE TEST — IMPORT VIDEO
==================================================

Test:

Open Caption Studio
↓
Click Import Video
↓
Select MP4
↓
Video loads
↓
Video displays
↓
Play works
↓
Pause works
↓
Seek works
↓
Volume works
↓
1x works
↓
2x works
↓
Fullscreen works
↓
Video zoom works

PASS only if all work.

==================================================
69. ACCEPTANCE TEST — IMPORT SUBTITLE
==================================================

Import video.

Then:

Import SRT.

Expected:

Captions immediately appear.

Test VTT.

Expected:

Captions immediately appear.

Test JSON.

Expected:

Captions immediately appear if schema is supported.

==================================================
70. ACCEPTANCE TEST — GENERATE
==================================================

Import video.

Click Generate.

Select:

Hindi

Generate.

Then:

English.

Generate.

Then:

Hinglish.

Generate.

Verify output language behavior.

Verify timestamps.

Verify captions appear on timeline.

==================================================
71. ACCEPTANCE TEST — STYLE
==================================================

Select caption.

Change:

Font
Size
Weight
Color
Stroke
Shadow
Glow
Background
Position
Scale

Every change must appear in preview.

==================================================
72. ACCEPTANCE TEST — MOVE CAPTION
==================================================

Select Caption Transform.

Drag caption.

Expected:

caption moves.

Video does NOT move.

Select Video Transform.

Drag/zoom video.

Expected:

video moves.

Caption does NOT move.

==================================================
73. ACCEPTANCE TEST — APPLY TO ALL
==================================================

Style one caption.

Click:

Apply to All.

Expected:

all captions receive style.

Do not modify caption text/timing unless specifically intended.

==================================================
74. ACCEPTANCE TEST — EXPORT
==================================================

Import video.

Import/generate captions.

Style captions.

Click Export.

Render.

Open exported MP4.

Expected:

captions are permanently visible in final video.

Verify:

position
font
size
color
stroke
background

==================================================
75. ACCEPTANCE TEST — NAVIGATION
==================================================

Click every Caption Studio entry in the application.

Expected:

all open the same Caption Studio page.

No:

404
blank page
broken route
console navigation error

==================================================
76. ACCEPTANCE TEST — COLLAPSE
==================================================

Click sidebar Collapse.

Expected:

sidebar becomes icon-only.

Main workspace expands.

Click again.

Expected:

sidebar returns.

Then test:

Collapse All

inside settings.

Expected:

all settings accordions collapse.

Then:

Expand All

Expected:

all expand.

==================================================
77. ACCEPTANCE TEST — RESPONSIVENESS
==================================================

Test:

1366×768
1600×900
1920×1080

No:

horizontal overflow
overlapping panels
hidden export button
broken sidebar
broken video preview
unreachable settings

At smaller widths, convert the three-column inspector into tabs/stacked sections rather than allowing the interface to break.

==================================================
78. FINAL VISUAL REQUIREMENT
==================================================

The final screen should visually read as:

UP CLIP STUDIO
        |
CAPTION STUDIO

LEFT:
existing Up Clip Studio navigation

CENTER:
large vertical video player

BOTTOM:
video controls + caption timeline

RIGHT:
three-column caption workspace

TOP:
Import Video
Import SRT/VTT/JSON
Generate
Export

The result should look like the handwritten notebook concept has been professionally converted into a real application.

==================================================
79. DO NOT DO THESE THINGS
==================================================

DO NOT:

- redesign the entire application
- replace existing navigation
- remove existing modules
- use black/white-only styling
- create fake buttons
- create non-functional controls
- make the settings panel non-scrollable
- make video zoom and caption zoom the same control
- make caption position fixed
- remove Apply to All
- remove custom presets
- remove SRT/VTT/JSON
- remove Generate
- remove Export
- require a cloud service
- break existing routes
- introduce unnecessary frameworks
- create duplicate Caption Studio pages
- replace the existing theme system
- overwrite user presets without confirmation

==================================================
80. FINAL DEVELOPMENT PROCESS
==================================================

Follow this sequence:

PHASE 1
Inspect existing project.

PHASE 2
Map existing architecture.

PHASE 3
Map existing theme/components/icons/routes.

PHASE 4
Implement Caption Studio layout.

PHASE 5
Implement video import/player.

PHASE 6
Implement subtitle import.

PHASE 7
Implement caption timeline.

PHASE 8
Implement generation language selector.

PHASE 9
Implement presets.

PHASE 10
Implement typography.

PHASE 11
Implement stroke/shadow/glow.

PHASE 12
Implement background/box.

PHASE 13
Implement caption positioning and scaling.

PHASE 14
Implement animations.

PHASE 15
Implement word-by-word/karaoke.

PHASE 16
Implement Apply to All.

PHASE 17
Implement custom presets.

PHASE 18
Implement export/render.

PHASE 19
Fix routing/navigation.

PHASE 20
Run full regression testing.

==================================================
81. FINAL OUTPUT REQUIRED FROM CODING AGENT
==================================================

After implementation provide:

1. Files changed.
2. Files created.
3. Dependencies added.
4. Existing dependencies reused.
5. Features implemented.
6. Any known limitations.
7. Test results.
8. Build result.
9. Run instructions.
10. Export/render test result.
11. Navigation test result.

Do not simply say:

"Done."

Provide a concise implementation report.

==================================================
FINAL INSTRUCTION
==================================================

BUILD THE ACTUAL FUNCTIONAL CAPTION STUDIO.

DO NOT ONLY CREATE A MOCKUP.

DO NOT ONLY CREATE HTML/CSS.

DO NOT CREATE STATIC BUTTONS.

DO NOT CREATE PLACEHOLDER SETTINGS.

EVERY IMPORTANT CONTROL MUST CONNECT TO REAL APPLICATION STATE.

THE FINAL UI MUST FOLLOW THE ATTACHED NOTEBOOK DESIGN AS CLOSELY AS PRACTICALLY POSSIBLE WHILE USING THE EXISTING UP CLIP STUDIO THEME, COMPONENTS, NAVIGATION AND ARCHITECTURE.

The existing Up Clip Studio project is authoritative for:
- theme
- navigation
- icons
- existing functionality
- architecture
- preferences

The handwritten notebook is authoritative for:
- Caption Studio layout
- panel organization
- workflow
- visual hierarchy

Final priority:

FUNCTIONALITY
>
EXISTING PROJECT CONSISTENCY
>
NOTEBOOK LAYOUT FIDELITY
>
PERFORMANCE
>
VISUAL POLISH

Do not change the requested functionality just to make implementation easier.
If an existing implementation already solves something correctly, reuse it instead of rebuilding it.
