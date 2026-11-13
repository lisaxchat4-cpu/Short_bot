import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from playwright.async_api import async_playwright

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def bypass_vipshort(url):
    async with async_playwright() as p:
        # Launch headless browser
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print(f"[*] Opening short link via browser: {url}")
            await page.goto(url, timeout=60000)
            
            # Wait for any potential timers or redirection scripts to run (e.g., 15 seconds)
            print("[*] Waiting for JS timers and Cloudflare protection...")
            await asyncio.sleep(15)
            
            # Try clicking common download / continue buttons automatically
            selectors = ["text=Continue", "text=Click Here", "text=Get Link", "#download-btn", ".btn-success", "a.get-link"]
            for selector in selectors:
                try:
                    btn = await page.wait_for_selector(selector, timeout=3000)
                    if btn:
                        print(f"[*] Found click element: {selector}")
                        await btn.click()
                        await asyncio.sleep(5)
                        break
                except:
                    continue
            
            # Grab final URL after redirection/clicks
            final_url = page.url
            
            # Check if we landed somewhere outside the shortener domain
            if "vipshort" not in final_url and "geniousguide" not in final_url:
                await browser.close()
                return f"[+] Final Bypassed Link:\n{final_url}"
                
            # Fallback: Search all links present on the final page
            links = await page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
            for l in links:
                if l and not any(x in l for x in ['vipshort', 'geniousguide', 'google', 'cloudflare', 'javascript']):
                    await browser.close()
                    return f"[+] Extracted Link from Page:\n{l}"
                    
            await browser.close()
            return f"[-] Could not find destination link. Current page: {final_url}"
            
        except Exception as e:
            await browser.close()
            return f"[-] Playwright Exception: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if "http://" in user_text or "https://" in user_text:
        msg = await update.message.reply_text("[*] Launching headless browser to bypass JS protection...")
        result = await bypass_vipshort(user_text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Bhai, valid short link bhej!")

if __name__ == '__main__':
    BOT_TOKEN = "9098391736:AAF8JTbu0pDoEj8NkENlQ-zm_6EhEzWnYq8"
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("[+] Playwright Bot is running...")
    application.run_polling()
    
