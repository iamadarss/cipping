"""Project SQLAlchemy database model for UpClip Studio."""

from datetime import datetime
from app import db


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

    def to_dict(self):
        """Serialize model instance to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "source_path": self.source_path,
            "thumbnail_path": self.thumbnail_path,
            "status": self.status,
            "duration": self.duration,
            "editor_state": self.editor_state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Project id={self.id} name='{self.name}' status='{self.status}'>"
