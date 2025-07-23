# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class OxigestiSPMSProductProductAdapter(Component):
    _name = "oxigesti.spms.product.product.adapter"
    _inherit = "oxigesti.spms.adapter"

    _apply_on = "oxigesti.spms.product.product"

    _sql_read = """
        SELECT p."Id",
         p."Codigo",
       p."Nome",
       p."PrecoUnitario",
       p."Articulo_Odoo",
       p."Fecha_Modifica",
       p."Lote"
        FROM dbo.Odoo_SPMS_Sistemas p
        """
    _sql_update = """UPDATE p
                        SET %(qset)s
                        FROM dbo.Odoo_SPMS_Sistemas p
                        WHERE p.Id = %%(Id)s
                   """

    def _create(self, values):
        raise ValidationError(
            _("Create operation is not supported on products by Oxigesti SPMS.")
        )
