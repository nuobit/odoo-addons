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

from odoo.addons.component.exception import NoComponentError
from odoo.addons.connector.exception import (RetryableJobError, InvalidDataError)
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class BinderComposite(AbstractComponent):
    """ The same as Binder but allowing composite external keys

    """
    _name = 'base.binder.composite'
    _inherit = 'base.binder'

    _internal_field = 'internal_id'

    _internal_alt_field = "_internal_alt_id"
    _external_alt_field = "_external_alt_id"

    _binding_field = None

    _odoo_extra_fields = []

    def idhash(self, external_id):
        odoo_hash = hashlib.sha256()
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
            odoo_hash.update(e9.encode('utf8'))
        return odoo_hash.hexdigest()

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
            constraint "my_backend_product_template_odoo_uniq"
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
            binding._model_fields[self._odoo_field]
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
            if not self._binding_field:
                raise Exception("_binding_field defined on synchronizer class is mandatory")
            binding_field = self._binding_field

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

    def bind_import(self, external_data, values):
        external_id = self.dict2id(external_data, in_field=False)
        values.update({
            self._backend_field: self.backend_record.id,
            self._sync_date_field: fields.Datetime.now(),
            **self.id2dict(external_id, in_field=True),
            **self._additional_internal_binding_fields(external_data),
        })
        with self._retry_unique_violation():
            return self.model.with_context(connector_no_export=True).create(values)

    def bind_export(self, external_data, relation):
        """ Create the link between an external ID and an Odoo ID

        :param external_id: external id to bind
        :param binding: Odoo record to bind
        :type binding: int
        """
        assert external_data and relation, (
            "external_data or relation missing, "
            "got: %s, %s" % (external_data, relation)
        )
        # avoid to trigger the export when we modify the `external_id`
        if isinstance(relation, models.BaseModel):
            relation.ensure_one()
            relation_id = relation.id
        else:
            relation_id = relation

        external_id = self.dict2id(external_data, in_field=False)
        with self._retry_unique_violation():
            return self.model.with_context(connector_no_export=True).create({
                self._backend_field: self.backend_record.id,
                self._odoo_field: relation_id,
                self._sync_date_field: fields.Datetime.now(),
                **self.id2dict(external_id, in_field=True),
                **self._additional_external_binding_fields(external_data),
            })

    def _additional_external_binding_fields(self, external_data):
        return {}

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

    def _to_record_from_external_key(self, map_record):
        """
        :param map_record:
        :return: binding with alternate external key
        """
        model_name = self.unwrap_model()
        internal_alt_id = self._internal_alt_field
        if internal_alt_id:
            if isinstance(internal_alt_id, str):
                internal_alt_id = [internal_alt_id]
            all_values = map_record.values(for_create=True, binding=self.model)
            if any([x not in all_values for x in internal_alt_id]):
                raise InvalidDataError(
                    "The alternative id (_internal_alt_field) '%s' must exist on mapper"
                    % internal_alt_id
                )
            id_values = {x: all_values[x] for x in internal_alt_id}
            record = self._get_internal_record_alt(model_name, id_values)
            if len(record) > 1:
                raise InvalidDataError(
                    "More than one '%s' found with id %s. "
                    "The alternate internal id field '%s' is not unique"
                    % (model_name, id_values, internal_alt_id)
                )
            return record
        return self.env[model_name]

    def to_binding_from_external_key(self, map_record):
        """
        :param map_record:
        :return: binding with alternate external key
        """
        record = self._to_record_from_external_key(map_record)
        if record:
            binding = self.wrap_record(record)
            if not binding:
                all_values = map_record.values(for_create=True, binding=self.model)
                values = {
                    k: all_values[k]
                    for k in set(self.model._model_fields) & set(all_values)
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
                binding = self.bind_import(map_record.source, values)
            _logger.debug("%d linked from Backend", binding)
            return binding
        return self.model

    def _additional_internal_binding_fields(self, external_data):
        return {}

    def _get_external_record_domain(self, values):
        return [(k, "=", v) for k, v in values.items()]

    def _get_external_record_alt(self, values):
        domain = self._get_external_record_domain(values)
        adapter = self.component(usage="backend.adapter")
        return adapter.search_read(domain)

    def to_binding_from_internal_key(self, relation):
        """
        Given an odoo object (not binding object) without binding related
        :param relation: odoo object, not a binding and without binding
        :return: binding
        """
        ext_alt_id = self._external_alt_field
        if not ext_alt_id:
            return self.model

        if isinstance(ext_alt_id, str):
            ext_alt_id = [ext_alt_id]

        export_mapper = self.component(usage="export.mapper")
        mapper_external_data = export_mapper.map_record(relation)
        id_fields = mapper_external_data._mapper.get_target_fields(
            mapper_external_data, fields=ext_alt_id
        )
        if not id_fields:
            raise ValidationError(
                _("External alternative id '%s' not found in export mapper")
                % (ext_alt_id,)
            )
        id_values = mapper_external_data.values(for_create=True, fields=id_fields, binding=self.model)
        record = self._get_external_record_alt(id_values)
        if record:
            if len(record) > 1:
                raise InvalidDataError(
                    "More than one external records found. "
                    "The alternate external id field '%s' is not "
                    "unique in the backend" % (ext_alt_id,)
                )
            record = record[0]
            external_id = self.dict2id(record, in_field=False)
            binding = self.wrap_record(relation)
            if binding:
                current_external_id = self.to_external(binding)
                if current_external_id != external_id:
                    raise InvalidDataError(
                        "Integrity error: The current external_id '%s' "
                        "should be the same as the one we are trying "
                        "to assign '%s'" % (current_external_id, external_id)
                    )
                _logger.debug("%d already binded to Backend", binding)
            else:
                import_mapper_exists = True
                try:
                    import_mapper = self.component(usage="import.mapper")
                    mapper_internal_data = import_mapper.map_record(record)
                    binding_ext_fields = mapper_internal_data._mapper.get_target_fields(
                        mapper_internal_data, fields=self.model._model_fields
                    )
                    importer = self.component(usage="direct.record.importer")
                    importer.run(
                        external_id,
                        external_data=record,
                        external_fields=binding_ext_fields,
                    )
                    binding = self.to_internal(external_id)
                except NoComponentError:
                    import_mapper_exists = False
                if not import_mapper_exists:
                    binding = self.bind_export(record, relation)
                    binding[self._sync_date_field] = fields.Datetime.now()
            if not binding:
                raise InvalidDataError(
                    "The binding with external id '%s' "
                    "not found and it should be" % external_id
                )
            _logger.debug("%d linked to Backend", binding)
            return binding

        return self.model

    def unwrap_binding(self, binding):
        if isinstance(binding, models.BaseModel):
            odoo_object_ids = binding.mapped(lambda x: x[self._odoo_field].id)
        else:
            odoo_object_ids = [binding]
        return self.model.browse(odoo_object_ids)

# TODO: naming the methods more intuitively
# TODO: unify both methods, they have a lot of common code
# TODO: extract parts to smaller and common methods reused by the main methods
# TODO: use .new instead of dicts on to_binding_from_internal_key
