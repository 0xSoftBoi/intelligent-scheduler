#!/usr/bin/env python
"""Initialize database script."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.database import Base, engine
from loguru import logger


def init_database():
    """Initialize database tables."""
    logger.info("Initializing database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
