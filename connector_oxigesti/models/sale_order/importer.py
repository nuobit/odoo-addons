# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class SaleOrderBatchImporter(Component):
    """Import the Oxigesti Services.

    For every sale order in the list, a delayed job is created.
    """

    _name = "oxigesti.sale.order.delayed.batch.importer"
    _inherit = "oxigesti.delayed.batch.importer"

    _apply_on = "oxigesti.sale.order"


class SaleOrderImporter(Component):
    _name = "oxigesti.sale.order.importer"
    _inherit = "oxigesti.importer"

    _apply_on = "oxigesti.sale.order"

    def _must_skip(self, binding):
        odoo_num_alb = self.external_data["Odoo_Numero_Albaran"] or None
        if binding:
            order = self.component(usage="binder").unwrap_binding(binding)
            if order.name != odoo_num_alb:
                raise ValidationError(
                    _(
                        "Inconsistent state: The Odoo sale order number on Oxigesti '%s' "
                        "is different than the one it's been trying to update on Odoo '%s'"
                    )
                    % (odoo_num_alb, order.name)
                )
            if order.state != "draft":
                state_option = dict(
                    order.fields_get(["state"], ["selection"])
                    .get("state")
                    .get("selection")
                )
                return _(
                    "The Order %s is already imported and is in state '%s' -> Update not allowed"
                    % (order.name, state_option[order.state])
                )
        else:
            if odoo_num_alb:
                raise ValidationError(
                    _(
                        "Inconsistent state: No binding found on Odoo but "
                        "there's Odoo_Numero_Albaran on Oxigesti '%s'"
                    )
                    % (odoo_num_alb)
                )
        return None

    def _import_dependencies(self):
        # customer
        external_id = (self.external_data["Codigo_Mutua"],)
        self._import_dependency(external_id, "oxigesti.res.partner", always=False)

        # products
        adapter = self.component(
            usage="backend.adapter", model_name="oxigesti.sale.order.line"
        )
        oxigesti_cargos_servicio = adapter.search(
            filters=[
                ("Codigo_Servicio", "=", self.external_data["Codigo_Servicio"]),
            ]
        )
        oxigesti_codigos_articulo = [
            adapter.id2dict(x)["CodigoArticulo"] for x in oxigesti_cargos_servicio
        ]

        exporter = self.component(
            usage="direct.batch.exporter", model_name="oxigesti.product.product"
        )
        exporter.run(
            domain=[
                ("company_id", "=", self.backend_record.company_id.id),
                ("default_code", "in", oxigesti_codigos_articulo),
            ]
        )

    def _after_import(self, binding):
        ## rebind the lines, for the sync date
        binder = self.binder_for("oxigesti.sale.order.line")
        for line in binding.oxigesti_order_line_ids:
            binder.bind(line.external_id, line)

        ## order validation
        binder = self.component(usage="binder")
        sale_order = binder.unwrap_binding(binding)
        sale_order.onchange_partner_id()
        for line in sale_order.order_line:
            line.product_id_change()
        sale_order.action_confirm()

        ## picking validation
        stock_order_lines = binding.oxigesti_order_line_ids.filtered(
            lambda x: x.move_ids
        )
        if stock_order_lines:
            try:
                binder = self.binder_for("oxigesti.sale.order.line")
                adapter = self.component(
                    usage="backend.adapter", model_name="oxigesti.sale.order.line"
                )
                picking_id = None
                for order_line_id in stock_order_lines:
                    if len(order_line_id.move_ids) > 1:
                        raise AssertionError(
                            "The order line '%s' has more than one move lines. "
                            "It should be exactly 1. " % (order_line_id,)
                        )
                    move_id = order_line_id.move_ids
                    if move_id.move_line_ids:
                        raise AssertionError(
                            "The movement '%s' already has lines. "
                            "It should be empty before inserting the new data"
                            % (move_id,)
                        )
                    if not picking_id:
                        picking_id = move_id.picking_id
                    else:
                        if picking_id != move_id.picking_id:
                            raise AssertionError(
                                "Unexpected error! The same order contains lines "
                                "belonging to a different picking '%s' and '%s'"
                                % (picking_id.name, move_id.picking_id.name)
                            )
                    move_line_id_d = {
                        "product_id": move_id.product_id.id,
                        "location_id": move_id.location_id.id,
                        "location_dest_id": move_id.location_dest_id.id,
                        "qty_done": move_id.product_uom_qty,
                        "product_uom_id": move_id.product_uom.id,
                        "picking_id": picking_id.id,
                    }

                    external_id = binder.to_external(order_line_id)
                    tracking_name = adapter.id2dict(external_id)["Partida"]

                    if not tracking_name and move_id.product_id.tracking == "lot":
                        tracking_name = "999"

                    if tracking_name:
                        Lot = self.env["stock.production.lot"]
                        lot_id = Lot.search(
                            [
                                ("company_id", "=", self.backend_record.company_id.id),
                                ("product_id", "=", move_id.product_id.id),
                                ("name", "=", tracking_name),
                            ]
                        )
                        picking_type_id = binding.warehouse_id.out_type_id
                        if not lot_id:
                            if not picking_type_id.use_create_lots:
                                raise AssertionError(
                                    "The creation of Lot/Serial number is "
                                    "not allowed in this operation type"
                                )
                            lot_id = Lot.create(
                                {
                                    "company_id": self.backend_record.company_id.id,
                                    "product_id": move_id.product_id.id,
                                    "name": tracking_name,
                                }
                            )
                        else:
                            if not picking_type_id.use_existing_lots:
                                raise AssertionError(
                                    "The use of existing Lot/Serial number is "
                                    "not allowed in this operation type"
                                )

                        move_line_id_d.update(
                            {
                                "lot_id": lot_id.id,
                            }
                        )
                    move_id.move_line_ids = [(0, False, move_line_id_d)]

                picking_id.button_validate()
            except:
                sale_order.action_cancel()
                sale_order.unlink()
                raise

        sale_order.action_done()
