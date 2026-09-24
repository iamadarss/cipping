"""YouTube Automation routes - OAuth, channel management, upload, metadata, queue."""

import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
import json
import config
import time
import sqlite3
import base64
import threading
import secrets
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, session, current_app, url_for, redirect
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from flask import current_app as _app

# ---------------------------------------------------------------
# Configuration & Environment
# ---------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "youtube.db"

# Load environment variables (.env as single source of truth)
load_dotenv(BASE_DIR / ".env")

# Single source of truth for YouTube OAuth scopes (minimum required scopes)
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
]

# YouTube API constants
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

logger = logging.getLogger(__name__)


def get_oauth_config() -> Dict[str, str]:
    """Retrieve and validate YouTube OAuth configuration from environment variables."""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://127.0.0.1:5000/youtube/callback"
    )

    if not client_id or not client_secret:
        raise ValueError("YouTube OAuth configuration is incomplete.")

    return {
        "client_id": client_id.strip(),
        "client_secret": client_secret.strip(),
        "redirect_uri": redirect_uri.strip(),
    }


def validate_oauth_config() -> bool:
    """Check if YouTube OAuth configuration exists."""
    try:
        get_oauth_config()
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------
# Flask Blueprint
# ---------------------------------------------------------------

youtube_bp = Blueprint("youtube", __name__, url_prefix="/youtube")

# ---------------------------------------------------------------
# Database helper
# ---------------------------------------------------------------


def get_db():
    """Get a database connection, initializing and migrating schema if needed."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # Create tables if not exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'default',
            channel_id TEXT,
            channel_name TEXT,
            channel_handle TEXT,
            channel_avatar TEXT,
            channel_subscribers TEXT,
            channel_video_count TEXT,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            expires_at INTEGER,
            created_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
            updated_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER))
        )
    """)

    # Ensure added columns exist if table was previously created with older schema
    for col in ["channel_handle", "channel_subscribers", "channel_video_count"]:
        try:
            conn.execute(f"ALTER TABLE tokens ADD COLUMN {col} TEXT")
        except Exception:
            pass

    conn.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            youtube_video_id TEXT,
            title TEXT,
            description TEXT,
            tags TEXT,
            category_id TEXT,
            visibility TEXT,
            status TEXT DEFAULT "queued",
            progress INTEGER DEFAULT 0,
            scheduled_at INTEGER,
            published_at INTEGER,
            file_size INTEGER,
            duration REAL,
            resolution TEXT,
            fps INTEGER,
            aspect_ratio TEXT,
            created_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
            updated_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            youtube_video_id TEXT,
            title TEXT,
            description TEXT,
            scheduled_at INTEGER NOT NULL,
            timezone TEXT DEFAULT "UTC",
            status DEFAULT "scheduled",
            created_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            youtube_video_id TEXT,
            title TEXT,
            description TEXT,
            visibility TEXT,
            published_at INTEGER,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title_pattern TEXT,
            description TEXT,
            tags TEXT,
            category_id TEXT,
            language TEXT,
            visibility TEXT,
            playlist_id TEXT,
            schedule_rule TEXT,
            created_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
            updated_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title_pattern TEXT,
            description TEXT,
            tags TEXT,
            category_id TEXT,
            language TEXT,
            visibility TEXT,
            playlist_id TEXT,
            schedule_rule TEXT,
            created_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
            updated_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS automation_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            when_condition TEXT,
            if_condition TEXT,
            then_action TEXT,
            created_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS upload_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            youtube_video_id TEXT,
            title TEXT,
            description TEXT,
            tags TEXT,
            category_id TEXT,
            visibility TEXT,
            scheduled_at INTEGER,
            status DEFAULT "queued",
            progress INTEGER DEFAULT 0,
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 3,
            created_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
            updated_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER)),
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS watch_folder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_path TEXT,
            connected INTEGER DEFAULT 0,
            last_checked INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS naming_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            pattern TEXT,
            description TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at INTEGER DEFAULT (CAST(strftime('%s', 'now') AS INTEGER))
        )
    """)

    # Ensure youtube_video_id column exists in upload_queue
    try:
        conn.execute("ALTER TABLE upload_queue ADD COLUMN youtube_video_id TEXT")
    except Exception:
        pass

    conn.commit()
    return conn


def init_db():
    """Initialize the database and clear interrupted uploads from prior sessions."""
    conn = get_db()
    try:
        # Mark any uploads interrupted by a previous server run as failed with clear reason
        conn.execute("""
            UPDATE upload_queue
            SET status = 'failed', error_message = 'Upload interrupted by server restart. Click Retry to re-upload.'
            WHERE status IN ('uploading', 'retrying')
        """)
        conn.execute("UPDATE videos SET status = 'failed' WHERE status IN ('uploading', 'retrying')")

        # Ensure default presets are available
        preset_count = conn.execute("SELECT COUNT(*) FROM templates").fetchone()[0]
        if preset_count == 0:
            default_presets = [
                (
                    "🎙️ Podcast Clips",
                    "{title} | Clip",
                    "Best moment from the podcast! Subscribe for daily insights and deep dives.\n\n#podcast #clips #interview",
                    json.dumps(["podcast", "interview", "highlights", "clips", "talkshow", "viral"]),
                    "22",
                    "en",
                    "public",
                    ""
                ),
                (
                    "🔥 Viral Shorts",
                    "{title} #shorts",
                    "Wait till the end! ⚡ Drop a like if you enjoyed this.\n\n#shorts #viral #trending #fyp",
                    json.dumps(["shorts", "viral", "trending", "fyp", "clip", "reels", "youtube"]),
                    "24",
                    "en",
                    "public",
                    ""
                ),
                (
                    "💻 Tech & Explainer",
                    "{title} Explained",
                    "A quick breakdown and tutorial. Check out the complete playlist for more guides.\n\n#tech #tutorial #explainer",
                    json.dumps(["tech", "explainer", "tutorial", "guide", "howto", "coding"]),
                    "28",
                    "en",
                    "public",
                    ""
                ),
            ]
            for p in default_presets:
                conn.execute(
                    """INSERT INTO templates (name, title_pattern, description, tags, category_id, language, visibility, playlist_id, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, CAST(strftime('%s', 'now') AS INTEGER), CAST(strftime('%s', 'now') AS INTEGER))""",
                    p,
                )
        conn.commit()
    except Exception as e:
        logger.warning("init_db cleanup exception: %s", e)
    finally:
        conn.close()


# ---------------------------------------------------------------
# OAuth helpers
# ---------------------------------------------------------------


def get_flow() -> Flow:
    """Create an OAuth flow instance from environment variables without requiring a JSON file."""
    cfg = get_oauth_config()

    client_config = {
        "web": {
            "client_id": cfg["client_id"],
            "client_secret": cfg["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [cfg["redirect_uri"]],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=YOUTUBE_SCOPES,
    )
    flow.redirect_uri = cfg["redirect_uri"]
    return flow


def credentials_to_dict(credentials: Credentials) -> Dict[str, Any]:
    """Convert Credentials object to a dictionary for safe handling."""
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }


def dict_to_credentials(d: Dict[str, Any]) -> Credentials:
    """Convert stored database credentials to Google Credentials using environment config."""
    cfg = get_oauth_config()
    return Credentials(
        token=d["access_token"],
        refresh_token=d.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
        scopes=YOUTUBE_SCOPES,
    )


# ---------------------------------------------------------------
# Token management (single channel, default user)
# ---------------------------------------------------------------


def get_credentials() -> Optional[Credentials]:
    """Get stored credentials from the database."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM tokens WHERE user_id = 'default' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if row and row["access_token"]:
        try:
            return dict_to_credentials(dict(row))
        except Exception as e:
            logger.error("Failed to construct credentials from database: %s", type(e).__name__)
            return None
    return None


def save_credentials(credentials: Credentials, channel_info: Optional[Dict[str, Any]] = None):
    """Save or update credentials and channel metadata in the database."""
    conn = get_db()
    access_expires = (
        int(credentials.expiry.timestamp())
        if getattr(credentials, "expiry", None)
        else int(time.time()) + 3600
    )

    row = conn.execute(
        "SELECT * FROM tokens WHERE user_id = 'default' ORDER BY id DESC LIMIT 1"
    ).fetchone()

    # Preserve existing refresh token if not returned on refresh
    refresh_token = credentials.refresh_token or (row["refresh_token"] if row else None)

    row_keys = row.keys() if row else []
    channel_id = (channel_info.get("id") if channel_info else None) or (row["channel_id"] if row else None)
    channel_name = (channel_info.get("title") if channel_info else None) or (row["channel_name"] if row else None)
    channel_handle = (channel_info.get("handle") if channel_info else None) or (row["channel_handle"] if row and "channel_handle" in row_keys else None)
    channel_avatar = (channel_info.get("avatar") if channel_info else None) or (row["channel_avatar"] if row else None)
    channel_subscribers = (channel_info.get("subscribers") if channel_info else None) or (row["channel_subscribers"] if row and "channel_subscribers" in row_keys else None)
    channel_video_count = (channel_info.get("video_count") if channel_info else None) or (row["channel_video_count"] if row and "channel_video_count" in row_keys else None)

    if row:
        conn.execute(
            """
            UPDATE tokens SET
                channel_id = ?,
                channel_name = ?,
                channel_handle = ?,
                channel_avatar = ?,
                channel_subscribers = ?,
                channel_video_count = ?,
                access_token = ?,
                refresh_token = ?,
                expires_at = ?,
                updated_at = CAST(strftime('%s', 'now') AS INTEGER)
            WHERE id = ?
            """,
            (
                channel_id,
                channel_name,
                channel_handle,
                channel_avatar,
                channel_subscribers,
                channel_video_count,
                credentials.token,
                refresh_token,
                access_expires,
                row["id"],
            ),
        )
    else:
        conn.execute(
            """
            INSERT INTO tokens (
                user_id, channel_id, channel_name, channel_handle, channel_avatar,
                channel_subscribers, channel_video_count, access_token, refresh_token,
                expires_at, created_at, updated_at
            ) VALUES ('default', ?, ?, ?, ?, ?, ?, ?, ?, ?, CAST(strftime('%s', 'now') AS INTEGER), CAST(strftime('%s', 'now') AS INTEGER))
            """,
            (
                channel_id,
                channel_name,
                channel_handle,
                channel_avatar,
                channel_subscribers,
                channel_video_count,
                credentials.token,
                refresh_token,
                access_expires,
            ),
        )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------
