# -*- coding: utf-8 -*-
# Copyright 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Binders
=======

Binders are components that know how to find the external ID for an
Odoo ID, how to find the Odoo ID for an external ID and how to
create the binding between them.

"""
import hashlib
import psycopg2
import logging

from odoo import fields, models, tools, _
from odoo.addons.component.core import AbstractComponent
from contextlib import contextmanager
from odoo.addons.connector.exception import (RetryableJobError, InvalidDataError)
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class BinderComposite(AbstractComponent):
    """ The same as Binder but allowing composite external keys

    """
    _name = 'base.binder.composite'
    _inherit = 'base.binder'

    _internal_field = 'internal_id'

    _internal_alt_id_field = "_internal_alt_id"
    _external_alt_id_field = "_external_alt_id"

    _default_binding_field = 'lengow_bind_ids'

    _odoo_extra_fields = []

    def idhash(self, external_id):
        _lengow_odoo_hash = hashlib.sha256()
        for e in external_id:
            if isinstance(e, int):
                e9 = str(e)
                if int(e9) != e:
                    raise Exception("Unexpected")
            elif isinstance(e, str):
                e9 = e
            elif e is None:
                pass
            else:
                raise Exception("Unexpected type for a key: type %" % type(e))
            _lengow_odoo_hash.update(e9.encode('utf8'))
        return _lengow_odoo_hash.hexdigest()

    def id2dict(self, _id, in_field=True):
        """ Return a dict with the internal or external fields and their values
        :param _id: Values to put on internal or external fields
        :param in_field: with True value, _internal_field defined in binder are used.
                        With this parameter False, _external_field will be used.
        """
        field = in_field and self._internal_field or self._external_field
        if not isinstance(_id, (tuple, list)):
            _id = [_id]
        else:
            if len(_id) == 1:
                raise ValidationError("If the id has only 1 element, it shouldn't be a list ")

        if not isinstance(field, (tuple, list)):
            field = [field]
        else:
            if len(field) == 1:
                raise ValidationError("If the id has only 1 element, it shouldn't be a list ")

        return dict(zip(field, _id))

    def dict2id(self, _dict, in_field=True):
        """ Giving a dict, return the values of the internal or external fields
        :param _dict: Dict (usually binder) to extract internal or external fields
        :param in_field: with True value, _internal_field defined in binder are used.
                        With this parameter False, _external_field will be used.
        """
        field = in_field and self._internal_field or self._external_field
        if isinstance(field, (tuple, list)):
            res = [_dict[x] for x in field]
            return len(res) == 1 and res[0] or res
        else:
            return _dict[field]

    @contextmanager
    def _retry_unique_violation(self):
        """ Context manager: catch Unique constraint error and retry the
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
                    'A database error caused the failure of the job:\n'
                    '%s\n\n'
                    'Likely due to 2 concurrent jobs wanting to create '
                    'the same record. The job will be retried later.' % err)
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
            raise Exception("The source object %s must not be a binding" % relation.model._name)

        if not set(self._odoo_extra_fields).issubset(set(binding_extra_vals.keys())):
            raise Exception("If _odoo_extra_fields are defined %s, "
                            "you must specify the correpsonding binding_extra_vals %s" % (
                                self._odoo_extra_fields, binding_extra_vals))
        domain = [(self._odoo_field, '=', relation.id),
                  (self._backend_field, '=', self.backend_record.id)]
        for f in self._odoo_extra_fields:
            domain.append((f, '=', binding_extra_vals[f]))
        binding = self.model.with_context(
            active_test=False).search(domain)
        if binding:
            binding.ensure_one()
        return binding

    def wrap_binding(self, relation, binding_field=None, binding_extra_vals={}):
        if not relation:
            return

        if binding_field is None:
            if not self._default_binding_field:
                raise Exception("_default_binding_field defined on synchronizer class is mandatory")
            binding_field = self._default_binding_field

        wrap = relation._name != self.model._name
        if wrap and hasattr(relation, binding_field):
            binding = self._find_binding(relation, binding_extra_vals)
            if not binding:
                _bind_values = {self._odoo_field: relation.id,
                                self._backend_field: self.backend_record.id}
                _bind_values.update(binding_extra_vals)
                with self._retry_unique_violation():
                    binding = (self.model
                               .with_context(connector_no_export=True)
                               .sudo()
                               .create(_bind_values))

                    if not tools.config['test_enable']:
                        self.env.cr.commit()  # nowait
        else:
            binding = relation

        if not self._is_binding(binding):
            raise Exception(
                "Expected binding '%s' and found regular model '%s'" % (self.model._name, relation._name))

        return binding

    def to_internal(self, external_id, unwrap=False):
        """ Give the Odoo recordset for an external ID

        :param external_id: external ID for which we want
                            the Odoo ID
        :param unwrap: if True, returns the normal record
                       else return the binding record
        :return: a recordset, depending on the value of unwrap,
                 or an empty recordset if the external_id is not mapped
        :rtype: recordset
        """
        context = self.env.context
        domain = [(self._backend_field, '=', self.backend_record.id)]
        for key, value in self.id2dict(external_id, in_field=True).items():
            domain.append((key, '=', value))

        bindings = self.model.with_context(active_test=False).search(
            domain
        )
        if not bindings:
            if unwrap:
                return self.model.browse()[self._odoo_field]
            return self.model.browse()
        bindings.ensure_one()
        if unwrap:
            bindings = bindings[self._odoo_field]
        bindings = bindings.with_context(context)
        return bindings

    def to_external(self, binding, wrap=False, wrapped_model=None, binding_extra_vals={}):
        """ Give the external ID for an Odoo binding ID

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
                    raise Exception("The wrapped model is mandatory if binding is not an object")
                binding = self.env[wrapped_model].browse(binding)
            else:
                binding = self.model.browse(binding)
        if wrap:
            binding = self._find_binding(binding, binding_extra_vals)
            if not binding:
                return None
        return self.dict2id(binding, in_field=True) or None

    def bind(self, external_id, binding):
        """ Create the link between an external ID and an Odoo ID

        :param external_id: external id to bind
        :param binding: Odoo record to bind
        :type binding: int
        """
        # Prevent False, None, or "", but not 0
        assert (external_id or external_id is 0) and binding, (
                "external_id or binding missing, "
                "got: %s, %s" % (external_id, binding)
        )
        # avoid to trigger the export when we modify the `external_id`
        now_fmt = fields.Datetime.now()
        if isinstance(binding, models.BaseModel):
            binding.ensure_one()
        else:
            binding = self.model.browse(binding)

        binding.with_context(connector_no_export=True).write({
            **self.id2dict(external_id, in_field=True),
            self._sync_date_field: now_fmt,
        })

    def _get_internal_record_domain(self, values):
        return [(k, "=", v) for k, v in values.items()]

    def _check_domain(self, domain):
        for field, _, value in domain:
            if isinstance(value, (list, tuple)):
                for e in value:
                    if isinstance(e, (tuple, list, set, dict)):
                        raise ValidationError(
                            _(
                                "Wrong domain value type '%s' on value '%s' of field '%s'"
                            )
                            % (type(e), e, field)
                        )

    def _get_internal_record_alt(self, model_name, values):
        domain = self._get_internal_record_domain(values)
        self._check_domain(domain)
        return self.env[model_name].search(domain)

    def wrap_record(self, relation):
        """Give the real record

        :param relation: Odoo real record for which we want to get its binding
        :param force: if this is True and not binding found it creates an
                      empty binding
        :return: binding corresponding to the real record or
                 empty recordset if the record has no binding
        """
        if isinstance(relation, models.BaseModel):
            relation.ensure_one()
        else:
            if not isinstance(relation, int):
                raise InvalidDataError(
                    "The real record (relation) must be a "
                    "regular Odoo record or an id (integer)"
                )
            relation = self.model.browse(relation)
            if not relation:
                raise InvalidDataError("The real record (relation) does not exist")

        if self.model._name == relation._name:
            raise Exception(
                _(
                    "The object '%s' is already wrapped, it's already a binding object. "
                    "You can only wrap Odoo objects"
                )
                % (relation)
            )

        binding = self.model.with_context(active_test=False).search(
            [
                (self._odoo_field, "=", relation.id),
                (self._backend_field, "=", self.backend_record.id),
            ]
        )
        if len(binding) > 1:
            raise InvalidDataError("More than one binding found")
        return binding

    def to_binding_from_external_key(self, mapper):
        """
        :param mapper:
        :return: binding with alternate external key
        """
        internal_alt_id = getattr(self, self._internal_alt_id_field, None)
        if internal_alt_id:
            if isinstance(internal_alt_id, str):
                internal_alt_id = [internal_alt_id]
            all_values = mapper.values(for_create=True)
            if any([x not in all_values for x in internal_alt_id]):
                raise InvalidDataError(
                    "The alternative id (_internal_alt_id) '%s' must exist on mapper"
                    % internal_alt_id
                )
            model_name = self.unwrap_model()
            id_values = {x: all_values[x] for x in internal_alt_id}
            record = self._get_internal_record_alt(model_name, id_values)
            if len(record) > 1:
                raise InvalidDataError(
                    "More than one internal records found. "
                    "The alternate internal id field '%s' is not unique"
                    % (internal_alt_id,)
                )
            if record:
                binding = self.wrap_record(record)
                if not binding:
                    values = {
                        k: all_values[k]
                        for k in set(self.model._fields) & set(all_values)
                    }
                    if self._odoo_field in values:
                        if values[self._odoo_field] != record.id:
                            raise InvalidDataError(
                                "The id found on the mapper ('%i') "
                                "is not the one expected ('%i')"
                                % (values[self._odoo_field], record.id)
                            )
                    else:
                        values[self._odoo_field] = record.id
                    binding = self.model.create(values)
                _logger.debug("%d linked from Backend", binding)
                return binding
        return self.model
