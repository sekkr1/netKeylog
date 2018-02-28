import { Observable } from "rxjs/Rx"
import { Host } from "./host";
import { EventEmitter } from "@angular/core";
import * as io from 'socket.io-client'

export interface HostData {
    data: string
}

export class HostsService {
    socket = io("localhost:5000")
    currentHost: string
    hostData: HostData = { data: "" }
    hosts: Host = {
        "192.168.1.2": { state: "online", name: "DEKEL-PC", user: "dekel" },
        "192.168.1.53": { state: "online", name: "OMER-PC", user: "omer" },
        "192.168.1.32": { state: "offline", name: "USER-PC", user: "User" },
        "192.168.1.52": { state: "away", name: "COMPUTER-1025", user: "asd" }
    }
    /*[
        { ip: "192.168.1.2", state: "online", name: "DEKEL-PC", user: "dekel" },
        { ip: "192.168.1.53", state: "online", name: "TOMER-PC", user: "tomer" },
        { ip: "192.168.1.32", state: "offline", name: "USER-PC", user: "User" },
        { ip: "192.168.1.52", state: "away", name: "COMPUTER-1025", user: "asd" }
    ]*/

    constructor() {
        this.socket.on("hosts", (hosts: Host) => {
            Object.assign(this.hosts, hosts)
        })
        this.socket.on("host data", (hostData: HostData) => {
            this.hostData.data += hostData
        })
    }

    getHosts(): Host {
        return this.hosts;
    }

    getHostData(ip: string): HostData {
        if (ip != this.currentHost) {
            this.currentHost = ip
            this.hostData.data = ""
            this.socket.emit("subscribe", ip)
        }
        return this.hostData
    }
}
