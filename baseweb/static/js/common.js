function syntaxHighlight(src, height) {
  if(typeof src !== "string" && !(src instanceof String)) {
    src = JSON.stringify(src, null, 2);
  }
  var html = hljs.highlightAuto(src).value;
  return "<pre style='background-color: #fafafa; padding:10px; max-height:"+height+"px; overflow:auto;'>" + html + "</pre>";
}

Vue.filter( "syntaxHighlight", syntaxHighlight);

Vue.filter('formatDate', function(value) {
  if (value) {
    return moment(value).format('DD/MM/YYYY HH:mm:ss')
  }
});

Vue.filter('formatEpoch', function(value) {
  if (value) {
    return moment(String(new Date(value).toISOString())).format('DD/MM/YYYY HH:mm:ss')
  }
});

// https://stackoverflow.com/questions/105034/create-guid-uuid-in-javascript
function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