# YouTube API helper (centralized credential service)
# ---------------------------------------------------------------


def get_youtube_service():
    """Build and return an authenticated YouTube API service object."""
    credentials = get_credentials()
    if not credentials:
        raise RuntimeError("No YouTube credentials found. Connect your channel first.")

    # Automatically refresh if expired
    if credentials.expired and credentials.refresh_token:
        from google.auth.transport.requests import Request
        try:
            credentials.refresh(Request())
            save_credentials(credentials)
        except Exception as e:
            logger.warning("YouTube OAuth token refresh failed: %s", type(e).__name__)
            raise RuntimeError("Your YouTube connection needs to be reauthorized. Please reconnect.")

    return build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        credentials=credentials,
        static_discovery=False,
    )


# ---------------------------------------------------------------
# OAuth API Routes
# ---------------------------------------------------------------


@youtube_bp.route("/connect", methods=["GET"])
def connect():
    """Initiate OAuth 2.0 flow."""
    is_json_req = (
        request.is_json
        or request.headers.get("Accept") == "application/json"
        or request.args.get("format") == "json"
    )
    try:
        if not validate_oauth_config():
            error_msg = "YouTube OAuth configuration is incomplete."
            if is_json_req:
                return jsonify({"success": False, "error": error_msg}), 500
            return redirect("/youtube-desk?error=config_incomplete")

        flow = get_flow()

        state = secrets.token_urlsafe(32)
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            prompt="consent",
            state=state,
            code_challenge_method="S256",
        )

        session["oauth_state"] = state
        session["oauth_code_verifier"] = flow.code_verifier

        if is_json_req:
            return jsonify({
                "success": True,
                "authorization_url": authorization_url,
            })

        return redirect(authorization_url)

    except Exception as e:
        logger.error("OAuth connect initiation failed: %s", type(e).__name__)
        error_msg = "YouTube OAuth configuration is incomplete." if "OAuth" in str(e) else "Unable to connect YouTube."
        if is_json_req:
            return jsonify({"success": False, "error": error_msg}), 500
        return redirect("/youtube-desk?error=connect_failed")


@youtube_bp.route("/callback", methods=["GET"])
def callback():
    """Handle OAuth 2.0 callback from Google."""
    is_json_req = (
        request.is_json
        or request.headers.get("Accept") == "application/json"
        or request.args.get("format") == "json"
    )
    try:
        # Check for OAuth error query params from Google
        error = request.args.get("error")
        if error:
            session.pop("oauth_state", None)
            session.pop("oauth_code_verifier", None)
            err_map = {
                "access_denied": "Authorization was cancelled or denied.",
                "redirect_uri_mismatch": "Redirect URI mismatch in Google Cloud configuration.",
                "invalid_client": "Invalid Google OAuth client configuration.",
                "invalid_grant": "Authorization code expired or invalid.",
            }
            user_msg = err_map.get(error, f"YouTube authorization failed ({error}).")
            if is_json_req:
                return jsonify({"success": False, "error": user_msg}), 400
            return redirect(f"/youtube-desk?error={error}")

        state = session.get("oauth_state")
        code_verifier = session.get("oauth_code_verifier")
        returned_state = request.args.get("state")

        if not state or not returned_state or state != returned_state:
            session.pop("oauth_state", None)
            session.pop("oauth_code_verifier", None)
            error_msg = "OAuth state validation failed. CSRF detected or session expired. Please reconnect YouTube."
            if is_json_req:
                return jsonify({"success": False, "error": error_msg}), 400
            return redirect("/youtube-desk?error=state_mismatch")

        code = request.args.get("code")
        if not code:
            session.pop("oauth_state", None)
            session.pop("oauth_code_verifier", None)
            error_msg = "Authorization code missing from Google callback."
            if is_json_req:
                return jsonify({"success": False, "error": error_msg}), 400
            return redirect("/youtube-desk?error=missing_code")

        flow = get_flow()

        flow.fetch_token(
            authorization_response=request.url,
            code_verifier=code_verifier,
        )

        session.pop("oauth_state", None)
        session.pop("oauth_code_verifier", None)

        credentials = flow.credentials
        save_credentials(credentials)

        # Retrieve authenticated YouTube channel info via channels.list(mine=True)
        channel_info = {}
        try:
            youtube = get_youtube_service()
            channels_response = youtube.channels().list(
                part="snippet,contentDetails,statistics",
                mine=True,
            ).execute()

            if channels_response.get("items"):
                channel = channels_response["items"][0]
                snippet = channel.get("snippet", {})
                statistics = channel.get("statistics", {})
                thumbnails = snippet.get("thumbnails", {})

                avatar = ""
                for size in ["high", "medium", "default"]:
                    if size in thumbnails and "url" in thumbnails[size]:
                        avatar = thumbnails[size]["url"]
                        break

                channel_info = {
                    "id": channel.get("id", ""),
                    "title": snippet.get("title", ""),
                    "handle": snippet.get("customUrl", ""),
                    "avatar": avatar,
                    "subscribers": str(statistics.get("subscriberCount", "0")),
                    "video_count": str(statistics.get("videoCount", "0")),
                }
                save_credentials(credentials, channel_info=channel_info)
        except Exception as api_err:
            logger.warning("Channel info fetch error: %s", type(api_err).__name__)

        if is_json_req:
            return jsonify({
                "success": True,
                "connected": True,
                "channel": channel_info,
            })

        return redirect("/youtube-desk?connected=1")

    except Exception as e:
        session.pop("oauth_state", None)
        session.pop("oauth_code_verifier", None)
        logger.error("OAuth callback processing failed: %s", type(e).__name__)
        safe_error = "YouTube authorization failed. Please try connecting again."
        if is_json_req:
            return jsonify({"success": False, "error": safe_error}), 500
        return redirect("/youtube-desk?error=oauth_failed")


def fetch_and_update_channel_info(credentials: Optional[Credentials] = None) -> Optional[Dict[str, Any]]:
    """Fetch live channel information from YouTube API and update database tokens."""
    try:
        if not credentials:
            credentials = get_credentials()
        if not credentials:
            return None
        youtube = get_youtube_service()
        channels_response = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True,
        ).execute()

        if channels_response.get("items"):
            channel = channels_response["items"][0]
            snippet = channel.get("snippet", {})
            statistics = channel.get("statistics", {})
            thumbnails = snippet.get("thumbnails", {})

            avatar = ""
            for size in ["high", "medium", "default"]:
                if size in thumbnails and "url" in thumbnails[size]:
                    avatar = thumbnails[size]["url"]
                    break

            channel_info = {
                "id": channel.get("id", ""),
                "title": snippet.get("title", ""),
                "handle": snippet.get("customUrl", ""),
                "avatar": avatar,
                "subscribers": str(statistics.get("subscriberCount", "0")),
                "video_count": str(statistics.get("videoCount", "0")),
                "view_count": str(statistics.get("viewCount", "0")),
            }
            save_credentials(credentials, channel_info=channel_info)
            logger.info("Updated YouTube channel stats for '%s': %s subs, %s videos", channel_info["title"], channel_info["subscribers"], channel_info["video_count"])
            return channel_info
    except Exception as api_err:
        logger.warning("Channel info fetch error: %s", type(api_err).__name__)
        return None


