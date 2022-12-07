import os
os.system("playwright install chromium")
from playwright.sync_api import sync_playwright
from time import sleep
import streamlit as st
from bs4 import BeautifulSoup
from latest_user_agents import get_random_user_agent

column1, column2 = st.columns(2)
column1.title('Sentimental Analysis')
symbol = column1.selectbox('Symbol to analyse', (
    'EUR/USD', 'AUD/USD', 'AUD/JPY', 'EUR/AUD', 'EUR/JPY', 
    'GBP/JPY', 'GBP/USD', 'NZD/USD', 'USD/CAD', 'USD/CHF', 
    'USD/JPY', 'XAU/USD'
))

#symbol = column1.text_input('Symbol to analyse')

button = column1.button('Analyse')
if button:
    with sync_playwright() as playwright:
        ua = get_random_user_agent()
        chromium = playwright.chromium # or "firefox" or "webkit".
        browser = chromium.launch()
        page = browser.new_page(extra_http_headers={
            'User-Agent': ua
        })
        page.goto("https://fxssi.com/tools/current-ratio?filter=AUDJPY", timeout=100000)


        page.locator(f'div.tool-button:text("{symbol}")').click()
        
        soup = BeautifulSoup(page.content(), 'lxml')

        buy = soup.select_one('#main-container > div.col-md-8 > div.tool-content.full-width.sharable-content > div.tools > div.row > div.tool-content.col-sm-8.sentiment-ratios > div > div.cur-rat-pairs > div.cur-rat-cur-pair.header.active > div.line.cur-rat-broker.broker-average > div > div > div.ratio > div.ratio-bar-left').text.strip()
        sell = soup.select_one('#main-container > div.col-md-8 > div.tool-content.full-width.sharable-content > div.tools > div.row > div.tool-content.col-sm-8.sentiment-ratios > div > div.cur-rat-pairs > div.cur-rat-cur-pair.header.active > div.line.cur-rat-broker.broker-average > div > div > div.ratio > div.ratio-bar-right').text.strip()
        buy = buy.replace('%', '')
        sell = sell.replace('%', '')
        
        # other actions...
        browser.close()
        
        col1, col2 = column1.columns(2)
        
        if buy > sell:
            buy2 = buy
            sell2 = "-" + sell
        else:
            buy2 = '-' + buy
            sell2 = sell
            
        col1.metric('Buy', value = float(buy), delta = buy2)
        col2.metric('Sell', value = float(sell), delta = sell2)
