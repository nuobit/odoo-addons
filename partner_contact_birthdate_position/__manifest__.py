# Copyright 2025 NuoBiT - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Partner Contact Birthdate Position",
    "summary": "This module moves birthdate and age fields in partner form",
    "version": "16.0.1.0.0",
    "category": "Contacts",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "partner_contact_birthdate",
    ],
    "data": [
        "views/res_partner.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "partner_contact_birthdate_position/static/src/scss/styles.scss",
        ],
    },
}
