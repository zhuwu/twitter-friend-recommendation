# -*- coding: utf-8 -*-
from peewee import *
from connection.model import Tweets, Strangers, psql_db
from settings import PAGE_SIZE
import helper
import multiprocessing

def process_strangers(strangers):
    for stranger in strangers:
        user_id1 = stranger.user_id1
        user_id2 = stranger.user_id2
        # print '===================='
        # print 'user_id1:', user_id1
        # print 'user_id2:', user_id2
        tweet_list1 = list(Tweets.select().where(Tweets.user_id == user_id1).limit(1))
        tweet_list2 = list(Tweets.select().where(Tweets.user_id == user_id2).limit(1))
        if len(tweet_list1) > 0 and len(tweet_list2) > 0:
            tweet1 = tweet_list1[0]
            tweet2 = tweet_list2[0]
            stranger.similarity = helper.computeSimilarity(tweet1, tweet2)
            stranger.save()
        elif len(tweet_list1) == 0:
            print user_id1, 'Empty'
        else:
            print user_id2, 'Empty'

process_count = 8

def fetch_strangers(modulus):
    sql = "SELECT * FROM strangers WHERE similarity is null AND id > 0 AND id %% {process} = {mod} order by id LIMIT {page} ".format(
        process=process_count,
        mod=modulus,
        page=PAGE_SIZE,
    )

    psql_db.connect()
    offset = 0
    strangers = list(Strangers.raw(sql))
    while len(strangers):
        process_strangers(strangers)
        last_stranger = strangers[-1]
        offset = last_stranger.id

        sql = "SELECT * FROM strangers WHERE similarity is null AND id > {offset} AND id %% {process} = {mod} order by id LIMIT {page} ".format(
            offset=offset,
            process=process_count,
            mod=modulus,
            page=PAGE_SIZE,
        )
        strangers = list(Strangers.raw(sql))
    psql_db.close()

if __name__ == '__main__':
    total_strangers = Strangers.select().count()
    print total_strangers

    processes = []
    for modulus in xrange(process_count):
        p = multiprocessing.Process(target=fetch_strangers, args=(modulus,))
        p.start()
        processes.append(p)

    while len(processes) > 0:
        processes = filter(lambda p: p.is_alive(), processes)
        for p in processes:
            p.join(1)
