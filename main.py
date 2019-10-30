from selenium import webdriver
from bs4 import BeautifulSoup as bs
import requests as req
import html5lib
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
import time

from Symbol import Symbol

SYMBOLS = [
   'AAPL',
   'MSFT',
   'AMZN',
   'TSLA',
   'V',
   'HPQ',
   'ACB',
   'INTC',
   'NVDA',
   'AMD',
   'MCD',
]
ROOT_URL = 'https://www.google.com/search?q={}+stock+news&tbm=nws'


def get_urls(driver, symbols):
    for symbol in symbols.keys():
        driver.get(ROOT_URL.format(symbol))
        driver.implicitly_wait(100)

        content = bs(driver.page_source, 'html5lib')
        links = content.find_all('div', class_='dbsr')
        for l in links:
            a_tag = l.find_all('a', href=True)
            for href in a_tag:
                symbols[symbol].urls.append(href['href'])


def get_sentiment(symbols):
    for symbol in symbols.keys():
        for url_ in symbols[symbol].urls:
            time.sleep(1)
            response = req.get(url_)
            content = bs(response.content, 'html5lib')
            p_tag = content.find_all('p')
            paragraph = ""
            for sentence in p_tag:
                paragraph += sentence.text
            date = datetime.now().strftime('%Y-%m-%d')
            sentiment = SentimentIntensityAnalyzer().polarity_scores(paragraph)['compound']
            symbols[symbol].update_sentiment(date, sentiment)
            print('{}: {} - {} [{}]'.format(date, symbol, sentiment, url_))


if __name__ == '__main__':
    driver = webdriver.Chrome()
    symbols = {}
    for s in SYMBOLS:
        symbols[s] = Symbol(s)
    get_urls(driver, symbols)
    get_sentiment(symbols)
    driver.close()
