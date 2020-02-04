var socket = io("//" + document.domain + ":" + location.port);

socket.on("connect", function() {
  app.connected = true;
  console.log("CONNECTED");
});

socket.on("disconnect", function() {
  app.connected = false;
  console.log("DISCONNECTED");
});
