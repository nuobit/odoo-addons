# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import fields, models


class PMSTinyAstrochannelLog(models.Model):
    _name = "pms.tiny.astrochannel.log"
    _description = "Astrochannel Log"
    _order = "id desc"

    message = fields.Text(
        required=True,
        readonly=True,
    )
