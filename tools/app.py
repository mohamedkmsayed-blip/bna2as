"""
Sooq Deals — Modal Application Definition
==========================================
Main entry point for the Modal serverless backend.
Defines the app, container image, persistent volume, and web endpoint.
"""

import modal

# ---------------------------------------------------------------------------
# Modal App & Infrastructure
# ---------------------------------------------------------------------------

import modal
from pathlib import Path

# ---------------------------------------------------------------------------
# Modal App & Infrastructure
# ---------------------------------------------------------------------------

app = modal.App("sooq-deals")

# Container image with all Python dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi>=0.115.0",
    "uvicorn>=0.34.0",
    "httpx>=0.28.0",
    "beautifulsoup4>=4.12.0",
    "lxml>=5.0.0",
    "pydantic>=2.10.0",
).add_local_dir(
    local_path=Path(__file__).parent,
    remote_path="/root",
    ignore=["**/__pycache__", "**/.git", "**/.venv", "**/node_modules"],
)

# Persistent volume for SQLite database
volume = modal.Volume.from_name("sooq-deals-db", create_if_missing=True)

# Mount removed in favor of image.add_local_dir

# Constants
DB_PATH = "/data/sooq_deals.db"
VOLUME_MOUNT = "/data"
