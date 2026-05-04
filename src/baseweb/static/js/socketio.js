// Check if socketio is enabled (set in main.html template)
var socketioEnabled = app.config.globalProperties.$socketio || false;

if( socketioEnabled ) {

  var socket = io("//" + document.domain + ":" + location.port);

  socket.on("connect", function() {
    if (window._socketConnected) {
      window._socketConnected.value = true;
    }
    console.log("🛜 socketio: connected to backend...");
  });

  socket.on("disconnect", function() {
    if (window._socketConnected) {
      window._socketConnected.value = false;
    }
    console.log("🛜 socketio: disconnected from backend");
  });

} else {
  var socket = {
    "on" : function() {
      console.log("socketio: support not enabled...");
    },
    "emit" : function(channel, args, callback) {
      console.log("socketio: support not enabled...");
      callback("🛜 socketio: support not enabled...");
    }
  }
}
