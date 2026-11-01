# Copyright NuoBiT Solutions 2025 - Deniz Gallo <dgallo@nuobit.com>
# Licencia AGPL-3.0 o posterior (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class L10nEsAeatMapTaxLine(models.Model):
    _inherit = "l10n.es.aeat.map.tax.line"

    map_parent_id = fields.Many2one(ondelete="cascade")
