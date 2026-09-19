"""Centralized Flask extensions for UpClip Studio.

Ensures a single shared SQLAlchemy instance is created and used across
all models, blueprints, and the application factory.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
