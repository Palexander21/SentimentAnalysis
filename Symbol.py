
class Symbol:
    def __init__(self, name):
        self.name = name
        self.urls = []
        self.content = []
        self.sentiments = {}

    def update_sentiment(self, date, score):
        self.sentiments[date] = score
