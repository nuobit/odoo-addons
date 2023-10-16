# Copyright 2013-2017 Camptocamp SA
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

"""
Binders
=======

Binders are components that know how to find the external ID for an
Odoo ID, how to find the Odoo ID for an external ID and how to
create the binding between them.

"""
import hashlib
import logging
from contextlib import contextmanager

import psycopg2

import odoo
from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.component.exception import NoComponentError
from odoo.addons.connector.exception import InvalidDataError, RetryableJobError

_logger = logging.getLogger(__name__)


class BinderComposite(AbstractComponent):
    """The same as Binder but allowing composite external keys"""

    _name = "generic.binder"
    _inherit = "base.binder"

    _internal_field = "internal_id"

    _internal_alt_field = "internal_alt_id"
    _external_alt_field = "external_alt_id"

    _default_binding_field = None

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
                raise Exception("Unexpected type for a key: type %s" % type(e))
            odoo_hash.update(e9.encode("utf8"))
        return odoo_hash.hexdigest()

    def get_id_fields(self, in_field=True, alt_field=False):
        if in_field:
            fields = self._internal_alt_field if alt_field else self._internal_field
        else:
            fields = self._external_alt_field if alt_field else self._external_field
        if not isinstance(fields, (tuple, list)):
            fields = [fields]
        fields_l = []
        for f in fields:
            if hasattr(self, f):
                fields = getattr(self, f)
                if isinstance(fields, (tuple, list)):
                    fields_l.extend(fields)
                else:
                    fields_l.append(fields)
            else:
                raise ValidationError(
                    _("Id field %(FIELD)s is not defined in model %(MODEL)s")
                    % {
                        "FIELD": f,
                        "MODEL": self._name,
                    }
                )
        return fields_l

    def id2dict(self, _id, in_field=True, alt_field=False):
        """Return a dict with the internal or external fields and their values
        :param _id: Values to put on internal or external fields
        :param in_field: with True value, _internal_field defined in binder are used.
                        With this parameter False, _external_field will be used.
        """
        if _id:
            fields = self.get_id_fields(in_field=in_field, alt_field=alt_field)
            return dict(zip(fields, _id))
        else:
            return None

    # This Function returns a dict with the external ids from a "dirty" dict
    def dict2id2dict(self, _dict, in_field=True, alt_field=False):
        """Giving a dict, return the a dict with internal or external ids
        :param _dict: Dict to extract internal or external fields
        :param in_field: with True value, _internal_field defined in binder are used.
                        With this parameter False, _external_field will be used.
        :param alt_field: with True value, alternative id fields defined in binder are used.
        """
        return self.id2dict(
            self.dict2id(_dict, in_field=in_field, alt_field=alt_field),
            in_field=in_field,
            alt_field=alt_field,
        )

    def dict2id(self, _dict, in_field=True, alt_field=False, unwrap=False):
        """Giving a dict, return the values of the internal or external fields
        :param _dict: Dict (usually binder) to extract internal or external fields
        :param in_field: with True value, _internal_field defined in binder are used.
                        With this parameter False, _external_field will be used.
        """
        fields = self.get_id_fields(in_field=in_field, alt_field=alt_field)
        res = []
        for f in fields:
            f_splitted = f.split(".")
            if f_splitted[0] in _dict or _dict.get(f_splitted[0]) is not None:
                val = _dict[f_splitted[0]]
            else:
                return None
            if len(f_splitted) == 2:
                if isinstance(val, models.BaseModel):
                    val = val[f_splitted[1]]
            if len(f_splitted) > 2:
                raise NotImplementedError(_("Multiple dot notation is not supported"))
            res.append(val)
        if unwrap:
            if len(res) == 1:
                return res[0]
            else:
                raise ValidationError(_("It's not possible to unwrap a composite id"))
        return res

    def is_complete_id(self, _id, in_field=True):
        fields = in_field and self._internal_field or self._external_field
        if not isinstance(fields, (tuple, list)):
            fields = [fields]
        if not isinstance(_id, (tuple, list)):
            _id = [_id]
        _id = list(filter(None, _id))
        return len(_id) == len(fields)

    @contextmanager
    def _retry_unique_violation(self):
        """Context manager: catch Unique constraint error and retry the
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
                    "A database error caused the failure of the job:\n"
                    "%s\n\n"
                    "Likely due to 2 concurrent jobs wanting to create "
                    "the same record. The job will be retried later." % err
                ) from err
            else:
                raise

    def _is_binding(self, binding):
        try:
            binding._fields[self._odoo_field]
        except KeyError:
            return False
        return True

    def _find_binding(self, relation, binding_extra_vals=None):
        if not binding_extra_vals:
            binding_extra_vals = {}
        if self._is_binding(relation):
            raise Exception(
                "The source object %s must not be a binding" % relation.model._name
            )

        domain = [
            (self._odoo_field, "=", relation.id),
            (self._backend_field, "=", self.backend_record.id),
        ]
        binding = self.model.with_context(active_test=False).search(domain)
        if binding:
            binding.ensure_one()
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
        context = self.env.context
        domain = [(self._backend_field, "=", self.backend_record.id)]
        for key, value in self.id2dict(external_id, in_field=True).items():
            domain.append((key, "=", value))

        bindings = self.model.with_context(active_test=False).search(domain)
        if not bindings:
            if unwrap:
                return self.model.browse()[self._odoo_field]
            return self.model.browse()
        bindings.ensure_one()
        if unwrap:
            bindings = bindings[self._odoo_field]
        bindings = bindings.with_context(**context)
        return bindings

    def to_external(self, binding, wrap=True, binding_extra_vals=None):
        """Give the external ID for an Odoo binding ID

        :param binding: Odoo binding for which we want the external id
        :param wrap: if False, binding is a normal record, the
                     method will search the corresponding binding and return
                     the external id of the binding
        :return: external ID of the record
        """
        if not binding_extra_vals:
            binding_extra_vals = {}
        if not wrap:
            binding = self._find_binding(binding, binding_extra_vals)
            if not binding:
                return None
        return self.dict2id(binding, in_field=True) or None

    def bind(self, external_id, binding):
        raise ValidationError(
            _("This method is deprecated. Use bind_export or bind_import instead")
        )

    def bind_import(self, external_data, values, sync_date, for_create=False):
        values.update(
            {
                self._sync_date_field: sync_date,
                **self._additional_internal_binding_fields(external_data),
            }
        )
        if for_create:
            external_id = self.dict2id(external_data, in_field=False)
            values.update(
                {
                    self._backend_field: self.backend_record.id,
                    **self.id2dict(external_id, in_field=True),
                }
            )

    def bind_export(self, external_data, relation):
        """Create the link between an external ID and an Odoo ID

        :param external_id: external id to bind
        :param binding: Odoo record to bind
        :type binding: int
        """
        assert (
            external_data and relation
        ), "external_data or relation missing, " "got: %s, %s" % (
            external_data,
            relation,
        )
        # avoid to trigger the export when we modify the `external_id`
        if isinstance(relation, models.BaseModel):
            relation.ensure_one()
            relation_id = relation.id
        else:
            relation_id = relation

        external_id = self.dict2id(external_data, in_field=False)
        with self._retry_unique_violation():
            binding = self.model.with_context(connector_no_export=True).create(
                {
                    self._backend_field: self.backend_record.id,
                    self._odoo_field: relation_id,
                    self._sync_date_field: fields.Datetime.now(),
                    **self.id2dict(external_id, in_field=True),
                    **self._additional_external_binding_fields(external_data),
                }
            )
            # Eager commit to avoid having 2 jobs
            # exporting at the same time. The constraint
            # will pop if an other job already created
            # the same binding. It will be caught and
            # raise a RetryableJobError.
            if not odoo.tools.config["test_enable"]:
                self.env.cr.commit()  # pylint: disable=E8102
            return binding

    def _additional_external_binding_fields(self, external_data):
        return {}

    def is_id_null(self, _id):
        if not isinstance(_id, (list, tuple)):
            _id = [_id]
        for value in _id:
            if value is None:
                return True
        return False

    def _get_internal_record_domain(self, values):
        return [(k, "=", v) for k, v in values.items()]

    def _check_domain(self, domain):
        for field, _op, value in domain:
            if isinstance(value, (list, tuple)):
                for e in value:
                    if isinstance(e, (tuple, list, set, dict)):
                        raise ValidationError(
                            _(
                                "Wrong domain value type '%(TYPE)s' on value "
                                "'%(VALUE)s' of field '%(FIELD)s'"
                            )
                            % {
                                "TYPE": type(e),
                                "VALUE": e,
                                "FIELD": field,
                            }
                        )

    def _get_internal_record_alt(self, values):
        model_name = self.unwrap_model()
        domain = self._get_internal_record_domain(values)
        self._check_domain(domain)
        return self.env[model_name].search(domain)

    def wrap_record(self, relation):
        """Give the real record

        :param relation: Odoo real record for which we want to get its binding
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
                % relation
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
        internal_alt_id = getattr(self, self._internal_alt_field, None)
        if internal_alt_id:
            if isinstance(internal_alt_id, str):
                internal_alt_id = [internal_alt_id]
            all_values = map_record.values(for_create=True, binding=self.model)
            if any([x not in all_values for x in internal_alt_id]):
                raise InvalidDataError(
                    "The alternative id '%s' must exist on mapper" % internal_alt_id
                )
            id_values = {x: all_values[x] for x in internal_alt_id}
            record = self._get_internal_record_alt(id_values)
            if len(record) > 1:
                raise InvalidDataError(
                    "More than one '%s' found with id %s: %s "
                    "The alternate internal id field '%s' is not unique"
                    % (model_name, id_values, record.ids, internal_alt_id)
                )
            return record
        return self.env[model_name]

    def to_binding_from_external_key(self, map_record, sync_date):
        """
        :param map_record:
        :return: binding with alternate external key
        """
        record = self._to_record_from_external_key(map_record)
        if record:
            binding = self.wrap_record(record)
            if not binding:
                binding_only_fields = set(binding._fields) - set(record._fields)
                update_values = map_record.values()
                values = {
                    k: update_values[k]
                    for k in binding_only_fields & set(update_values)
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
                self.bind_import(map_record.source, values, sync_date, for_create=True)
                importer = self.component(usage="record.direct.importer")
                binding = importer._create(values)
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

        ext_alt_id = getattr(self, self._external_alt_field, None)
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
        id_values = mapper_external_data.values(
            for_create=True,
            fields=id_fields,
            binding=self.model,
            ignore_required_fields=True,
        )
        record = self._get_external_record_alt(id_values)
        # TODO: check if we can put this in a hook
        external_alt_id = self.dict2id(id_values, in_field=False, alt_field=True)
        if self.is_id_null(external_alt_id):
            return self.model
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
                        mapper_internal_data, fields=self.model._fields
                    )
                    importer = self.component(usage="record.direct.importer")
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
        if not isinstance(binding, models.BaseModel):
            if isinstance(binding, (tuple, list)):
                odoo_object_ids = binding
            elif isinstance(binding, int):
                odoo_object_ids = [binding]
            else:
                raise ValidationError(_("Invalid binding type"))
            binding = self.model.browse(odoo_object_ids)
        return binding.mapped(self._odoo_field)

    def get_external_dict_ids(self, relation, check_external_id=True):
        external_id = self.to_external(relation, wrap=False)
        if check_external_id:
            assert external_id, (
                "Unexpected error on %s:"
                "The backend id cannot be obtained."
                "At this stage, the backend record should have been already linked via "
                "._export_dependencies. " % relation._name
            )
        return self.id2dict(external_id, in_field=False)


# TODO: naming the methods more intuitively
# TODO: unify both methods, they have a lot of common code
# TODO: extract parts to smaller and common methods reused by the main methods
# TODO: use .new instead of dicts on to_binding_from_internal_key