@youtube_bp.route("/status", methods=["GET"])
def status():
    """Check YouTube connection status with live refresh support."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM tokens WHERE user_id = 'default' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()

    if not row or not row["access_token"]:
        return jsonify({
            "connected": False,
            "channel": None
        })

    row_dict = dict(row)
    force_refresh = request.args.get("refresh") in ("1", "true", "True")

    # Auto-refresh live stats if requested or if current metrics are placeholder '0' / None
    if force_refresh or row_dict.get("channel_subscribers") in (None, "0", ""):
        live_info = fetch_and_update_channel_info()
        if live_info:
            return jsonify({
                "connected": True,
                "channel": {
                    "id": live_info.get("id") or "",
                    "title": live_info.get("title") or "Connected YouTube Channel",
                    "handle": live_info.get("handle") or "",
                    "avatar": live_info.get("avatar") or "",
                    "thumbnail": live_info.get("avatar") or "",
                    "subscribers": live_info.get("subscribers") or "0",
                    "video_count": live_info.get("video_count") or "0",
                    "view_count": live_info.get("view_count") or "0",
                }
            })

    avatar = row_dict.get("channel_avatar") or ""
    handle = row_dict.get("channel_handle") or ""
    title = row_dict.get("channel_name") or "Connected YouTube Channel"
    subscribers = str(row_dict.get("channel_subscribers") or "0")
    video_count = str(row_dict.get("channel_video_count") or "0")

    return jsonify({
        "connected": True,
        "channel": {
            "id": row_dict.get("channel_id") or "",
            "title": title,
            "handle": handle,
            "avatar": avatar,
            "thumbnail": avatar,
            "subscribers": subscribers,
            "video_count": video_count,
        }
    })


@youtube_bp.route("/refresh-channel", methods=["POST", "GET"])
def refresh_channel():
    """Explicitly refresh YouTube channel statistics and channel info from YouTube API."""
    live_info = fetch_and_update_channel_info()
    if not live_info:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM tokens WHERE user_id = 'default' ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if row and row["access_token"]:
            r = dict(row)
            live_info = {
                "id": r.get("channel_id") or "",
                "title": r.get("channel_name") or "Connected YouTube Channel",
                "handle": r.get("channel_handle") or "",
                "avatar": r.get("channel_avatar") or "",
                "thumbnail": r.get("channel_avatar") or "",
                "subscribers": str(r.get("channel_subscribers") or "0"),
                "video_count": str(r.get("channel_video_count") or "0"),
            }
        else:
            return jsonify({"success": False, "connected": False, "error": "Not connected to YouTube"}), 400

    return jsonify({
        "success": True,
        "connected": True,
        "channel": live_info
    })


@youtube_bp.route("/disconnect", methods=["POST"])
def disconnect():
    """Disconnect YouTube channel."""
    try:
        conn = get_db()
        conn.execute("DELETE FROM tokens WHERE user_id = 'default'")
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error("Disconnect error: %s", type(e).__name__)

    return jsonify({
        "success": True,
        "connected": False,
        "message": "YouTube disconnected."
    })


# ---------------------------------------------------------------
# Video metadata and import
# ---------------------------------------------------------------


@youtube_bp.route("/metadata", methods=["GET"])
def get_metadata():
    """Get video metadata from the database by id or filename."""
    video_id = request.args.get("id")
    filename = request.args.get("filename")
    conn = get_db()

    if video_id:
        row = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
    elif filename:
        row = conn.execute(
            "SELECT * FROM videos WHERE filename = ? ORDER BY created_at DESC LIMIT 1",
            (Path(filename).name,),
        ).fetchone()
    else:
        conn.close()
        return jsonify({"success": False, "error": "Video ID or filename required"}), 400

    conn.close()

    if not row:
        return jsonify({"success": False, "error": "Video not found"}), 404

    result = dict(row)
    # If tags is a JSON string, parse it
    if result.get("tags"):
        try:
            result["tags"] = json.loads(result["tags"])
        except (json.JSONDecodeError, TypeError):
            result["tags"] = []
    else:
        result["tags"] = []

    # Resolve the actual on-disk path
    video_path = config.INPUT_DIR / result["filename"]
    if video_path.exists():
        result["path"] = str(video_path)
        result["video_url"] = f"/download/input/{result['filename']}"
        # Generate thumbnail if missing
        thumb_name = f"{Path(result['filename']).stem}_thumb.jpg"
        thumb_path = config.THUMBNAIL_DIR / thumb_name
        if not thumb_path.exists():
            try:
                from utils.video_utils import VideoLoader
                loader = VideoLoader(video_path)
                loader.thumbnail(thumb_path)
                loader.close()
            except Exception:
                pass
        if thumb_path.exists():
            result["thumbnail"] = f"/download/thumbnail/{thumb_name}"
    else:
        result["path"] = None

    return jsonify({"success": True, "metadata": result})


@youtube_bp.route("/import", methods=["POST"])
def import_video():
    """Import a video file that already exists locally (e.g. from a download, clip, or upload).

    Accepts either a multipart/form-data file upload or a JSON body with a filename
    referencing an existing file in the input directory. Creates a DB record and returns
    its numeric id so subsequent upload/schedule operations can reference it.
    Does NOT copy the file if it already lives in the input directory — it reuses the
    existing path to avoid unnecessary duplicates.
    """
    config.INPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

    # --- Case 1: multipart file upload (drag & drop or file picker) ---
    if "video" in request.files:
        file = request.files["video"]
        if not file or file.filename == "":
            return jsonify({
                "success": False,
                "error": "Please drop a video file or choose one from your device."
            }), 400

        filename = Path(file.filename).name

        # Validate video extension
        ext = Path(filename).suffix.lower()
        if ext not in {".mp4", ".mov", ".webm", ".mkv", ".avi"}:
            return jsonify({
                "success": False,
                "error": "This video format isn't supported. Please choose MP4, MOV, WebM, MKV, or AVI."
            }), 400

        save_path = config.INPUT_DIR / filename

        # Avoid duplicate: if a file with the same name already exists, reuse it
        # instead of overwriting (preserves the original source file).
        if not save_path.exists():
            file.save(str(save_path))

        # Extract metadata & thumbnail
        metadata = _extract_video_metadata(save_path)
        thumb_url = _ensure_thumbnail(save_path, metadata)

        video_id = _insert_video_record(filename, metadata)
        return jsonify({
            "success": True,
            "video_id": video_id,
            "filename": filename,
            "metadata": metadata,
            "thumbnail": thumb_url,
            "video_url": f"/download/input/{filename}",
        })

    # --- Case 2: JSON body referencing an existing local file ---
    data = request.get_json(silent=True) or {}
    filename = data.get("filename", "").strip()

    if not filename:
        return jsonify({
            "success": False,
            "error": "No video file provided. Please drop a video file or choose one from your device."
        }), 400

    filename = Path(filename).name
    video_path = config.INPUT_DIR / filename

    if not video_path.exists():
        # Also check clips and final output dirs
        for check_dir in [config.CLIPS_DIR, config.FINAL_DIR]:
            candidate = check_dir / filename
            if candidate.exists():
                video_path = candidate
                break

    if not video_path.exists():
        return jsonify({
            "success": False,
            "error": "The selected video file could not be found on disk."
        }), 404

    metadata = _extract_video_metadata(video_path)
    thumb_url = _ensure_thumbnail(video_path, metadata)

    video_id = _insert_video_record(filename, metadata)
    return jsonify({
        "success": True,
        "video_id": video_id,
        "filename": filename,
        "metadata": metadata,
        "thumbnail": thumb_url,
        "video_url": f"/download/input/{filename}",
        "path": str(video_path),
    })


def _extract_video_metadata(video_path):
    """Extract metadata from a video file. Returns a dict, never raises."""
    metadata = {}
    try:
        from utils.video_utils import VideoLoader
        loader = VideoLoader(video_path)
        metadata = loader.metadata()
        loader.close()
    except Exception:
        metadata = {
            "filename": video_path.name,
            "width": None,
            "height": None,
            "fps": None,
            "duration": None,
            "size_bytes": video_path.stat().st_size if video_path.exists() else 0,
        }
    return metadata


def _ensure_thumbnail(video_path, metadata):
    """Return a thumbnail URL, regenerating the thumbnail if it doesn't exist yet."""
    stem = Path(video_path.name).stem
    thumb_name = f"{stem}_thumb.jpg"
    thumb_path = config.THUMBNAIL_DIR / thumb_name
    if not thumb_path.exists():
        try:
            from utils.video_utils import VideoLoader
            loader = VideoLoader(video_path)
            loader.thumbnail(thumb_path)
            loader.close()
        except Exception:
            pass
    if thumb_path.exists():
        return f"/download/thumbnail/{thumb_name}"
    # Fallback: use the metadata thumbnail if the upload returned one
    if metadata and metadata.get("thumbnail"):
        return metadata["thumbnail"]
    return None


def _insert_video_record(filename, metadata):
    """Insert (or update) a videos table row. Reuse existing record if filename matches."""
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM videos WHERE filename = ? ORDER BY created_at DESC LIMIT 1",
        (filename,),
    ).fetchone()

    if existing:
        video_id = existing["id"]
    else:
        row = conn.execute(
            """
            INSERT INTO videos (filename, title, description, tags, category_id,
                               visibility, duration, resolution, fps, aspect_ratio, file_size)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                filename,
                metadata.get("filename", filename),
                "",
                json.dumps([]),
                None,
                "public",
                metadata.get("duration"),
                metadata.get("resolution"),
                metadata.get("fps"),
                metadata.get("aspect_ratio"),
                metadata.get("size_bytes"),
            ),
        )
        video_id = row.lastrowid

    conn.commit()
    conn.close()
    return video_id


@youtube_bp.route("/videos", methods=["POST"])
def create_video():
    """Create a new video entry in the queue (from JSON metadata only)."""
    data = request.get_json() or {}
    filename = data.get("filename", "")

    conn = get_db()
    # Check if a record already exists for this filename (avoid duplicates)
    existing = conn.execute(
        "SELECT id FROM videos WHERE filename = ? ORDER BY created_at DESC LIMIT 1",
        (filename,),
    ).fetchone()

    if existing:
        video_id = existing["id"]
        conn.close()
        return jsonify({"success": True, "video_id": video_id, "metadata": {}})

    # Check if file exists locally
    video_path = BASE_DIR / "input" / filename
    metadata = {}

    if video_path.exists():
        metadata = _extract_video_metadata(video_path)

    video_id = _insert_video_record(filename, metadata)
    conn.close()

    return jsonify({"success": True, "video_id": video_id, "metadata": metadata})


@youtube_bp.route("/videos", methods=["GET"])
def list_videos():
    """List all videos in the queue."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM videos ORDER BY created_at DESC").fetchall()
    conn.close()
    videos = []
    for row in rows:
        d = dict(row)
        if d.get("tags"):
            try:
                d["tags"] = json.loads(d["tags"])
            except (json.JSONDecodeError, TypeError):
                d["tags"] = []
        else:
            d["tags"] = []
        # Resolve on-disk path and generate thumbnail if needed
        filename = d.get("filename", "")
        video_path = config.INPUT_DIR / filename
        if not video_path.exists():
            video_path = config.CLIPS_DIR / filename
        if not video_path.exists():
            video_path = config.FINAL_DIR / filename
        if video_path.exists():
            d["path"] = str(video_path)
            d["video_url"] = f"/download/input/{filename}"
            thumb_name = f"{Path(filename).stem}_thumb.jpg"
            thumb_path = config.THUMBNAIL_DIR / thumb_name
            if thumb_path.exists():
                d["thumbnail"] = f"/download/thumbnail/{thumb_name}"
            else:
                # Try to generate thumbnail
                try:
                    from utils.video_utils import VideoLoader
                    loader = VideoLoader(video_path)
                    loader.thumbnail(thumb_path)
                    loader.close()
                    if thumb_path.exists():
                        d["thumbnail"] = f"/download/thumbnail/{thumb_name}"
                except Exception:
                    pass
        videos.append(d)
    return jsonify({"success": True, "videos": videos})


