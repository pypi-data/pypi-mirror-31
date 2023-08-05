"use strict";
// Scripted Forms -- Making GUIs easy for everyone on your team.
// Copyright (C) 2017 Simon Biggs
var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
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
var widgets_1 = require("@phosphor/widgets");
var coreutils_1 = require("@phosphor/coreutils");
var core_1 = require("@angular/core");
var platform_browser_dynamic_1 = require("@angular/platform-browser-dynamic");
var AngularLoader = /** @class */ (function () {
    function AngularLoader(ngModuleRef) {
        this.injector = ngModuleRef.injector;
        this.applicationRef = this.injector.get(core_1.ApplicationRef);
        this.ngZone = this.injector.get(core_1.NgZone);
        this.componentFactoryResolver = this.injector.get(core_1.ComponentFactoryResolver);
    }
    AngularLoader.prototype.attachComponent = function (ngComponent, dom) {
        var _this = this;
        var componentRef;
        this.ngZone.run(function () {
            var componentFactory = _this.componentFactoryResolver.resolveComponentFactory(ngComponent);
            componentRef = componentFactory.create(_this.injector, [], dom);
            _this.applicationRef.attachView(componentRef.hostView);
        });
        return componentRef;
    };
    return AngularLoader;
}());
exports.AngularLoader = AngularLoader;
var AngularWidget = /** @class */ (function (_super) {
    __extends(AngularWidget, _super);
    function AngularWidget(ngComponent, ngModule, options) {
        var _this = _super.call(this, options) || this;
        _this.componentReady = new coreutils_1.PromiseDelegate();
        platform_browser_dynamic_1.platformBrowserDynamic().bootstrapModule(ngModule)
            .then(function (ngModuleRef) {
            _this.angularLoader = new AngularLoader(ngModuleRef);
            _this.ngZone = _this.angularLoader.ngZone;
            _this.componentRef = _this.angularLoader.attachComponent(ngComponent, _this.node);
            _this.componentInstance = _this.componentRef.instance;
            _this.componentReady.resolve(undefined);
        });
        return _this;
    }
    AngularWidget.prototype.run = function (func) {
        var _this = this;
        this.componentReady.promise.then(function () {
            _this.ngZone.run(func);
        });
    };
    AngularWidget.prototype.dispose = function () {
        var _this = this;
        this.ngZone.run(function () {
            _this.componentRef.destroy();
        });
        _super.prototype.dispose.call(this);
    };
    return AngularWidget;
}(widgets_1.Widget));
exports.AngularWidget = AngularWidget;
//# sourceMappingURL=phosphor-angular-loader.js.map