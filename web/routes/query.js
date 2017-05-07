var express = require('express');
var db = require('../model/db');
var util = require('../helper/util');

var router = express.Router();

router.get('/', function(req, res) {
  var username = req.query['username'].trim(),
      renderResult = returnResult(res, username);
  
  db.one({
    name: 'find-user',
    text: 'select * from tweets where username = $1 limit 1',
    values: [username]
  }).then(function(user1) {
    db.one({
      name: 'get-recommendation',
      text: 'select * from strangers where user_id1 = $1 or user_id2 = $1 order by similarity desc limit 1',
      values: [user1['user_id']]
    }).then(function(friend) {
      var result = {},
          userId2 = friend['user_id1'] === user1['user_id'] ? friend['user_id2'] : friend['user_id1'];
      result['similarity'] = friend['similarity'];
      result['user1'] = user1['username'];
      result['hash_tags1'] = util.sortObjByKeys(user1['hash_tags']);
      result['words1'] = util.sortObjByKeys(user1['tweet_text']);

      db.one({
        name: 'get-friend-user',
        text: 'select * from tweets where user_id = $1 limit 1',
        values: [userId2]
      }).then(function(user2) {
        result['user2'] = user2['username'];
        result['hash_tags2'] = util.sortObjByKeys(user2['hash_tags']);
        result['words2'] = util.sortObjByKeys(user2['tweet_text']);
        result['common_hash_tags'] = util.getCommonKeys(result['hash_tags1'], result['hash_tags2']);
        result['common_words'] = util.getCommonKeys(result['words1'], result['words2']);
        
        renderResult(result);
      }).catch(function(error) {
        console.log(error);
        renderResult();
      });
    }).catch(function(error) {
      console.log(error);
      renderResult();
    });
  }).catch(function(error) {
    console.log(error);
    renderResult();
  });
});


function returnResult(res, username) {
  return function(resultObj) {
    res.render('query/result', {username: username, result: resultObj});
  }
}

module.exports = router;