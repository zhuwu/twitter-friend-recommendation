# -*- coding: utf-8 -*-
import csv
import multiprocessing
from connection.model import Tweets, psql_db
from settings import NUMBER_TO_SCREEN_FILE, TWEETS_BATCH_SIZE

process_count = 16


def read_user_names():
    all_lines = ''
    with open(NUMBER_TO_SCREEN_FILE, 'r') as user_file:
        all_lines = user_file.readlines()

    username_to_ids = {}
    csv_reader = csv.DictReader(all_lines, delimiter=' ', fieldnames=('user_id', 'username'))
    for row in csv_reader:
        username_to_ids[row['username'].lower().strip()] = row['user_id']

    return username_to_ids


def process_tweets(tweets, username_to_ids):
    for tweet in tweets:
        user_id = username_to_ids.get(tweet.username, None)
        if user_id:
            tweet.user_id = user_id
            tweet.save()


def fetch_tweets(modulus, username_to_ids):
    sql = "SELECT * FROM tweets WHERE user_id is null AND id > 0  AND id %% {process} = {mod} order by id LIMIT {page} ".format(
        process=process_count,
        mod=modulus,
        page=TWEETS_BATCH_SIZE,
    )

    psql_db.connect()
    offset = 0
    tweets = list(Tweets.raw(sql))
    while len(tweets):
        process_tweets(tweets, username_to_ids)
        last_tweet = tweets[-1]
        offset = last_tweet.id

        sql = "SELECT * FROM tweets WHERE user_id is null AND id > {offset} AND id %% {process} = {mod} order by id LIMIT {page} ".format(
            offset=offset,
            process=process_count,
            mod=modulus,
            page=TWEETS_BATCH_SIZE,
        )
        tweets = list(Tweets.raw(sql))
    psql_db.close()


def update_user_ids():
    username_to_ids = read_user_names()
    print 'Total user_id found: ', len(username_to_ids)

    processes = []
    for modulus in xrange(process_count):
        p = multiprocessing.Process(target=fetch_tweets, args=(modulus, username_to_ids, ))
        p.start()
        processes.append(p)

    while len(processes) > 0:
        processes = filter(lambda p: p.is_alive(), processes)
        for p in processes:
            p.join(1)

if __name__ == '__main__':
    update_user_ids()
