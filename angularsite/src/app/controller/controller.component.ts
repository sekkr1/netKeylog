import { ActivatedRoute } from '@angular/router';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { Params } from '@angular/router/src/shared';
import { Subscription } from 'rxjs/Rx';

@Component({
  selector: 'app-controller',
  templateUrl: './controller.component.html',
  styleUrls: ['./controller.component.css']
})
export class ControllerComponent implements OnInit, OnDestroy {

  selectedHostIp: string
  paramSubscription: Subscription;

  constructor(private route: ActivatedRoute) { }

  ngOnInit() {
    this.paramSubscription = this.route.params.subscribe((params: Params) => {
      this.selectedHostIp = params["id"]
      console.log(this.selectedHostIp)
    })
  }
  ngOnDestroy() {
    this.paramSubscription.unsubscribe()
  }
}