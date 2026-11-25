# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

EDITABLE_FILES = "editable_file_ids"


def _models_with_editable_files(model, path):
    """The names of the models whose editable files the field path ``path`` of
    ``model`` goes through."""
    name, _dot, rest = path.partition(".")
    field = model._fields.get(name)
    here = {model._name} if field is not None and name == EDITABLE_FILES else set()
    further = (
        _models_with_editable_files(model.env[field.comodel_name], rest)
        if field is not None and field.relational and rest
        else set()
    )
    return here | further


class DocumentPageEditableMixin(models.AbstractModel):
    _name = "document.page.editable.mixin"
    _description = "Searches on the editable files"

    # Odoo 14 checks the groups of a field when the field is read or written, not
    # when a search filters by it: a user who cannot see the editable files would
    # learn from what such a search returns which documents and versions hold
    # them. A search and a grouped search pass their domain here before they
    # query, which is where Odoo 18 checks the groups of the fields it names. Odoo
    # neither groups nor sorts by a one2many, so the domain is all there is to
    # check. Each condition's field path is followed here: Odoo searches the
    # model behind each step of a path, which brings that step here too, except
    # behind a field with auto_join, such as the document's history_head, which
    # it joins without searching
    def _flush_search(self, domain, fields=None, order=None, seen=None):
        model_names = set().union(
            *(
                _models_with_editable_files(self, arg[0])
                for arg in domain
                if not isinstance(arg, str) and isinstance(arg[0], str)
            )
        )
        for model_name in model_names:
            self.env[model_name].check_field_access_rights("read", [EDITABLE_FILES])
        return super()._flush_search(domain, fields=fields, order=order, seen=seen)
