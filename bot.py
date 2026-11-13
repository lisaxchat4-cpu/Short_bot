import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from playwright.async_api import async_playwright

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def bypass_vipshort(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print(f"[*] Opening short link: {url}")
            await page.goto(url, timeout=60000)
            
            print("[*] Waiting for 15 seconds timer...")
            await asyncio.sleep(15)
            
            # Print all buttons and links text to Render logs for debugging
            buttons = await page.eval_on_selector_all("button, input[type='submit'], a", "elements => elements.map(e => e.innerText.trim() + ' | ' + e.href)")
            print(f"[*] Available elements on page: {buttons[:15]}") # Print first 15 elements
            
            # Try clicking common continue/verify buttons
            selectors = ["text=Continue", "text=Click Here", "text=Get Link", "text=Verify", "text=Open Link", ".btn", "#btn", "button"]
            for selector in selectors:
                try:
                    btns = await page.locator(selector).all()
                    for b in btns:
                        if await b.is_visible():
                            print(f"[*] Clicking visible element matching: {selector}")
                            await b.click()
                            await asyncio.sleep(5)
                            break
                except:
                    continue
            
            final_url = page.url
            print(f"[*] Current page URL after click: {final_url}")
            
            if "vipshort" not in final_url and "geniousguide" not in final_url:
                await browser.close()
                return f"[+] Final Bypassed Link:\n{final_url}"
                
            # Grab all links as fallback
            links = await page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
            for l in links:
                if l and not any(x in l for x in ['vipshort', 'geniousguide', 'google', 'cloudflare', 'javascript', '#']):
                    await browser.close()
                    return f"[+] Extracted Link:\n{l}"
                    
            await browser.close()
            return f"[-] Final link not found. Current URL: {final_url}"
            
        except Exception as e:
            await browser.close()
            return f"[-] Playwright Exception: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if "http://" in user_text or "https://" in user_text:
        await update.message.reply_text("[*] Processing via Playwright browser...")
        result = await bypass_vipshort(user_text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Bhai, valid short link bhej!")

if __name__ == '__main__':
    BOT_TOKEN = "9098391736:AAF8JTbu0pDoEj8NkENlQ-zm_6EhEzWnYq8"
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("[+] Debugging Bot is running...")
    application.run_polling()
  
