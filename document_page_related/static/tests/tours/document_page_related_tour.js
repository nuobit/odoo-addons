/* Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("document_page_related.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var list = '.o_field_widget[name="related_page_ids"]';

    tour.register(
        "document_page_related_tour",
        {
            test: true,
        },
        [
            {
                content: "edit the document",
                trigger: ".o_form_button_edit",
            },
            {
                content: "open the tab of the related documents",
                trigger: '.nav-link:contains("Related Documents")',
                extra_trigger: ".o_form_editable",
            },
            {
                content: "add related documents",
                trigger: list + " .o_field_x2many_list_row_add a",
            },
            {
                content:
                    "the dialog lists the documents with the columns of their menu",
                trigger: '.o_data_row:contains("Law")',
                extra_trigger: 'th[data-name="content_date"]',
                run: function () {
                    // Only wait for it
                },
            },
            {
                content: "the dialog does not offer to create a document",
                trigger:
                    '.modal-footer:has(.o_select_button):not(:has(button:contains("Create")))',
                run: function () {
                    // Only wait for it
                },
            },
            {
                content: "select the law",
                trigger: '.o_data_row:contains("Law") .o_list_record_selector input',
            },
            {
                content: "select the guide",
                trigger: '.o_data_row:contains("Guide") .o_list_record_selector input',
            },
            {
                content: "add the selected documents",
                trigger: ".modal-footer .o_select_button",
            },
            {
                content: "the law is in the list, with its category",
                trigger: list + ' .o_data_row:contains("Law"):contains("Quality")',
                extra_trigger: list + ' .o_data_row:contains("Guide")',
                run: function () {
                    // Only wait for it
                },
            },
            {
                content: "save the document",
                trigger: ".o_form_button_save",
            },
            {
                content: "edit the document again",
                trigger: ".o_form_button_edit",
            },
            {
                content: "open the tab again",
                trigger: '.nav-link:contains("Related Documents")',
                extra_trigger: ".o_form_editable",
            },
            {
                content: "remove the guide",
                trigger: list + ' .o_data_row:contains("Guide") .o_list_record_remove',
            },
            {
                content: "save the document without the guide",
                trigger: ".o_form_button_save",
                extra_trigger: list + ':not(:has(.o_data_row:contains("Guide")))',
            },
            {
                content: "the document is saved",
                trigger: ".o_form_button_edit",
                run: function () {
                    // Only wait for it
                },
            },
        ]
    );
});
