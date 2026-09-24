/** @odoo-module **/
/* Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {session} from "@web/session";

/**
 * Return the URL of the flat icon that replaces the icon at the given URL, or
 * the given URL itself when no flat icon replaces it.
 *
 * @param {String} url
 * @returns {String}
 */
export function flatIconUrl(url) {
    // Pages that are not the web client, such as the test suite, have no flat
    // icon URLs in their session.
    const flatIconUrls = session.flat_icon_urls || {};
    return flatIconUrls[url] || url;
}
