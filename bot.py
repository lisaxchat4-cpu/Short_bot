import logging
import time
import cloudscraper
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def resolve_links(url):
    scraper = cloudscraper.create_scraper(allow_brotli=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Referer": "https://www.google.com/"
    }
    
    try:
        # --- STEP 1: Bypass VIPShort ---
        print(f"[*] Opening VIPShort link: {url}")
        res = scraper.get(url, headers=headers, allow_redirects=True, timeout=15)
        intermediate_url = res.url
        print(f"[*] Intermediate Blog URL: {intermediate_url}")
        
        # Give a small pause for simulation
        time.sleep(5)
        
        # --- STEP 2: Fetch Intermediate Blog Page ---
        print(f"[*] Fetching blog page content...")
        blog_res = scraper.get(intermediate_url, headers=headers, allow_redirects=True, timeout=15)
        soup = BeautifulSoup(blog_res.text, 'html.parser')
        
        # Check for form action
        form = soup.find('form')
        if form and form.get('action'):
            action_url = form.get('action')
            if not action_url.startswith('http'):
                base = "https://" + intermediate_url.split('/')[2]
                action_url = base + action_url if action_url.startswith('/') else base + '/' + action_url
            return f"[+] Final Destination (Form Action):\n{action_url}"
            
        # Search all external links on the blog page
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http') and not any(x in href for x in ['vipshort', 'hindumantra', 'geniousguide', 'google', 'cloudflare', 'javascript', '#', 'facebook', 'telegram']):
                return f"[+] Final Destination Link:\n{href}"
                
        # Fallback if blog URL itself changed externally
        if "hindumantra" not in intermediate_url and "vipshort" not in intermediate_url:
            return f"[+] Final Destination Link:\n{intermediate_url}"
            
        return f"[-] Blog page reached, but couldn't extract final link. URL: {intermediate_url}"
        
    except Exception as e:
        return f"[-] Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if "http://" in user_text or "https://" in user_text:
        await update.message.reply_text("[*] Processing multi-step short link...")
        result = resolve_links(user_text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Bhai, valid short link bhej!")

if __name__ == '__main__':
    BOT_TOKEN = "9098391736:AAF8JTbu0pDoEj8NkENlQ-zm_6EhEzWnYq8"
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("[+] Two-Step Resolver Bot is running...")
    application.run_polling()
