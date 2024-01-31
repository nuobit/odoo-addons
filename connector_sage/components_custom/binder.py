# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Binders
=======

Binders are components that know how to find the external ID for an
Odoo ID, how to find the Odoo ID for an external ID and how to
create the binding between them.

"""

from odoo import fields, models

from odoo.addons.component.core import AbstractComponent


class SageBinderComposite(AbstractComponent):
    """The same as Binder but allowing composite external keys"""

    _name = "base.binder.composite"
    _inherit = "base.binder"

    def to_binding_from_external_key(self, internal_data):
        return self.model

    def to_internal(self, external_id, unwrap=False):
        """Give the Odoo recordset for an external ID

        :param external_id: external ID for which we want
                            the Odoo ID
        :param unwrap: if True, returns the normal record
                       else return the binding record
        :return: a recordset, depending on the value of unwrap,
                 or an empty recordset if the external_id is not mapped
        :rtype: recordset
        """
        if isinstance(self._external_field, str):
            self._external_field = [self._external_field]

        domain = [(self._backend_field, "=", self.backend_record.id)]
        for k, v in zip(self._external_field, external_id):
            domain.append((k, "=", v))

        bindings = self.model.with_context(active_test=False).search(domain)
        if not bindings:
            if unwrap:
                return self.model.browse()[self._odoo_field]
            return self.model.browse()
        bindings.ensure_one()
        if unwrap:
            bindings = bindings[self._odoo_field]
        return bindings

    def to_external(self, binding, wrap=False):
        """Give the external ID for an Odoo binding ID

        :param binding: Odoo binding for which we want the external id
        :param wrap: if True, binding is a normal record, the
                     method will search the corresponding binding and return
                     the external id of the binding
        :return: external ID of the record
        """
        if isinstance(self._external_field, str):
            self._external_field = [self._external_field]

        if isinstance(binding, models.BaseModel):
            binding.ensure_one()
        else:
            binding = self.model.browse(binding)
        if wrap:
            binding = self.model.with_context(active_test=False).search(
                [
                    (self._odoo_field, "=", binding.id),
                    (self._backend_field, "=", self.backend_record.id),
                ]
            )
            if not binding:
                return None
            binding.ensure_one()
            return [binding[f] for f in self._external_field]
        return [binding[f] for f in self._external_field]

    def bind(self, external_id, binding):
        """Create the link between an external ID and an Odoo ID

        :param external_id: external id to bind
        :param binding: Odoo record to bind
        :type binding: int
        """
        # Prevent False, None, or "", but not 0
        assert (
            external_id or external_id == 0
        ) and binding, "external_id or binding missing, " "got: %s, %s" % (
            external_id,
            binding,
        )
        # avoid to trigger the export when we modify the `external_id`
        now_fmt = fields.Datetime.now()
        if isinstance(binding, models.BaseModel):
            binding.ensure_one()
        else:
            binding = self.model.browse(binding)

        if isinstance(self._external_field, str):
            self._external_field = [self._external_field]

        values = {self._sync_date_field: now_fmt}
        values.update(dict(zip(self._external_field, external_id)))

        binding.with_context(connector_no_export=True).write(values)
