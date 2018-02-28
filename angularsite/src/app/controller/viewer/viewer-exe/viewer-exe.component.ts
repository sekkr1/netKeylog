import { Component, OnInit } from '@angular/core';
import { Input } from '@angular/core';

@Component({
  selector: 'exe',
  templateUrl: './viewer-exe.component.html'
})
export class ViewerExeComponent {
  @Input() name: string
  @Input() exe: string
  @Input() date: number
}
