twitter-mood
============
[![Build Status](https://travis-ci.org/jmhossler/twitter-mood.svg?branch=master)](https://travis-ci.org/jmhossler/twitter-mood)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

twitter-mood is a python tool meant to simplify sentiment analysis of twitter queries.


Description
-----------

Using textblob and python-twitter, twitter-mood aggregates sentiment analysis of
tweets from twitter matching a specific query.

Requirements
------------

Other python requirements will be installed automatically with a pip install.
Outside of that, the system requirements are very simple: \>python v3.4

Installation
------------

twitter-mood is on pypi! You can install twitter-mood with a simple pip command:
```bash
pip install twitter-mood
```

Usage
-----

### Intialize Mood Gatherer
```python
from twitter_mood import TwitterMoodGatherer
import twitter

consumer_key='consumer_key'
consumer_secret='consumer_secret'
access_token_key='access_token'
access_token_secret='access_token_secret'


twitter_api = twitter.Api(consumer_secret=consumer_secret,
                          api_token_key=api_token_key,
                          api_token_secret=api_token_secret,
                          consumer_key=consumer_key)

twitter_mood_tool = TwitterMoodGatherer(twitter_api, query)
```

### Retrieve 100 tweets matching query and get average sentiment
```python
twitter_mood_tool.gather_tweets()

mood = twitter_mood_tool.get_mood()  # return Sentiment Aggregate
polartiy = mood.polarity
subjectivity = mood.subjectivity
```

### Get individual analysis of tweets
```python
twitter_mood_tool.gather_tweets()

moods = twitter_mood_tool.get_moods()

for mood in moods:
  subjectivity = mood.sentiment.subjectivity
  polarity = mood.sentiment.polarity
  created_at = mood.created_at
  tweet_url = mood.url
```

### Get mood analysis of stream of tweets
```python
twitter_mood_tool.gather_tweet_stream()

for mood in twitter_mood_tool.get_mood_stream():
  subjectivity = mood.sentiment.subjectivity
  polarity = mood.sentiment.polarity
  created_at = mood.created_at
  tweet_url = mood.url
```

Development
-----------

### Testing
```
pip install pytest
pip install pytest-cov
pip install -r requirements.txt
pip install .
pytest tests
```

Note
----

This project has been set up using PyScaffold 3.0.1. For details and usage
information on PyScaffold see http://pyscaffold.org/.
