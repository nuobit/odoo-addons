# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class LMTreeMixin(models.AbstractModel):
    _name = "lm.tree.mixin"
    _description = "LMTreeMixin"

    # complete_name
    complete_name = fields.Char(
        string="Complete Name",
        compute="_compute_complete_name",
        search="_search_complete_name",
    )

    def name_get(self):
        vals = []
        for record in self:
            vals.append((record.id, record.complete_name))
        return vals

    def _get_node_ancestors_chain(self):
        self.ensure_one()
        return (
            self.parent_id
            and self.parent_id._get_node_ancestors_chain()
            or self.env[self._name]
        ) | self

    @api.depends("parent_id")
    def _compute_complete_chain_ids(self):
        for rec in self:
            rec.complete_chain_ids = rec._get_node_ancestors_chain()

    def get_complete_name(self):
        self.ensure_one()
        return " / ".join(self.complete_chain_ids.mapped("name"))

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = "%s / %s" % (rec.parent_id.complete_name, rec.name)
            else:
                rec.complete_name = rec.name

    def _search_complete_name(self, operator, value):
        operation_mapping = {
            "=": lambda x, y: x == y,
            "!=": lambda x, y: x != y,
            "like": lambda x, y: x in y,
            "not like": lambda x, y: x not in y,
            "ilike": lambda x, y: x.lower() in y.lower(),
            "not ilike": lambda x, y: x.lower() not in y.lower(),
            "=like": lambda x, y: x == y,
            "=ilike": lambda x, y: x.lower() == y.lower(),
        }
        if operator not in operation_mapping:
            raise UserError(_("Operator %s not implemented") % operator)
        node_ids = []
        for node in self.env[self._name].search([]):
            complete_name = node.get_complete_name()
            if operation_mapping[operator](value, complete_name):
                node_ids.append(node.id)

        return [("id", "in", node_ids)]
