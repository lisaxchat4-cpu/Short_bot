import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def resolve_link(url):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Referer": "https://www.google.com/"
    }
    
    try:
        print(f"[*] Requesting: {url}")
        res = session.get(url, headers=headers, allow_redirects=True, timeout=15)
        current_url = res.url
        print(f"[*] Current URL: {current_url}")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Check for meta refresh redirect
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh:
            content = meta_refresh.get('content', '')
            if 'url=' in content.lower():
                target = content.split('url=')[-1].strip(' "\'')
                print(f"[*] Found meta refresh target: {target}")
                current_url = target
                res = session.get(current_url, headers=headers, allow_redirects=True, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')

        # Check for form action or hidden inputs
        form = soup.find('form')
        if form and form.get('action'):
            action_url = form.get('action')
            if not action_url.startswith('http'):
                base = "https://" + current_url.split('/')[2]
                action_url = base + action_url if action_url.startswith('/') else base + '/' + action_url
            print(f"[*] Form action found: {action_url}")
            res = session.get(action_url, headers=headers, allow_redirects=True, timeout=15)
            current_url = res.url

        # Search for final target link inside the page text/buttons
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http') and not any(x in href for x in ['vipshort', 'hindumantra', 'geniousguide', 'google', 'cloudflare', 'javascript', '#']):
                return f"[+] Final Destination Link:\n{href}"
                
        # If no specific 'a' tag, check if current_url is clean
        if not any(x in current_url for x in ['vipshort', 'hindumantra', 'geniousguide']):
            return f"[+] Final Destination Link:\n{current_url}"
            
        return f"[-] Could not auto-resolve. Reached: {current_url}"
        
    except Exception as e:
        return f"[-] Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if "http://" in user_text or "https://" in user_text:
        await update.message.reply_text("[*] Resolving link instantly...")
        result = resolve_link(user_text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Bhai, valid short link bhej!")

if __name__ == '__main__':
    BOT_TOKEN = "9098391736:AAF8JTbu0pDoEj8NkENlQ-zm_6EhEzWnYq8"
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("[+] Fast Link Resolver Bot is running...")
    application.run_polling()
  
