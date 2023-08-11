# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component

DEBUG_FILE = "connector_pms_tiny_anphitrion_debug.csv"

HEADERS = [
    "next_sync_date",
    "last_sync_date",
    "domain",
    "NumReserva",
    "SNumero",
    "FechaModificada",
    "Anulada",
    "FechaCancelada",
]


class AnphitrionPMSTinyReservationAdapter(Component):
    _inherit = "anphitrion.pms.tiny.reservation.adapter"

    def search_read(self, domain):
        analize_data = None
        new_domain = []
        for e in domain:
            if e[0] == "analize_data":
                analize_data = e[1]
            else:
                new_domain.append(e)
        res = super().search_read(new_domain)
        if analize_data:
            res_ord = sorted(res, key=lambda x: x["FechaModificada"])
            utc2local = self.backend_record.tz_to_local
            new_file = False
            try:
                with open(DEBUG_FILE, "r"):
                    pass
            except FileNotFoundError:
                new_file = True
            with open(DEBUG_FILE, "a") as f:
                if new_file:
                    f.write(",".join(HEADERS) + "\n")
                if not res_ord:
                    line = [
                        utc2local(analize_data["next_sync_date"]).isoformat(),
                        utc2local(analize_data["last_sync_date"]).isoformat(),
                        str(new_domain),
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                    f.write(",".join(map(lambda x: f'"{x}"', line)) + "\n")
                else:
                    for rec in res_ord:
                        line = [
                            utc2local(analize_data["next_sync_date"]).isoformat(),
                            utc2local(analize_data["last_sync_date"]).isoformat(),
                            str(new_domain),
                            str(rec["NumReserva"]),
                            rec["SNumero"],
                            utc2local(rec["FechaModificada"]).isoformat(),
                            str(rec["Anulada"]),
                            utc2local(rec["FechaCancelada"]).isoformat()
                            if rec["FechaCancelada"]
                            else "",
                        ]
                        f.write(",".join(map(lambda x: f'"{x}"', line)) + "\n")
        return res
