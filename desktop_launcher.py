"""UpClip Studio - Desktop Launcher & Executable Entry Point."""

import os
import sys
import time
import socket
import threading
import webbrowser
import urllib.request
from pathlib import Path

# Ensure working directory is set to application root
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
    os.chdir(str(APP_DIR))
else:
    APP_DIR = Path(__file__).resolve().parent

import config
from app import create_app


def is_our_server(port: int) -> bool:
    """Check if the server running on port is actually UpClip Studio."""
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/",
            headers={"User-Agent": "UpClipStudioLauncher/1.0"}
        )
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            content = resp.read(2048).decode("utf-8", errors="ignore")
            return "UpClip" in content or "shorts" in content.lower()
    except Exception:
        return False


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        return s.connect_ex(("127.0.0.1", port)) == 0


def find_best_port(preferred_port: int = 5000) -> int:
    """Find a port that is free or already running our own UpClip Studio instance."""
    if is_port_in_use(preferred_port):
        if is_our_server(preferred_port):
            return preferred_port
        # Port is used by another application, search for next free port
        for p in range(5001, 5050):
            if not is_port_in_use(p):
                return p
    return preferred_port


def run_server(port: int = 5000):
    app = create_app()
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def open_folder(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        os.startfile(str(path))
    else:
        import subprocess
        subprocess.Popen(["xdg-open", str(path)])


def launch_gui(port: int = 5000):
    try:
        import customtkinter as ctk

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        window = ctk.CTk()
        window.title("UpClip Studio - Desktop")
        window.geometry("520x460")
        window.resizable(False, False)

        icon_path = getattr(config, "STATIC_DIR", config.ROOT_DIR / "static") / "favicon.ico"
        if not icon_path.exists() and getattr(sys, "frozen", False):
            internal_ico = Path(sys.executable).resolve().parent / "_internal" / "static" / "favicon.ico"
            if internal_ico.exists():
                icon_path = internal_ico

        if icon_path.exists():
            try:
                window.iconbitmap(str(icon_path))
            except Exception:
                pass

        header_frame = ctk.CTkFrame(window, corner_radius=12, fg_color="#18181b")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="✨ UpClip Studio",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#10b981",
        )
        title_lbl.pack(pady=(12, 2))

        sub_lbl = ctk.CTkLabel(
            header_frame,
            text="AI Shorts Generator & Automated YouTube Desk",
            font=ctk.CTkFont(size=12),
            text_color="#a1a1aa",
        )
        sub_lbl.pack(pady=(0, 12))

        status_frame = ctk.CTkFrame(window, corner_radius=8, fg_color="#064e3b")
        status_frame.pack(fill="x", padx=20, pady=8)

        status_lbl = ctk.CTkLabel(
            status_frame,
            text=f"🟢 Server Active: http://127.0.0.1:{port}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#34d399",
        )
        status_lbl.pack(pady=8)

        btn_frame = ctk.CTkFrame(window, corner_radius=12, fg_color="#18181b")
        btn_frame.pack(fill="both", expand=True, padx=20, pady=10)

        btn_open = ctk.CTkButton(
            btn_frame,
            text="🌐 Open Studio Web App",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42,
            fg_color="#059669",
            hover_color="#047857",
            command=lambda: webbrowser.open(f"http://127.0.0.1:{port}"),
        )
        btn_open.pack(fill="x", padx=20, pady=(16, 6))

        btn_yt = ctk.CTkButton(
            btn_frame,
            text="🎬 YouTube Desk Workspace",
            font=ctk.CTkFont(size=13),
            height=36,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=lambda: webbrowser.open(f"http://127.0.0.1:{port}/youtube-desk"),
        )
        btn_yt.pack(fill="x", padx=20, pady=6)

        folder_subframe = ctk.CTkFrame(btn_frame, fg_color="transparent")
        folder_subframe.pack(fill="x", padx=20, pady=6)

        btn_output = ctk.CTkButton(
            folder_subframe,
            text="📂 Output Clips",
            font=ctk.CTkFont(size=12),
            height=34,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=lambda: open_folder(config.OUTPUT_DIR),
        )
        btn_output.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_input = ctk.CTkButton(
            folder_subframe,
            text="📂 Input Videos",
            font=ctk.CTkFont(size=12),
            height=34,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=lambda: open_folder(config.INPUT_DIR),
        )
        btn_input.pack(side="right", fill="x", expand=True, padx=(6, 0))

        btn_quit = ctk.CTkButton(
            btn_frame,
            text="⏹️ Stop & Exit",
            font=ctk.CTkFont(size=12),
            height=32,
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            command=lambda: (window.destroy(), sys.exit(0)),
        )
        btn_quit.pack(fill="x", padx=20, pady=(12, 16))

        window.protocol("WM_DELETE_WINDOW", lambda: (window.destroy(), sys.exit(0)))
        window.mainloop()

    except Exception as e:
        print(f"GUI launch notice: {e}. Running in console mode.")
        print(f"UpClip Studio is running at: http://127.0.0.1:{port}")
        print("Press Ctrl+C to terminate.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)


def main():
    config.INPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    config.FINAL_DIR.mkdir(parents=True, exist_ok=True)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)

    port = find_best_port(5000)

    if not is_our_server(port):
        server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
        server_thread.start()

        for _ in range(30):
            if is_port_in_use(port):
                break
            time.sleep(0.3)

    webbrowser.open(f"http://127.0.0.1:{port}")
    launch_gui(port)


if __name__ == "__main__":
    main()
