#!/bin/bash
set -e

echo "========================================="
echo "🤖 সান NXT অটো ডাউনলোডার বট"
echo "========================================="

# 1. Chromium ইন্সটল (Selenium এর জন্য)
echo "[1/4] Chromium ইন্সটল হচ্ছে..."
apt-get update -qq
apt-get install -y -qq chromium chromium-driver > /dev/null 2>&1
echo "✅ Chromium প্রস্তুত"

# 2. N_m3u8DL-RE ইন্সটল
echo "[2/4] N_m3u8DL-RE ইন্সটল হচ্ছে..."
if ! command -v N_m3u8DL-RE &> /dev/null; then
    wget -q https://github.com/nilaoda/N_m3u8DL-RE/releases/latest/download/N_m3u8DL-RE_Linux_x86_64.tar.gz
    tar -xzf N_m3u8DL-RE_Linux_x86_64.tar.gz
    chmod +x N_m3u8DL-RE
    mv N_m3u8DL-RE /usr/local/bin/
    rm -f N_m3u8DL-RE_Linux_x86_64.tar.gz
    echo "✅ N_m3u8DL-RE ইন্সটল হয়েছে"
else
    echo "✅ N_m3u8DL-RE আগেই আছে"
fi

# 3. Python ডিপেন্ডেন্সি
echo "[3/4] Python প্যাকেজ ইন্সটল হচ্ছে..."
pip install -r requirements.txt -q
echo "✅ Python প্যাকেজ প্রস্তুত"

# 4. ফোল্ডার তৈরি
echo "[4/4] ফোল্ডার তৈরি হচ্ছে..."
mkdir -p downloads cdm

echo ""
echo "========================================="
echo "✅ বট চালু হচ্ছে..."
echo "========================================="

# বট চালান
python main.py
