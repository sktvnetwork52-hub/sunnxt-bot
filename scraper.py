"""
সান NXT DRM বাইপাস — ব্রাউজার + pywidevine দিয়ে Keys জেনারেট
"""

import os
import re
import json
import time
import logging
import requests
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import USER_AGENT, CDM_DIR, CLIENT_ID_FILE, PRIVATE_KEY_FILE

logger = logging.getLogger(__name__)

class SunNXTDRM:
    """সান NXT DRM বাইপাস ক্লাস"""
    
    def __init__(self):
        self.driver = None
        self.has_cdm = os.path.exists(CLIENT_ID_FILE) and os.path.exists(PRIVATE_KEY_FILE)
    
    def _start_browser(self):
        """হেডলেস Chrome ব্রাউজার চালু"""
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument(f"--user-agent={USER_AGENT}")
        opts.add_argument("--window-size=1920,1080")
        opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        
        self.driver = webdriver.Chrome(options=opts)
        self.driver.set_page_load_timeout(30)
        logger.info("✅ ব্রাউজার চালু")
    
    def _close_browser(self):
        """ব্রাউজার বন্ধ"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🛑 ব্রাউজার বন্ধ")
            except:
                pass
    
    def _find_mpd_and_license(self, url):
        """পেজ লোড করে MPD + License URL ক্যাপচার"""
        
        self.driver.get(url)
        time.sleep(5)
        
        # প্লে বাটন থাকলে ক্লিক
        try:
            btns = self.driver.find_elements(By.CSS_SELECTOR, 
                "button[class*='play'], video, [class*='player']")
            for btn in btns[:3]:
                try:
                    btn.click()
                    time.sleep(3)
                    break
                except:
                    pass
        except:
            pass
        
        time.sleep(5)  # নেটওয়ার্ক ক্যাপচারের জন্য অপেক্ষা
        
        mpd_url = None
        license_url = None
        
        # পারফরমেন্স লগ চেক
        logs = self.driver.get_log("performance")
        
        for log_entry in logs:
            try:
                msg = json.loads(log_entry.get('message', '{}'))
                params = msg.get('message', {}).get('params', {})
                req_url = params.get('request', {}).get('url', '')
                
                if '.mpd' in req_url or '/Manifest' in req_url:
                    mpd_url = req_url
                    logger.info(f"📡 MPD: {req_url[:80]}...")
                
                if 'license' in req_url.lower() or 'widevine' in req_url.lower():
                    if '.lic' in req_url.lower() or '/wv' in req_url.lower():
                        license_url = req_url
                        logger.info(f"🔑 License: {req_url[:80]}...")
            except:
                continue
        
        return mpd_url, license_url
    
    def _get_pssh_from_mpd(self, mpd_url):
        """MPD ফাইল থেকে PSSH বের করে"""
        try:
            resp = requests.get(mpd_url, headers={'User-Agent': USER_AGENT}, timeout=10)
            if resp.status_code == 200:
                match = re.search(
                    r'<cenc:pssh[^>]*>(.*?)</cenc:pssh>',
                    resp.text, re.DOTALL
                )
                if match:
                    return match.group(1).strip()
        except Exception as e:
            logger.error(f"PSSH extraction failed: {e}")
        return None
    
    def _get_keys(self, pssh_b64, license_url):
        """CDM দিয়ে Keys জেনারেট"""
        if not self.has_cdm:
            log_error("CDM ফাইল নেই!")
            return []
        
        if not pssh_b64 or not license_url:
            return []
        
        try:
            from pywidevine.cdm import Cdm
            from pywidevine.device import Device
            from pywidevine.pssh import PSSH
            
            logger.info("🔑 Keys জেনারেট করা হচ্ছে...")
            
            device = Device.load(CDM_DIR)
            cdm = Cdm.from_device(device)
            pssh = PSSH(pssh_b64)
            session = cdm.open()
            
            headers = {
                'User-Agent': USER_AGENT,
                'Content-Type': 'application/octet-stream',
            }
            
            keys = cdm.get_keys(session, license_url, pssh.dumps(), headers=headers)
            
            result = []
            for key in keys:
                if key.type == "CONTENT":
                    result.append(f"{key.kid.hex()}:{key.key.hex()}")
            
            cdm.close(session)
            logger.info(f"✅ {len(result)}টি Keys পাওয়া গেছে")
            return result
            
        except ImportError:
            logger.error("pywidevine ইন্সটল নেই!")
            return []
        except Exception as e:
            logger.error(f"Keys error: {e}")
            return []
    
    def process(self, video_url):
        """সম্পূর্ণ প্রক্রিয়া"""
        
        result = {
            'success': False,
            'mpd_url': None,
            'license_url': None,
            'pssh': None,
            'keys': [],
            'error': None
        }
        
        try:
            self._start_browser()
            
            mpd_url, license_url = self._find_mpd_and_license(video_url)
            
            if not mpd_url:
                result['error'] = "MPD URL পাওয়া যায়নি"
                return result
            
            if not license_url:
                result['error'] = "License URL পাওয়া যায়নি"
                return result
            
            result['mpd_url'] = mpd_url
            result['license_url'] = license_url
            
            # PSSH বের করুন
            pssh = self._get_pssh_from_mpd(mpd_url)
            if not pssh:
                result['error'] = "PSSH পাওয়া যায়নি"
                return result
            
            result['pssh'] = pssh
            
            # Keys জেনারেট
            keys = self._get_keys(pssh, license_url)
            result['keys'] = keys
            
            if keys:
                result['success'] = True
            else:
                result['error'] = "Keys জেনারেট করা যায়নি"
        
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Process error: {e}")
        
        finally:
            self._close_browser()
        
        return result
