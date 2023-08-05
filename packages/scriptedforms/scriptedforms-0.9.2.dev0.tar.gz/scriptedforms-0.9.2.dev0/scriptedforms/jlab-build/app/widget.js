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
var apputils_1 = require("@jupyterlab/apputils");
var coreutils_1 = require("@jupyterlab/coreutils");
var phosphor_angular_loader_1 = require("./phosphor-angular-loader");
var app_component_1 = require("./app.component");
var app_module_1 = require("./app.module");
var AngularWrapperWidget = /** @class */ (function (_super) {
    __extends(AngularWrapperWidget, _super);
    function AngularWrapperWidget(options) {
        var _this = _super.call(this, app_component_1.AppComponent, app_module_1.AppModule) || this;
        _this.scriptedFormsOptions = Object.assign({
            node: _this.node
        }, options);
        return _this;
    }
    AngularWrapperWidget.prototype.initiliseScriptedForms = function () {
        var _this = this;
        this.run(function () {
            _this.componentInstance.initiliseScriptedForms(_this.scriptedFormsOptions);
        });
    };
    AngularWrapperWidget.prototype.initiliseBaseScriptedForms = function () {
        var _this = this;
        this.run(function () {
            _this.componentInstance.initiliseBaseScriptedForms(_this.scriptedFormsOptions);
        });
    };
    AngularWrapperWidget.prototype.setTemplateToString = function (dummyPath, template) {
        var _this = this;
        this.run(function () {
            _this.componentInstance.setTemplateToString(dummyPath, template);
        });
    };
    return AngularWrapperWidget;
}(phosphor_angular_loader_1.AngularWidget));
exports.AngularWrapperWidget = AngularWrapperWidget;
var ScriptedFormsWidget = /** @class */ (function (_super) {
    __extends(ScriptedFormsWidget, _super);
    function ScriptedFormsWidget(options) {
        var _this = _super.call(this) || this;
        if (options.context) {
            _this._context = options.context;
            _this.onPathChanged();
            _this._context.pathChanged.connect(_this.onPathChanged, _this);
        }
        _this.addClass('scripted-form-widget');
        var layout = (_this.layout = new widgets_1.BoxLayout());
        var toolbar = new apputils_1.Toolbar();
        toolbar.addClass('jp-NotebookPanel-toolbar');
        toolbar.addClass('custom-toolbar');
        layout.addWidget(toolbar);
        widgets_1.BoxLayout.setStretch(toolbar, 0);
        var angularWrapperWidgetOptions = Object.assign({ toolbar: toolbar }, options);
        _this.form = new AngularWrapperWidget(angularWrapperWidgetOptions);
        _this.form.addClass('form-container');
        layout.addWidget(_this.form);
        widgets_1.BoxLayout.setStretch(_this.form, 1);
        return _this;
    }
    Object.defineProperty(ScriptedFormsWidget.prototype, "ready", {
        get: function () {
            return Promise.resolve();
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ScriptedFormsWidget.prototype, "context", {
        get: function () {
            return this._context;
        },
        enumerable: true,
        configurable: true
    });
    ScriptedFormsWidget.prototype.onPathChanged = function () {
        this.title.label = coreutils_1.PathExt.basename(this._context.path);
    };
    ScriptedFormsWidget.prototype.dispose = function () {
        this.form.dispose();
        _super.prototype.dispose.call(this);
    };
    return ScriptedFormsWidget;
}(widgets_1.Widget));
exports.ScriptedFormsWidget = ScriptedFormsWidget;
//# sourceMappingURL=widget.js.map