# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models

from odoo.addons.base.models.res_users import (
    is_reified_group,
    name_boolean_group,
    name_selection_groups,
)


class ResUsers(models.Model):
    _inherit = "res.users"

    def write(self, vals):
        """Take the users who leave the Restricted tasks group off its marked
        tasks. Only a write of the groups can make anyone leave, directly or
        through the user form's group fields."""
        if "groups_id" not in vals and not any(map(is_reified_group, vals)):
            return super().write(vals)
        with self.env["project.task"]._restricted_leavers_removed():
            return super().write(vals)

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """The user form edits groups through generated fields that send no
        onchange (`base/models/res_users.py`). Make the Restricted tasks
        checkbox and the User Type send one, so that leaving the group through
        either of them can warn."""
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        arch = etree.fromstring(result["arch"])
        nodes = arch.xpath(
            "//field[@name=$group or @name=$user_type]",
            group=self._restricted_group_field(),
            user_type=self._restricted_user_type_field(),
        )
        if nodes:
            for node in nodes:
                node.set("on_change", "1")
            result["arch"] = etree.tostring(arch, encoding="unicode")
        return result

    def onchange(self, values, field_name, field_onchange):
        """Before a member leaves the Restricted tasks group on the user form,
        by unticking it or by stopping being an internal user, warn how many
        marked tasks they will be taken off. Odoo answers a generated group
        field with an empty result, so there is no other warning to keep."""
        result = super().onchange(values, field_name, field_onchange)
        names = field_name if isinstance(field_name, list) else [field_name]
        group_field = self._restricted_group_field()
        user_type_field = self._restricted_user_type_field()
        leaving = (group_field in names and not values.get(group_field)) or (
            user_type_field in names
            and values.get(user_type_field) != self.env.ref("base.group_user").id
        )
        if leaving:
            tasks = self.env["project.task"]
            warning = tasks._restricted_leave_warning(
                self & tasks._restricted_members()
            )
            if warning is not None:
                result["warning"] = warning
        return result

    @api.model
    def _restricted_group_field(self):
        """The user form's checkbox of the Restricted tasks group."""
        return name_boolean_group(
            self.env.ref("project_task_restricted.group_restricted_task").id
        )

    @api.model
    def _restricted_user_type_field(self):
        """The user form's User Type, the choice among internal, portal and
        public user."""
        user_types = self.env["res.groups"].search(
            [("category_id", "=", self.env.ref("base.module_category_user_type").id)]
        )
        return name_selection_groups(user_types.ids)
