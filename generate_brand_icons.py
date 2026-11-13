"""Generate UpClip Studio brand icons and favicons.
Generates:
- favicon.svg
- favicon.ico (16, 32, 48)
- favicon-16x16.png
- favicon-32x32.png
- apple-touch-icon.png (180x180)
- android-chrome-192x192.png
- android-chrome-512x512.png
- site.webmanifest
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

SVG_CONTENT = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <linearGradient id="emerald-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#34D399" />
      <stop offset="50%" stop-color="#10B981" />
      <stop offset="100%" stop-color="#059669" />
    </linearGradient>
    <linearGradient id="cut-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6EE7B7" />
      <stop offset="100%" stop-color="#10B981" />
    </linearGradient>
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#111827" />
      <stop offset="100%" stop-color="#0B0F17" />
    </linearGradient>
    <filter id="subtle-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="14" flood-color="#10B981" flood-opacity="0.35" />
    </filter>
    <filter id="white-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="6" flood-color="#000000" flood-opacity="0.4" />
    </filter>
  </defs>

  <!-- Deep Charcoal Squircle Background -->
  <rect x="20" y="20" width="472" height="472" rx="108" fill="url(#bg-grad)" stroke="#1F2937" stroke-width="6" />

  <!-- Inner subtle border highlight -->
  <rect x="24" y="24" width="464" height="464" rx="104" fill="none" stroke="#10B981" stroke-width="2" stroke-opacity="0.25" />

  <g filter="url(#subtle-glow)">
    <!-- Stylized Geometric "U" Left Stem and Bottom Bowl -->
    <!-- Left arm going down, curving through bottom bowl and rising towards right cut -->
    <path d="M 120 116
             C 120 102 131 92 145 92
             L 187 92
             C 201 92 212 102 212 116
             L 212 280
             C 212 304 232 324 256 324
             C 280 324 300 304 300 280
             L 300 236
             L 392 236
             L 392 280
             C 392 355 331 416 256 416
             C 181 416 120 355 120 280
             Z"
          fill="url(#emerald-grad)" />

    <!-- Stylized "U" Right Stem with Angled Razor Cut (Editing Slice) -->
    <!-- Sliced cleanly at a dynamic 35-degree cutting angle -->
    <path d="M 300 92
             L 367 92
             C 381 92 392 103 392 117
             L 392 196
             L 300 144
             Z"
          fill="url(#cut-grad)" />

    <!-- Video Play Symbol (Forward Triangle) Integrated in Center Core -->
    <polygon points="216,168 316,226 216,284"
             fill="#FFFFFF"
             filter="url(#white-glow)" />

    <!-- Subtle Razor Cut Accent Line -->
    <line x1="288" y1="202" x2="404" y2="202" stroke="#0B0F17" stroke-width="10" stroke-linecap="round" />
  </g>
</svg>
'''

WEBMANIFEST_CONTENT = '''{
  "name": "UpClip Studio",
  "short_name": "UpClip",
  "description": "AI Video Clipper, Cinematic Subtitles and Shorts Automation Studio",
  "icons": [
    {
      "src": "/static/favicon-16x16.png",
      "sizes": "16x16",
      "type": "image/png"
    },
    {
      "src": "/static/favicon-32x32.png",
      "sizes": "32x32",
      "type": "image/png"
    },
    {
      "src": "/static/android-chrome-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/android-chrome-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "theme_color": "#10B981",
  "background_color": "#0B0F17",
  "display": "standalone"
}
'''

def render_icon_bitmap(size: int) -> Image.Image:
    """Render high-resolution icon bitmap with PIL supersampling."""
    # Scale factor for crisp supersampling
    scale = 4 if size <= 64 else (2 if size <= 256 else 1)
    render_size = size * scale

    img = Image.new("RGBA", (render_size, render_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = render_size / 512.0

    # Draw charcoal rounded background
    pad = 20 * s
    rect_w = 472 * s
    radius = int(108 * s)
    bg_color = (13, 17, 23, 255)       # #0D1117 charcoal
    border_color = (31, 41, 55, 255)   # #1F2937
    inner_rim = (16, 185, 129, 65)     # subtle emerald highlight

    # Outer rounded rect
    draw.rounded_rectangle(
        [(pad, pad), (pad + rect_w, pad + rect_w)],
        radius=radius,
        fill=bg_color,
        outline=border_color,
        width=max(1, int(6 * s))
    )

    if render_size >= 64:
        draw.rounded_rectangle(
            [(pad + 4 * s, pad + 4 * s), (pad + rect_w - 4 * s, pad + rect_w - 4 * s)],
            radius=max(4, radius - int(4 * s)),
            outline=inner_rim,
            width=max(1, int(2 * s))
        )

    # Coordinates scaled
    emerald_main = (16, 185, 129, 255)   # #10B981
    emerald_cut = (52, 211, 153, 255)    # #34D399
    white_play = (255, 255, 255, 255)
    charcoal_cut = (11, 15, 23, 255)

    # Main U body (outer curved bowl + inner curved bowl)
    # Left stem: (120..212, 100..280)
    # Right lower stem: (300..392, 236..280)
    # Bottom bowl: outer r=136 from (256,280), inner r=44 from (256,280)
    # For small sizes (16, 32), draw clean geometric shapes
    left_x1, left_x2 = int(120 * s), int(212 * s)
    right_x1, right_x2 = int(300 * s), int(392 * s)
    top_y = int(96 * s)
    bowl_top_y = int(280 * s)
    bottom_y = int(416 * s)

    # Draw U bowl: arc/pie between 120 and 392
    draw.pieslice([(int(120 * s), int(144 * s)), (int(392 * s), bottom_y)], start=0, end=180, fill=emerald_main)
    # Clear inner bowl
    draw.pieslice([(left_x2, int(236 * s)), (right_x1, int(324 * s))], start=0, end=180, fill=bg_color)

    # Left stem
    draw.rounded_rectangle([(left_x1, top_y), (left_x2, bowl_top_y)], radius=int(20 * s), fill=emerald_main)
    # Right lower stem
    draw.rectangle([(right_x1, int(236 * s)), (right_x2, bowl_top_y)], fill=emerald_main)

    # Upper right stem with editing cut notch
    cut_top = top_y
    cut_bottom = int(196 * s)
    draw.polygon([
        (right_x1, cut_top),
        (right_x2, cut_top + int(10 * s)),
        (right_x2, cut_bottom),
        (right_x1, cut_bottom - int(48 * s))
    ], fill=emerald_cut)

    # Cut gap line
    gap_y = int(210 * s)
    gap_h = max(2, int(16 * s))
    draw.rectangle([(right_x1 - int(4 * s), gap_y - gap_h // 2), (right_x2 + int(6 * s), gap_y + gap_h // 2)], fill=bg_color)

    # Play triangle in center
    play_p1 = (int(216 * s), int(166 * s))
    play_p2 = (int(318 * s), int(226 * s))
    play_p3 = (int(216 * s), int(286 * s))
    draw.polygon([play_p1, play_p2, play_p3], fill=white_play)

    # Resize down with Lanczos for smooth antialiasing
    if scale > 1:
        img = img.resize((size, size), Image.Resampling.LANCZOS)

    return img

def main():
    static_dir = Path(__file__).resolve().parent / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write SVG
    svg_path = static_dir / "favicon.svg"
    svg_path.write_text(SVG_CONTENT.strip(), encoding="utf-8")
    print(f"✅ Generated {svg_path.name}")

    # 2. Write WebManifest
    manifest_path = static_dir / "site.webmanifest"
    manifest_path.write_text(WEBMANIFEST_CONTENT.strip(), encoding="utf-8")
    print(f"✅ Generated {manifest_path.name}")

    # 3. Generate PNG sizes
    sizes = {
        "favicon-16x16.png": 16,
        "favicon-32x32.png": 32,
        "apple-touch-icon.png": 180,
        "android-chrome-192x192.png": 192,
        "android-chrome-512x512.png": 512,
    }

    images = {}
    for filename, sz in sizes.items():
        img = render_icon_bitmap(sz)
        out_path = static_dir / filename
        img.save(out_path, format="PNG", optimize=True)
        images[sz] = img
        print(f"✅ Generated {filename} ({sz}x{sz})")

    # 4. Generate multi-resolution favicon.ico (16, 32, 48)
    img_48 = render_icon_bitmap(48)
    ico_path = static_dir / "favicon.ico"
    images[16].save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=[images[32], img_48]
    )
    print(f"✅ Generated {ico_path.name} (16x16, 32x32, 48x48)")

if __name__ == "__main__":
    main()

