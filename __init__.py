from datetime import timedelta
from tornado.httpserver import HTTPServer
from tornado.options import define, options
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler
from tornado.template import Loader
import os
import json  
define('port', default=os.environ.get("PORT", 8888), help='port to listen on')
define("ROOM_LIMIT", default=20, help="Limit for room")

class Room:
    def __init__(self):
        self.peers = []
        print("Oda kuruldu")

    def add_peer(self, peer):
        self.peers.append(peer)
        server.peers.append(peer)    

    def  remove_peer(self, peer):
        self.peers.remove(peer)
        server.peers.remove(peer)

class Server:
    def __init__(self):
        self.peers = []
        self.rooms = []

    def create_room(self):
        room = Room()
        self.rooms.append(room)
        return room

    def get_room(self):
        for room in self.rooms:
            if len(room.peers) < options.ROOM_LIMIT:
                return room
        return self.create_room()

server = Server()

class GameHandler(WebSocketHandler):

    def check_origin(self, origin):
        return True

    async def open(self):
        print("Websocket bağlandı")
        self.peer_number = 0
        self.room = server.get_room()
        self.write_message(json.dumps({"peerNumber": len(self.room.peers), "id":id(self)}))
        self.room.add_peer(self)
        self.peer = self.room.peers[self.peer_number]
        self.ping = True
        await self.send_ping()

    def on_message(self, msg):
        message = json.loads(msg)
        if message["Server"] == "Next":
            self.peer_number += 1
            self.peer = self.room.peers[self.peer_number]

        if self.peer is self:
            self.peer_number += 1
            self.peer = self.room.peers[self.peer_number]

        if not message["Server"]:
            self.peer.peer = self
            self.peer.write_message(msg)

    def on_close(self):
        self.room.remove_peer(self)
        self.ping = False

    async def send_ping(self):
        if self.ping:
            # await sleep(25)
            IOLoop.instance().add_callback(callback=lambda: self.write_message(json.dumps({"ping" : True})))
            IOLoop.instance().add_timeout(timedelta(seconds=25), self.send_ping)


if __name__ == '__main__':
    """Construct and serve the tornado application."""
    app = Application([
        (r"/ws/", GameHandler),
        (r"/", MainHandler),
    ],
    )
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    IOLoop.current().start()
