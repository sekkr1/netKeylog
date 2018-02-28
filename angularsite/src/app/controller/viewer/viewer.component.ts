import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { HostsService, HostData } from './../hosts.service';
import { Component, OnInit, OnChanges, Input, NgModuleFactory } from '@angular/core';

@Component({
  selector: 'app-viewer',
  template: '<dynamic *ngIf="data?.data" html="{{ data.data }}</tab></exe>"></dynamic>'
})
export class ViewerComponent {

  @Input() selectedHostIp: string

  get data() {
    return this.hostsService.getHostData(this.selectedHostIp)
  }

  constructor(private hostsService: HostsService) { }
}

