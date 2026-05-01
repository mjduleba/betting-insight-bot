from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_level: str = 'INFO') -> None:
    '''
    Configure root logging handlers for console and file output.

    Args:
        log_level (str): desired log level string
    '''
    # Parse requested log level, fallback to INFO
    resolved_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logs directory and target file path
    log_dir = Path('logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'app.log'

    # Build reusable formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')

    # Build stream handler for local terminal visibility
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(resolved_level)
    stream_handler.setFormatter(formatter)

    # Build rotating file handler for debug history
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=1_000_000,
        backupCount=3,
        encoding='utf-8',
    )
    file_handler.setLevel(resolved_level)
    file_handler.setFormatter(formatter)

    # Reset root handlers for deterministic module-managed logging setup
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(resolved_level)
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
