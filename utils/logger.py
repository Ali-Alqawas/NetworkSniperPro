"""
نظام التسجيل الاحترافي
"""
import logging
import os
from logging.handlers import RotatingFileHandler
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LOG_DIR, LOG_MAX_SIZE, LOG_BACKUP_COUNT


def setup_logger(name="NetworkSniperPro"):
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), LOG_DIR)
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    log_file = os.path.join(log_dir, "app.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=LOG_MAX_SIZE, backupCount=LOG_BACKUP_COUNT, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(fmt)
    console_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

log = setup_logger()
