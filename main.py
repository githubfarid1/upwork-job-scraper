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
import parsedatetime

from datetime import datetime
load_dotenv()
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
SECONDS = float(os.environ.get("SECONDS"))

# breakpoint()
url = 'https://www.upwork.com/nx/search/jobs/?amount=100-&nbs=1&q=web%20scraping&sort=recency&t=0,1'


def parse_datetime(datetime_string):
    datetime_parser = parsedatetime.Calendar()
    timestamp = datetime_parser.parse(datetime_string)
    if len(timestamp) == 2:
        if timestamp[1] == 0:
            raise ValueError(u'Failed to parse datetime: %s' % datetime_string)
        timestamp = timestamp[0]
    return datetime.fromtimestamp(time.mktime(timestamp))

def send_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={quote(message)}"
    r = requests.get(telegram_url)

def find_job(html):
    jobs = []
    soup = BeautifulSoup(html,'html.parser')
    # breakpoint()

    trs = soup.find_all("article")
    for tr in trs:
        postat = tr.find_all("span")[1].text
        headertext = tr.find("div", class_="job-tile-header").find("a").text
        headerhref = tr.find("div", class_="job-tile-header").find("a")['href']
        jobs.append({"postat": postat, "headertext": headertext, "headerhref": headerhref})
    return jobs 

async def run(playwright):
    
    # page = await playwright.new_page(proxy={"server": "http://43.152.113.55:2334","username": "u0a8c217b562505b8-zone-custom-region-us","password": "u0a8c217b562505b8"})
    page = await playwright.new_page()
    isfirst = True
    while True:
        idtime = random.choice(range(120, 180))
        try:
            # breakpoint()
            await page.goto(url, wait_until="domcontentloaded")
            # await page.click('text=Accept', timeout=3000)
            time.sleep(3)
            html = await page.content()
            jobs = find_job(html)
            for idx, job in enumerate(jobs):
                seconds = (datetime.today() - parse_datetime(job['postat'])).total_seconds()
                jobs[idx]['seconds'] = seconds
            # breakpoint()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error(str(exc_type) + " " + str(fname) + " " + str(exc_tb.tb_lineno))
            time.sleep(3)
            print(exc_type,fname,exc_tb.tb_lineno)
            continue
        # breakpoint()
        for job in jobs:
            if job['headertext'] not in listjob:
                if job['seconds'] < SECONDS:
                    message = f"{job['headertext']} https://www.upwork.com{job['headerhref']}"
                    listjob.append(job['headertext'])
                    send_telegram(message=message)
        print("idle time", idtime, "seconds")
        time.sleep(idtime)
        # if isfirst:
        #     isfirst = False
        #     message = f"{headertext} https://www.upwork.com{headerhref}"
        #     send_telegram(message=message)
        #     listjob.append(headertext)
        #     print("idle time", idtime, "seconds")
        #     time.sleep(idtime)
        #     continue
        # if headertext not in listjob:
        #     listjob.append(headertext)
        #     message = f"{headertext} https://www.upwork.com{headerhref}"
        #     send_telegram(message=message)
        # print("idle time", idtime, "seconds")
        # time.sleep(idtime)
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
            print(exc_type,fname,exc_tb.tb_lineno)
            time.sleep(10)
            continue        

asyncio.run(main())
