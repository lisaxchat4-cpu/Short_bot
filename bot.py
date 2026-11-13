import logging
import cloudscraper
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def bypass_short_link(url):
    # Using cloudscraper with a realistic browser fingerprint to bypass Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.google.com/"
    }
    
    try:
        print(f"[*] Requesting link with cloudscraper: {url}")
        response = scraper.get(url, headers=headers, timeout=10, allow_redirects=True)
        current_url = response.url
        print(f"[*] Resolved URL: {current_url}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Search for external destination links in the page
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http') and not any(x in href for x in ['vipshort', 'hindumantra', 'geniousguide', 'google', 'cloudflare', 'javascript', '#']):
                return f"[+] Final Destination Link:\n{href}"
                
        # If no <a> tag found, check if current URL itself is clean
        if "vipshort" not in current_url and "hindumantra" not in current_url:
            return f"[+] Final Link:\n{current_url}"
            
        return f"[-] Cloudflare challenged or intermediate page reached: {current_url}"
        
    except Exception as e:
        return f"[-] Request Timeout or Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if "http://" in user_text or "https://" in user_text:
        await update.message.reply_text("[*] Processing link instantly...")
        result = bypass_short_link(user_text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Bhai, valid short link bhej!")

if __name__ == '__main__':
    BOT_TOKEN = "9098391736:AAF8JTbu0pDoEj8NkENlQ-zm_6EhEzWnYq8"
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("[+] Instant Resolver Bot is running...")
    application.run_polling()
    
