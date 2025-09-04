# Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import fields, models


class BarcodeLabelTemplateConfigurationField(models.Model):
    _name = "barcode.label.template.configuration.field"
    _description = "Barcode Label Template Configuration Field"
    _order = "configuration_id,sequence"

    sequence = fields.Integer(default=10)

    configuration_id = fields.Many2one(
        comodel_name="barcode.label.template.configuration",
        required=True,
        ondelete="cascade",
    )
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        required=True,
        ondelete="cascade",
        domain="[('model', '=', 'stock.lot')]",
    )
    target_field = fields.Text()
    position_x = fields.Float()
    position_y = fields.Float()
    width = fields.Float()
