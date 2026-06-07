export default function messageSocket(io) {
  io.on("connection", (socket) => {
    console.log("client connected:", socket.id);

    socket.on("message", (msg) => {
      console.log("message:", msg);
      io.emit("message", msg);
    });

    socket.on("disconnect", () => {
      console.log("client disconnected:", socket.id);
    });
  });
}
