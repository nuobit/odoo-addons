# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


def map_op(op):
    if op == "=":
        op = "=="
    return op


class QualityTreeMixin(models.AbstractModel):
    _name = "quality.tree.mixin"
    _description = "Quality Tree Mixin"

    # complete_name
    complete_name = fields.Char(
        "Complete Name",
        compute="_compute_complete_name",
        search="_search_complete_name",
    )

    def get_complete_name(self):
        self.ensure_one()

        def get_node_ancestors_chain(parent_id, child_ids):
            if not parent_id:
                return child_ids
            else:
                return get_node_ancestors_chain(
                    parent_id.parent_id, parent_id | child_ids
                )

        return " / ".join(
            get_node_ancestors_chain(self, self.env[self._name]).mapped("name")
        )

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = "%s / %s" % (rec.parent_id.complete_name, rec.name)
            else:
                rec.complete_name = rec.name

    def _search_complete_name(self, operator, value):
        node_ids = []
        for node in self.env[self._name].search([]):
            complete_name = node.get_complete_name()
            if operator == "=":
                if value == complete_name:
                    node_ids.append(node.id)
            elif operator == "!=":
                if value != complete_name:
                    node_ids.append(node.id)
            elif operator == "like":
                if value in complete_name:
                    node_ids.append(node.id)
            elif operator == "ilike":
                if value.lower() in complete_name.lower():
                    node_ids.append(node.id)
            elif operator == "=like":
                if value == complete_name:
                    node_ids.append(node.id)
            elif operator == "=ilike":
                if value.lower() == complete_name.lower():
                    node_ids.append(node.id)
            else:
                raise UserError(_("Operator %s not implemented") % operator)
        return [("id", "in", node_ids)]

    @api.model
    def get_leaf_from_complete_name(self, complete_name):
        def complete_name_to_leaf(parent, childs):
            if not childs:
                return parent
            else:
                nodes = self.env[self._name].search(
                    [
                        ("parent_id", "=", parent.id),
                        ("name", "=", childs[0]),
                    ]
                )
                leafs = self.env[self._name]
                for node in nodes:
                    leafs += complete_name_to_leaf(node, childs[1:])
                return leafs

        return complete_name_to_leaf(self.env[self._name], complete_name.split(" / "))

    # level
    level = fields.Integer(
        string="Level",
        compute="_compute_level",
        search="_search_level",
        # store=True
    )

    def _get_level(self):
        self.ensure_one()
        if not self.parent_id:
            return 0
        else:
            return self.parent_id._get_level() + 1

    @api.depends("parent_id")
    def _compute_level(self):
        for rec in self:
            rec.level = rec._get_level()

    def _search_level(self, operator, value):
        node_ids = []
        for node in self.env[self._name].search([]):
            level = node._get_level()
            if safe_eval("%s %s %s" % (level, map_op(operator), value)):
                node_ids.append((node.id, level))
        return [("id", "in", node_ids)]

    # root
    def _get_root(self):
        self.ensure_one()
        if not self.parent_id:
            return self
        else:
            return self.parent_id._get_root()
