var express = require('express');
var db = require('../model/db');
var util = require('../helper/util');

var router = express.Router();

router.get('/', function(req, res) {
  var username1 = req.query['username1'].trim(),
      username2 = req.query['username2'].trim(),
      renderResult = returnResult(res, username1, username2);

      db.one({
        name: 'find-user1',
        text: 'select * from tweets where username = $1 limit 1',
        values: [username1]
      }).then(function(user1) {
        db.one({
          name: 'find-user2',
          text: 'select * from tweets where username = $1 limit 1',
          values: [username2]
        }).then(function(user2) {
          var userId1 = user1['user_id'] < user2['user_id'] ? user1['user_id'] : user2['user_id'];
          var userId2 = user1['user_id'] < user2['user_id'] ? user2['user_id'] : user1['user_id'];
          db.one({
            name: 'find-similarity',
            text: 'select * from friends where user_id1 = $1 and user_id2 = $2 limit 1',
            values: [userId1, userId2]
          }).then(function(friend) {
            var result = {};
            result['similarity'] = friend['similarity'];
            result['user1'] = user1['username'];
            result['hash_tags1'] = util.sortObjByKeys(user1['hash_tags']);
            result['words1'] = util.sortObjByKeys(user1['tweet_text']);
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


function returnResult(res, username1, username2) {
  return function(resultObj) {
    res.render('verify/result', {username1: username1, username2: username2, result: resultObj});
  }
}

module.exports = router;