// this import should be first in order to load some required settings (like globals and reflect-metadata)
import { platformNativeScript } from "nativescript-angular/platform-static";


import "nativescript-websockets";
import "moment";


import 'rxjs/add/observable/zip';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/zip';
import 'rxjs/add/operator/filter';
import 'rxjs/add/operator/takeUntil';
import 'rxjs/add/operator/first';


// Import some stuff that we need
import "@synerty/vortexjs";

import {VortexService} from "@synerty/vortexjs";
VortexService.setVortexUrl(null);
VortexService.setVortexClientName("peek-mobile");

// Enable the use of workers for the payload
import {Payload} from "@synerty/vortexjs";
import {PayloadDelegateNs} from "@synerty/vortexjs/index-nativescript";

Payload.setWorkerDelegate(new PayloadDelegateNs());

import { AppModuleNgFactory } from "./app.module.ngfactory";

platformNativeScript().bootstrapModuleFactory(AppModuleNgFactory);
