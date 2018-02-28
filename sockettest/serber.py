from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms, Namespace

app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template('index.html')


class SocketServer(Namespace):
    def on_subscribe(self, host):
        data = {
            "192.168.1.2": "<exe style='height:100%' title='asd' name='Google Chrome' exe='chrome.exe'><tab tabTitle='Facebook'><hotkey ctrl shift key='PrintScreen'></hotkey>adasdsad",
            "192.168.1.53": "<exe name='Steam' exe='steam.exe'><tab tabTitle='Steam'>user12<hotkey key='tab'></hotkey>pass123 dasd",
            "192.168.1.32": "<exe name='Google Chrome' exe='chrome.exe'><tab tabTitle='blayh'><hotkey ctrl shift key='PrintScreen'></hotkey>adasdsad</tab><tab tabTitle='nggger2'>bllall",
            "192.168.1.52": "<exe name='Google Chrome' exe='chrome.exe'><tab tabTitle='blahblah'><hotkey ctrl shift key='PrintScreen'></hotkey>adasdsad"
        }
        if host in data:
            for room in rooms():
                if room != request.sid:
                    leave_room(room)
            emit("host data", data[host])
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
