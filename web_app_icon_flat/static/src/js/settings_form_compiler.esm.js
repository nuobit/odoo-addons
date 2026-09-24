/** @odoo-module **/
/* Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {SettingsFormCompiler} from "@web/webclient/settings_form_view/settings_form_compiler";
import {flatIconUrl} from "@web_app_icon_flat/js/flat_icon_url.esm";
import {patch} from "@web/core/utils/patch";

patch(SettingsFormCompiler.prototype, "web_app_icon_flat", {
    setup() {
        this._super(...arguments);
        const appCompiler = this.compilers.find(
            (compiler) => compiler.selector === "div.app_settings_block"
        );
        const compileApp = appCompiler.fn;
        appCompiler.fn = function (el, params) {
            // The app's params.module is also its entry in the Settings sidebar,
            // which the settings page serializes once all its apps are compiled.
            params.module.imgurl = flatIconUrl(params.module.imgurl);
            return compileApp.call(this, el, params);
        };
    },
});
