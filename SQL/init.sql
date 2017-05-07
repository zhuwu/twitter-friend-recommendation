CREATE DATABASE cs5344;

CREATE TABLE tweets (
  id SERIAL PRIMARY KEY NOT NULL,
  user_id integer UNIQUE DEFAULT NULL,
  username varchar(32) UNIQUE,
  hash_tags jsonb DEFAULT '{}',
  tweet_text jsonb DEFAULT '{}',
  original_tweets text default NULL,
  hash_tags_tfidf jsonb DEFAULT '{}',
  tweet_text_tfidf jsonb DEFAULT '{}');

CREATE TABLE friends (
  id  SERIAL PRIMARY KEY NOT NULL,
  user_id1 integer DEFAULT NULL,
  user_id2 integer DEFAULT NULL,
  similarity double precision DEFAULT NULL);

CREATE INDEX friends_user_id1_idx ON friends (user_id1);
CREATE INDEX friends_user_id2_idx ON friends (user_id2);
CREATE INDEX friends_similarity_idx ON friends (similarity);
CREATE INDEX friends_pairs_idx ON friends(user_id1, user_id2);


CREATE TABLE strangers (
  id  SERIAL PRIMARY KEY NOT NULL,
  user_id1 integer DEFAULT NULL,
  user_id2 integer DEFAULT NULL,
  similarity double precision DEFAULT NULL);

CREATE INDEX strangers_user_id1_idx ON strangers (user_id1);
CREATE INDEX strangers_user_id2_idx ON strangers (user_id2);
CREATE INDEX strangers_similarity_idx ON strangers (similarity);
CREATE INDEX strangers_pairs_idx ON strangers(user_id1, user_id2);
