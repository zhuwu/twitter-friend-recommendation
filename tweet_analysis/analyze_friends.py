# -*- coding: utf-8 -*-
import csv
from peewee import *
from connection.model import Friends, psql_db
from settings import TWITTER_FOLLOWER_FILE


def find_friends():
    friends_list = []
    max_count = 100000

    follower_set = set()
    pair_count = 0
    with open(TWITTER_FOLLOWER_FILE, 'r') as follower_file:
        csv_reader = csv.DictReader(follower_file, delimiter='\t', fieldnames=('user_id', 'follower_id'))
        for row in csv_reader:
            relation = (row['user_id'], row['follower_id'])
            reverse_relation = (row['follower_id'], row['user_id'])
            if reverse_relation in follower_set:
                # print 'Found friend: {id1}-{id2}'.format(id1=row['user_id'], id2=row['follower_id'])
                try:
                    follower_set.remove(reverse_relation)
                except KeyError:
                    print 'KeyError friend: {id1}-{id2}'.format(id1=row['user_id'], id2=row['follower_id'])

                # Write to DB.
                friend = {
                    'user_id1': min(*relation),
                    'user_id2': max(*relation)
                }
                friends_list.append(friend)
                pair_count += 1
                if len(friends_list) >= max_count:
                    print 'Insert friends into db: ', len(friends_list)
                    with psql_db.atomic():
                        Friends.insert_many(friends_list).execute()
                    friends_list = []

            else:
                follower_set.add(relation)
        if friends_list:
            with psql_db.atomic():
                Friends.insert_many(friends_list).execute()
            friends_list = []

    print 'Friend Pairs found: ', pair_count
