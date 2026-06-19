import os

# ========== টেলিগ্রাম কনফিগারেশন ==========
# Railway Environment Variables থেকে নিবে
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "@your_channel")

# ========== ডাউনলোড সেটিংস ==========
DOWNLOAD_DIR = "downloads"
MAX_FILE_SIZE = 1.8 * 1024 * 1024 * 1024  # 2GB
DOWNLOAD_TIMEOUT = 600  # 10 মিনিট

# ========== CDM ফাইল ==========
CDM_DIR = os.path.join(os.path.dirname(__file__), "cdm")
CLIENT_ID_FILE = os.path.join(CDM_DIR, "client_id.bin")
PRIVATE_KEY_FILE = os.path.join(CDM_DIR, "private_key.pem")

# ========== ব্রাউজার ==========
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
