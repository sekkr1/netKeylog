import { Observable } from 'rxjs/Rx';
import { HostsService } from './controller/hosts.service';
import { Router, ActivatedRouteSnapshot, RouterStateSnapshot, CanActivate, RouterModule, Routes } from '@angular/router';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule, Injectable } from '@angular/core';

import { AppComponent } from './app.component';
import { NavbarComponent } from './controller/navbar/navbar.component';
import { ControllerComponent } from './controller/controller.component';
import { AppRoutingModule } from './app-routing.module';
import { ViewerComponent } from './controller/viewer/viewer.component';
import { DynamicComponent } from './controller/viewer/dynamic-component/dynamic-component.component'

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    ControllerComponent,
    ViewerComponent,
    DynamicComponent
  ],
  imports: [
    AppRoutingModule,
    BrowserModule
  ],
  providers: [HostsService],
  bootstrap: [AppComponent]
})
export class AppModule { }
