# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class OxigestiSPMSSPMSLotAdapter(Component):
    _name = "oxigesti.spms.spms.lot.adapter"
    _inherit = "oxigesti.spms.adapter"

    _apply_on = "oxigesti.spms.spms.lot"

    _sql_read = """
        SELECT  p."Id",
                p."Nome"
        FROM dbo.Odoo_SPMS_Lotes p
        """
    _sql_update = """UPDATE c
                            SET %(qset)s
                            FROM dbo.Odoo_SPMS_Lotes c
                            WHERE c.Id = %%(Id)s
                       """

    _sql_insert = """INSERT INTO dbo.Odoo_SPMS_Lotes
                         (%(fields)s)
                     VALUES (%(phvalues)s);
                     SELECT scope_identity() AS %(retvalues)s;
                     """

    def _create(self, values):
        raise ValidationError(
            _("Create operation is not supported on products by Oxigesti SPMS.")
        )
