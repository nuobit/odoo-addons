# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
import collections
import logging
from itertools import zip_longest

from odoo import _, fields
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.components.mapper import m2o_to_external

_logger = logging.getLogger(__name__)


def required(*args):
    """Decorator, declare that a method is a required field.

    It is then used by the :py:class:`Mapper` to validate the records.

    Usage::

        @required
        def any(self, record):
            return {'output_field': record['input_field']}

    """

    def required_mapping(func):
        func.required = args
        return func

    return required_mapping
    # func.is_required = True
    # return func


class ConnectorExtensionMapper(AbstractComponent):
    _name = "connector.extension.mapper"
    _inherit = "base.mapper"

    def _apply_with_options(self, map_record):
        """
        Hack to allow having non required children field
        """
        assert (
            self.options is not None
        ), "options should be defined with '_mapping_options'"
        _logger.debug("converting record %s to model %s", map_record.source, self.model)

        fields = self.options.fields
        for_create = self.options.for_create
        result = {}
        for from_attr, to_attr in self.direct:
            if isinstance(from_attr, collections.abc.Callable):
                attr_name = self._direct_source_field_name(from_attr)
            else:
                attr_name = from_attr

            if not fields or attr_name in fields:
                value = self._map_direct(map_record.source, from_attr, to_attr)
                result[to_attr] = value

        for meth, definition in self.map_methods:
            mapping_changed_by = definition.changed_by
            if not fields or (
                mapping_changed_by and mapping_changed_by.intersection(fields)
            ):
                if definition.only_create and not for_create:
                    continue
                values = meth(map_record.source)
                if not values:
                    continue
                if not isinstance(values, dict):
                    raise ValueError(
                        "%s: invalid return value for the "
                        "mapping method %s" % (values, meth)
                    )
                if not self.options.get("ignore_required_fields"):
                    for field_required in getattr(meth, "required", []):
                        if field_required not in values or not values[field_required]:
                            raise ValidationError(
                                _("Missing required field '%s'") % field_required
                            )
                result.update(values)

        for from_attr, to_attr, model_name in self.children:
            if not fields or from_attr in fields:
                if from_attr in map_record.source:
                    items = self._map_child(map_record, from_attr, to_attr, model_name)
                    if items:
                        result[to_attr] = items
        return self.finalize(map_record, result)

    def get_target_fields(self, map_record, fields):
        if not fields:
            return []
        fields = set(fields)
        result = {}
        for from_attr, to_attr in self.direct:
            if isinstance(from_attr, collections.abc.Callable):
                from_attr = self._direct_source_field_name(from_attr)

            if to_attr in fields:
                if to_attr in result:
                    raise ValidationError(_("Field '%s' mapping defined twice"))
                result[to_attr] = from_attr

        # TODO: create a new decorator to write the field mapping manually
        #   I think this is not necessary, just use changed_by is precisely for that
        for meth, definition in self.map_methods:
            mapping_changed_by = definition.changed_by
            if definition.changed_by:
                if len(definition.changed_by) > 1:
                    raise ValidationError(_("Changed by can only be one field"))
                values = meth(map_record.source)
                if len(values) != 1:
                    raise ValidationError(
                        _(
                            "Return values of a mapper must be unique "
                            "if it has changed by decorator"
                        )
                    )
                from_attr, to_attr = list(mapping_changed_by)[0], list(values.keys())[0]
                if to_attr in fields:
                    if to_attr in result:
                        raise ValidationError(
                            _("Field '%s' mapping defined twice") % to_attr
                        )
                    result[to_attr] = from_attr
        for from_attr, to_attr, _model_name in self.children:
            if to_attr in fields:
                if to_attr in result:
                    raise ValidationError(
                        _("Field '%s' mapping defined twice") % to_attr
                    )
                result[to_attr] = from_attr
        return list(set(result.values()))


class ConnectorExtensionChildMapper(AbstractComponent):
    _name = "connector.extension.child.mapper"
    _inherit = "base.map.child"

    def get_all_items(self, mapper, items, parent, to_attr, options):
        mapped = []
        for item in items:
            map_record = mapper.map_record(item, parent=parent)
            if self.skip_item(map_record):
                continue
            item_values = self.get_item_values(map_record, to_attr, options)
            if item_values:
                self._child_bind(map_record, item_values)
                mapped.append(item_values)
        return mapped

    def get_items(self, items, parent, to_attr, options):
        mapper = self._child_mapper()
        mapped = self.get_all_items(mapper, items, parent, to_attr, options)
        mapped = self.classify_items(mapped, to_attr, options)
        return self.format_items(mapped)

    def _child_bind(self, map_record, item_values):
        raise NotImplementedError

    def classify_items(self, mapped, to_attr, options):
        raise NotImplementedError


