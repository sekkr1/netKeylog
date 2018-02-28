import { ViewerComponent } from './controller/viewer/viewer.component';
import { ControllerComponent } from './controller/controller.component';
import { Observable } from 'rxjs/Rx';
import { Router, CanActivate, RouterStateSnapshot, ActivatedRouteSnapshot, Routes, RouterModule } from '@angular/router';
import { HostsService } from './controller/hosts.service';
import { NgModule, Injectable } from '@angular/core';

@Injectable()
class CanActivateHost implements CanActivate {

    constructor(private router: Router,
        private hostsService: HostsService) { }

    canActivate(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot
    ): Observable<boolean> | Promise<boolean> | boolean {
        const exists = route.params['id'] in this.hostsService.getHosts()
        console.log(exists)
        if (!exists)
            this.router.navigate(['/controller']);
        return exists;
    }
}

const appRoutes: Routes = [
    { path: 'controller', component: ControllerComponent },
    { path: 'controller/:id', component: ControllerComponent, canActivate: [CanActivateHost] },
    {
        path: '',
        redirectTo: 'controller',
        pathMatch: 'full'
    }
];

@NgModule({
    imports: [RouterModule.forRoot(appRoutes)],
    exports: [RouterModule],
    providers: [CanActivateHost]
})
export class AppRoutingModule { }