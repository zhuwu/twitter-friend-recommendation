# -*- coding: utf-8 -*-
from peewee import *
from connection.model import Tweets, Friends
import helper


def check():
    tweets = Tweets.select().order_by(Tweets.user_id)
    total_similarity = 0
    pair_count = 0
    for tweet in tweets:
        print 'User: ', tweet.username
        other_tweets = Tweets.select().where(Tweets.user_id > tweet.user_id).order_by(Tweets.user_id)

        for other in other_tweets:
            friends = Friends.select().where(
                ((Friends.user_id1 == tweet.user_id) & (Friends.user_id2 == other.user_id))
                |
                ((Friends.user_id2 == tweet.user_id) & (Friends.user_id1 == other.user_id))
            )
            if friends.count() > 0:
                print 'Friens, ignore.'
                continue

            similarity = helper.computeSimilarity(tweet, other)
            print 'Similarity: {user}-{other}: {simi}'.format(user=tweet.username,
                                                              other=other.username,
                                                              simi=similarity)
            total_similarity += similarity
            pair_count += 1

    print 'Pair count: ', pair_count
    print 'Average: ', total_similarity / pair_count


if __name__ == '__main__':
    check()
