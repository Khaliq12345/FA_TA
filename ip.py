import os
os.system("playwright install chromium")
from playwright.sync_api import sync_playwright
from time import sleep
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from tradingview_ta import TA_Handler, Interval, Exchange
from latest_user_agents import get_random_user_agent

column1, column2 = st.columns(2)
column1.subheader('Sentimental Analysis')
column2.subheader('Technical Analysis')
symbol = column1.selectbox('Symbol to analyse the sentiments', (
    'EUR/USD', 'AUD/USD', 'AUD/JPY', 'EUR/AUD', 'EUR/JPY', 
    'GBP/JPY', 'GBP/USD', 'NZD/USD', 'USD/CAD', 'USD/CHF', 
    'USD/JPY', 'XAU/USD'
))

if symbol:
    with sync_playwright() as playwright:
        ua = get_random_user_agent()
        chromium = playwright.chromium # or "firefox" or "webkit".
        browser = chromium.launch()
        page = browser.new_page(extra_http_headers={
            'User-Agent': ua
        })
        page.goto("https://fxssi.com/tools/current-ratio?filter=AUDJPY", timeout=100000)


        page.locator(f'div.tool-button:text("{symbol}")').click()
        sleep(2)
        
        soup = BeautifulSoup(page.content(), 'lxml')

        buy = soup.select_one('#main-container > div.col-md-8 > div.tool-content.full-width.sharable-content > div.tools > div.row > div.tool-content.col-sm-8.sentiment-ratios > div > div.cur-rat-pairs > div.cur-rat-cur-pair.header.active > div.line.cur-rat-broker.broker-average > div > div > div.ratio > div.ratio-bar-left').text.strip()
        sell = soup.select_one('#main-container > div.col-md-8 > div.tool-content.full-width.sharable-content > div.tools > div.row > div.tool-content.col-sm-8.sentiment-ratios > div > div.cur-rat-pairs > div.cur-rat-cur-pair.header.active > div.line.cur-rat-broker.broker-average > div > div > div.ratio > div.ratio-bar-right').text.strip()
        buy = buy.replace('%', '')
        sell = sell.replace('%', '')
        
        # other actions...
        browser.close()
        
        col1, col2 = st.columns(2)
        
        if buy > sell:
            buy2 = buy
            sell2 = "-" + sell
        else:
            buy2 = '-' + buy
            sell2 = sell
            
        column1.metric('Buy', value = float(buy), delta = buy2)
        column1.metric('Sell', value = float(sell), delta = sell2)
        
symbol2 = column2.selectbox('Symbol to analyse', (
    'EURUSD', 'AUDUSD', 'AUDJPY', 'EURAUD', 'EURJPY', 
    'GBPJPY', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 
    'USDJPY', 'XAUUSD'
))

Interval.INTERVAL_1_MINUTE = "1m"
Interval.INTERVAL_5_MINUTES = "5m"
Interval.INTERVAL_15_MINUTES = "15m"
Interval.INTERVAL_30_MINUTES = "30m"
Interval.INTERVAL_1_HOUR = "1h"
Interval.INTERVAL_2_HOURS = "2h"
Interval.INTERVAL_4_HOURS = "4h"
Interval.INTERVAL_1_DAY = "1d"
Interval.INTERVAL_1_WEEK = "1W"
Interval.INTERVAL_1_MONTH = "1M"

time_frame = column2.radio('TimeFrame', (
    '1m', '5m', '15m', '30m', '1h',
    '2h','4h', '1d', '1W', '1M' 
), horizontal=True)

handler = TA_Handler(
    symbol= symbol2,
    exchange="FX_IDC",
    screener="forex",
    interval= time_frame,
    timeout=None
)

summary = handler.get_analysis().summary
df = pd.DataFrame(summary, index=[0])
column2.table(df)

