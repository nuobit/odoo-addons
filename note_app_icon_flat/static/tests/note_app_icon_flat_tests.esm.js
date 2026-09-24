/** @odoo-module **/
/* Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {patchWithCleanup} from "@web/../tests/helpers/utils";
import {session} from "@web/session";
import {start} from "@mail/../tests/helpers/test_utils";

const {QUnit} = window;

QUnit.module("note_app_icon_flat", {
    beforeEach() {
        patchWithCleanup(session, {
            flat_icon_urls: {
                "/note/static/description/icon.svg":
                    "/web_app_icon_flat/static/img/note/icon.svg",
            },
        });
    },
});

QUnit.test("activity menu shows the flat icon of a new note", async function (assert) {
    assert.expect(1);

    const {click} = await start();
    await click('.dropdown-toggle[title="Activities"]');
    await click(".o_note_show");
    assert.strictEqual(
        document.querySelector(".o_note img").dataset.src,
        "/web_app_icon_flat/static/img/note/icon.svg",
        "should show the flat icon of Notes"
    );
});
