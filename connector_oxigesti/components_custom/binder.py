# Copyright 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Binders
=======

Binders are components that know how to find the external ID for an
Odoo ID, how to find the Odoo ID for an external ID and how to
create the binding between them.

"""
import json
from contextlib import contextmanager

import psycopg2

import odoo
from odoo import fields, models

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import RetryableJobError


class BinderComposite(AbstractComponent):
    """The same as Binder but allowing composite external keys"""

    _name = "base.binder.composite"
    _inherit = "base.binder"

    _default_binding_field = "oxigesti_bind_ids"
    _external_display_field = "external_id_display"

    _odoo_extra_fields = []

    @contextmanager
    def _retry_unique_violation(self):
        """Context manager: catch Unique constraint error and retry the
        job later.

        When we execute several jobs workers concurrently, it happens
        that 2 jobs are creating the same record at the same time (binding
        record created by :meth:`_export_dependency`), resulting in:

            IntegrityError: duplicate key value violates unique
            constraint "my_backend_product_product_odoo_uniq"
            DETAIL:  Key (backend_id, odoo_id)=(1, 4851) already exists.

        In that case, we'll retry the import just later.

        .. warning:: The unique constraint must be created on the
                     binding record to prevent 2 bindings to be created
                     for the same External record.

        """
        try:
            yield
        except psycopg2.IntegrityError as err:
            if err.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                raise RetryableJobError(
                    "A database error caused the failure of the job:\n"
                    "%s\n\n"
                    "Likely due to 2 concurrent jobs wanting to create "
                    "the same record. The job will be retried later." % err
                )
            else:
                raise

    def _is_binding(self, binding):
        try:
            binding._fields[self._odoo_field]
        except KeyError:
            return False

        return True

    def _find_binding(self, relation, binding_extra_vals={}):
        if self._is_binding(relation):
            raise Exception(
                "The source object %s must not be a binding" % relation.model._name
            )

        if not set(self._odoo_extra_fields).issubset(set(binding_extra_vals.keys())):
            raise Exception(
                "If _odoo_extra_fields are defined %s, "
                "you must specify the correpsonding binding_extra_vals %s"
                % (self._odoo_extra_fields, binding_extra_vals)
            )
        domain = [
            (self._odoo_field, "=", relation.id),
            (self._backend_field, "=", self.backend_record.id),
        ]
        for f in self._odoo_extra_fields:
            domain.append((f, "=", binding_extra_vals[f]))
        binding = self.model.with_context(active_test=False).search(domain)

        if binding:
            binding.ensure_one()

        return binding

    def wrap_binding(self, relation, binding_field=None, binding_extra_vals={}):
        if not relation:
            return

        if binding_field is None:
            if not self._default_binding_field:
                raise Exception(
                    "_default_binding_field defined on synchronizer class is mandatory"
                )
            binding_field = self._default_binding_field

        # wrap is typically True if the relation is a 'product.product'
        # record but the binding model is 'oxigesti.product.product'
        wrap = relation._name != self.model._name
        if wrap and hasattr(relation, binding_field):
            binding = self._find_binding(relation, binding_extra_vals)
            if not binding:
                # we are working with a unwrapped record (e.g.
                # product.template) and the binding does not exist yet.
                # Example: I created a product.product and its binding
                # oxigesti.product.product, it is exported, but we need to
                # create the binding for the template.
                _bind_values = {
                    self._odoo_field: relation.id,
                    self._backend_field: self.backend_record.id,
                }
                _bind_values.update(binding_extra_vals)
                # If 2 jobs create it at the same time, retry
                # one later. A unique constraint (backend_id,
                # odoo_id) should exist on the binding model
                with self._retry_unique_violation():
                    binding = (
                        self.model.with_context(connector_no_export=True)
                        .sudo()
                        .create(_bind_values)
                    )

                    # Eager commit to avoid having 2 jobs
                    # exporting at the same time. The constraint
                    # will pop if an other job already created
                    # the same binding. It will be caught and
                    # raise a RetryableJobError.
                    if not odoo.tools.config["test_enable"]:
                        self.env.cr.commit()  # nowait
        else:
            # If oxigest_bind_ids does not exist we are typically in a
            # "direct" binding (the binding record is the same record).
            # If wrap is True, relation is already a binding record.
            binding = relation

        if not self._is_binding(binding):
            raise Exception(
                "Expected binding '%s' and found regular model '%s'"
                % (self.model._name, relation._name)
            )

        return binding

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
        domain = [
            (self._backend_field, "=", self.backend_record.id),
            (self._external_display_field, "=", json.dumps(external_id)),
        ]
        bindings = self.model.with_context(active_test=False).search(domain)
        if not bindings:
            if unwrap:
                return self.model.browse()[self._odoo_field]
            return self.model.browse()
        bindings.ensure_one()
        if unwrap:
            bindings = bindings[self._odoo_field]
        return bindings

    def to_external(
        self, binding, wrap=False, wrapped_model=None, binding_extra_vals={}
    ):
        """Give the external ID for an Odoo binding ID

        :param binding: Odoo binding for which we want the external id
        :param wrap: if True, binding is a normal record, the
                     method will search the corresponding binding and return
                     the external id of the binding
        :return: external ID of the record
        """
        if isinstance(binding, models.BaseModel):
            binding.ensure_one()
        else:
            if wrap:
                if not wrapped_model:
                    raise Exception(
                        "The wrapped model is mandatory if binding is not an object"
                    )
                binding = self.env[wrapped_model].browse(binding)
            else:
                binding = self.model.browse(binding)
        if wrap:
            binding = self._find_binding(binding, binding_extra_vals)
            if not binding:
                return None

        return binding[self._external_field] or None

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

        binding.with_context(connector_no_export=True).write(
            {
                self._external_field: external_id,
                self._sync_date_field: now_fmt,
            }
        )

    def _get_external_id(self, binding):
        return None
