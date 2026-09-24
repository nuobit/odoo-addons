/** @odoo-module **/
/* Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {flatIconUrl} from "@web_app_icon_flat/js/flat_icon_url.esm";
import {registerPatch} from "@mail/model/model_core";

registerPatch({
    name: "Message",
    modelMethods: {
        convertData(data) {
            // The module icon is replaced only where the server sent one: the
            // thread of a message sent without it keeps the icon it has.
            return this._super(
                "module_icon" in data
                    ? {...data, module_icon: flatIconUrl(data.module_icon)}
                    : data
            );
        },
    },
});
