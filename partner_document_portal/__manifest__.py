# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Partner document Portal",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "maintainer": "NuoBiT",
    "category": "Dive",
    "depends": [
        "portal",
        "partner_document",
    ],
    "website": "https://github.com/nuobit/odoo-addons",
    "data": [
        "security/ir.model.access.csv",
        "security/partner_documents_security.xml",
        "views/portal_templates.xml",
    ],
    "license": "AGPL-3",
}
