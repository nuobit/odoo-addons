# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    test_id = fields.Many2one(comodel_name='lighting.test', ondelete='restrict', string='Test')

    fan_control_chk = fields.Boolean(related='test_id.fan_control_chk')

    #TODO: eliminar el field_ids i creauna rel 1 a n amb totss els camps fan_control_chk per producte al test,
    # fer que el producte id ssigui unique per simualr una relacio 1 a nb
    # crear tant camps related , etc i
    #