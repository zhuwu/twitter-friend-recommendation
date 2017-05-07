# -*- coding: utf-8 -*-
from peewee import *
from connection.model import Friends, Tweets
from settings import FRIENDS_PAGE_SIZE, FRIENDS_BATCH_REMOVE_SIZE


def cleanup():
    valid_users = set()
    total_deleted = 0

    for user in Tweets.select().where(~(Tweets.user_id >> None)).order_by(Tweets.user_id):
        valid_users.add(user.user_id)

    invalid_friend_ids = []
    last_stop_id = 0

    while True:
        batch_friends = Friends.select().where(Friends.id > last_stop_id).order_by(Friends.id).limit(FRIENDS_PAGE_SIZE)
        if not batch_friends.count():
            break

        for friend in batch_friends:
            if (friend.user_id1 not in valid_users) or (friend.user_id2 not in valid_users):
                invalid_friend_ids.append(friend.id)
                if len(invalid_friend_ids) >= FRIENDS_BATCH_REMOVE_SIZE:
                    print 'Deleting friends, count: ', len(invalid_friend_ids)
                    total_deleted += len(invalid_friend_ids)
                    query = Friends.delete().where(Friends.id << invalid_friend_ids)
                    query.execute()
                    invalid_friend_ids = []

            last_stop_id = friend.id

    if invalid_friend_ids:
        print 'Deleting friends, count: ', len(invalid_friend_ids)
        total_deleted += len(invalid_friend_ids)
        query = Friends.delete().where(Friends.id << invalid_friend_ids)
        query.execute()
        invalid_friend_ids = []

    print 'Last Stop ID: ', last_stop_id
    print 'Total deleted count: ', total_deleted

if __name__ == '__main__':
    cleanup()
