from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
AN = SentimentIntensityAnalyzer()

def fetch_headlines(ticker: str):
    # placeholder until i find a news API i can implement in here
    return [
        {"title": f"{ticker} is doing great!", "link": "http://example.com/1"},
        {"title": f"Analysts are worried about {ticker}", "link": "http://example.com/2"},
        {"title": f"{ticker} hits new highs", "link": "http://example.com/3"},
    ]

def avg_vader_sent(headlines):
    if not headlines:
        return 0.0
    scores = [AN.polarity_scores(h["title"])["compound"] for h in headlines]
    return sum(scores) / len(scores)