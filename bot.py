import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from playwright.async_api import async_playwright

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def bypass_vipshort(url):
    async with async_playwright() as p:
        # Memory-saving flags for Render free tier
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print(f"[*] Opening via Optimized Browser: {url}")
            await page.goto(url, timeout=50000)
            
            print("[*] Waiting for Cloudflare & Timers...")
            await asyncio.sleep(12)
            
            current_url = page.url
            print(f"[*] Current URL: {current_url}")
            
            # If we landed on intermediate blog, click any proceed/continue button
            if "hindumantra" in current_url or "blog." in current_url:
                await asyncio.sleep(5)
                try:
                    btn = await page.locator("text=Continue, text=Get Link, .btn, button").first
                    if btn:
                        await btn.click()
                        await asyncio.sleep(4)
                except:
                    pass
                current_url = page.url
            
            # Extract final external link
            links = await page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
            for l in links:
                if l and not any(x in l for x in ['vipshort', 'hindumantra', 'geniousguide', 'google', 'cloudflare', 'javascript', '#']):
                    await browser.close()
                    return f"[+] Final Destination Link:\n{l}"
                    
            if "vipshort" not in current_url:
                await browser.close()
                return f"[+] Final Page Link:\n{current_url}"
                
            await browser.close()
            return f"[-] Could not resolve. Reached: {current_url}"
            
        except Exception as e:
            await browser.close()
            return f"[-] Playwright Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if "http://" in user_text or "https://" in user_text:
        await update.message.reply_text("[*] Bypassing Cloudflare via optimized browser...")
        result = await bypass_vipshort(user_text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Bhai, valid short link bhej!")

if __name__ == '__main__':
    BOT_TOKEN = "9098391736:AAF8JTbu0pDoEj8NkENlQ-zm_6EhEzWnYq8"
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("[+] Optimized Browser Bot is running...")
    application.run_polling()
    
