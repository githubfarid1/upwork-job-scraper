import time
from bs4 import BeautifulSoup
from camoufox.async_api import AsyncCamoufox
import asyncio
# from playwright.async_api import async_playwright, Playwright
import random
import requests
from urllib.parse import unquote, quote, unquote_plus, quote_plus
import logging
import sys
import os
from dotenv import load_dotenv, dotenv_values
load_dotenv()
# config = dotenv_values(".env")
# breakpoint()
# create an instance of the logger
try:
    logging.basicConfig(filename='/home/pi/dev/python/upwork-job-scraper/bot.log', level=logging.INFO,
                    format='%(asctime)-15s %(levelname)-2s %(message)s')
except:
    logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)-15s %(levelname)-2s %(message)s')

logger = logging.getLogger()
listjob = []
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
HEADLESS = (os.getenv('HEADLESS', 'False') == 'True')
# breakpoint()
url = 'https://www.upwork.com/nx/search/jobs/?amount=100-&nbs=1&q=web%20scraping&sort=recency&t=0,1'

def send_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={quote(message)}"
    r = requests.get(telegram_url)

def find_job(html):
    soup = BeautifulSoup(html,'html.parser')
    # breakpoint()
    headertext = soup.find("div", class_="job-tile-header").find("a").text
    headerhref = soup.find("div", class_="job-tile-header").find("a")['href']
    return headertext, headerhref 

async def run(playwright):
    
    
    page = await playwright.new_page()

    isfirst = True
    while True:
        idtime = random.choice(range(120, 180))
        try:
            await page.goto(url, wait_until="domcontentloaded")
            # await page.click('text=Accept', timeout=3000)
            time.sleep(3)
            html = await page.content()
            headertext, headerhref = find_job(html)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error(str(exc_type) + " " + str(fname) + " " + str(exc_tb.tb_lineno))
            time.sleep(3)
            continue
        # breakpoint()
        if isfirst:
            isfirst = False
            message = f"{headertext} https://www.upwork.com{headerhref}"
            send_telegram(message=message)
            listjob.append(headertext)
            print("idle time", idtime, "seconds")
            time.sleep(idtime)
            continue
        if headertext not in listjob:
            listjob.append(headertext)
            message = f"{headertext} https://www.upwork.com{headerhref}"
            send_telegram(message=message)
        print("idle time", idtime, "seconds")
        time.sleep(idtime)
    # await browser.close()

async def main():
    message = "Starting bot..."
    send_telegram(message=message)
    logger.info(message)
    while True:
        try:
            async with AsyncCamoufox(headless=HEADLESS) as playwright:
                await run(playwright)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error(str(exc_type) + " " + str(fname) + " " + str(exc_tb.tb_lineno))
            time.sleep(10)
            continue        

asyncio.run(main())
