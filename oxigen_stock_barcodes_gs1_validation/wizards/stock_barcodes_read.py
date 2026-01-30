# Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import ValidationError


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    def _validate_gs1_ai(self, ai, value):
        domain = [("company_id", "=", self.env.company.id)]
        record = False
        if ai in ["01", "240"]:
            domain.append(("barcode", "=", value))
            record = self.env["product.product"].search_count(domain)
        elif ai in ["10", "21"]:
            domain.append(("name", "=", value))
            record = self.env["stock.lot"].search_count(domain)
        elif ai == "02":
            domain.append(("barcode", "=", value))
            record = self.env["product.packaging"].search_count(domain)

        if not record:
            raise ValidationError(
                _("GS1 Barcode not found: AI(%(ai)s) - %(value)s")
                % {"ai": ai, "value": value}
            )
        return True

    def _process_ai_01(self, gs1_list):
        ai_item = next(filter(lambda f: f["ai"] == "01", gs1_list), False)
        if ai_item and len(gs1_list) == 1:
            self._validate_gs1_ai("01", ai_item["value"])
        return super()._process_ai_01(gs1_list)

    def _process_ai_02(self, gs1_list):
        ai_item = next(filter(lambda f: f["ai"] == "02", gs1_list), False)
        if ai_item and len(gs1_list) == 1:
            self._validate_gs1_ai("02", ai_item["value"])
        return super()._process_ai_02(gs1_list)

    def _process_ai_10(self, gs1_list):
        ai_item = next(filter(lambda f: f["ai"] == "10", gs1_list), False)
        if ai_item and len(gs1_list) == 1:
            self._validate_gs1_ai("10", ai_item["value"])
        return super()._process_ai_10(gs1_list)

    def _process_ai_21(self, gs1_list):
        ai_item = next(filter(lambda f: f["ai"] == "21", gs1_list), False)
        lot_ai = next(filter(lambda f: f["ai"] == "10", gs1_list), False)
        if ai_item and len(gs1_list) == 1 and not lot_ai:
            self._validate_gs1_ai("21", ai_item["value"])
        return super()._process_ai_21(gs1_list)

    def _process_ai_240(self, gs1_list):
        ai_item = next(filter(lambda f: f["ai"] == "240", gs1_list), False)
        if ai_item and len(gs1_list) == 1:
            self._validate_gs1_ai("240", ai_item["value"])
        return super()._process_ai_240(gs1_list)
