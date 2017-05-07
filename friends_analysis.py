# -*- coding: utf-8 -*-
from connection.model import Friends, Strangers


step = 0.001
result = [None]*3000
for i in xrange(0, 3000):
  print i
  arr = [None]*3
  arr[0] = str((i + 1) * step)
  arr[1] = Friends.select().where((Friends.similarity >= i * step) & (Friends.similarity < (i + 1) * step)).count()
  arr[2] = Strangers.select().where((Strangers.similarity >= i * step) & (Strangers.similarity < (i + 1) * step)).count()
  result[i] = arr

print result