# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class OxigestiSpmsResPartnerAdapter(Component):
    _name = "oxigesti.spms.res.partner.adapter"
    _inherit = "oxigesti.spms.adapter"

    _apply_on = "oxigesti.spms.res.partner"

    _sql_read = r"""
        SELECT
            c."Id",
            c."UnidadeLocalSalude",
            c."Cidade",
            c."CodigoPostal",
            c."Domicilio",
            c."NIF",
            c."CodigoConvencao",
            c."Cliente_Odoo",
            c."Fecha_Modifica"
        FROM dbo.Odoo_SPMS_ULS c
    """

    _sql_insert = """INSERT INTO dbo.Odoo_SPMS_ULS
                                 (%(fields)s)
                             VALUES (%(phvalues)s);
                             SELECT scope_identity() AS %(retvalues)s;
                             """

    _sql_update = """UPDATE c
                     SET %(qset)s
                     FROM dbo.Odoo_SPMS_ULS c
                     WHERE c.Id = %%(Id)s
                """

    def _create(self, values):
        raise ValidationError(
            _("Create operation is not supported on partners by Oxigesti SPMS.")
        )
