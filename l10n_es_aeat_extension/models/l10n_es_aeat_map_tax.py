# Copyright NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# Licencia AGPL-3.0 o posterior (http://www.gnu.org/licenses/agpl)
from datetime import timedelta

from odoo import _, exceptions, fields, models


class L10nEsAeatMapTax(models.Model):
    _inherit = "l10n.es.aeat.map.tax"

    map_line_ids = fields.One2many(copy=True)

    def copy(self, default=None):
        self.ensure_one()

        if not self.date_from or not self.date_to:
            raise exceptions.ValidationError(
                _("Start date or end date is not defined.")
            )

        tomorrow = self.date_to + timedelta(days=1)

        new_map = super().copy(default={"date_from": tomorrow, "date_to": False})

        return new_map
