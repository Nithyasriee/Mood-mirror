from textblob import TextBlob

def analyze_posts(post):
    # basic sentiment using TextBlob
    blob = TextBlob(post)
    polarity = blob.sentiment.polarity  # -1 .. +1

    # map to mood labels (tuned thresholds)
    if polarity > 0.5:
        mood = "Happy"
    elif polarity > 0.1:
        mood = "Calm"
    elif polarity > -0.1:
        mood = "Neutral"
    elif polarity > -0.5:
        mood = "Sad"
    else:
        mood = "Anxious"

    return mood, polarity
