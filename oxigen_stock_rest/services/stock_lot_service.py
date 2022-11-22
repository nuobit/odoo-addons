# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class LotService(Component):
    _inherit = "stock.lot.service"

    def _filter_lots(self, lots):
        clasified_lots = {}
        for lot in lots:
            key = 3
            if lot.nos and not lot.nos_unknown:
                key = 1
            elif lot.nos_unknown:
                key = 2
            clasified_lots.setdefault(lot.name, {}).setdefault(key, []).append(lot.id)
        lot_ids = []
        for data in clasified_lots.values():
            lot_ids += data[min(data.keys())]
        if lot_ids:
            lots = self.env[lots._name].browse(lot_ids)
        return super()._filter_lots(lots)
