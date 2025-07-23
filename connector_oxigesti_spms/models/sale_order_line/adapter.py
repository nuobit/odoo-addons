# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SaleOrderLineAdapter(Component):
    _name = "oxigesti.spms.sale.order.line.adapter"
    _inherit = "oxigesti.spms.adapter"

    _apply_on = "oxigesti.spms.sale.order.line"

    _sql_read = """
        SELECT f.Id,
            f.NumeroLinha,
            f."LinhaDispensa_Sistema",
            f."LinhaDispensa_Quantidade",
            f."LinhaDispensa_Contexto",  c."Codigo" AS "CodigoContexto",
            f."NumeroPrescricao",
            f."NumeroUtente",
            f."NumeroBenef",
            f.TipoPrescricao,   p."Codigo" AS "CodigoPrescricao",
            f."DataInicio",
            f."DataFim",
            f."MotivoSuspensao", m."Codigo" AS "CodigoMotivoSuspensao",
            f."FacturaId"
            FROM dbo.Odoo_SPMS_Facturas_Dispensas f
                    INNER JOIN dbo.Odoo_SPMS_Contextos c ON f."LinhaDispensa_Contexto" = c."Id"
                    INNER JOIN dbo.Odoo_SPMS_TipoPrescricao p ON f."TipoPrescricao"  = p."Id"
                    LEFT JOIN dbo.Odoo_SPMS_MotivoSuspensao m ON f."MotivoSuspensao" = m."Id"

            """
