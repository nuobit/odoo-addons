# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Connector WordPress WMPL",
    "version": "14.0.0.1.0",
    "author": "NuoBiT Solutions, S.L.",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/nuobit/odoo-addons",
    "depends": [
        "connector_wordpress",
    ],
    "data": [
        "views/ir_attachment_views.xml",
        "views/res_lang_views.xml",
        "views/wordpress_backend_view.xml",
    ],
    "installable": True,
}
