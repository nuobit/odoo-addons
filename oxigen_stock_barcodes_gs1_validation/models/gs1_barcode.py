# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import ValidationError


class GS1Barcode(models.Model):
    _inherit = "gs1_barcode"

    def decode(self, barcode):
        res = super(GS1Barcode, self).decode(barcode)
        if len(res) == 1:
            ai, value = list(res.items())[0]
            record = True
            domain = [("company_id", "=", self.env.company.id)]
            if ai in ["01", "240"]:
                domain.append(("barcode", "=", value))
                record = self.env["product.product"].search_count(domain)
            elif ai in ["10", "21"]:
                domain.append(("name", "=", value))
                record = self.env["stock.production.lot"].search_count(domain)
            elif ai == "02":
                domain.append(("barcode", "=", value))
                record = self.env["product.packaging"].search_count(domain)
            if not record:
                raise ValidationError(_("GS1 Barcode not found"))
        return res
