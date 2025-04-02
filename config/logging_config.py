import logging
import os
from logging.handlers import RotatingFileHandler
from .settings import LOG_LEVEL, LOG_FILE

def setup_logging():
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handler
    file_handler = RotatingFileHandler(
        os.path.join('logs', LOG_FILE),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create logger for the application
    logger = logging.getLogger('news_agent')
    logger.setLevel(LOG_LEVEL)
    
    return logger

# Create logger instance
logger = setup_logging() 