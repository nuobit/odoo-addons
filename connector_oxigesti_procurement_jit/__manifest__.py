# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector Oxigesti Procurement JIT",
    "summary": "Glue module beetwen Connector Oxigesti and Procurement JIT"
    "to avoid stock reservation when importing sales orders.",
    "version": "14.0.1.0.0",
    "category": "Inventory",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "AGPL-3",
    "depends": ["connector_oxigesti", "procurement_jit"],
    "auto_install": True,
}
