#!/usr/bin/env python3
"""
সান NXT অটো ডাউনলোডার বট — সম্পূর্ণ অটোমেটিক
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import BOT_TOKEN, DOWNLOAD_DIR, MAX_FILE_SIZE
from utils import extract_urls, format_size, generate_id, log_info, log_error, log_success
from scraper import SunNXTDRM
from downloader import Downloader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ===== হ্যান্ডলার =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🎬 **সান NXT অটো ডাউনলোডার**\n\n"
        f"স্বাগতম {user.first_name}! 👋\n\n"
        f"**কিভাবে ব্যবহার করবেন:**\n"
        f"শুধু একটি সান NXT ভিডিও লিংক পাঠান।\n"
        f"বট নিজেই সব করবে:\n"
        f"1️⃣ DRM বাইপাস 🔓\n"
        f"2️⃣ ডাউনলোড ⬇️\n"
        f"3️⃣ ভিডিও পাঠাবে 📤\n\n"
        f"**সময়:** ১-৫ মিনিট\n\n"
        f"⚙️ /status - বট স্ট্যাটাস",
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import CLIENT_ID_FILE, PRIVATE_KEY_FILE
    
    cdm_ok = os.path.exists(CLIENT_ID_FILE) and os.path.exists(PRIVATE_KEY_FILE)
    
    import shutil
    dl_ok = shutil.which("N_m3u8DL-RE") is not None
    
    await update.message.reply_text(
        f"📊 **বট স্ট্যাটাস**\n\n"
        f"{'✅' if cdm_ok else '❌'} CDM\n"
        f"{'✅' if dl_ok else '❌'} N_m3u8DL-RE\n"
        f"✅ বট চালু আছে",
        parse_mode='Markdown'
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """মেইন হ্যান্ডলার — ইউজার URL পাঠালে"""
    
    text = update.message.text or ""
    urls = extract_urls(text)
    
    if not urls:
        await update.message.reply_text("❌ কোনো URL পাওয়া যায়নি।")
        return
    
    video_url = urls[0]
    
    if 'sunnxt' not in video_url.lower():
        await update.message.reply_text("⚠️ শুধু সান NXT লিংক সাপোর্ট করে।")
        return
    
    # প্রক্রিয়া শুরু
    msg = await update.message.reply_text(
        "⏳ **প্রক্রিয়া শুরু...**\n\n"
        "1️⃣ ব্রাউজার খোলা হচ্ছে...\n"
        "2️⃣ MPD খোঁজা হচ্ছে...\n"
        "3️⃣ Keys জেনারেট করা হচ্ছে...\n"
        "4️⃣ ডাউনলোড করা হচ্ছে...\n"
        "5️⃣ আপলোড করা হচ্ছে...\n\n"
        "⏱️ ১-৫ মিনিট সময় লাগতে পারে",
        parse_mode='Markdown'
    )
    
    try:
        # === STEP 1: DRM BYPASS ===
        await msg.edit_text("🔄 **ধাপ ১/৩:** DRM বাইপাস করা হচ্ছে...\n🔍 ব্রাউজারে ভিডিও লোড করা হচ্ছে", parse_mode='Markdown')
        
        drm = SunNXTDRM()
        result = drm.process(video_url)
        
        if not result['success']:
            error = result.get('error', 'অজানা ত্রুটি')
            await msg.edit_text(f"❌ **ব্যর্থ!**\n\n{error}\n\nআবার চেষ্টা করুন।", parse_mode='Markdown')
            return
        
        if not result.get('keys'):
            await msg.edit_text("❌ **Keys পাওয়া যায়নি!** CDM চেক করুন।", parse_mode='Markdown')
            return
        
        # === STEP 2: DOWNLOAD ===
        await msg.edit_text(
            f"⬇️ **ধাপ ২/৩:** ডাউনলোড করা হচ্ছে...\n\n"
            f"🔑 Keys: {len(result['keys'])}টি\n"
            f"⏱️ দয়া করে অপেক্ষা করুন...",
            parse_mode='Markdown'
        )
        
        user_dir = os.path.join(DOWNLOAD_DIR, str(update.effective_user.id))
        os.makedirs(user_dir, exist_ok=True)
        
        file_path = Downloader.download(
            mpd_url=result['mpd_url'],
            keys=result['keys'],
            output_dir=user_dir
        )
        
        if not file_path or not os.path.exists(file_path):
            await msg.edit_text("❌ **ডাউনলোড ব্যর্থ!** আবার চেষ্টা করুন।", parse_mode='Markdown')
            return
        
        file_size = os.path.getsize(file_path)
        
        if file_size > MAX_FILE_SIZE:
            await msg.edit_text(f"⚠️ ফাইল বড়! ({format_size(file_size)})", parse_mode='Markdown')
            os.remove(file_path)
            return
        
        if file_size < 1024:
            await msg.edit_text("❌ ফাইল ত্রুটিপূর্ণ!", parse_mode='Markdown')
            os.remove(file_path)
            return
        
        # === STEP 3: UPLOAD ===
        await msg.edit_text(
            f"📤 **ধাপ ৩/৩:** আপলোড করা হচ্ছে...\n\n"
            f"📦 {format_size(file_size)}",
            parse_mode='Markdown'
        )
        
        try:
            with open(file_path, "rb") as f:
                await update.message.reply_video(
                    video=f,
                    caption=f"✅ **সম্পূর্ণ!**\n📦 {format_size(file_size)}\n⚡ অথোরাইজড পেন্টেস্ট",
                    supports_streaming=True,
                    timeout=600
                )
            
            await msg.delete()
            log_success(f"{update.effective_user.first_name} এর জন্য সম্পূর্ণ!")
        
        except Exception as e:
            await msg.edit_text(f"❌ আপলোড ব্যর্থ: {str(e)[:100]}", parse_mode='Markdown')
        
        finally:
            try:
                os.remove(file_path)
            except:
                pass
    
    except Exception as e:
        logger.error(f"Error: {traceback.format_exc()}")
        await msg.edit_text(f"❌ ত্রুটি: {str(e)[:150]}", parse_mode='Markdown')

# ===== মেইন =====

def main():
    logger.info("="*40)
    logger.info("🤖 সান NXT বট চালু হচ্ছে...")
    
    # চেক CDM
    from config import CLIENT_ID_FILE, PRIVATE_KEY_FILE
    if not os.path.exists(CLIENT_ID_FILE):
        logger.warning("⚠️ client_id.bin নেই!")
    if not os.path.exists(PRIVATE_KEY_FILE):
        logger.warning("⚠️ private_key.pem নেই!")
    
    # চেক N_m3u8DL-RE
    import shutil
    if not shutil.which("N_m3u8DL-RE"):
        logger.warning("⚠️ N_m3u8DL-RE নেই!")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    logger.info("✅ বট চালু! ইউজারের অপেক্ষায়...")
    app.run_polling()

if __name__ == "__main__":
    main()
