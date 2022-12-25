if( app.socketio ) {

  var socket = io("//" + document.domain + ":" + location.port);

  socket.on("connect", function() {
    app.connected = true;
    console.log("CONNECTED");
  });

  socket.on("disconnect", function() {
    app.connected = false;
    console.log("DISCONNECTED");
  });

} else {
  var socket = {
    "on" : function() {
      console.log("no socketio support enabled...");    
    },
    "emit" : function(channel, args, callback) {
      console.log("no socketio support enabled...");
      callback("no socketio support enabled...");
    }
  }
}
