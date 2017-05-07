# -*- coding: utf-8 -*-
import re
from collections import defaultdict
from settings import INPUT_TWEETS_FILE, IGNORED_TWEETS, TWEETS_BATCH_SIZE
from connection.model import Tweets, psql_db


def read_tweet_lines(max_line=None):
    all_user_tweets = defaultdict(list)

    with open(INPUT_TWEETS_FILE, 'r') as tweet_file:
        all_lines = tweet_file.readlines()  # load all tweets into memory

        current_user = ''
        for line in all_lines:
            if re.search(r'^[U]\s+', line):  # User line
                username = line.split('/')[-1].rstrip().lower()
                if not username:
                    continue
                current_user = username
            elif re.search(r'^[W]\s+', line):  # Tweet line
                if not current_user:
                    # warning here
                    print 'current_user empty when reading tweet...'
                    continue
                tweet = re.sub(r'^W\s+|\s+$', '', line)
                if tweet not in IGNORED_TWEETS:
                    user_tweets = all_user_tweets[current_user]
                    user_tweets.append(tweet)
            else:
                current_user = ''


    loop_count = 0
    tweets_records = []
    for username, tweet_list in all_user_tweets.items():
        if loop_count >= TWEETS_BATCH_SIZE:
            with psql_db.atomic():
                Tweets.insert_many(tweets_records).execute()
                tweets_records = []
                loop_count = 0
        record = {
            'username': username,
            'original_tweets': '\n'.join(tweet_list),
        }
        tweets_records.append(record)
        loop_count += 1