@youtube_bp.route("/scan", methods=["GET"])
def scan_videos():
    """Scan all video source directories and return a unified list of available videos."""
    video_exts = {".mp4", ".webm", ".mkv", ".avi", ".mov"}
    sources = {
        "local_upload": config.INPUT_DIR,
        "yt_downloader": config.INPUT_DIR,
        "clip_cutter": config.CLIPS_DIR,
        "caption_studio": config.FINAL_DIR,
        "processed": config.FINAL_DIR,
    }
    seen = set()
    items = []
    for source, directory in sources.items():
        if not directory.exists():
            continue
        for p in sorted(directory.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if p.is_file() and p.suffix.lower() in video_exts:
                if p.name in seen:
                    continue
                seen.add(p.name)
                stat = p.stat()
                ext = p.suffix.lower().lstrip(".")
                # Determine the download/stream URL based on which directory the file is in
                if directory == config.INPUT_DIR:
                    video_url = f"/download/input/{p.name}"
                    stream_url = f"/download/input/stream/{p.name}"
                elif directory == config.CLIPS_DIR:
                    video_url = f"/download/clip/{p.name}"
                    stream_url = f"/download/clip/stream/{p.name}"
                else:
                    video_url = f"/download/final/{p.name}"
                    stream_url = f"/download/final/{p.name}"
                thumb_name = f"{p.stem}_thumb.jpg"
                thumb_path = config.THUMBNAIL_DIR / thumb_name
                thumbnail = f"/download/thumbnail/{thumb_name}" if thumb_path.exists() else None
                items.append({
                    "filename": p.name,
                    "source": source,
                    "video_url": video_url,
                    "stream_url": stream_url,
                    "size": stat.st_size,
                    "size_formatted": _format_file_size(stat.st_size),
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "extension": ext,
                    "thumbnail": thumbnail,
                })
    return jsonify({"success": True, "videos": items})


def _format_file_size(size_bytes):
    """Format file size in human-readable form."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


@youtube_bp.route("/videos/<int:video_id>", methods=["PUT"])
def update_video(video_id: int):
    """Update video metadata."""
    data = request.get_json() or {}
    conn = get_db()

    update_fields = []
    params = []

    for field in ["title", "description", "tags", "category_id", "visibility"]:
        if field in data:
            val = data[field]
            if field == "tags" and isinstance(val, (list, dict)):
                val = json.dumps(val)
            update_fields.append(f"{field} = ?")
            params.append(val)

    if not update_fields:
        conn.close()
        return jsonify({"success": False, "error": "No fields to update"}), 400

    update_fields.append("updated_at = CAST(strftime('%s', 'now') AS INTEGER)")
    params.append(video_id)

    conn.execute(
        f"UPDATE videos SET {', '.join(update_fields)} WHERE id = ?",
        params,
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ---------------------------------------------------------------
# Upload endpoints
# ---------------------------------------------------------------


@youtube_bp.route("/upload/start", methods=["POST"])
def upload_start():
    """Start a resumable upload to YouTube."""
    data = request.get_json() or {}
    video_id = data.get("video_id")

    conn = get_db()
    video_row = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()

    if not video_row:
        conn.close()
        return jsonify({"success": False, "error": "Video not found"}), 404

    try:
        youtube = get_youtube_service()

        # Get video file path — check input, clips, and final directories
        filename = video_row["filename"]
        video_path = config.INPUT_DIR / filename
        if not video_path.exists():
            video_path = config.CLIPS_DIR / filename
        if not video_path.exists():
            video_path = config.FINAL_DIR / filename
        if not video_path.exists():
            conn.close()
            return jsonify({"success": False, "error": "Video file not found"}), 404

        # Get metadata
        title = video_row["title"] or video_row["filename"]
        description = video_row["description"] or ""
        tags = json.loads(video_row["tags"]) if video_row["tags"] else []
        category_id = video_row["category_id"] or "22"  # People & Blogs default
        visibility = video_row["visibility"] or "public"

        # Build body
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags[:5] if tags else [],  # YouTube allows max 5 tags in snippet
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": visibility,
            },
        }

        # Resumable upload
        media = MediaFileUpload(
            str(video_path),
            resumable=True,
            chunksize=1024 * 1024 * 5,  # 5MB chunks
        )

        insert_request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        # Return upload URL info
        return jsonify({
            "success": True,
            "upload_url": insert_request.resumable_url,
            "video_id": video_id,
            "title": title,
            "visibility": visibility,
            "filename": filename,
            "video_path": str(video_path),
        })

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500


_active_upload_threads = set()


def start_upload_worker(queue_id: int, video_id: int):
    """Execute upload in a background thread with real-time progress and error handling."""
    _active_upload_threads.add(queue_id)

    def _do_upload():
        try:
            conn = get_db()
            q_row = conn.execute("SELECT * FROM upload_queue WHERE id = ?", (queue_id,)).fetchone()
            v_row = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
            conn.close()

            if not v_row:
                c = get_db()
                c.execute("UPDATE upload_queue SET status = 'failed', error_message = 'Video record not found' WHERE id = ?", (queue_id,))
                c.commit()
                c.close()
                return

            q_dict = dict(q_row) if q_row else {}
            v_dict = dict(v_row) if v_row else {}

            filename = v_dict.get("filename", "")
            title = q_dict.get("title") or v_dict.get("title") or filename
            description = q_dict.get("description") or v_dict.get("description") or ""
            tags_raw = q_dict.get("tags") or v_dict.get("tags") or "[]"
            category_id = str(q_dict.get("category_id") or v_dict.get("category_id") or "22")
            visibility = q_dict.get("visibility") or v_dict.get("visibility") or "public"
            playlist_id = q_dict.get("playlist_id") or v_dict.get("playlist_id") or None

            # Resolve video file path
            p = Path(filename)
            video_path = None
            if p.is_absolute() and p.exists():
                video_path = p
            elif (config.INPUT_DIR / filename).exists():
                video_path = config.INPUT_DIR / filename
            elif (config.CLIPS_DIR / filename).exists():
                video_path = config.CLIPS_DIR / filename
            elif (config.FINAL_DIR / filename).exists():
                video_path = config.FINAL_DIR / filename
            elif (config.DOWNLOAD_DIR / filename).exists():
                video_path = config.DOWNLOAD_DIR / filename

            if not video_path or not video_path.exists():
                c = get_db()
                c.execute("UPDATE upload_queue SET status = 'failed', error_message = 'Video file not found on disk' WHERE id = ?", (queue_id,))
                c.execute("UPDATE videos SET status = 'failed' WHERE id = ?", (video_id,))
                c.commit()
                c.close()
                return

            # Parse tags safely
            parsed_tags = []
            if tags_raw:
                if isinstance(tags_raw, str):
                    try:
                        parsed_tags = json.loads(tags_raw)
                    except Exception:
                        parsed_tags = [t.strip().lstrip('#') for t in tags_raw.split(',') if t.strip()]
                elif isinstance(tags_raw, list):
                    parsed_tags = [str(t).lstrip('#') for t in tags_raw]

            # Mark upload starting
            c = get_db()
            c.execute("UPDATE upload_queue SET status = 'uploading', progress = 10, updated_at = CAST(strftime('%s', 'now') AS INTEGER) WHERE id = ?", (queue_id,))
            c.commit()
            c.close()

            youtube = get_youtube_service()

            file_size = video_path.stat().st_size
            media = MediaFileUpload(
                str(video_path),
                resumable=True,
                chunksize=1024 * 1024 * 2,  # 2MB chunks for smoother progress
            )

            body = {
                "snippet": {
                    "title": title[:100],  # YouTube title max 100 chars
                    "description": description[:5000],  # YouTube desc max 5000 chars
                    "tags": parsed_tags[:20],
                    "categoryId": category_id,
                },
                "status": {
                    "privacyStatus": visibility,
                },
            }

            insert_request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                status, response = insert_request.next_chunk()
                if status:
                    uploaded = int(status.resumable_progress or 0)
                    pct = round(min(98, (uploaded / file_size) * 100)) if file_size else 10
                    c = get_db()
                    c.execute(
                        "UPDATE upload_queue SET progress = ?, updated_at = CAST(strftime('%s', 'now') AS INTEGER) WHERE id = ?",
                        (pct, queue_id),
                    )
                    c.execute("UPDATE videos SET progress = ? WHERE id = ?", (pct, video_id))
                    c.commit()
                    c.close()

            youtube_video_id = response.get("id")

            # Check and upload custom thumbnail if exists
            thumb_name = f"{Path(filename).stem}_thumb.jpg"
            thumb_path = config.THUMBNAIL_DIR / thumb_name
            if thumb_path.exists() and youtube_video_id:
                try:
                    youtube.thumbnails().set(
                        videoId=youtube_video_id,
                        media_body=MediaFileUpload(str(thumb_path), resumable=True),
                    ).execute()
                except Exception as th_err:
                    logger.warning("Thumbnail upload skipped/failed: %s", th_err)

            # Add to playlist if specified
            if playlist_id and youtube_video_id:
                try:
                    youtube.playlistItems().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": playlist_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": youtube_video_id,
                                },
                            }
                        },
                    ).execute()
                except Exception as pl_err:
                    logger.warning("Playlist insertion skipped: %s", pl_err)

            # Finalize completion in DB
            c = get_db()
            c.execute(
                """UPDATE videos SET youtube_video_id = ?, status = 'uploaded', progress = 100,
                   published_at = CAST(strftime('%s', 'now') AS INTEGER),
                   updated_at = CAST(strftime('%s', 'now') AS INTEGER) WHERE id = ?""",
                (youtube_video_id, video_id),
            )
            c.execute(
                """UPDATE upload_queue SET status = 'completed', progress = 100,
                   youtube_video_id = ?, updated_at = CAST(strftime('%s', 'now') AS INTEGER)
                   WHERE id = ?""",
                (youtube_video_id, queue_id),
            )
            # Update matching schedules
            c.execute(
                "UPDATE schedules SET status = 'published', youtube_video_id = ? WHERE video_id = ?",
                (youtube_video_id, video_id),
            )
            # Record in History
            c.execute(
                """INSERT INTO history (video_id, youtube_video_id, title, description, visibility, published_at, created_at)
                   VALUES (?, ?, ?, ?, ?, CAST(strftime('%s', 'now') AS INTEGER), CAST(strftime('%s', 'now') AS INTEGER))""",
                (video_id, youtube_video_id, title, description, visibility),
            )
            c.commit()
            c.close()

            logger.info("Successfully uploaded YouTube video: %s (ID: %s)", title, youtube_video_id)
            # Sync fresh channel stats
            fetch_and_update_channel_info()

        except Exception as e:
            err_str = str(e)
            logger.error("YouTube upload failed for queue #%s: %s", queue_id, err_str)
            if "quotaExceeded" in err_str or "uploadLimitExceeded" in err_str:
                user_msg = "YouTube daily upload limit reached for today. Please try again tomorrow."
            elif "invalid_grant" in err_str or "expired" in err_str:
                user_msg = "YouTube authorization expired. Please reconnect in YouTube Connection tab."
            elif "unsupportedMediaFormat" in err_str:
                user_msg = "Unsupported media format for YouTube."
            else:
                user_msg = f"Upload failed: {err_str[:200]}"

            c = get_db()
            c.execute(
                """UPDATE upload_queue SET status = 'failed', error_message = ?,
                   updated_at = CAST(strftime('%s', 'now') AS INTEGER) WHERE id = ?""",
                (user_msg, queue_id),
            )
            c.execute(
                """UPDATE videos SET status = 'failed',
                   updated_at = CAST(strftime('%s', 'now') AS INTEGER) WHERE id = ?""",
                (video_id,),
            )
            c.commit()
            c.close()
        finally:
            _active_upload_threads.discard(queue_id)

    thread = threading.Thread(target=_do_upload, daemon=True)
    thread.start()


@youtube_bp.route("/upload/execute", methods=["POST"])
def upload_execute():
    """Execute the actual YouTube upload to completion in a background thread."""
    data = request.get_json() or {}
    video_id = data.get("video_id")

    if not video_id:
        return jsonify({"success": False, "error": "video_id required"}), 400

    conn = get_db()
    video_row = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
    if not video_row:
        conn.close()
        return jsonify({"success": False, "error": "Video not found"}), 404

    title = video_row["title"] or video_row["filename"]
    description = video_row["description"] or ""
    tags = video_row["tags"] or json.dumps([])
    category_id = video_row["category_id"] or "22"
    visibility = video_row["visibility"] or "public"
    scheduled_at = data.get("scheduled_at")

    cursor = conn.execute(
        """
        INSERT INTO upload_queue (video_id, title, description, tags, category_id,
                                  visibility, scheduled_at, status, progress, retry_count, max_retries)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'uploading', 5, 0, 3)
        """,
        (video_id, title, description, tags, category_id, visibility, scheduled_at),
    )
    queue_id = cursor.lastrowid
    conn.commit()
    conn.close()

    start_upload_worker(queue_id, video_id)

    return jsonify({
        "success": True,
        "queue_id": queue_id,
        "video_id": video_id,
        "status": "uploading",
    })


@youtube_bp.route("/upload/chunk", methods=["POST"])
def upload_chunk():
    """Handle a chunk of resumable upload."""
    data = request.get_json() or {}
    video_id = data.get("video_id")
    position = data.get("position", 0)

    conn = get_db()
    video_row = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()

    if not video_row:
        conn.close()
        return jsonify({"success": False, "error": "Video not found"}), 404

    try:
        youtube = get_youtube_service()

        # Return status
        file_size = video_row["file_size"] or 1
        if file_size <= 0:
            file_size = 1
        return jsonify({
            "success": True,
            "status": "uploading",
            "progress": min(100, int((position / file_size) * 100)),
        })

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500


@youtube_bp.route("/upload/progress/<int:video_id>", methods=["GET"])
def upload_progress(video_id: int):
    """Get upload progress for a video — checks the upload_queue first, then the videos table."""
    conn = get_db()
    queue_row = conn.execute(
        "SELECT * FROM upload_queue WHERE video_id = ? ORDER BY id DESC LIMIT 1",
        (video_id,),
    ).fetchone()
    if queue_row:
        yt_id = queue_row["youtube_video_id"]
        status_val = queue_row["status"] or "queued"
        progress_val = 100 if status_val in ("completed", "uploaded") else (queue_row["progress"] or 0)
        result = {
            "success": True,
            "progress": progress_val,
            "status": status_val,
            "queue_id": queue_row["id"],
            "error_message": queue_row["error_message"],
            "retry_count": queue_row["retry_count"] or 0,
            "youtube_video_id": yt_id,
            "youtube_url": f"https://youtu.be/{yt_id}" if yt_id else None,
        }
        conn.close()
        return jsonify(result)

    row = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
    conn.close()

    if not row:
        return jsonify({"success": False, "error": "Video not found"}), 404

    yt_id = row["youtube_video_id"]
    status_val = row["status"] or "queued"
    progress_val = 100 if status_val in ("completed", "uploaded") else (row["progress"] or 0)
    return jsonify({
        "success": True,
        "progress": progress_val,
        "status": status_val,
        "youtube_video_id": yt_id,
        "youtube_url": f"https://youtu.be/{yt_id}" if yt_id else None,
    })


# ---------------------------------------------------------------
# Scheduler endpoints
# ---------------------------------------------------------------


@youtube_bp.route("/schedules", methods=["POST"])
def create_schedule():
    """Create a scheduled upload."""
    data = request.get_json() or {}
    video_id = data.get("video_id")
    scheduled_at = data.get("scheduled_at")  # Unix timestamp
    timezone = data.get("timezone", "UTC")

    if not video_id or not scheduled_at:
        return jsonify({"success": False, "error": "video_id and scheduled_at required"}), 400

    conn = get_db()
    # Check video exists
    video_row = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
    if not video_row:
        conn.close()
        return jsonify({"success": False, "error": "Video not found"}), 404

    # Convert to unix timestamp if needed
    if isinstance(scheduled_at, str):
        try:
            dt = datetime.fromisoformat(scheduled_at)
            scheduled_at = int(dt.timestamp())
        except ValueError:
            scheduled_at = int(scheduled_at)

    conn.execute(
        """
        INSERT INTO schedules (video_id, youtube_video_id, title, description,
                               scheduled_at, timezone, status)
        VALUES (?, ?, ?, ?, ?, ?, 'scheduled')
    """,
        (
            video_id,
            video_row["filename"],
            video_row["title"],
            video_row["description"],
            scheduled_at,
            timezone,
        ),
    )

    # Update video status
    conn.execute(
        "UPDATE videos SET status = 'scheduled', updated_at = CAST(strftime('%s', 'now') AS INTEGER) WHERE id = ?",
        (video_id,),
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "scheduled_at": scheduled_at})


@youtube_bp.route("/schedules", methods=["GET"])
def list_schedules():
    """List all schedules, automatically launching any releases that have become due."""
    conn = get_db()
    now_ts = int(time.time())

    # Check for any scheduled items that have reached their release timestamp
    due_rows = conn.execute(
        "SELECT * FROM schedules WHERE status = 'scheduled' AND scheduled_at <= ?",
        (now_ts,),
    ).fetchall()

    for sched in due_rows:
        try:
            s_id = sched["id"]
            v_id = sched["video_id"]
            v_row = conn.execute("SELECT * FROM videos WHERE id = ?", (v_id,)).fetchone()
            if v_row:
                conn.execute(
                    "UPDATE schedules SET status = 'publishing' WHERE id = ?",
                    (s_id,),
                )
                cur = conn.execute(
                    """INSERT INTO upload_queue (video_id, title, description, tags, category_id,
                                              visibility, scheduled_at, status, progress, retry_count, max_retries)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 'uploading', 5, 0, 3)""",
                    (
                        v_id,
                        v_row["title"] or v_row["filename"],
                        v_row["description"] or "",
                        v_row["tags"] or "[]",
                        v_row["category_id"] or "22",
                        v_row["visibility"] or "public",
                        sched["scheduled_at"],
                    ),
                )
                conn.commit()
                start_upload_worker(cur.lastrowid, v_id)
        except Exception as e:
            logger.warning("Auto-trigger schedule %s error: %s", sched["id"], e)

    rows = conn.execute(
        """SELECT s.*, v.title as video_title, v.filename as video_filename
           FROM schedules s JOIN videos v ON s.video_id = v.id ORDER BY s.scheduled_at ASC"""
    ).fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        d["due_now"] = bool((d.get("scheduled_at") or 0) <= now_ts)
        result.append(d)

    return jsonify({"success": True, "schedules": result})


@youtube_bp.route("/schedules/<int:schedule_id>/publish-now", methods=["POST"])
def publish_schedule_now(schedule_id: int):
    """Manually trigger immediate upload of a scheduled video."""
    conn = get_db()
    sched = conn.execute("SELECT * FROM schedules WHERE id = ?", (schedule_id,)).fetchone()
    if not sched:
        conn.close()
        return jsonify({"success": False, "error": "Schedule not found"}), 404

    v_id = sched["video_id"]
    v_row = conn.execute("SELECT * FROM videos WHERE id = ?", (v_id,)).fetchone()
    if not v_row:
        conn.close()
        return jsonify({"success": False, "error": "Associated video not found"}), 404

    conn.execute(
        "UPDATE schedules SET status = 'publishing', updated_at = CAST(strftime('%s', 'now') AS INTEGER) WHERE id = ?",
        (schedule_id,),
    )
    cur = conn.execute(
        """INSERT INTO upload_queue (video_id, title, description, tags, category_id,
                                  visibility, scheduled_at, status, progress, retry_count, max_retries)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'uploading', 5, 0, 3)""",
        (
            v_id,
            v_row["title"] or v_row["filename"],
            v_row["description"] or "",
            v_row["tags"] or "[]",
            v_row["category_id"] or "22",
            v_row["visibility"] or "public",
            sched["scheduled_at"],
        ),
    )
    queue_id = cur.lastrowid
    conn.commit()
    conn.close()

    start_upload_worker(queue_id, v_id)
    return jsonify({
        "success": True,
        "queue_id": queue_id,
        "video_id": v_id,
        "status": "uploading",
        "message": "Scheduled video publishing started immediately.",
    })


@youtube_bp.route("/schedules/<int:schedule_id>", methods=["PUT"])
def update_schedule(schedule_id: int):
    """Update a schedule."""
    data = request.get_json() or {}
    conn = get_db()

    update_fields = []
    params = []

    for field in ["title", "description", "timezone", "status"]:
        if field in data:
            update_fields.append(f"{field} = ?")
            params.append(data[field])

    if not update_fields:
        return jsonify({"success": False, "error": "No fields to update"}), 400

    update_fields.append("updated_at = CAST(strftime('%s', 'now') AS INTEGER)")
    params.append(schedule_id)

    conn.execute(
        f"UPDATE schedules SET {', '.join(update_fields)} WHERE id = ?",
        params,
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})


@youtube_bp.route("/schedules/<int:schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id: int):
    """Delete a schedule."""
    conn = get_db()
    conn.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ---------------------------------------------------------------
# Playlist endpoints
# ---------------------------------------------------------------


@youtube_bp.route("/playlists", methods=["GET"])
def list_playlists():
    """Fetch user's YouTube playlists."""
    try:
        youtube = get_youtube_service()
        response = youtube.playlists().list(
            part="snippet,contentDetails",
            mine=True,
        ).execute()

        playlists = response.get("items", [])
        result = []
        for p in playlists:
            result.append({
                "id": p["id"],
                "title": p["snippet"]["title"],
                "thumbnail": p["snippet"]["thumbnails"]["high"]["url"],
                "channel_id": p["snippet"]["channelId"],
            })

        conn = get_db()
        # Store in DB
        for pl in result:
            conn.execute(
                """INSERT OR REPLACE INTO playlists (title, thumbnail, channel_id)
                   VALUES (?, ?, ?)""",
                (pl["title"], pl["thumbnail"], pl["channel_id"]),
            )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "playlists": result})

    except Exception as e:
        try:
            conn = get_db()
            rows = conn.execute("SELECT id, title, thumbnail, channel_id FROM playlists").fetchall()
            conn.close()
            if rows:
                return jsonify({"success": True, "playlists": [dict(r) for r in rows]})
        except Exception:
            pass
        return jsonify({"success": True, "playlists": [], "warning": str(e)})


