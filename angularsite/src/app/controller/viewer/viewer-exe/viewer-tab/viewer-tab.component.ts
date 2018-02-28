import { Component, OnInit } from '@angular/core';
import { Input } from '@angular/core';

declare var M: any;

@Component({
  selector: 'tab',
  templateUrl: './viewer-tab.component.html'
})
export class ViewerTabComponent implements OnInit {

  @Input("tabTitle") title: string
  @Input() date: number

  ngOnInit() {
    for (let elem of <Node[]><any>document.querySelectorAll(".collapsible"))
      new M.Collapsible(elem, {})
  }
}
