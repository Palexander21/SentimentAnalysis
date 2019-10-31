from tabulate import tabulate
import numpy as np


class Symbol:
    def __init__(self, symbol, name):
        self.symbol = symbol
        self.name = name
        self.urls = []
        self.content = []
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
