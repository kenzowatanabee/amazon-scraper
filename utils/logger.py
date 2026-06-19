# utils/logger.py
import logging
import os
from logging import Logger

class ColoredFormatter(logging.Formatter):
    # ANSI Escape Sequences
    grey = "\x1b[38;20m"
    cyan = "\x1b[36m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    magenta = "\x1b[35m"  # 🔮 New distinctive color for saved data strings
    reset = "\x1b[0m"
    
    log_format = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s"

    LEVEL_COLORS = {
        logging.DEBUG: cyan + log_format + reset,
        logging.INFO: green + log_format + reset,
        logging.WARNING: yellow + log_format + reset,
        logging.ERROR: red + log_format + reset,
        logging.CRITICAL: bold_red + log_format + reset
    }

    def format(self, record):
        # 1. Get the baseline format for the standard logging level
        log_fmt = self.LEVEL_COLORS.get(record.levelno, self.grey + self.log_format + self.reset)
        
        # 2. 🎯 Keyword Override: If it's an INFO log but contains our data hook, switch to magenta!
        if record.levelno == logging.INFO and "data saved" in record.getMessage().lower():
            log_fmt = self.magenta + self.log_format + self.reset

        formatter = logging.Formatter(fmt=log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_custom_logger(name: str, log_file: str = "data/logs/scraper.log", level=logging.INFO) -> Logger:
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.hasHandlers():
        logger.handlers.clear()

    file_formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger