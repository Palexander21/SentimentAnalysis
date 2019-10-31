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
