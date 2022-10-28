# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    # Prepared in case they want this again
    # def _prepare_mrw_bultos(self, picking):
    #     bultos = []
    #     for _i in range(picking.number_of_packages):
    #         bultos.append(
    #             {
    #                 "Alto": 1,
    #                 "Largo": 1,
    #                 "Ancho": 1,
    #                 "Dimension": "",
    #                 "Referencia": "",
    #                 "Peso": 1,
    #             }
    #         )
    #     return {"BultoRequest": bultos}

    def _prepare_mrw_shipping(self, picking):
        num_bultos = picking.with_context(
            force_write_number_of_packages=True
        ).number_of_packages
        res = super()._prepare_mrw_shipping(picking)
        res["DatosServicio"]["Referencia"] = (
            picking.sale_id.client_order_ref or picking.sale_id.name or "",
        )
        res["DatosServicio"]["NumeroBultos"] = num_bultos
        # if picking.number_of_packages > 1:
        #     bultos = self._prepare_mrw_bultos(picking)
        #     res["DatosServicio"]["Bultos"] = bultos
        #     res["DatosServicio"]["Peso"] = picking.number_of_packages
        return res
