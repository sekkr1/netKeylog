from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms, Namespace
from tinydb import Query

app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template('index.html')


class SocketServer(Namespace):
    def __init__(self, data):
        self.data = data

    def on_subscribe(self, host):
        hostData = self.data.search(Query().ip == host)
        if hostData:
            for room in rooms():
                if room != request.sid:
                    leave_room(room)
            emit("host data", hostData)
            join_room(host)

    def on_connect(self):
        emit('hosts', {
            "192.168.1.2": {"state": "online", "name": "DEKEL-PC", "user": "dekel"},
            "192.168.1.53": {"state": "online", "name": "NOMER-PC", "user": "omer"},
            "192.168.1.32": {"state": "offline", "name": "USER-PC", "user": "User"},
            "192.168.1.52": {"state": "away", "name": "COMPUTER-1025", "user": "asd"}
        })


def sendData():
    with app.app_context():
        socketio.emit("hosts", {
            "192.168.1.2": {"state": "away", "name": "DEKEL-PC", "user": "dekel"}
        },
            broadcast=True)


if __name__ == '__main__':
    socketio.on_namespace(SocketServer())
    socketio.run(app)
