from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as Soup
import requests as req
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime, timedelta, date
import time
import argparse
import numpy as np
import pandas as pd
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Failed to load matplotlib. Graphs will not be rendered")
from tabulate import tabulate
import sys

from Symbol import Symbol
from Constants import *


def get_urls(driver, symbols):
    for symbol in symbols.keys():
        driver.get(SEARCH_URL.format(symbol))
        driver.implicitly_wait(100)

        content = Soup(driver.page_source, 'html5lib')
        links = content.find_all('div', class_='dbsr')
        for l in links:
            a_tag = l.find_all('a', href=True)
            for href in a_tag:
                symbols[symbol].urls.append(href['href'])


def get_sentiments(url_, obj, timestamp):
    response = req.get(url_, headers=HEADERS)
    content = Soup(response.content, 'html5lib')
    p_tag = content.find_all('p')
    paragraph = ""
    for sentence in p_tag:
        paragraph += sentence.text
    sentiment = SentimentIntensityAnalyzer().polarity_scores(paragraph)['compound']
    obj.update_sentiment(timestamp, sentiment)
    print('{}: {} {} [{}]'.format(timestamp, obj.symbol, url_, sentiment))


def get_content(driver, symbols):
    for symbol in symbols.keys():
        for url_ in symbols[symbol].urls:
            time.sleep(1)
            today = date.today()
            get_sentiments(url_, symbols[symbol], today)


def get_historical(driver, args):
    year = timedelta(days=365)
    month = timedelta(days=30)
    today = date.today()
    if args.date_type == 'year':
        delta = today - timedelta(days=(args.date_val * year))
    elif args.date_type == 'month':
        delta = today - timedelta(days=(args.date_val * month))
    else:
        delta = today - timedelta(weeks=args.date_val)

    last_date = date.today()
    links = []
    dates = []
    driver.get(HISTORICAL_URL.format(args.name))
    driver.implicitly_wait(1000)
    while last_date >= delta:
        html = Soup(driver.page_source, 'html5lib')
        links = html.select('h3 a', href=True)
        dates = html.find_all('h5', class_='search-result-timestamp')
        tmp_date = dates[-1].text.split()[0:3]
        tmp_date = ' '.join(tmp_date)
        last_date = datetime.strptime(tmp_date, '%B %d, %Y').date()
        driver.find_element_by_css_selector('.search-result-more-txt').click()
    stock = Symbol(args.symbol, args.name)

    for url_, d in zip(links, dates):
        article_list = d.text.split()[0:3]
        article_str = ' '.join(article_list)
        article_date = datetime.strptime(article_str, '%B %d, %Y').date()
        if article_date < delta:
            break
        else:
            time.sleep(1)
            get_sentiments(REUTERS_ROOT.format(url_['href']), stock, article_date)
    stock.report()


def report(symbols):
    headers = ['Date', 'Symbol', 'Mean', 'Median', 'StdDev']
    data = []
    for _, v in symbols.items():
        for k in v.sentiments.keys():
            sent = v.sentiments.get(k)
            data.append([k, v.symbol, np.mean(sent), np.median(sent), np.std(sent)])
    print(tabulate(data, headers=headers))


def to_dataframe(symbols):
    data = []
    for _, v in symbols.items():
        for k in v.sentiments.keys():
            sent = v.sentiments.get(k)
            data.append({
                'Date': k,
                'Symbol': v.symbol,
                'Sentiments': sent,
            })

    df = pd.DataFrame(data).set_index(['Symbol', 'Date'])
    df = df.Sentiments.apply(lambda x: pd.Series(x))
    df['Mean'] = df.mean(axis=1)
    df['Median'] = df.median(axis=1)
    df['StdDev'] = df.std(axis=1)
    return df


def plot(symbols):
    df = to_dataframe(symbols)
    df.plot(kind='bar', y=['Mean', 'Median', 'StdDev'])
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--historical', action='store_true', help='Search articles until specified date for a given stock')
    parser.add_argument('--date-type', action='store', dest='date_type', help="week, month, year, default=week", default='week', type=str)
    parser.add_argument('--date-value', action='store', dest='date_val', help="default=1", default=1, type=int)
    parser.add_argument('-n', '--name', action='store', dest='name', help='Full company name, not symbol', type=str)
    parser.add_argument('-s', '--symbol', action='store', dest='symbol', help='Stock symbol', type=str)
    parser.add_argument('-S', '--silent', action='store_true',  help='Run in headless mode')
    args = parser.parse_args()

    chrome_options = Options()
    if args.silent:
        chrome_options.add_argument('--headless')
    if sys.platform == 'linux':
        driver = webdriver.Chrome(executable_path='/mnt/c/Program Files/ChromeDriver/chromedriver.exe', chrome_options=chrome_options)
    else:
        driver = webdriver.Chrome(chrome_options=chrome_options)
    symbols = {}
    for s, n in zip(SYMBOLS, STOCKS):
        symbols[s] = Symbol(s, n)
    if args.historical:
        if args.name and args.symbol:
            get_historical(driver, args)
        else:
            print('[Error]: -n and -s are required when -H is enabled')
    else:
        get_urls(driver, symbols)
        get_content(driver, symbols)
        report(symbols)
    driver.close()
    if sys.platform == 'linux':
        plot(symbols)
    else:
        df = to_dataframe(symbols)
        df.to_csv('data/data_{}.csv'.format(date.today()))
