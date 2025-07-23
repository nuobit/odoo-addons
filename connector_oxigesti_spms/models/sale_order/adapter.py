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
        SELECT f."Id", -- PK
       f."UnidadeLocalSalude", -- client FK: service_spms_facturas_ULS
       f."DataFim", -- date order
       f."Fecha_Modifica",
       f."Invoice_Id",
       f."Odoo_Verificado"
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
        line_adapter = self.component(
            usage="backend.adapter", model_name="oxigesti.spms.sale.order.line"
        )
        for order in orders:
            order["lines"] = line_adapter.search_read(
                domain=[("FacturaId", "=", order["Id"])],
            )
        return orders
