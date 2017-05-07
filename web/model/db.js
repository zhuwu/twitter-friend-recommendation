var pgp = require('pg-promise')();
var cn = require('../settings');
var db = pgp(cn); // database instance;

module.exports = db;