@youtube_bp.route("/playlists", methods=["POST"])
def create_playlist():
    """Create a new playlist."""
    data = request.get_json() or {}
    title = data.get("title", "New Playlist")

    try:
        youtube = get_youtube_service()

        body = {
            "snippet": {
                "title": title,
                "description": "",
            },
            "status": {
                "privacyStatus": "private",
            },
        }

        response = youtube.playlists().insert(
            part="snippet,status",
            body=body,
        ).execute()

        playlist_id = response["id"]
        thumbnail = response["snippet"]["thumbnails"]["high"]["url"]

        conn = get_db()
        conn.execute(
            """INSERT OR REPLACE INTO playlists (title, thumbnail, channel_id)
               VALUES (?, ?, ?)""",
            (title, thumbnail, None),
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "playlist_id": playlist_id})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@youtube_bp.route("/videos/<int:video_id>/add-to-playlist", methods=["POST"])
def add_to_playlist(video_id: int):
    """Add a video to a playlist."""
    data = request.get_json() or {}
    playlist_id = data.get("playlist_id")

    if not playlist_id:
        return jsonify({"success": False, "error": "playlist_id required"}), 400

    conn = get_db()
    video_row = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
    if not video_row:
        conn.close()
        return jsonify({"success": False, "error": "Video not found"}), 404

    try:
        youtube = get_youtube_service()

        body = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_row.get("youtube_video_id", ""),
                },
            },
        }

        youtube.playlists().insert(
            part="snippet",
            body=body,
        ).execute()

        conn.close()
        return jsonify({"success": True})

    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------------------
