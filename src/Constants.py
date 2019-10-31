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
    'SP500'
]
STOCKS = [
    'Apple',
    'Microsoft',
    'Amazon',
    'Tesla',
    'Visa',
    'Hewlett Packard',
    'Aurora Cannabis',
    'Intel',
    'Nvidia',
    'AMD',
    'S&P500'
]
SEARCH_URL = 'https://www.google.com/search?q={}+stock+news&tbm=nws'
HISTORICAL_URL = 'https://www.reuters.com/search/news?sortBy=date&dateRange=all&blob={}'
REUTERS_ROOT = 'https://www.reuters.com{}'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "close",
    "Upgrade-Insecure-Requests": "1"
}
