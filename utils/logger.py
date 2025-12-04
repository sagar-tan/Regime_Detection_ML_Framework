import logging
from pathlib import Path

def setup_logger(name: str, log_file: str = "project.log", level=logging.INFO):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_path = log_dir / log_file

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # File Handler
    file_handler = logging.FileHandler(log_path, mode="a")
    file_handler.setFormatter(formatter)
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    # Logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
