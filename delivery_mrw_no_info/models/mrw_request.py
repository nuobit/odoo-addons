# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime
import logging

import pytz

from odoo.addons.delivery_mrw.models.mrw_request import MRWRequest

_logger = logging.getLogger(__name__)

_original_get_tracking_states = MRWRequest._get_tracking_states


def _get_tracking_states(self, vals):
    response = _original_get_tracking_states(self, vals)
    if response["MensajeSeguimiento"] != "Busqueda correcta por Número de Albarán.":
        response["MensajeSeguimiento"] = "Busqueda correcta por Número de Albarán."
        date = datetime.datetime.now(pytz.timezone("Europe/Madrid"))
        response["Seguimiento"]["Abonado"].append(
            {
                "SeguimientoAbonado": {
                    "Seguimiento": [
                        {
                            "Estado": "60",
                            "EstadoDescripcion": "Información no disponible, "
                            "contacte con su Fq.",
                            "FechaEntrega": date.strftime("%d%m%Y"),
                            "HoraEntrega": date.strftime("%H%M"),
                        }
                    ]
                }
            }
        )
    return response


MRWRequest._get_tracking_states = _get_tracking_states