# Templates endpoints
# ---------------------------------------------------------------


@youtube_bp.route("/templates", methods=["GET"])
@youtube_bp.route("/presets", methods=["GET"])
def list_templates():
    """List metadata templates / presets with parsed tags."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM templates ORDER BY created_at DESC").fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        raw_tags = d.get("tags")
        if raw_tags:
            if isinstance(raw_tags, str):
                try:
                    d["tags"] = json.loads(raw_tags)
                except Exception:
                    d["tags"] = [t.strip().lstrip("#") for t in raw_tags.split(",") if t.strip()]
        else:
            d["tags"] = []
        result.append(d)

    return jsonify({"success": True, "templates": result, "presets": result})


@youtube_bp.route("/templates", methods=["POST"])
@youtube_bp.route("/presets", methods=["POST"])
def create_template():
    """Create a new metadata template / preset."""
    data = request.get_json() or {}
    name = (data.get("name") or "New Preset").strip()

    tags = data.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip().lstrip("#") for t in tags.split(",") if t.strip()]

    conn = get_db()
    cur = conn.execute(
        """INSERT INTO templates (name, title_pattern, description, tags, category_id,
                                  language, visibility, playlist_id, schedule_rule, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CAST(strftime('%s', 'now') AS INTEGER), CAST(strftime('%s', 'now') AS INTEGER))""",
        (
            name,
            data.get("title_pattern", ""),
            data.get("description", ""),
            json.dumps(tags),
            str(data.get("category_id") or "22"),
            data.get("language") or "en",
            data.get("visibility", "public"),
            data.get("playlist_id") or "",
            data.get("schedule_rule") or "",
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    return jsonify({"success": True, "id": new_id, "name": name})


@youtube_bp.route("/templates/<int:template_id>", methods=["PUT"])
@youtube_bp.route("/presets/<int:template_id>", methods=["PUT"])
def update_template(template_id: int):
    """Update a metadata template / preset."""
    data = request.get_json() or {}
    conn = get_db()

    update_fields = []
    params = []

    for field in ["name", "title_pattern", "description", "category_id",
                  "language", "visibility", "playlist_id", "schedule_rule"]:
        if field in data:
            update_fields.append(f"{field} = ?")
            params.append(data[field])

    if "tags" in data:
        tags = data["tags"]
        if isinstance(tags, str):
            tags = [t.strip().lstrip("#") for t in tags.split(",") if t.strip()]
        update_fields.append("tags = ?")
        params.append(json.dumps(tags))

    if not update_fields:
        conn.close()
        return jsonify({"success": False, "error": "No fields to update"}), 400

    update_fields.append("updated_at = CAST(strftime('%s', 'now') AS INTEGER)")
    params.append(template_id)

    conn.execute(
        f"UPDATE templates SET {', '.join(update_fields)} WHERE id = ?",
        params,
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})


@youtube_bp.route("/templates/<int:template_id>", methods=["DELETE"])
@youtube_bp.route("/presets/<int:template_id>", methods=["DELETE"])
def delete_template(template_id: int):
    """Delete a metadata template / preset."""
    conn = get_db()
    conn.execute("DELETE FROM templates WHERE id = ?", (template_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@youtube_bp.route("/templates/apply/<int:template_id>", methods=["POST"])
@youtube_bp.route("/presets/apply/<int:template_id>", methods=["POST"])
def apply_template(template_id: int):
    """Apply a preset to a video record."""
    data = request.get_json() or {}
    video_id = data.get("video_id")

    if not video_id:
        return jsonify({"success": False, "error": "video_id required"}), 400

    conn = get_db()
    template_row = conn.execute("SELECT * FROM templates WHERE id = ?", (template_id,)).fetchone()
    video_row = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()

    if not template_row or not video_row:
        conn.close()
        return jsonify({"success": False, "error": "Template or video not found"}), 404

    t_dict = dict(template_row)
    updates = {}

    if t_dict.get("title_pattern"):
        updates["title"] = t_dict["title_pattern"]

    if t_dict.get("description"):
        updates["description"] = t_dict["description"]

    if t_dict.get("tags"):
        updates["tags"] = t_dict["tags"]

    if t_dict.get("category_id"):
        updates["category_id"] = str(t_dict["category_id"])

    if t_dict.get("visibility"):
        updates["visibility"] = t_dict["visibility"]

    for field, value in updates.items():
        conn.execute(f"UPDATE videos SET {field} = ? WHERE id = ?", (value, video_id))

    conn.commit()
    conn.close()

    raw_tags = t_dict.get("tags")
    parsed_tags = []
    if raw_tags:
        try:
            parsed_tags = json.loads(raw_tags)
        except Exception:
            parsed_tags = [t.strip().lstrip("#") for t in raw_tags.split(",") if t.strip()]

    return jsonify({
        "success": True,
        "updated": updates,
        "preset": {
            "id": t_dict["id"],
            "name": t_dict["name"],
            "title_pattern": t_dict.get("title_pattern") or "",
            "description": t_dict.get("description") or "",
            "tags": parsed_tags,
            "category_id": t_dict.get("category_id") or "22",
            "playlist_id": t_dict.get("playlist_id") or "",
            "visibility": t_dict.get("visibility") or "public",
        }
    })


# ---------------------------------------------------------------
# Automation rules endpoints
# ---------------------------------------------------------------


@youtube_bp.route("/rules", methods=["GET"])
def list_rules():
    """List automation rules."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM automation_rules ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify({"success": True, "rules": [dict(r) for r in rows]})


@youtube_bp.route("/rules", methods=["POST"])
def create_rule():
    """Create an automation rule."""
    data = request.get_json() or {}
    name = data.get("name", "New Rule")
    when_condition = data.get("when")
    if_condition = data.get("if")
    then_action = data.get("then")

    conn = get_db()
    conn.execute(
        """INSERT INTO automation_rules (name, when_condition, if_condition, then_action)
           VALUES (?, ?, ?, ?)""",
        (name, when_condition, if_condition, then_action),
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})


