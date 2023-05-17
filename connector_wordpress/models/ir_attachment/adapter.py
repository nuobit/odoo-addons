# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressIrAttachment(Component):
    _name = "wordpress.ir.attachment.adapter"
    _inherit = "wordpress.adapter"

    _apply_on = "wordpress.ir.attachment"

    def create(self, data):  # pylint: disable=W8106
        attachment_id = data.pop("id")
        attachment = self.env["ir.attachment"].browse(attachment_id)
        binded_attachments_ids = self.env["ir.attachment"].search(
            [
                (
                    "id",
                    "in",
                    self.env["wordpress.ir.attachment"]
                    .search([])
                    .mapped("odoo_id")
                    .ids,
                ),
                ("checksum", "=", attachment.checksum),
            ],
            limit=1,
        )
        alternative_binding_id = (
            self.env["wordpress.ir.attachment"]
            .search([("odoo_id", "=", binded_attachments_ids.id)])
            .wordpress_idattachment
        )
        if alternative_binding_id:
            return {"id": alternative_binding_id}
        return self._exec("post", "media", data=data)
