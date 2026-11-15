# core/font_manager.py
"""
Typography and Font Asset Manager for UpClip Studio.
Manages Open Font Licensed (OFL) creator fonts, Devanagari Unicode support,
font discovery, downloading, and validation for viral subtitle rendering.
"""

import shutil
import urllib.request
from pathlib import Path
from typing import Dict, Any, List

import config
from core.logger import logger

FONT_CATALOG = {
    "montserrat": {
        "id": "montserrat",
        "name": "Montserrat Bold",
        "filename": "Montserrat-Bold.ttf",
        "format": "TTF",
        "category": "Creator Bold",
        "license": "SIL Open Font License (OFL)",
        "recommended_for": "Punchy word-by-word karaoke & viral headlines",
        "url": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
        "estimated_bytes": 745000
    },
    "notosansdevanagari": {
        "id": "notosansdevanagari",
        "name": "Noto Sans Devanagari Bold",
        "filename": "NotoSansDevanagari-Bold.ttf",
        "format": "TTF",
        "category": "Indic & Hinglish",
        "license": "SIL Open Font License (OFL)",
        "recommended_for": "Hindi, Hinglish, Marathi and Devanagari script shorts",
        "url": "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf",
        "estimated_bytes": 642000
    },
    "poppins": {
        "id": "poppins",
        "name": "Poppins Bold",
        "filename": "Poppins-Bold.ttf",
        "format": "TTF",
        "category": "Modern Geometric",
        "license": "SIL Open Font License (OFL)",
        "recommended_for": "Clean educational, finance and lifestyle reels",
        "url": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf",
        "estimated_bytes": 156000
    },
    "inter": {
        "id": "inter",
        "name": "Inter Bold",
        "filename": "Inter-Bold.ttf",
        "format": "TTF",
        "category": "High Legibility",
        "license": "SIL Open Font License (OFL)",
        "recommended_for": "Ultra-readable subtitle tracks on mobile screens",
        "url": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
        "estimated_bytes": 876000
    },
    "bebasneue": {
        "id": "bebasneue",
        "name": "Bebas Neue Regular",
        "filename": "BebasNeue-Regular.ttf",
        "format": "TTF",
        "category": "All-Caps Display",
        "license": "SIL Open Font License (OFL)",
        "recommended_for": "Uppercase cinematic titles and podcast captions",
        "url": "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf",
        "estimated_bytes": 61400
    },
    "arialblack": {
        "id": "arialblack",
        "name": "Arial Black",
        "filename": "Arial-Black.ttf",
        "format": "TTF",
        "category": "Heavy Impact",
        "license": "System / Core TTF",
        "recommended_for": "Hormozi, MrBeast heavy outline captions",
        "url": None,
        "system_fallback": "C:/Windows/Fonts/ariblk.ttf",
        "estimated_bytes": 117000
    }
}


class FontManager:
    """Manages local creator font assets, validation, and installation."""

    def __init__(self, font_dir: Path = None):
        self.font_dir = font_dir or config.FONT_DIR
        self.font_dir.mkdir(parents=True, exist_ok=True)

    def get_font_catalog(self) -> List[Dict[str, Any]]:
        """List all catalog fonts with real local disk status and metadata."""
        catalog = []
        for fid, meta in FONT_CATALOG.items():
            dest = self.font_dir / meta["filename"]
            is_installed = dest.exists() and dest.stat().st_size > 1024
            size_str = f"{round(dest.stat().st_size / 1024, 1)} KB" if is_installed else f"{round(meta['estimated_bytes'] / 1024, 1)} KB"
            catalog.append({
                "id": fid,
                "name": meta["name"],
                "filename": meta["filename"],
                "format": meta["format"],
                "category": meta["category"],
                "license": meta["license"],
                "recommended_for": meta["recommended_for"],
                "is_installed": is_installed,
                "status": "Installed" if is_installed else "Available for Download",
                "size_formatted": size_str,
                "path": str(dest) if is_installed else None
            })
        return catalog

    def install_font(self, font_id: str) -> Dict[str, Any]:
        """Download or copy a specific font and validate integrity."""
        if font_id not in FONT_CATALOG:
            return {"success": False, "error": f"Unknown font: {font_id}"}

        meta = FONT_CATALOG[font_id]
        dest = self.font_dir / meta["filename"]

        # 1. System file copy fallback (e.g. Arial Black)
        if meta.get("system_fallback"):
            sys_p = Path(meta["system_fallback"])
            if sys_p.exists():
                try:
                    shutil.copy(sys_p, dest)
                    if self._validate_font_file(dest):
                        return {"success": True, "font_id": font_id, "name": meta["name"], "message": f"{meta['name']} installed from system fonts"}
                except Exception as e:
                    logger.warning(f"Error copying system font {font_id}: {e}")

        # 2. Remote download from Google Fonts OFL
        url = meta.get("url")
        if not url:
            return {"success": False, "error": f"No download URL available for {meta['name']}"}

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "UpClipStudio/2.0 (Font Downloader)"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                if len(data) < 1000:
                    return {"success": False, "error": f"Invalid download stream for {meta['name']}"}
                dest.write_bytes(data)

            if not self._validate_font_file(dest):
                dest.unlink(missing_ok=True)
                return {"success": False, "error": f"Corrupt or invalid TTF font header for {meta['name']}"}

            logger.app(f"Font installed and validated: {meta['name']} ({len(data)} bytes)")
            return {
                "success": True,
                "font_id": font_id,
                "name": meta["name"],
                "message": f"{meta['name']} downloaded and verified successfully."
            }
        except Exception as e:
            dest.unlink(missing_ok=True)
            logger.app(f"Failed to install font {meta['name']}: {e}", level="error")
            return {"success": False, "error": f"Download failed: {str(e)}"}

    def install_all_fonts(self) -> Dict[str, Any]:
        """Install all available creator fonts."""
        results = []
        for fid in FONT_CATALOG:
            res = self.install_font(fid)
            results.append(res)
        success_count = sum(1 for r in results if r.get("success"))
        return {
            "success": True,
            "installed_count": success_count,
            "total_count": len(FONT_CATALOG),
            "results": results
        }

    def _validate_font_file(self, path: Path) -> bool:
        """Validate that a font file has genuine TrueType/OpenType magic headers."""
        if not path.exists() or path.stat().st_size < 1024:
            return False
        try:
            with open(path, "rb") as f:
                header = f.read(4)
                # TrueType 1.0 (0x00010000), OpenType ('OTTO'), TrueType Collections ('ttcf'), or 'true'
                return header in (b"\x00\x01\x00\x00", b"OTTO", b"ttcf", b"true")
        except Exception:
            return False

    def get_diagnostics(self) -> Dict[str, Any]:
        """Inspect directory and report font health for Diagnostics."""
        ttf_files = list(self.font_dir.glob("*.ttf")) + list(self.font_dir.glob("*.otf"))
        valid_fonts = [f for f in ttf_files if self._validate_font_file(f)]
        has_devanagari = any("devanagari" in f.name.lower() or "noto" in f.name.lower() for f in valid_fonts)
        font_names = [f.stem.replace("-", " ") for f in valid_fonts]

        return {
            "count": len(valid_fonts),
            "is_operational": len(valid_fonts) > 0,
            "has_devanagari": has_devanagari,
            "fonts": font_names,
            "directory": str(self.font_dir)
        }


font_manager = FontManager()
