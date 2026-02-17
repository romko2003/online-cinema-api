from __future__ import annotations

import logging
from typing import Final

LOG_FORMAT: Final[str] = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(level: int = logging.INFO) -> None:
    """
    Basic logging configuration for local development and containerized runs.
    """
    logging.basicConfig(level=level, format=LOG_FORMAT)
