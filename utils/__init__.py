from loguru import logger

# Configure proper timestamp format
import os

logger.configure(
    handlers=[
        {
            "sink": os.path.expanduser("~/agent.log"),
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {message}",
        }
    ]
)