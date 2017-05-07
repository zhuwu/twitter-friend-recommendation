# -*- coding: utf-8 -*-
from peewee import *
from collections import defaultdict
from connection.model import Tweets, Friends, Strangers, psql_db
import itertools

USER_LIMIT = 300000
STRANGER_LIMIT = 3000000
appear_limit = 60

DB_BATCH_SIZE = 5000


def generate_stranger_pairs():
    tweets = Tweets.select(Tweets.user_id).limit(USER_LIMIT)
    users = [tweet.user_id for tweet in tweets]

    friends = Friends.select(Friends.user_id1, Friends.user_id2).where(
        Friends.user_id1 << users & Friends.user_id2 << users)
    user_friends = set((friend.user_id1, friend.user_id2) for friend in friends)

    count = 0
    user_appearance = defaultdict(int)

    loop_count = 0
    data_batch = []
    for user1, user2 in itertools.combinations(users, 2):
        if loop_count >= DB_BATCH_SIZE:
            with psql_db.atomic():
                Strangers.insert_many(data_batch).execute()
            loop_count = 0
            data_batch = []

        if count >= STRANGER_LIMIT:
            break
        if user_appearance[user1] > appear_limit or user_appearance[user2] > appear_limit:
            continue
        if (user1, user2) in user_friends or (user2, user1) in user_friends:
            pass
            # print 'Found friend %s and %s' % (user1, user2)
        else:
            # print ' ===> Found stranger %s and %s' % (user1, user2)
            stranger = {
                'user_id1': user1,
                'user_id2': user2,
            }
            data_batch.append(stranger)

            user_appearance[user1] += 1
            user_appearance[user2] += 1
            count += 1
            loop_count += 1
    if data_batch:
        with psql_db.atomic():
            Strangers.insert_many(data_batch).execute()
        loop_count = 0
        data_batch = []

if __name__ == '__main__':
    generate_stranger_pairs()
