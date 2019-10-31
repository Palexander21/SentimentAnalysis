from selenium import webdriver
from bs4 import BeautifulSoup as bs
import requests as req
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import timedelta, date
import time
import argparse
import numpy as np
from tabulate import tabulate

from src.Symbol import Symbol
from src.Constants import *


def get_urls(driver, symbols):
    for symbol in symbols.keys():
        driver.get(SEARCH_URL.format(symbol))
        driver.implicitly_wait(100)

        content = bs(driver.page_source, 'html5lib')
        links = content.find_all('div', class_='dbsr')
        for l in links:
            a_tag = l.find_all('a', href=True)
            for href in a_tag:
                symbols[symbol].urls.append(href['href'])


def get_content(driver, symbols):
    for symbol in symbols.keys():
        for url_ in symbols[symbol].urls:
            time.sleep(1)
            response = req.get(url_, headers=HEADERS)
            content = bs(response.content, 'html5lib')
            p_tag = content.find_all('p')
            paragraph = ""
            for sentence in p_tag:
                paragraph += sentence.text
            today = date.today()
            sentiment = SentimentIntensityAnalyzer().polarity_scores(paragraph)['compound']
            symbols[symbol].update_sentiment(today, sentiment)
            print('{}: {} - {} [{}]'.format(today, symbol, sentiment, url_))


def get_historical(driver, symbols, args):
    year = timedelta(days=365)
    month = timedelta(days=30)
    today = date.today()
    if args.date_type == 'year':
        delta = today - timedelta(days=(args.date_val * year))
    elif args.date_type == 'month':
        delta = today - timedelta(days=(args.date_val * month))
    else:
        delta = today - timedelta(weeks=args.date_val)

    response = req.get(HISTORICAL_URL, headers=HEADERS)
    content = bs(response, 'html5lib')



def report(symbols):
    headers = ['Date', 'Symbol', 'Mean', 'Median', 'StdDev']
    data = []
    for _, v in symbols.items():
        for k in v.sentiments.keys():
            sent = v.sentiments.get(k)
            data.append([k, v.symbol, np.mean(sent), np.median(sent), np.std(sent)])
    print(tabulate(data, headers=headers))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--historical', action='store_true')
    parser.add_argument('--date-type', action='store', dest='date_type', help="week, month, year, default=week", default='week', type=str)
    parser.add_argument('--date-value', action='store', dest='date_val', help="default=1", default=1, type=int)
    args = parser.parse_args()

    driver = webdriver.Chrome()
    symbols = {}
    for s, n in zip(SYMBOLS, STOCKS):
        symbols[s] = Symbol(s, n)
    if args.historical:
        get_historical(driver, symbols, args)
    else:
        get_urls(driver, symbols)
        get_content(driver, symbols)
    driver.close()
    report(symbols)

