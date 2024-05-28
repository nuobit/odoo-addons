# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Res Lang Shortname",
    "summary": "This module adds a shortname field"
    "to the res.lang model to get the abbreviated name.",
    "version": "16.0.1.0.0",
    "category": "Language",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["base_setup"],
    "data": [
        "views/res_lang_views.xml",
        "views/res_config_settings_views.xml",
    ],
}
