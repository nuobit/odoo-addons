# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AnphitrionPMSTinyReservationBinding(models.Model):
    _inherit = "anphitrion.pms.tiny.reservation"

    def _prepare_import_data_domain(self, backend, since_date):
        domain = super()._prepare_import_data_domain(backend, since_date)
        if since_date:
            domain += [
                (
                    "analize_data",
                    {
                        "next_sync_date": backend.import_reservations_since_date,
                        "last_sync_date": since_date,
                    },
                )
            ]
        return domain
