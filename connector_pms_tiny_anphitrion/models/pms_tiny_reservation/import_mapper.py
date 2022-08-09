# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime
import json

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class AnphitrionPMSTinyReservationImportMapper(Component):
    _name = "anphitrion.pms.tiny.reservation.import.mapper"
    _inherit = "anphitrion.import.mapper"

    _apply_on = "anphitrion.pms.tiny.reservation"

    children = [
        ("Habitaciones", "aphitrion_room_ids", "anphitrion.pms.tiny.reservation.room")
    ]

    direct = [
        ("Entrada", "checkin_date"),
        ("Salida", "checkout_date"),
        ("FechaModificada", "updated_date"),
    ]

    @only_create
    @mapping
    def property_id(self, record):
        return {"property_id": self.backend_record.property_id.id}

    # @mapping
    # def state(self, record):
    #     if record["FechaCancelada"]:
    #         state = 'cancel'
    #     else:
    #         binding = self.options.get("binding")
    #         if binding:
    #             if record["FechaModificada"] and binding.updated_date:
    #                 if record["FechaModificada"] > binding.updated_date:
    #                     state = 'modified'
    #             elif record["FechaModificada"] and not binding.updated_date:
    #                 state = 'modified'
    #         else:
    #             state = 'new'
    #     return {"state": state}

    @only_create
    @mapping
    def code(self, record):
        return {"code": record["NumReserva"]}

    @only_create
    @mapping
    def date(self, record):
        return {"date": record["FechaReserva"]}

    @only_create
    @mapping
    def locator(self, record):
        return {"locator": record["SNumero"]}

    @only_create
    @mapping
    def agency_code(self, record):
        return {"agency_code": record["Agencia"]}

    @mapping
    def raw_data(self, record):
        # convert data to json to store in a model
        def _convert(data):
            if isinstance(data, (datetime.datetime, datetime.date)):
                data = data.isoformat()
            return data

        return {
            "raw_data": json.dumps(
                record, default=_convert, indent=4, ensure_ascii=False
            )
        }
