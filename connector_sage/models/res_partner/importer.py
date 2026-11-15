# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ResPartnerBatchImporter(Component):
    """Import the Sage Partners.

    For every partner in the list, a delayed job is created.
    """

    _name = "sage.res.partner.delayed.batch.importer"
    _inherit = "sage.delayed.batch.importer"
    _apply_on = "sage.res.partner"


class ResPartnerImporter(Component):
    _name = "sage.res.partner.importer"
    _inherit = "sage.importer"
    _apply_on = "sage.res.partner"

    def _validate_update(self, binding, values):
        """Stop the import when the employee code was reassigned in Sage.

        Sage reuses employee codes: a code can be given to a different
        person. The partner vat holds the identity the code belonged to
        when it was first imported (the euvat mapping is @only_create, so
        no later sync rewrites it): a different incoming SiglaNacion+Dni
        means the code changed hands, and updating would relabel the
        employee while the partner keeps the old person, misattributing
        payroll payments. The error message documents both unlock
        procedures.

        Partners without vat (e.g. excluded by
        employees_exclude_nif_pattern) cannot be checked and are skipped.
        """
        vat = binding.odoo_id.vat
        mapper = self.component(usage="import.mapper")
        incoming_dni = mapper.sage_identity(self.external_data)
        if not vat or not incoming_dni or vat == incoming_dni:
            return
        incoming_name = " ".join(
            part
            for part in (
                self.external_data["NombreEmpleado"],
                self.external_data["PrimerApellidoEmpleado"],
                self.external_data["SegundoApellidoEmpleado"],
            )
            if part
        )
        raise ValidationError(
            _(
                "The Sage employee code %(company)s/%(code)s seems to have "
                "been reassigned to a different person: it belonged to "
                "'%(partner)s' (VAT %(vat)s) but Sage now returns "
                "'%(incoming_name)s' (DNI %(incoming_dni)s). The import of "
                "this record has been stopped to avoid mixing people.\n"
                "- If this is the same person with a new identity document, "
                "update the partner VAT and retry the job.\n"
                "- If the code was really reassigned to a new person, delete "
                "the Sage bindings (partner and employee) of this code and "
                "retry the job; the old partner and employee will be kept, "
                "unbound."
            )
            % {
                "company": binding.sage_codigo_empresa,
                "code": binding.sage_codigo_empleado,
                "partner": binding.odoo_id.display_name,
                "vat": vat,
                "incoming_name": incoming_name,
                "incoming_dni": incoming_dni,
            }
        )
