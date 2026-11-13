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
            # --- STEP 1: Open VIPShort Link ---
            print(f"[*] Opening initial short link: {url}")
            await page.goto(url, timeout=60000)
            
            print("[*] Waiting for 15 seconds timer on first page...")
            await asyncio.sleep(15)
            
            # Click common continue/verify buttons on first page
            selectors = ["text=Continue", "text=Click Here", "text=Get Link", "text=Verify", "text=Open Link", ".btn", "#btn", "button"]
            for selector in selectors:
                try:
                    btns = await page.locator(selector).all()
                    for b in btns:
                        if await b.is_visible():
                            print(f"[*] Clicking element on step 1: {selector}")
                            await b.click()
                            await asyncio.sleep(5)
                            break
                except:
                    continue
            
            # Get intermediate link (like blog.hindumantra.net)
            current_url = page.url
            print(f"[*] Landed on intermediate URL: {current_url}")
            
            # --- STEP 2: If we hit a blog/interstitial page, handle it ---
            if "blog." in current_url or "hindumantra" in current_url or "vipshort" in current_url:
                print("[*] Detected intermediate blog page. Waiting for final destination...")
                await asyncio.sleep(10) # Wait for blog page timers
                
                # Look for external destination links or click buttons on the blog page
                for selector in selectors:
                    try:
                        btns = await page.locator(selector).all()
                        for b in btns:
                            if await b.is_visible():
                                print(f"[*] Clicking element on blog page: {selector}")
                                await b.click()
                                await asyncio.sleep(5)
                                break
                    except:
                        continue
                
                current_url = page.url
                print(f"[*] URL after blog interaction: {current_url}")

            # --- STEP 3: Extract final clean URL ---
            links = await page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
            for l in links:
                if l and not any(x in l for x in ['vipshort', 'hindumantra', 'geniousguide', 'google', 'cloudflare', 'javascript', '#', 'facebook', 'telegram', 'whatsapp']):
                    if any(l.startswith(proto) for proto in ['http://', 'https://']):
                        await browser.close()
                        return f"[+] Final Destination Link:\n{l}"
            
            # Fallback to current page url if it's external
            if not any(x in current_url for x in ['vipshort', 'hindumantra', 'geniousguide']):
                await browser.close()
                return f"[+] Final Destination Link:\n{current_url}"
                
            await browser.close()
            return f"[-] Could not extract final link. Stuck at: {current_url}"
            
        except Exception as e:
            await browser.close()
            return f"[-] Playwright Exception: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if "http://" in user_text or "https://" in user_text:
        await update.message.reply_text("[*] Processing multi-step bypass via browser...")
        result = await bypass_vipshort(user_text)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Bhai, valid short link bhej!")

if __name__ == '__main__':
    BOT_TOKEN = "9098391736:AAF8JTbu0pDoEj8NkENlQ-zm_6EhEzWnYq8"
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("[+] Multi-step Bypasser Bot is running...")
    application.run_polling()
  
