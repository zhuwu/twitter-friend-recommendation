# twitter-friend-recommendation

This project recommend a twitter user to another according to their tweets content similarity.

---

Model:

tweet:
```
userid, username, hash_tags, tweet_text, hash_tags_tfidf, tweet_text_tfidf
```

friends
```
userid1, userid2, similarity  (1 < 2)
```

generated_similarity
```
userid1, userid2, similarity  (1 < 2)
```

---

To Run Test:
```
>>> python analyze.py | less
```