class ConnectorExtensionMapChildImport(AbstractComponent):
    _name = "connector.extension.map.child.import"
    _inherit = ["base.map.child.import", "connector.extension.child.mapper"]

    def _child_bind(self, map_record, item_values):
        binder = self.binder_for()
        if not binder._is_wrapped(self.model):
            return
        external_id = binder.dict2id(map_record.source, in_field=False)
        values = {
            binder._backend_field: self.backend_record.id,
            binder._sync_date_field: fields.Datetime.now(),
            **binder.id2dict(external_id, in_field=True),
            **binder._additional_internal_binding_fields(map_record.source),
        }
        if map_record.parent:
            binding = binder.to_internal(external_id, unwrap=False)
            if not binding:
                record = binder._to_record_from_external_key(map_record)
                if record:
                    values.update({binder._odoo_field: record.id})
        item_values.update(values)

    def format_items(self, items_values):
        ops = []
        for values in items_values:
            _id = values.pop("id", None)
            if _id:
                if values:
                    ops.append((1, _id, values))
                else:
                    ops.append((2, _id, False))
            else:
                ops.append((0, False, values))
        return ops

    def _prepare_existing_records(self, records):
        return records

    def classify_items(self, mapped, to_attr, options):
        def keygen(_id):
            return tuple(binder.dict2id(_id))

        binding = options["binding"]
        binder = self.binder_for()
        if binding:
            existing = {}
            for rec in self._prepare_existing_records(options["binding"][to_attr]):
                existing.setdefault(keygen(rec), []).append(rec.id)
            new = {}
            for value in mapped:
                new.setdefault(keygen(value), []).append(value)
            res = []
            # update ( create,delete )
            for key in set(existing.keys()) & set(new.keys()):
                for _id, value in zip_longest(existing[key], new[key]):
                    # update
                    if value and _id:
                        res.append({"id": _id, **value})
                    # delete
                    elif not value:
                        res.append({"id": _id})
                    # create
                    elif not _id:
                        res.append(value)
            # create
            for key in set(new.keys()) - set(existing.keys()):
                res += new[key]
            # delete
            for key in set(existing.keys()) - set(new.keys()):
                res += [{"id": x} for x in existing[key]]
            return res
        return mapped


class ConnectorExtensionMapChildExport(AbstractComponent):
    _name = "connector.extension.map.child.export"
    _inherit = ["base.map.child.export", "connector.extension.child.mapper"]

    def _child_bind(self, map_record, item_values):
        # TODO: implement this method
        return
        # raise NotImplementedError

    def classify_items(self, mapped, to_attr, options):
        return mapped


# TODO: create a fix on OCA repo and remove this class
class ConnectorExtensionExportMapper(AbstractComponent):
    _name = "connector.extension.export.mapper"
    _inherit = ["base.export.mapper", "connector.extension.mapper"]

    def _map_direct(self, record, from_attr, to_attr):
        """Apply the ``direct`` mappings.

        :param record: record to convert from a source to a target
        :param from_attr: name of the source attribute or a callable
        :type from_attr: callable | str
        :param to_attr: name of the target attribute
        :type to_attr: str
        """
        if isinstance(from_attr, collections.abc.Callable):
            return from_attr(self, record, to_attr)

        value = record[from_attr]
        if value is None:  # we need to allow fields with value 0
            return False

        # Backward compatibility: when a field is a relation, and a modifier is
        # not used, we assume that the relation model is a binding.
        # Use an explicit modifier m2o_to_external  in the 'direct' mappings to
        # change that.
        field = self.model._fields[from_attr]
        if field.type == "many2one":
            mapping_func = m2o_to_external(from_attr)
            value = mapping_func(self, record, to_attr)
        return value

    def check_external_id(self, external_id, relation):
        assert external_id, (
            "Unexpected error on %s:"
            "The backend id cannot be obtained."
            "At this stage, the backend record should have been already linked via "
            "._export_dependencies. " % relation._name
        )


class ConnectorExtensionImportMapper(AbstractComponent):
    _name = "connector.extension.import.mapper"
    _inherit = ["base.import.mapper", "connector.extension.mapper"]


class ConnectorExtensionDeleteMapChild(AbstractComponent):
    """:py:class:`MapChild` for the Deleters"""

    _name = "connector.extension.base.map.child.deleter"
    _inherit = "base.map.child"
    _usage = "delete.map.child"

    def _child_mapper(self):
        return self.component(usage="import.mapper")

    def format_items(self, items_values):
        """Format the values of the items mapped from the child Mappers.

        It can be overridden for instance to add the Odoo
        relationships commands ``(6, 0, [IDs])``, ...

        As instance, it can be modified to handle update of existing
        items: check if an 'id' has been defined by
        :py:meth:`get_item_values` then use the ``(1, ID, {values}``)
        command

        :param items_values: list of values for the items to create
        :type items_values: list

        """
        return [(0, 0, values) for values in items_values]
