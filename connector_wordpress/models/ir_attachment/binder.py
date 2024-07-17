# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressIrAttachmentBinder(Component):
    _name = "wordpress.ir.attachment.binder"
    _inherit = "wordpress.binder"

    _apply_on = "wordpress.ir.attachment"

    external_id = "id"
    internal_id = "wordpress_idattachment"

    def _get_external_record_domain(self, relation, values):
        equivalent_binding_attachment = self.env["wordpress.ir.attachment"].search(
            [
                ("checksum", "=", relation.checksum),
                ("backend_id", "=", self.backend_record.id),
            ],
            limit=1,
        )
        if equivalent_binding_attachment:
            return [("id", "=", equivalent_binding_attachment.wordpress_idattachment)]
        else:
            return None

    def _additional_external_binding_fields(self, external_data, relation):
        return {
            **super()._additional_external_binding_fields(external_data, relation),
            "wordpress_source_url": external_data["source_url"],
        }
