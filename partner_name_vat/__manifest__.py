# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Partner name with vat",
    "summary": "This module concatenates vat number to partner name on display_name",
    "version": "12.0.1.0.0",
    "category": "Web",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "website": "https://github.com/nuobit",
    "license": "AGPL-3",
    "depends": [
        "base",
    ],
    "post_init_hook": "post_init_hook_vat_update",
    "uninstall_hook": "uninstall_hook_vat_remove",
    "installable": True,
    "auto_install": False,
}