@youtube_bp.route("/rules/<int:rule_id>", methods=["PUT"])
def update_rule(rule_id: int):
    """Update an automation rule."""
    data = request.get_json() or {}
    conn = get_db()

    update_fields = []
    params = []

    for field in ["name", "when_condition", "if_condition", "then_action"]:
        if field in data:
            update_fields.append(f"{field} = ?")
            params.append(data[field])

    if not update_fields:
        return jsonify({"success": False, "error": "No fields to update"}), 400

    update_fields.append("updated_at = CAST(strftime('%s', 'now') AS INTEGER)")
    params.append(rule_id)

    conn.execute(
        f"UPDATE automation_rules SET {', '.join(update_fields)} WHERE id = ?",
        params,
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})


@youtube_bp.route("/rules/<int:rule_id>", methods=["DELETE"])
def delete_rule(rule_id: int):
    """Delete an automation rule."""
    conn = get_db()
    conn.execute("DELETE FROM automation_rules WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ---------------------------------------------------------------
# Upload history endpoints
# ---------------------------------------------------------------


@youtube_bp.route("/history", methods=["GET"])
def list_history():
    """List upload history."""
    conn = get_db()
    rows = conn.execute(
        """SELECT h.*, v.title as video_title FROM history h
           JOIN videos v ON h.video_id = v.id ORDER BY h.published_at DESC"""
    ).fetchall()
    conn.close()
    return jsonify({"success": True, "history": [dict(r) for r in rows]})


@youtube_bp.route("/history/search", methods=["GET"])
def search_history():
    """Search history by title."""
    query = request.args.get("q", "")
    conn = get_db()

    if query:
        rows = conn.execute(
            """SELECT h.*, v.title as video_title FROM history h
               JOIN videos v ON h.video_id = v.id
               WHERE h.title LIKE ? OR v.title LIKE ?
               ORDER BY h.published_at DESC""",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT h.*, v.title as video_title FROM history h
               JOIN videos v ON h.video_id = v.id ORDER BY h.published_at DESC"""
        ).fetchall()

    conn.close()
    return jsonify({"success": True, "history": [dict(r) for r in rows]})


# ---------------------------------------------------------------
# Error center
# ---------------------------------------------------------------


@youtube_bp.route("/errors", methods=["GET"])
def list_errors():
    """List upload errors."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM upload_queue WHERE status = 'failed' ORDER BY created_at DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return jsonify({"success": True, "errors": [dict(r) for r in rows]})


@youtube_bp.route("/errors/<int:queue_id>/retry", methods=["POST"])
def retry_error(queue_id: int):
    """Retry a failed upload from Error Center."""
    return retry_queue_item(queue_id)


# ---------------------------------------------------------------
# Watch folder
# ---------------------------------------------------------------


@youtube_bp.route("/watch-folder", methods=["POST"])
def set_watch_folder():
    """Set a watch folder for automation."""
    data = request.get_json() or {}
    folder_path = data.get("folder_path")

    conn = get_db()
    conn.execute(
        """INSERT OR REPLACE INTO watch_folder (folder_path, connected, last_checked)
           VALUES (?, 1, CAST(strftime('%s', 'now') AS INTEGER))""",
        (folder_path,),
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})


@youtube_bp.route("/watch-folder", methods=["GET"])
def get_watch_folder():
    """Get watch folder status."""
    conn = get_db()
    row = conn.execute("SELECT * FROM watch_folder ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if row:
        return jsonify({"success": True, "folder": dict(row)})
    return jsonify({"success": True, "folder": None})


# ---------------------------------------------------------------
# File naming templates
# ---------------------------------------------------------------


@youtube_bp.route("/naming-templates", methods=["GET"])
def list_naming_templates():
    """List file naming templates."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM naming_templates ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify({"success": True, "templates": [dict(r) for r in rows]})


@youtube_bp.route("/naming-templates", methods=["POST"])
def create_naming_template():
    """Create a file naming template."""
    data = request.get_json() or {}
    name = data.get("name", "New Template")

    conn = get_db()
    conn.execute(
        """INSERT INTO naming_templates (name, pattern, description)
           VALUES (?, ?, ?)""",
        (name, data.get("pattern", ""), data.get("description", "")),
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ---------------------------------------------------------------
# Multi-channel support
# ---------------------------------------------------------------


@youtube_bp.route("/channels", methods=["GET"])
def list_channels():
    """List authorized channels (multi-channel support)."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM tokens WHERE channel_id IS NOT NULL ORDER BY updated_at DESC").fetchall()
    conn.close()
    channels = [dict(r) for r in rows]
    return jsonify({"success": True, "channels": channels})


@youtube_bp.route("/channel/selector", methods=["POST"])
def set_selected_channel():
    """Set the selected channel for uploads."""
    data = request.get_json() or {}
    channel_id = data.get("channel_id")

    conn = get_db()
    # Update the default token entry to mark which channel is selected
    conn.execute(
        "UPDATE tokens SET updated_at = CAST(strftime('%s', 'now') AS INTEGER) WHERE user_id = 'default'",
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "channel_id": channel_id})


# ---------------------------------------------------------------
# Upload Queue endpoint
# ---------------------------------------------------------------


