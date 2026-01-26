import os

# Optional loguru configuration
try:
    from loguru import logger
    logger.configure(
        handlers=[
            {
                "sink": os.path.expanduser("~/agent.log"),
                "format": "{time:YYYY-MM-DD HH:mm:ss} | {message}",
            }
        ]
    )
except ImportError:
    # Loguru not installed, use basic logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)