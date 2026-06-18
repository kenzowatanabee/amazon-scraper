import logging
import os
from logging import Logger

def setup_custom_logger(name: str, log_file: str = "data/logs/scraper.log", level=logging.INFO) -> Logger:
    """Configures a custom dual-output logger (Console + File)."""
    
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # create a unique logger instance
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # prevent duplicate log messages if logger is initialized multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # define a clean, professional format
    # example output: [2026-06-18 15:10:42] [INFO] [worker.py:24]: Message here
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # create Console Handler (Terminal output)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # create File Handler (Permanent disk storage)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger