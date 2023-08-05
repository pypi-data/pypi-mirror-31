"use strict";
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
var widgets_1 = require("@phosphor/widgets");
var application_1 = require("@jupyterlab/application");
var coreutils_1 = require("@jupyterlab/coreutils");
var docregistry_1 = require("@jupyterlab/docregistry");
var services_1 = require("@jupyterlab/services");
var apputils_1 = require("@jupyterlab/apputils");
var widget_1 = require("./../app/widget");
var FACTORY = 'ScriptedForms';
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.preview = 'scriptedforms:open';
})(CommandIDs || (CommandIDs = {}));
function loadApp() {
    var serviceManager = new services_1.ServiceManager();
    var contentsManager = new services_1.ContentsManager();
    var formWidget = new widget_1.ScriptedFormsWidget({
        serviceManager: serviceManager,
        contentsManager: contentsManager
    });
    formWidget.form.initiliseScriptedForms();
    window.onresize = function () { formWidget.update(); };
    widgets_1.Widget.attach(formWidget, document.body);
}
exports.loadApp = loadApp;
var ScriptedFormsWidgetFactory = /** @class */ (function (_super) {
    __extends(ScriptedFormsWidgetFactory, _super);
    function ScriptedFormsWidgetFactory(options) {
        var _this = _super.call(this, options) || this;
        _this.serviceManager = options.serviceManager;
        _this.contentsManager = options.contentsManager;
        return _this;
    }
    ScriptedFormsWidgetFactory.prototype.createNewWidget = function (context) {
        var formWidget = new widget_1.ScriptedFormsWidget({
            serviceManager: this.serviceManager,
            contentsManager: this.contentsManager,
            context: context
        });
        formWidget.context.ready.then(function () {
            formWidget.form.initiliseScriptedForms();
        });
        return formWidget;
    };
    return ScriptedFormsWidgetFactory;
}(docregistry_1.ABCWidgetFactory));
exports.ScriptedFormsWidgetFactory = ScriptedFormsWidgetFactory;
function activate(app, restorer, settingRegistry) {
    app.docRegistry.addFileType({
        name: 'scripted-form',
        mimeTypes: ['text/markdown'],
        extensions: ['.form.md'],
        contentType: 'file',
        fileFormat: 'text'
    });
    var factory = new ScriptedFormsWidgetFactory({
        name: FACTORY,
        fileTypes: ['markdown', 'scripted-form'],
        defaultFor: ['scripted-form'],
        readOnly: true,
        serviceManager: app.serviceManager,
        contentsManager: app.serviceManager.contents,
    });
    app.docRegistry.addWidgetFactory(factory);
    var tracker = new apputils_1.InstanceTracker({
        namespace: '@simonbiggs/scriptedforms'
    });
    restorer.restore(tracker, {
        command: 'docmanager:open',
        args: function (widget) { return ({ path: widget.context.path, factory: FACTORY }); },
        name: function (widget) { return widget.context.path; }
    });
    factory.widgetCreated.connect(function (sender, widget) {
        tracker.add(widget);
        widget.context.pathChanged.connect(function () {
            tracker.save(widget);
        });
    });
    app.commands.addCommand(CommandIDs.preview, {
        label: 'ScriptedForms',
        execute: function (args) {
            var path = args['path'];
            if (typeof path !== 'string') {
                return;
            }
            return app.commands.execute('docmanager:open', {
                path: path, factory: FACTORY
            });
        }
    });
}
exports.plugin = {
    id: '@simonbiggs/scriptedforms:plugin',
    autoStart: true,
    requires: [application_1.ILayoutRestorer, coreutils_1.ISettingRegistry],
    activate: activate
};
//# sourceMappingURL=jupyterlab-plugin.js.map