from __future__ import annotations

from textblob import TextBlob


def analyze_sentiment(text: str) -> str:
    """
    Analyze sentiment for a piece of text using TextBlob polarity.

    Returns one of: "positive", "neutral", "negative"

    Rules:
    - polarity > 0.1  -> positive
    - polarity < -0.1 -> negative
    - otherwise       -> neutral
    """

    polarity = float(TextBlob(text).sentiment.polarity)

    if polarity > 0.1:
        return "positive"
    if polarity < -0.1:
        return "negative"
    return "neutral"

