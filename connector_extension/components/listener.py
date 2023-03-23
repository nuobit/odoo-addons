# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent


class ConnectorExtensionEventListener(AbstractComponent):
    _name = "connector.extension.event.listener"
    _inherit = "base.event.listener"

    def on_record_after_unlink(self, binding_data):
        # Binding data is a dictionary with the following keys
        # - backend: backend
        # - binding_name: the name of the binding model
        # - external_id: the external id of the record to delete
        # It's normally called AFTER actual deletion on Odoo
        external_id = binding_data.get("external_id")
        if not external_id:
            raise ValidationError(_("The external_id of the binding is null"))
        with binding_data["backend"].work_on(binding_data["binding_name"]) as work:
            work.component(usage="record.direct.deleter").run(external_id)
