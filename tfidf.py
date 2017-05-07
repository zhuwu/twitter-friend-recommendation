# -*- coding: utf-8 -*-
from peewee import *
from connection.model import Tweets, psql_db
import math
from settings import PAGE_SIZE
import time
import multiprocessing

# import logging
# logger = logging.getLogger('peewee')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())


def build_document_reverse_index():
    manager = multiprocessing.Manager()
    hash_tag_reverse_index = manager.dict()
    tweet_word_reverse_index = manager.dict()

    for tweet in Tweets.select().order_by(Tweets.id):
        for hash_tag, count in tweet.hash_tags.iteritems():
            count = hash_tag_reverse_index.get(hash_tag, 0)
            hash_tag_reverse_index[hash_tag] = count + 1
        for word, count in tweet.tweet_text.iteritems():
            count = tweet_word_reverse_index.get(word, 0)
            tweet_word_reverse_index[word] = count + 1

    print 'ht_index', hash_tag_reverse_index
    print 'tw_index', tweet_word_reverse_index
    return hash_tag_reverse_index, tweet_word_reverse_index


# def get_hash_tag_document_frequency(hash_tag):
#     ht = Tweets.hash_tags
#     # psql_db.connect()
#     frequency = Tweets.select().where(ht.contains(hash_tag)).count()
#     # psql_db.close()
#     return frequency
#
#
# def get_word_document_frequency(word):
#     tt = Tweets.tweet_text
#     # psql_db.connect()
#     frequency = Tweets.select().where(tt.contains(word)).count()
#     # psql_db.close()
#     return frequency


def get_tf_idf(term_frequency, total_documents, document_frequency):
    return (1 + math.log(term_frequency)) * (math.log((1.0 * total_documents) / document_frequency))


def process_tweets(tweets, ht_index, tw_index):
    for tweet in tweets:
        if tweet.hash_tags_tfidf == {} and tweet.tweet_text_tfidf == {}:
            tweet_hash_tags = tweet.hash_tags
            tweet_text = tweet.tweet_text

            # Compute TF-IDF for hash tags
            tag_tf_idfs = {}
            tag_sum_square_tf_idf = 0
            for tag in tweet_hash_tags:
                tag_frequency = tweet_hash_tags[tag]
                # Get document frequency from dictionary first.
                # Get from DB and store in dictionary when it cannot be found from dictionary.
                document_frequency = ht_index.get(tag)
                tf_idf = get_tf_idf(tag_frequency, total_documents, document_frequency)
                if (tf_idf > 0):
                    tag_tf_idfs[tag] = tf_idf
                    tag_sum_square_tf_idf = tag_sum_square_tf_idf + tf_idf * tf_idf

            # Normalize TF-IDF for hash tags
            tag_sum_sqrt_tf_idf = math.sqrt(tag_sum_square_tf_idf)
            for tag in tag_tf_idfs:
                tag_tf_idfs[tag] = tag_tf_idfs[tag] / tag_sum_sqrt_tf_idf

            # Comput TF-IDF for words
            word_tf_idfs = {}
            word_sum_square_tf_idf = 0
            for word in tweet_text:
                word_frequency = tweet_text[word]
                # Get document frequency from dictionary first.
                # Get from DB and store in dictionary when it cannot be found from dictionary.
                document_frequency = tw_index.get(word)
                tf_idf = get_tf_idf(word_frequency, total_documents, document_frequency)
                if (tf_idf > 0):
                    word_tf_idfs[word] = tf_idf
                    word_sum_square_tf_idf = word_sum_square_tf_idf + tf_idf * tf_idf

            # Normalize TF-IDF for words
            word_sum_sqrt_tf_idf = math.sqrt(word_sum_square_tf_idf)
            for word in word_tf_idfs:
                word_tf_idfs[word] = word_tf_idfs[word] / word_sum_sqrt_tf_idf

            tweet.hash_tags_tfidf = tag_tf_idfs
            tweet.tweet_text_tfidf = word_tf_idfs

            # psql_db.connect()
            tweet.save()
            # psql_db.close()


process_count = 8


def fetch_tweets(modulus, ht_index, tw_index):
    sql = "SELECT * FROM tweets WHERE tweet_text_tfidf = '{{}}' AND id > 0 AND id %% {process} = {mod} order by id LIMIT {page} ".format(
        process=process_count,
        mod=modulus,
        page=PAGE_SIZE,
    )

    psql_db.connect()
    offset = 0
    tweets = list(Tweets.raw(sql))
    while len(tweets):
        process_tweets(tweets, ht_index, tw_index)
        last_tweet = tweets[-1]
        offset = last_tweet.id

        sql = "SELECT * FROM tweets WHERE tweet_text_tfidf = '{{}}' AND id > {offset} AND id %% {process} = {mod} order by id LIMIT {page} ".format(
            offset=offset,
            process=process_count,
            mod=modulus,
            page=PAGE_SIZE,
        )
        tweets = list(Tweets.raw(sql))
    psql_db.close()


if __name__ == '__main__':
    start = time.time()
    total_documents = Tweets.select().count()
    print total_documents

    hash_tag_reverse_index, tweet_word_reverse_index = build_document_reverse_index()

    processes = []
    for modulus in xrange(process_count):
        p = multiprocessing.Process(target=fetch_tweets, args=(
            modulus, hash_tag_reverse_index, tweet_word_reverse_index))
        p.start()
        processes.append(p)

    while len(processes) > 0:
        processes = filter(lambda p: p.is_alive(), processes)
        for p in processes:
            p.join(1)

    end = time.time()

    print 'Time: ', end - start
    print 'Average:', total_documents / (end - start)
