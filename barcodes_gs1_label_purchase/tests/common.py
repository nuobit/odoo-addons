# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form

from odoo.addons.barcodes_gs1_label.tests.common import TestCommon


class TestPurchaseCommon(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor"})
        cls.uom_gram = cls.env.ref("uom.product_uom_gram")

    def _purchase(self, product, quantity, uom):
        purchase = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_qty": quantity,
                            "product_uom": uom.id,
                        }
                    )
                ],
            }
        )
        purchase.button_confirm()
        return purchase.picking_ids

    def _create_dynamic_uom(self, name="Piece", ratio=1):
        # its kilos per unit are known only when the goods are received
        return self.env["uom.uom"].create(
            {
                "name": name,
                "category_id": self.uom_kg.category_id.id,
                "uom_type": "bigger",
                "ratio": ratio,
                "dynamic_ratio": True,
            }
        )

    def _create_return(self, receipt, quantity):
        return_wizard = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=receipt.ids,
                active_id=receipt.id,
                active_model="stock.picking",
            )
        ).save()
        return_wizard.product_return_moves.write(
            {"quantity": quantity, "to_refund": True}
        )
        return self.env["stock.picking"].browse(
            return_wizard.action_create_returns()["res_id"]
        )

    def _return_to_vendor(self, receipt, quantity):
        return_picking = self._create_return(receipt, quantity)
        return_picking.button_validate()
        return return_picking
