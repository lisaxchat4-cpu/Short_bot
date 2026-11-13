import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def resolve_link(url):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/"
    }
    
    try:
        print(f"[*] Fetching: {url}")
        # Disable automatic redirects to capture intermediate header locations manually
        response = session.get(url, headers=headers, allow_redirects=False, timeout=15)
        
        # Check if there's a Location header (direct redirect)
        if 'Location' in response.headers:
            target = response.headers['Location']
            print(f"[*] Found direct redirect: {target}")
            return f"[+] Target Link:\n{target}"
            
        # If response is normal, parse with BeautifulSoup to look for window.location or meta refresh
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check script tags for window.location redirects
        for script in soup.find_all('script'):
            if script.string and 'window.location' in script.string:
                print(f"[*] Found JS redirect script")
                # Extract URL from script if possible
                
        # Fallback: check all links
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http') and 'vipshort' not in href and 'google' not in href:
                return f"[+] Extracted Link:\n{href}"
                
        return f"[-] Blocked or protected by Cloudflare/JS. URL: {url}"
        
    except Exception as e:
        return f"[-] Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if "http://" in user_text or "https://" in user_text:
        await update.message.reply_text("[*] Tracing redirect headers...")
        result = resolve_link(user_text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Bhai, valid short link bhej!")

if __name__ == '__main__':
    BOT_TOKEN = "9098391736:AAF8JTbu0pDoEj8NkENlQ-zm_6EhEzWnYq8"
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("[+] Header Tracer Bot is running...")
    application.run_polling()
    
