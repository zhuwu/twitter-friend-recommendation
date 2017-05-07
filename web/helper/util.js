var util = {
  sortObjByKeys: function(unordered) {
    const ordered = {};
    Object.keys(unordered).sort().forEach(function(key) {
      ordered[key] = unordered[key];
    });
    return ordered;
  },

  getCommonKeys: function(object1, object2) {
    var commonKeys = {};

    Object.keys(object1).filter(function (key) {
      return object2.hasOwnProperty(key);
    }).forEach(function(key) {
      commonKeys[key] = true;
    });

    return commonKeys;
  }
};

module.exports = util;