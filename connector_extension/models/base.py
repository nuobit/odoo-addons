# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

"""
Base Model
==========

Extend the 'base' Odoo Model to add Events related features.


"""

from odoo import models


class Base(models.AbstractModel):
    """The base model, which is implicitly inherited by all models.

    Add an :meth:`_event` method to all Models. This method allows to
    trigger events.

    It also notifies the following events:

    * ``on_record_post_unlink(self, bindings_data)``

    ``on_record_post_unlink`` is notified just *after* the unlink is done.

    """

    _inherit = "base"

    def _dict_binding_data(self, binding):
        with binding.backend_id.work_on(binding._name) as work:
            binder = work.component(usage="binder")
            external_id = binder.to_external(binding)
            return {
                "backend": binding.backend_id,
                "binding_name": binding._name,
                "external_id": external_id,
            }

    def unlink(self):
        to_remove = []
        binding_field = self.env.context.get("binding_field")
        if binding_field:
            for record in self:
                bindings = record[binding_field]
                for binding in bindings:
                    to_remove.append(self._dict_binding_data(binding))
        result = super(Base, self).unlink()
        for bindings_data in to_remove:
            self._event("on_record_after_unlink").notify(bindings_data)
        return result
