# -*- coding: utf-8 -*-
from connection.model import Friends, Strangers
import numpy

print 'test'
friends_similarity = [friend.similarity for friend in Friends.select(Friends.similarity)]
print 'friends similarity'
print numpy.median(numpy.array(friends_similarity))

strangers_similarity = [stranger.similarity for stranger in Strangers.select(Strangers.similarity)]
print 'strangers similarity'
print numpy.median(numpy.array(strangers_similarity))
