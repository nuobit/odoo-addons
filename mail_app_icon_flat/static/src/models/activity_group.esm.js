/** @odoo-module **/
/* Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {flatIconUrl} from "@web_app_icon_flat/js/flat_icon_url.esm";
import {registerPatch} from "@mail/model/model_core";

registerPatch({
    name: "ActivityGroup",
    modelMethods: {
        convertData(data) {
            return this._super({...data, icon: flatIconUrl(data.icon)});
        },
    },
});
