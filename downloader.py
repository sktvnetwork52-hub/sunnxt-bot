"""
N_m3u8DL-RE দিয়ে ডাউনলোড
"""

import os
import subprocess
import logging
from pathlib import Path

from config import DOWNLOAD_DIR, DOWNLOAD_TIMEOUT
from utils import generate_id, log_info, log_error, log_success

logger = logging.getLogger(__name__)

class Downloader:
    
    @staticmethod
    def download(mpd_url, keys, output_dir=None):
        """MPD + Keys দিয়ে ডাউনলোড"""
        
        if not output_dir:
            output_dir = DOWNLOAD_DIR
        
        os.makedirs(output_dir, exist_ok=True)
        name = f"sunnxt_{generate_id()}"
        
        cmd = [
            "N_m3u8DL-RE",
            mpd_url,
            "--save-name", name,
            "--save-dir", output_dir,
            "-M", "format=mp4",
            "--download-retry-count", "3",
            "--thread-count", "4",
        ]
        
        for k in keys:
            cmd.extend(["--key", k])
        
        log_info(f"ডাউনলোড শুরু: {name}")
        
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=DOWNLOAD_TIMEOUT)
            
            if proc.returncode == 0:
                for f in Path(output_dir).iterdir():
                    if name in f.name and f.suffix in ['.mp4', '.mkv']:
                        log_success(f"ডাউনলোড সফল: {f.name}")
                        return str(f)
                return None
            else:
                log_error(f"ডাউনলোড ব্যর্থ: {proc.stderr[:200]}")
                return None
        
        except subprocess.TimeoutExpired:
            log_error("টাইমআউট")
            return None
        except Exception as e:
            log_error(f"Error: {e}")
            return None
