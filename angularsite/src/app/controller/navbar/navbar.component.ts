import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { HostsService } from '../hosts.service';
import { Host } from '../host';
import { ActivatedRoute } from '@angular/router';

declare var M: any

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {

  objectKeys = Object.keys
  hosts: Host
  @Input() selectedHostIp: string
  get selectedHost() { return this.hosts[this.selectedHostIp] }

  constructor(private hostsService: HostsService, private activatedRoute: ActivatedRoute) { }

  ngOnInit() {
    this.hosts = this.hostsService.getHosts()
    new M.Sidenav(document.querySelector(".sidenav"), {})
    this.activatedRoute.url.subscribe(() => {
      M.Sidenav.getInstance(document.querySelector(".sidenav")).close()
    });
  }
}
