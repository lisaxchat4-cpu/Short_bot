import logging
import time
import re
import cloudscraper
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def bypass_vipshort(url):
    scraper = cloudscraper.create_scraper(allow_brotli=False)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Referer": "https://www.google.com/"
        }
        
        print(f"[*] Opening short link: {url}")
        response = scraper.get(url, headers=headers, allow_redirects=True)
        current_url = response.url
        
        print("[*] Waiting for timer simulation (15 seconds)...")
        time.sleep(15)
        
        response = scraper.get(current_url, headers=headers, allow_redirects=True)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 1. Check for any form action URL
        form = soup.find('form')
        if form and form.get('action'):
            action_url = form.get('action')
            if not action_url.startswith('http'):
                base_domain = "https://" + current_url.split('/')[2]
                action_url = base_domain + action_url if action_url.startswith('/') else base_domain + '/' + action_url
            return f"[+] Form Action Destination Found:\n{action_url}"
            
        # 2. Check for hidden input fields carrying target links
        inputs = soup.find_all('input', {'type': 'hidden'})
        for inp in inputs:
            val = inp.get('value', '')
            if val.startswith('http') and not 'vipshort' in val and not 'geniousguide' in val:
                return f"[+] Hidden Input Target Link:\n{val}"
                
        # 3. Fallback: Scan all external links
        all_urls = re.findall(r'https?://[^\s\'"<>]+', response.text)
        for u in all_urls:
            u = u.rstrip('\'");}')
            if not any(x in u for x in ['vipshort', 'geniousguide', 'google', 'cloudflare', 'jquery', 'bootstrap', 'gstatic', 'cdnjs']):
                if not any(u.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.ico', '.css', '.js', '.svg', '.webp']):
                    return f"[+] Target Link Found:\n{u}"
                    
        return "[-] Could not extract final link automatically."
        
    except Exception as e:
        return f"[-] Exception: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if "http://" in user_text or "https://" in user_text:
        await update.message.reply_text("[*] Processing link on cloud server...")
        result = bypass_vipshort(user_text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Bhai, valid short link bhej!")

if __name__ == '__main__':
    BOT_TOKEN = "9098391736:AAF8JTbu0pDoEj8NkENlQ-zm_6EhEzWnYq8"
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("[+] Cloud Bypasser Bot is running...")
    application.run_polling()
  
