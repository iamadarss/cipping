"""Project SQLAlchemy database model for UpClip Studio."""

from datetime import datetime
from extensions import db


class Project(db.Model):
    """Represents an UpClip Studio video processing project."""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, default='Untitled Project')
    source_path = db.Column(db.String(512), nullable=True)
    thumbnail_path = db.Column(db.String(512), nullable=True)
    status = db.Column(db.String(50), default='ready')
    duration = db.Column(db.Float, default=0.0)
    editor_state = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(
        self,
        name: str = "Untitled Project",
        source_path: str | None = None,
        thumbnail_path: str | None = None,
        status: str = "ready",
        duration: float = 0.0,
        editor_state: str | None = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.name = name
        self.source_path = source_path
        self.thumbnail_path = thumbnail_path
        self.status = status
        self.duration = duration
        self.editor_state = editor_state
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        """Serialize model instance to dictionary format."""
        import config
        from pathlib import Path

        thumb = self.thumbnail_path
        if thumb and "/download/thumbnail/" in thumb:
            thumb_name = Path(thumb.split("/download/thumbnail/")[-1]).name
        elif thumb:
            thumb_name = Path(thumb).name
        elif self.source_path:
            thumb_name = f"{Path(self.source_path).stem}_thumb.jpg"
        else:
            thumb_name = None

        if thumb_name:
            if (config.THUMBNAIL_DIR / thumb_name).exists():
                thumb = f"/download/thumbnail/{thumb_name}"
            elif self.source_path and (config.INPUT_DIR / Path(self.source_path).name).exists():
                thumb = f"/download/thumbnail/{thumb_name}"
            elif thumb and thumb.startswith("/static/"):
                thumb = thumb
            else:
                thumb = "/static/img/default_thumb.png"
        elif thumb and (thumb.startswith("/static/") or thumb.startswith("http")):
            thumb = thumb
        else:
            thumb = "/static/img/default_thumb.png"

        return {
            "id": self.id,
            "name": self.name,
            "source_path": self.source_path,
            "thumbnail_path": thumb,
            "status": self.status,
            "duration": self.duration,
            "editor_state": self.editor_state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Project id={self.id} name='{self.name}' status='{self.status}'>"
