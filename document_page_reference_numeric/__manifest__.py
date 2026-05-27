# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Document Page Numeric Reference",
    "summary": "Auto-generate unique 10-digit numeric references for "
    "document pages.",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "category": "Knowledge Management",
    "depends": [
        "document_page_reference",
    ],
    "data": [
        "data/ir_sequence.xml",
    ],
    "post_init_hook": "post_init_hook",
}
