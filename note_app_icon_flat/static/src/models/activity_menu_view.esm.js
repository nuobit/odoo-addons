/** @odoo-module **/
/* Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {attr} from "@mail/model/model_field";
import {flatIconUrl} from "@web_app_icon_flat/js/flat_icon_url.esm";
import {registerPatch} from "@mail/model/model_core";

registerPatch({
    name: "ActivityMenuView",
    fields: {
        noteIconUrl: attr({
            compute() {
                return flatIconUrl("/note/static/description/icon.svg");
            },
        }),
    },
});
