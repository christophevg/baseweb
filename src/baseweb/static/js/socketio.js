if( app.socketio ) {

  var socket = io("//" + document.domain + ":" + location.port);

  socket.on("connect", function() {
    app.connected = true;
    console.log("🛜 socketio: connected to backend...");
  });

  socket.on("disconnect", function() {
    app.connected = false;
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
