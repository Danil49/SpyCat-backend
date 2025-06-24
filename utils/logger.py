import logging
import os
import coloredlogs

from config import Config

logger = logging.getLogger()

if logger.hasHandlers():
    logger.handlers.clear()

logger.setLevel(Config.LOGGING_LEVEL)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(Config.LOGGING_LEVEL)
formatter_console = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter_console)

# File Handler
log_dir = "./Logs"
log_file = os.path.join(log_dir, "logs.log")
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(log_file, mode='a')
file_handler.setLevel(Config.LOGGING_LEVEL)
formatter_file = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s\n')
file_handler.setFormatter(formatter_file)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Colored Logs for Console
coloredlogs.install(
    level=Config.LOGGING_LEVEL,
    fmt=formatter_console._fmt,
    datefmt="%H:%M:%S",
    logger=logger,
    level_styles={
        'info': {'color': 'green'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red'},
        'critical': {'color': 'magenta'}
    }
)
