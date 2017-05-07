# -*- coding: utf-8 -*-
from settings import HASH_TAG_MULTIPLIER, TEXT_MULTIPLIER

def computeSimilarity(tweet1, tweet2):
    return HASH_TAG_MULTIPLIER * computeHashTagSimilarity(tweet1.hash_tags_tfidf, tweet2.hash_tags_tfidf) + \
            TEXT_MULTIPLIER * computeTextSimilarity(tweet1.tweet_text_tfidf, tweet2.tweet_text_tfidf)

def computeHashTagSimilarity(hash_tags_tfidf1, hash_tags_tfidf2):
    result = 0
    for key, weight1 in hash_tags_tfidf1.iteritems():
        weight2 = hash_tags_tfidf2.get(key, 0)
        result = result + weight1 * weight2
    return result

def computeTextSimilarity(tweet_text_tfidf1, tweet_text_tfidf2):
    result = 0
    for key, weight1 in tweet_text_tfidf1.iteritems():
        weight2 = tweet_text_tfidf2.get(key, 0)
        result = result + weight1 * weight2
    return result