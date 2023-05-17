# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WordPressIrAttachmentBinder(Component):
    _name = "wordpress.ir.attachment.binder"
    _inherit = "wordpress.binder"

    _apply_on = "wordpress.ir.attachment"

    # This checksum is included manually for search purposes and avoid exporting the same image twice
    external_id = "id"
    internal_id = "wordpress_idattachment"

    # # todo: call super
    # def _additional_internal_binding_fields(self, external_data):
    #     return {"checksum": external_data["checksum"]}

    # def wrap_record(self, relation):
    #     binding= super(WordPressIrAttachmentBinder, self).wrap_record(relation)
    #     if not binding:
    #         other_bindings=self.env["wordpress.ir.attachment"].search([("checksum", "=", relation.checksum)])
    #         if other_bindings:
    #             binding =
    #         binding =
    #     return binding
