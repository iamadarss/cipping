"""UpClip Studio - Flask Web Application."""

import os
import sys
import subprocess
from pathlib import Path

# ---------------------------------------------------------------
# Environment guard: re-launch using the project .venv interpreter
# if the currently-running interpreter is missing required packages
# (e.g. cv2). This makes `python app.py` work from any shell.
# ---------------------------------------------------------------
def _ensure_environment():
    project_root = Path(__file__).resolve().parent
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    current_python = Path(sys.executable).resolve()

    # Already running with this project's .venv
    try:
        if current_python == venv_python.resolve():
            return
    except OSError:
        pass

    # Project .venv exists and running directly → relaunch with it
    if __name__ == "__main__" and venv_python.is_file():
        print(f"Using project interpreter: {venv_python}")
        try:
            ret = subprocess.call(
                [
                    str(venv_python),
                    str(Path(__file__).resolve()),
                    *sys.argv[1:],
                ]
            )
            sys.exit(ret)
        except KeyboardInterrupt:
            sys.exit(0)

    # .venv not found; continue with current interpreter
    if __name__ == "__main__" and not venv_python.is_file():
        print("[Warning] .venv not found; running with current Python interpreter.")


_ensure_environment()

import config

from flask import Flask, send_from_directory, request, jsonify, render_template
from extensions import db


# ===================================================
# Flask Web Application
# ===================================================

def create_app():

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        internal_dir = exe_dir / "_internal"
        template_dir = (
            internal_dir / "templates"
            if (internal_dir / "templates").exists()
            else (exe_dir / "templates")
        )
        static_dir = (
            internal_dir / "static"
            if (internal_dir / "static").exists()
            else (exe_dir / "static")
        )
    else:
        base_dir = Path(__file__).resolve().parent
        template_dir = base_dir / "templates"
        static_dir = base_dir / "static"

    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir)
    )

    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024  # 1 GB
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["SESSION_COOKIE_HTTPONLY"] = config.SESSION_COOKIE_HTTPONLY
    app.config["SESSION_COOKIE_SAMESITE"] = config.SESSION_COOKIE_SAMESITE
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    db_path = (config.DATA_DIR / "app.db").resolve().as_posix()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Path to media root for MediaManager and thumbnail endpoint
    app.config["MEDIA_ROOT"] = str(config.MEDIA_ROOT)

    db.init_app(app)
    with app.app_context():
        db.create_all()
    from routes.home import home_bp
    from routes.upload import upload_bp
    from routes.process import process_bp
    from routes.download import download_bp
    from routes.caption_studio import caption_studio_bp
    from routes.youtube import youtube_bp
    from routes.studio_navigation import studio_nav_bp
    from routes.projects import projects_bp
    from routes.editor import editor_bp
    from routes.media_thumbnail import media_thumbnail_bp
    from routes.workflows_api import workflows_bp
    from routes.settings import settings_bp
    app.register_blueprint(media_thumbnail_bp)
    app.register_blueprint(editor_bp)
    app.register_blueprint(workflows_bp)
    app.register_blueprint(settings_bp)

    app.register_blueprint(home_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(process_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(caption_studio_bp)
    app.register_blueprint(youtube_bp)
    app.register_blueprint(studio_nav_bp)
    app.register_blueprint(projects_bp)

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    @app.route("/favicon.svg")
    def favicon_svg():
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.svg",
            mimetype="image/svg+xml",
        )

    @app.errorhandler(404)
    def handle_not_found(e):
        if request.path.startswith(("/api/", "/editor/api/")) or request.is_json:
            return jsonify({
                "success": False,
                "error": "The requested API endpoint was not found",
                "code": 404
            }), 404
        return render_template("404.html", error=str(e)), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        import logging
        logging.getLogger("UpClip.App").error(f"Internal server error: {e}", exc_info=True)
        if request.path.startswith(("/api/", "/editor/api/")) or request.is_json:
            return jsonify({
                "success": False,
                "error": "An internal server error occurred",
                "code": 500
            }), 500
        return render_template("500.html", error=str(e)), 500

    return app


# ===================================================
# Entry Point
# ===================================================

if __name__ == "__main__":

    import os

    # Ensure Windows console renders emoji correctly
    os.environ["PYTHONIOENCODING"] = "utf-8"

    # Ensure bundled FFmpeg is on PATH for Whisper
    if config.FFMPEG_PATH and os.path.exists(config.FFMPEG_PATH):
        os.environ["PATH"] = (
            str(os.path.dirname(config.FFMPEG_PATH))
            + os.pathsep
            + os.environ["PATH"]
        )

    app = create_app()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=os.environ.get('FLASK_DEBUG', '0').lower() in ('1', 'true'),
        use_reloader=False
    )

