import { Component, OnInit } from '@angular/core';
import { Input } from '@angular/core';

@Component({
  selector: 'hotkey',
  templateUrl: './viewer-hotkey.component.html',
  styleUrls: ['./keys.css']
})
export class ViewerHotkeyComponent implements OnInit {
  @Input() ctrl: boolean
  @Input() shift: boolean
  @Input() alt: boolean
  @Input() key: string

  ngOnInit() {
    this.ctrl = this.ctrl != undefined
    this.shift = this.shift != undefined
    this.alt = this.alt != undefined
  }
}
