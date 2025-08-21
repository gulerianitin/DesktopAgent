from loguru import logger

# Configure proper timestamp format
logger.configure(
    handlers=[
        {
            "sink": "agent.log",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {message}",
        }
    ]
)