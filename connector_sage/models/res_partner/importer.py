# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


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

    def _create_binding(self, internal_data):
        create_vals = internal_data.values(for_create=True)
        vat = create_vals.get("vat")
        company_id = create_vals.get("company_id")
        if vat:
            related = self.env["res.partner"].search(
                [("vat", "=", vat), ("company_id", "in", [False, company_id])], limit=1
            )
            if related:
                vals = internal_data.values()
                vals["odoo_id"] = related.id
                return self.model.with_company(self.backend_record.company_id).create(
                    vals
                )
        return super()._create_binding(internal_data)
