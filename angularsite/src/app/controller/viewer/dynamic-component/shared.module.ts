import { NgModule, ModuleWithProviders } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ViewerExeComponent } from '../viewer-exe/viewer-exe.component';
import { ViewerTabComponent } from '../viewer-exe/viewer-tab/viewer-tab.component';
import { ViewerHotkeyComponent } from '../viewer-exe/viewer-tab/viewer-hotkey/viewer-hotkey.component';


@NgModule({
    imports: [CommonModule],
    declarations: [ViewerExeComponent, ViewerTabComponent, ViewerHotkeyComponent],
    exports: [ViewerExeComponent, ViewerTabComponent, ViewerHotkeyComponent],
    entryComponents: [ViewerExeComponent, ViewerTabComponent, ViewerHotkeyComponent]
})
export class SharedModule {
    static forRoot(): ModuleWithProviders {
        return {
            ngModule: SharedModule,
            providers: []
        };
    }
}

