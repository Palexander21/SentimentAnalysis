from tabulate import tabulate
import numpy as np
import pandas as pd
try:
    import pandas_datareader.data as web
    import matplotlib.pyplot as plt
except ImportError:
    print('[ERROR] Failed to load datareader')


class Symbol:
    def __init__(self, symbol, name):
        self.symbol = symbol
        self.name = name
        self.urls = []
        self.prices = pd.DataFrame()
        self.sentiments = {}

    def update_sentiment(self, date, score):
        if self.sentiments.get(date):
            self.sentiments.get(date).append(score)
        else:
            self.sentiments[date] = [score]

    def report(self):
        headers = ['Date', 'Symbol', 'Mean', 'Median', 'StdDev']
        data = []
        for k, v in self.sentiments.items():
            data.append([k, self.symbol, np.mean(v), np.median(v), np.std(v)])
        print(tabulate(data, headers=headers))

    def to_dict(self):
        return {
            'Symbol': self.symbol,
            'Dates': self.sentiments.keys(),
            'Sentiments': self.sentiments.values(),
        }

    def get_prices(self, start, end):
        self.prices = web.DataReader(self.symbol, 'yahoo', start, end)

    def to_df(self):
        data = []
        for k in self.sentiments.keys():
            sent = self.sentiments.get(k)
            data.append({
                'Date': k,
                'Symbol': self.symbol,
                'Sentiments': sent,
            })
        df = pd.DataFrame(data).set_index(['Date'])
        df = df.Sentiments.apply(lambda x: pd.Series(x))
        df['Mean'] = df.mean(axis=1)
        df['Median'] = df.median(axis=1)
        df['StdDev'] = df.std(axis=1)
        return df

    def plot(self):
        df = self.to_df()
        norm = (self.prices - self.prices.mean()) / (self.prices.max() - self.prices.min())
        n = norm.join(df['Median']).fillna(method='backfill')
        fig, ax = plt.subplots()
        ax.plot(n.index, n['Median'], label='Sentiment')
        ax.plot(n.index, n['Adj Close'], label='Price')
        ax.legend()
        plt.xticks(rotation='vertical')
        plt.show()

    def to_csv(self):
        self.to_df().to_csv('data/data.csv')
