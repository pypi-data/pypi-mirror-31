"use strict";
// Scripted Forms -- Making GUIs easy for everyone on your team.
// Copyright (C) 2017 Simon Biggs
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version (the "AGPL-3.0+").
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Affero General Public License and the additional terms for more
// details.
// You should have received a copy of the GNU Affero General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.
// ADDITIONAL TERMS are also included as allowed by Section 7 of the GNU
// Affrero General Public License. These aditional terms are Sections 1, 5,
// 6, 7, 8, and 9 from the Apache License, Version 2.0 (the "Apache-2.0")
// where all references to the definition "License" are instead defined to
// mean the AGPL-3.0+.
// You should have received a copy of the Apache-2.0 along with this
// program. If not, see <http://www.apache.org/licenses/LICENSE-2.0>.
/*
The root form component.

Passes the jupyterlab session into the kernel service and connects. Passes
through the `setFormContents` function.
*/
var core_1 = require("@angular/core");
var rendermime_1 = require("@jupyterlab/rendermime");
var outputarea_1 = require("@jupyterlab/outputarea");
var form_builder_component_1 = require("./form-builder-module/form-builder.component");
var initialisation_service_1 = require("./services/initialisation.service");
var form_service_1 = require("./services/form.service");
var kernel_service_1 = require("./services/kernel.service");
var variable_service_1 = require("./services/variable.service");
var file_service_1 = require("./services/file.service");
var AppComponent = /** @class */ (function () {
    function AppComponent(myFileService, myFormService, myInitialisationService, myKernelSevice, myVariableService) {
        this.myFileService = myFileService;
        this.myFormService = myFormService;
        this.myInitialisationService = myInitialisationService;
        this.myKernelSevice = myKernelSevice;
        this.myVariableService = myVariableService;
        this.kernelStatus = 'unknown';
        this.formStatus = null;
        this.variableStatus = null;
        this.queueLength = null;
    }
    AppComponent.prototype.ngAfterViewInit = function () {
        var _this = this;
        this.myFormService.formBuilderComponent = this.formBuilderComponent;
        var rendermime = new rendermime_1.RenderMimeRegistry({ initialFactories: rendermime_1.standardRendererFactories });
        this.myKernelSevice.jupyterError.subscribe(function (msg) {
            if (msg !== null) {
                var msgType = msg.header.msg_type;
                var model = new outputarea_1.OutputAreaModel();
                var output = msg.content;
                output.output_type = msgType;
                model.add(output);
                var outputArea = new outputarea_1.OutputArea({ model: model, rendermime: rendermime });
                var errorDiv = _this.jupyterErrorMsg.nativeElement;
                var errorHeading = document.createElement('h2');
                errorHeading.innerText = 'Python Error:';
                var errorParagraph = document.createElement('p');
                errorParagraph.innerText = ('A Python error has occured. This could be due to an error within ' +
                    'your ScriptedForms template or an issue with ScriptedForms itself.');
                var errorParagraphAfter = document.createElement('p');
                errorParagraphAfter.innerText = ('This error message will not go away until after a page refresh.');
                errorDiv.appendChild(errorHeading);
                errorDiv.appendChild(errorParagraph);
                errorDiv.appendChild(outputArea.node);
                errorDiv.appendChild(errorParagraphAfter);
            }
        });
        this.myFormService.formStatus.subscribe(function (status) {
            console.log('form: ' + status);
            _this.formStatus = status;
        });
        this.myVariableService.variableStatus.subscribe(function (status) {
            console.log('variable: ' + status);
            _this.variableStatus = status;
        });
        this.myKernelSevice.kernelStatus.subscribe(function (status) {
            console.log('kernel: ' + status);
            _this.kernelStatus = status;
        });
        this.myKernelSevice.queueLength.subscribe(function (length) {
            console.log('queue-length: ' + length);
            _this.queueLength = length;
        });
    };
    AppComponent.prototype.initiliseScriptedForms = function (options) {
        this.myInitialisationService.initiliseScriptedForms(options);
    };
    AppComponent.prototype.initiliseBaseScriptedForms = function (options) {
        this.myInitialisationService.initiliseBaseScriptedForms(options);
    };
    AppComponent.prototype.setTemplateToString = function (dummyPath, template) {
        this.myFileService.setTemplateToString(dummyPath, template);
    };
    __decorate([
        core_1.ViewChild('formBuilderComponent'),
        __metadata("design:type", form_builder_component_1.FormBuilderComponent)
    ], AppComponent.prototype, "formBuilderComponent", void 0);
    __decorate([
        core_1.ViewChild('jupyterErrorMsg'),
        __metadata("design:type", core_1.ElementRef)
    ], AppComponent.prototype, "jupyterErrorMsg", void 0);
    AppComponent = __decorate([
        core_1.Component({
            selector: 'app-root',
            template: "\n<div class=\"margin\">\n  <div class=\"hide-on-print\">\n    <toolbar-base></toolbar-base>\n    <mat-progress-spinner\n      color=\"accent\"\n      *ngIf=\"kernelStatus !== 'idle' || formStatus !== 'ready' || variableStatus !== 'idle' || queueLength !== 0\"\n      class=\"floating-spinner\"\n      mode=\"indeterminate\">\n    </mat-progress-spinner>\n  </div>\n  <app-form-builder #formBuilderComponent><div #jupyterErrorMsg></div></app-form-builder>\n  <div class=\"footer-space\"></div>\n</div>"
        }),
        __metadata("design:paramtypes", [file_service_1.FileService,
            form_service_1.FormService,
            initialisation_service_1.InitialisationService,
            kernel_service_1.KernelService,
            variable_service_1.VariableService])
    ], AppComponent);
    return AppComponent;
}());
exports.AppComponent = AppComponent;
//# sourceMappingURL=app.component.js.map