@youtube_bp.route("/upload-queue", methods=["GET"])
def list_upload_queue():
    """List upload queue items, auto-detecting and cleaning up stalled or orphaned uploads."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM upload_queue ORDER BY created_at DESC LIMIT 50"
    ).fetchall()

    now_ts = int(time.time())
    updated_any = False
    for r in rows:
        st = r["status"]
        q_id = r["id"]
        v_id = r["video_id"]
        if st in ("uploading", "retrying") and q_id not in _active_upload_threads:
            upd = r["updated_at"] or r["created_at"] or 0
            if now_ts - upd > 15:
                conn.execute(
                    """UPDATE upload_queue SET status = 'failed',
                       error_message = 'Upload interrupted or thread halted. Click Retry to re-upload.',
                       updated_at = ? WHERE id = ?""",
                    (now_ts, q_id),
                )
                if v_id:
                    conn.execute(
                        "UPDATE videos SET status = 'failed', updated_at = ? WHERE id = ?",
                        (now_ts, v_id),
                    )
                updated_any = True

    if updated_any:
        conn.commit()
        rows = conn.execute(
            "SELECT * FROM upload_queue ORDER BY created_at DESC LIMIT 50"
        ).fetchall()

    conn.close()
    return jsonify({"success": True, "items": [dict(r) for r in rows]})


@youtube_bp.route("/upload-queue/<int:queue_id>/retry", methods=["POST"])
def retry_queue_item(queue_id: int):
    """Retry a failed upload queue item by re-launching the upload worker."""
    conn = get_db()
    row = conn.execute("SELECT * FROM upload_queue WHERE id = ?", (queue_id,)).fetchone()

    if not row:
        conn.close()
        return jsonify({"success": False, "error": "Queue item not found"}), 404

    video_id = row["video_id"]
    new_retry_count = (row["retry_count"] or 0) + 1

    # Reset status and clear previous error
    conn.execute(
        """UPDATE upload_queue SET retry_count = ?, status = 'uploading', progress = 5,
           error_message = NULL, updated_at = CAST(strftime('%s', 'now') AS INTEGER)
           WHERE id = ?""",
        (new_retry_count, queue_id),
    )
    if video_id:
        conn.execute(
            """UPDATE videos SET status = 'uploading', progress = 5,
               updated_at = CAST(strftime('%s', 'now') AS INTEGER)
               WHERE id = ?""",
            (video_id,),
        )
    conn.commit()
    conn.close()

    start_upload_worker(queue_id, video_id)
    return jsonify({
        "success": True,
        "retry_count": new_retry_count,
        "status": "uploading",
        "queue_id": queue_id,
        "video_id": video_id,
    })


@youtube_bp.route("/upload-queue/<int:queue_id>", methods=["DELETE"])
def delete_queue_item(queue_id: int):
    """Remove an item from the upload queue."""
    conn = get_db()
    row = conn.execute("SELECT * FROM upload_queue WHERE id = ?", (queue_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"success": False, "error": "Queue item not found"}), 404

    conn.execute("DELETE FROM upload_queue WHERE id = ?", (queue_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@youtube_bp.route("/upload-queue", methods=["POST"])
def add_to_upload_queue():
    """Add a video to the upload queue (creates queue entry from a videos table row)."""
    data = request.get_json() or {}
    video_id = data.get("video_id")

    if not video_id:
        return jsonify({"success": False, "error": "video_id required"}), 400

    conn = get_db()
    video_row = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
    if not video_row:
        conn.close()
        return jsonify({"success": False, "error": "Video not found"}), 404

    title = video_row["title"] or video_row["filename"]
    description = video_row["description"] or ""
    tags = video_row["tags"] or json.dumps([])
    category_id = video_row["category_id"] or "22"
    visibility = video_row["visibility"] or "public"
    scheduled_at = data.get("scheduled_at")

    conn.execute(
        """
        INSERT INTO upload_queue (video_id, title, description, tags, category_id,
                                  visibility, scheduled_at, status, retry_count, max_retries)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'queued', 0, 3)
        """,
        (video_id, title, description, tags, category_id, visibility, scheduled_at),
    )
    conn.commit()
    queue_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()

    return jsonify({"success": True, "queue_id": queue_id, "video_id": video_id})


# ---------------------------------------------------------------
# Thumbnail endpoints
# ---------------------------------------------------------------


@youtube_bp.route("/thumbnail/upload", methods=["POST"])
def upload_thumbnail():
    """Upload a thumbnail image for a video."""
    if "thumbnail" not in request.files:
        return jsonify({"success": False, "error": "No thumbnail file provided"}), 400
    file = request.files["thumbnail"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"}), 400

    from pathlib import Path
    thumb_dir = config.THUMBNAIL_DIR
    thumb_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(file.filename).name
    save_path = thumb_dir / filename
    file.save(str(save_path))

    return jsonify({
        "success": True,
        "url": f"/download/thumbnail/{filename}",
        "filename": filename,
    })


@youtube_bp.route("/thumbnail/capture", methods=["POST"])
def capture_thumbnail():
    """Capture a frame from a video as thumbnail."""
    data = request.get_json() or {}
    filename = data.get("filename", "")
    video_id = data.get("video_id")
    if not filename and video_id:
        try:
            conn = get_db()
            row = conn.execute("SELECT filename FROM videos WHERE id = ?", (video_id,)).fetchone()
            conn.close()
            if row:
                filename = row["filename"]
        except Exception:
            pass

    if not filename:
        return jsonify({"success": False, "error": "Filename required"}), 400

    video_path = config.INPUT_DIR / filename
    if not video_path.exists():
        return jsonify({"success": False, "error": "Video not found"}), 404

    try:
        from utils.video_utils import VideoLoader
        loader = VideoLoader(video_path)
        thumb_dir = config.THUMBNAIL_DIR
        thumb_dir.mkdir(parents=True, exist_ok=True)
        thumb_path = thumb_dir / f"{Path(filename).stem}_frame.jpg"
        loader.thumbnail(thumb_path)
        loader.close()
        thumb_url = f"/download/thumbnail/{thumb_path.name}"
        return jsonify({
            "success": True,
            "thumbnail_url": thumb_url,
            "url": thumb_url,
            "filename": thumb_path.name,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------------------
# Settings endpoints
# ---------------------------------------------------------------


@youtube_bp.route("/settings", methods=["GET"])
def get_settings():
    """Get YouTube automation settings."""
    conn = get_db()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    settings = {r["key"]: r["value"] for r in rows}
    return jsonify({"success": True, "settings": settings})


@youtube_bp.route("/settings", methods=["POST"])
def save_settings():
    """Save YouTube automation settings."""
    data = request.get_json() or {}
    conn = get_db()
    for key, value in data.items():
        conn.execute(
            """
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CAST(strftime('%s', 'now') AS INTEGER))
            """,
            (key, str(value)),
        )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ---------------------------------------------------------------
# Data management endpoints
# ---------------------------------------------------------------


@youtube_bp.route("/data/clear", methods=["POST"])
def clear_data():
    """Clear all local YouTube automation data."""
    conn = get_db()
    tables = [
        "tokens", "videos", "schedules", "history", "playlists",
        "templates", "automation_rules", "upload_queue", "watch_folder",
        "naming_templates", "settings",
    ]
    for table in tables:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@youtube_bp.route("/data/export", methods=["GET"])
def export_data():
    """Export all local YouTube automation data as JSON."""
    conn = get_db()
    data = {}
    tables = [
        "tokens", "videos", "schedules", "history", "playlists",
        "templates", "automation_rules", "upload_queue", "watch_folder",
        "naming_templates", "settings",
    ]
    for table in tables:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        data[table] = [dict(r) for r in rows]
    conn.close()
    return jsonify(data)


# ---------------------------------------------------------------
# Smart Scheduling & Learning Advisory Endpoints
# ---------------------------------------------------------------


@youtube_bp.route("/smart-schedule-advice", methods=["GET"])
def smart_schedule_advice():
    """
    Returns AI-powered scheduling recommendations based on YouTube Shorts algorithm patterns:
    - Peak audience engagement time windows
    - Safe spacing between consecutive Shorts (4-6 hours)
    - Calculated next optimal upload slot
    - Headline and hashtag recommendations
    """
    conn = get_db()
    
    # Find the latest scheduled or published video
    latest_sched = conn.execute(
        "SELECT scheduled_at FROM schedules WHERE status IN ('scheduled', 'pending') ORDER BY scheduled_at DESC LIMIT 1"
    ).fetchone()
    
    latest_history = conn.execute(
        "SELECT published_at FROM history ORDER BY published_at DESC LIMIT 1"
    ).fetchone()
    conn.close()

    now = datetime.now()
    
    # Peak slots daily (hours in local 24h format):
    # Morning: 09:00, Afternoon: 13:30, Evening prime: 18:30, Late prime: 21:00
    peak_hours = [9, 13, 18, 21]
    
    # Determine base reference time
    ref_time = now
    if latest_sched and latest_sched["scheduled_at"]:
        try:
            val = latest_sched["scheduled_at"]
            if isinstance(val, (int, float)) or (isinstance(val, str) and val.isdigit()):
                s_dt = datetime.fromtimestamp(int(val))
            else:
                s_dt = datetime.fromisoformat(str(val).replace("Z", ""))
            if s_dt > ref_time:
                ref_time = s_dt
        except Exception:
            pass

    # Spacing rule: Minimum 4.5 hours after ref_time
    min_next_time = ref_time + timedelta(hours=4.5)
    if min_next_time < now + timedelta(minutes=15):
        min_next_time = now + timedelta(minutes=15)

    # Snap to next available peak hour
    candidate = min_next_time.replace(minute=0, second=0, microsecond=0)
    found_slot = None
    for day_offset in range(7):
        target_date = (candidate + timedelta(days=day_offset)).date()
        for h in peak_hours:
            slot_candidate = datetime.combine(target_date, datetime.min.time()).replace(hour=h, minute=0)
            if slot_candidate >= min_next_time:
                found_slot = slot_candidate
                break
        if found_slot:
            break

    if not found_slot:
        found_slot = min_next_time

    return jsonify({
        "success": True,
        "advice": {
            "peak_slots": [
                {"label": "Morning Kickoff", "time": "09:00 AM", "audience": "Commute & Morning Feed"},
                {"label": "Lunch Break", "time": "01:30 PM", "audience": "Quick Mobile Browsing"},
                {"label": "Prime Evening (Top Performing)", "time": "06:30 PM", "audience": "Peak Engagement & Retention"},
                {"label": "Late Evening Chill", "time": "09:00 PM", "audience": "Leisure & Bedtime Scroll"}
            ],
            "spacing_rule": {
                "hours_min": 4,
                "hours_ideal": 5,
                "reason": "Prevents YouTube algorithm self-cannibalization; allows test cohort data to mature before launching the next Short."
            },
            "next_recommended_slot": {
                "iso": found_slot.isoformat(),
                "formatted": found_slot.strftime("%a, %b %d at %I:%M %p"),
                "timestamp": int(found_slot.timestamp())
            },
            "content_tactics": {
                "title_length": "Keep under 50 characters so it doesn't truncate on mobile feeds",
                "required_hashtags": ["#Shorts", "#Viral", "#Trending"],
                "hook_first_rule": "First 3 seconds must ask a burning question or show immediate high-energy action.",
                "caption_preset_recommended": "Hormozi Pop or MrBeast Glow for highest viewer retention."
            }
        }
    })


@youtube_bp.route("/auto-schedule", methods=["POST"])
def auto_schedule_clips():
    """
    Automatically spaces and schedules a list of clip filenames across optimal peak time slots.
    """
    data = request.get_json() or {}
    clip_names = data.get("clips") or []
    if not clip_names:
        if config.OUTPUT_DIR.exists():
            clip_names = [p.name for p in sorted(config.OUTPUT_DIR.glob("*.mp4")) if not p.name.startswith("temp_")][:10]
    if not clip_names:
        # Provide sample clip for testing/demonstration if output dir is empty
        clip_names = ["Auto_Scheduled_Short_01.mp4"]

    conn = get_db()
    # Find latest scheduled time to avoid collision
    latest_sched = conn.execute(
        "SELECT scheduled_at FROM schedules WHERE status IN ('scheduled', 'pending') ORDER BY scheduled_at DESC LIMIT 1"
    ).fetchone()

    now = datetime.now()
    ref_time = now
    if latest_sched and latest_sched["scheduled_at"]:
        try:
            val = latest_sched["scheduled_at"]
            if isinstance(val, (int, float)) or (isinstance(val, str) and val.isdigit()):
                s_dt = datetime.fromtimestamp(int(val))
            else:
                s_dt = datetime.fromisoformat(str(val).replace("Z", ""))
            if s_dt > ref_time:
                ref_time = s_dt
        except Exception:
            pass

    peak_hours = [9, 13, 18, 21]
    scheduled_plan = []
    current_time = max(now + timedelta(minutes=30), ref_time + timedelta(hours=4.5))

    for clip_name in clip_names:
        # Find next peak slot >= current_time
        slot = None
        for day_offset in range(14):
            candidate_date = (current_time + timedelta(days=day_offset)).date()
            for h in peak_hours:
                candidate_slot = datetime.combine(candidate_date, datetime.min.time()).replace(hour=h, minute=0)
                if candidate_slot >= current_time:
                    slot = candidate_slot
                    break
            if slot:
                break
        if not slot:
            slot = current_time

        # Format title cleanly from clip_name
        clean_title = Path(clip_name).stem.replace("_", " ").strip()
        if not clean_title.lower().endswith("#shorts"):
            clean_title = f"{clean_title} #Shorts"

        ts = int(slot.timestamp())
        # Insert video record if not existing
        v_row = conn.execute("SELECT id FROM videos WHERE filename = ?", (clip_name,)).fetchone()
        if v_row:
            v_id = v_row["id"]
            conn.execute(
                "UPDATE videos SET title = ?, visibility = 'public', scheduled_at = ? WHERE id = ?",
                (clean_title, ts, v_id)
            )
        else:
            cur = conn.execute(
                "INSERT INTO videos (filename, title, description, tags, category_id, visibility, scheduled_at, status, progress, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, 'scheduled', 0, ?, ?)",
                (clip_name, clean_title, f"{clean_title}\n\nCreated with UpClip Studio #Shorts #Viral", json.dumps(["Shorts", "Viral"]), "22", "public", ts, int(time.time()), int(time.time()))
            )
            v_id = cur.lastrowid

        # Insert schedule entry
        conn.execute(
            "INSERT INTO schedules (video_id, scheduled_at, status, created_at) VALUES (?, ?, 'scheduled', ?)",
            (v_id, ts, int(time.time()))
        )

        scheduled_plan.append({
            "clip_name": clip_name,
            "video_id": v_id,
            "title": clean_title,
            "scheduled_time": slot.strftime("%a, %b %d at %I:%M %p"),
            "timestamp": ts,
        })

        # Advance current_time by at least 5 hours for the next Short
        current_time = slot + timedelta(hours=5)

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "scheduled_count": len(scheduled_plan),
        "plan": scheduled_plan
    })