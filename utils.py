import os
import re
import json
import hashlib
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_id():
    return hashlib.md5(os.urandom(16)).hexdigest()[:12]

def extract_urls(text):
    url_pattern = r'https?://[^\s<>"]+'
    return re.findall(url_pattern, text)

def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f}TB"

def log_info(msg):
    logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def log_error(msg):
    logger.error(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {msg}")

def log_success(msg):
    logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {msg}")
