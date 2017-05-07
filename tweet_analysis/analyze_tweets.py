# -*- coding: utf-8 -*-
import multiprocessing
import re
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from connection.model import Tweets, psql_db
from settings import TWEETS_BATCH_SIZE

process_count = 16
tweet_stopwords = stopwords.words('english')
stemmer = SnowballStemmer('english')


def analyze_user_tweets(current_tweet):
    user_hash_tags = defaultdict(int)
    user_tweet_words = defaultdict(int)

    tweet_hash_tags = re.findall(r'#[^#\s]+', current_tweet)
    for tag in tweet_hash_tags:
        user_hash_tags[tag] += 1

    # Replace Non-Ascii chars with *

    ascii_tweet = ''.join([i if ord(i) < 128 else '' for i in current_tweet])
    tweet_words = re.split(r'[\s,"\-]+', ascii_tweet)
    # Remove stop words
    punct_removed_words = [re.sub(r'(^[^@A-Za-z0-9_\']+)|(\W+$)', '', word) for word in tweet_words]
    # print 'punct-removed words', punct_removed_words
    filtered_words = [word for word in punct_removed_words if word not in tweet_stopwords]
    # print 'After stopwords removed:', filtered_words

    stemmed_words = [stemmer.stem(word) for word in filtered_words]
    # print 'Stemmed words: ', stemmed_words
    for word in stemmed_words:
        if not word:
            continue
        user_tweet_words[word] += 1
    return dict(user_hash_tags), dict(user_tweet_words)


def process_tweets(tweets):
    for tweet in tweets:
        tweet.hash_tags, tweet.tweet_text = analyze_user_tweets(tweet.original_tweets)
        tweet.save()


def fetch_tweets(modulus):
    sql = "SELECT * FROM tweets WHERE tweet_text = '{{}}' AND id > 0  AND id %% {process} = {mod} order by id LIMIT {page} ".format(
        process=process_count,
        mod=modulus,
        page=TWEETS_BATCH_SIZE,
    )

    psql_db.connect()
    offset = 0
    tweets = list(Tweets.raw(sql))
    while len(tweets):
        process_tweets(tweets)
        last_tweet = tweets[-1]
        offset = last_tweet.id

        sql = "SELECT * FROM tweets WHERE tweet_text = '{{}}' AND id > {offset} AND id %% {process} = {mod} order by id LIMIT {page} ".format(
            offset=offset,
            process=process_count,
            mod=modulus,
            page=TWEETS_BATCH_SIZE,
        )
        tweets = list(Tweets.raw(sql))
    psql_db.close()


def count_tweet_hashtag_word():
    processes = []
    for modulus in xrange(process_count):
        p = multiprocessing.Process(target=fetch_tweets, args=(modulus,))
        p.start()
        processes.append(p)

    while len(processes) > 0:
        processes = filter(lambda p: p.is_alive(), processes)
        for p in processes:
            p.join(1)
