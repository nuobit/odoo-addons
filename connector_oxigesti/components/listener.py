# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent


class OxigestiEventListener(AbstractComponent):
    _name = "oxigesti.event.listener"
    _inherit = "base.event.listener"

    def on_record_post_unlink(self, backend_external):
        # executed AFTER actual deletion on Odoo
        for backend_id, binding_name, external_id in backend_external:
            backend = self.env["oxigesti.backend"].browse(backend_id)
            with backend.work_on(binding_name) as work:
                adapter = work.component(usage="backend.adapter")
                if not external_id:
                    raise ValidationError("The external_id of the binding is null")
                adapter.delete(external_id)
