# -*- coding: utf-8 -*-

try:
    import simplejson as json
except ImportError:
    import json
from peewee import *
from playhouse.postgres_ext import *
from playhouse.pool import PooledPostgresqlExtDatabase

psql_db = PooledPostgresqlExtDatabase(
    'test_app',
    host='test.gtoweb.garenanow.com',
    user='test_user',
    password='test_user',
    max_connections=80,
    stale_timeout=3000,
    register_hstore=False)


class BaseModel(Model):
    """ A base model for using our PostgresqlDatabase """
    class Meta:
        database = psql_db


class Tweets(BaseModel):
    id = PrimaryKeyField()
    user_id = IntegerField(index=True)
    username = CharField(null=False, index=True)
    hash_tags = BinaryJSONField()
    tweet_text = BinaryJSONField()
    original_tweets = TextField()
    hash_tags_tfidf = JSONField()
    tweet_text_tfidf = JSONField()


class Friends(BaseModel):
    id = PrimaryKeyField()
    user_id1 = IntegerField(index=True)
    user_id2 = IntegerField(index=True)
    similarity = DoubleField()


class Strangers(BaseModel):
    id = PrimaryKeyField()
    user_id1 = IntegerField(index=True)
    user_id2 = IntegerField(index=True)
    similarity = DoubleField()


if __name__ == '__main__':
    for tweet in Tweets.select():
        print 'User:', tweet.username
        print 'tweet text: ', tweet.tweet_text

    for friend in Friends.select():
        print 'User ID:', friend.user_id1
        print 'Friend ID:', friend.user_id2
