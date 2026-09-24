/** @odoo-module **/
/* Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {
    getFixture,
    mockTimeout,
    nextTick,
    patchWithCleanup,
} from "@web/../tests/helpers/utils";
import {makeView, setupViewRegistries} from "@web/../tests/views/helpers";
import {editSearch} from "@web/../tests/search/helpers";
import {session} from "@web/session";

const {QUnit} = window;

let target = null;
let serverData = null;
let execTimeouts = null;

QUnit.module("web_app_icon_flat", (hooks) => {
    hooks.beforeEach(() => {
        serverData = {
            models: {
                "res.config.settings": {
                    fields: {
                        foo: {string: "Foo", type: "boolean"},
                    },
                },
            },
        };
        target = getFixture();
        setupViewRegistries();
        const {execRegisteredTimeouts} = mockTimeout();
        execTimeouts = () => {
            execRegisteredTimeouts();
            return nextTick();
        };
        patchWithCleanup(session, {
            flat_icon_urls: {
                "/crm/static/description/icon.png":
                    "/web_app_icon_flat/static/img/crm/icon.png",
            },
        });
    });

    QUnit.test("settings show the flat icon of an Odoo app", async function (assert) {
        await makeView({
            type: "form",
            resModel: "res.config.settings",
            serverData,
            arch: `
                <form string="Settings" class="oe_form_configuration o_base_settings" js_class="base_settings">
                    <div class="o_setting_container">
                        <div class="settings">
                            <div class="app_settings_block" string="CRM" data-key="crm">
                                <div class="row mt16 o_settings_container">
                                    <div class="col-12 col-lg-6 o_setting_box">
                                        <div class="o_setting_left_pane">
                                            <field name="foo"/>
                                        </div>
                                        <div class="o_setting_right_pane">
                                            <label for="foo"/>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>`,
        });
        assert.strictEqual(
            target.querySelector(".settings_tab .tab[data-key='crm'] .icon").style
                .backgroundImage,
            'url("/web_app_icon_flat/static/img/crm/icon.png")',
            "the sidebar should show the flat icon"
        );

        await editSearch(target, "Foo");
        await execTimeouts();
        assert.strictEqual(
            target.querySelector(".settingSearchHeader img").dataset.src,
            "/web_app_icon_flat/static/img/crm/icon.png",
            "the search should show the flat icon"
        );
    });

    QUnit.test("settings keep the icon of another module", async function (assert) {
        await makeView({
            type: "form",
            resModel: "res.config.settings",
            serverData,
            arch: `
                <form string="Settings" class="oe_form_configuration o_base_settings" js_class="base_settings">
                    <div class="o_setting_container">
                        <div class="settings">
                            <div class="app_settings_block" string="Web App Icon Flat" data-key="web_app_icon_flat">
                                <div class="row mt16 o_settings_container">
                                    <div class="col-12 col-lg-6 o_setting_box">
                                        <div class="o_setting_left_pane">
                                            <field name="foo"/>
                                        </div>
                                        <div class="o_setting_right_pane">
                                            <label for="foo"/>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>`,
        });
        assert.strictEqual(
            target.querySelector(
                ".settings_tab .tab[data-key='web_app_icon_flat'] .icon"
            ).style.backgroundImage,
            'url("/web_app_icon_flat/static/description/icon.png")',
            "the sidebar should keep the icon of the module"
        );

        await editSearch(target, "Foo");
        await execTimeouts();
        assert.strictEqual(
            target.querySelector(".settingSearchHeader img").dataset.src,
            "/web_app_icon_flat/static/description/icon.png",
            "the search should keep the icon of the module"
        );
    });
});
