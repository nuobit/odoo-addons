# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class OxigestiSPMSSaleOrderAdapter(Component):
    _name = "oxigesti.spms.sale.order.adapter"
    _inherit = "oxigesti.spms.adapter"

    _apply_on = "oxigesti.spms.sale.order"
    _sql_read = """
        SELECT f."Id",
       f."UnidadeLocalSalude",
       f."DataFactura",
       f."Fecha_Modifica",
       f."Invoice_Id"
        FROM dbo.Odoo_SPMS_Facturas f
    """

    _sql_update = """UPDATE c
                        SET %(qset)s
                        FROM dbo.Odoo_SPMS_Facturas  c
                        WHERE c.Id = %%(Id)s
                   """

    def _create(self, values):
        raise ValidationError(
            _("Create operation is not supported on products by Oxigesti SPMS.")
        )

    def search_read(self, domain=None):
        orders = super().search_read(domain=domain)
        if orders:
            order_ids = [x["Id"] for x in orders if "Id"]
            line_adapter = self.component(
                usage="backend.adapter", model_name="oxigesti.spms.sale.order.line"
            )

            lines = line_adapter.search_read(
                domain=[("FacturaId", "in", order_ids)],
            )
            lines_d = {}

            for line in lines:
                lines_d.setdefault(line["FacturaId"], []).append(line)

            if lines_d:
                for order in orders:
                    order["lines"] = lines_d[order["Id"]]

        return orders
