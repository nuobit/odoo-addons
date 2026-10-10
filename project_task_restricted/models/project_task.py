# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from contextlib import contextmanager

from markupsafe import escape

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task"

    restricted = fields.Boolean(
        groups="project_task_restricted.group_restricted_task",
        tracking=True,
        help="Hide this task from everyone outside the Restricted tasks group.",
    )

    @api.constrains("restricted", "user_ids")
    def _check_restricted_user_ids(self):
        members = self._restricted_members()
        for task in self._filter_restricted():
            outsiders = task.user_ids - members
            if outsiders:
                raise task._restricted_assignee_error(outsiders)

    @api.constrains("restricted")
    def _check_restricted_activity_users(self):
        members = self._restricted_members()
        for task in self._filter_restricted():
            outsiders = task.sudo().activity_ids.user_id - members
            if outsiders:
                raise task._restricted_activity_error(outsiders)

    def _restricted_assignee_error(self, outsiders):
        """The error for users outside the group assigned to this marked
        task."""
        self.ensure_one()
        return ValidationError(
            _(
                "Only members of the Restricted tasks group can be assigned to "
                'the restricted task "%(task)s". Not in the group: %(users)s. '
                "Remove them from the assignees, or untick Restricted.",
                task=self.name,
                users=", ".join(outsiders.mapped("name")),
            )
        )

    def _restricted_activity_error(self, outsiders):
        """The error for users outside the group with activities on this
        marked task."""
        self.ensure_one()
        return ValidationError(
            _(
                "Only members of the Restricted tasks group can have activities "
                'on the restricted task "%(task)s". Not in the group: %(users)s. '
                "Assign those activities to a member, or untick Restricted.",
                task=self.name,
                users=", ".join(outsiders.mapped("name")),
            )
        )

    @api.model
    def _restricted_refuse_partners(self, model, res_id, partners, refusal):
        """Refuse partners outside the group for a document reference (a
        model name and an id) when it is a marked task; refusal words it,
        from the task and those partners."""
        task = self._restricted_task_of(model, res_id)
        outsiders = task._restricted_outsiders(partners)
        if outsiders:
            raise UserError(refusal(task, outsiders))

    @api.onchange("parent_id")
    def _onchange_parent_id_restricted(self):
        """A new task with a marked parent in the form, picked or given by the
        context, gets marked, and its creator may untick it."""
        if not self._origin and self.parent_id._filter_restricted():
            self.restricted = True

    @api.model_create_multi
    def create(self, vals_list):
        """A new subtask of a marked task is born marked, unless whoever
        creates it sets the mark. The parent is the one Odoo gives it: the
        value, or else the context's default."""
        default_parent_id = self.env.context.get("default_parent_id")
        parent_ids = [vals.get("parent_id", default_parent_id) for vals in vals_list]
        marked_parent_ids = (
            self.browse({parent_id for parent_id in parent_ids if parent_id})
            .exists()
            ._filter_restricted()
            .ids
        )
        return super().create(
            [
                dict(vals, restricted=True)
                if "restricted" not in vals and parent_id in marked_parent_ids
                else vals
                for vals, parent_id in zip(vals_list, parent_ids)
            ]
        )

    def write(self, vals):
        newly_marked = (
            self - self._filter_restricted()
            if vals.get("restricted")
            else self.browse()
        )
        res = super().write(vals)
        newly_marked._restricted_revoke_outsiders()
        return res

    @api.model
    def _restricted_members(self):
        return (
            self.env.ref("project_task_restricted.group_restricted_task")
            .sudo()
            .with_context(active_test=False)
            .users
        )

    def _filter_restricted(self):
        """The marked tasks of self. Only the group can read the field, while
        these checks run for every user, so it is read as superuser."""
        return self.filtered(lambda task: task.sudo().restricted)

    @api.model
    def _restricted_task_of(self, model, res_id):
        """The marked task a document reference (a model name and an id)
        points to, or an empty recordset."""
        tasks = self.browse(res_id) if model == self._name else self.browse()
        return tasks.exists()._filter_restricted()

    @api.model
    def _restricted_reference_search(self, model_field, id_field, operator, value):
        """The domain for a search on the `restricted` field of a model whose
        records point to a document through a model-name field and an id
        field: the records about a marked task, or the others."""
        if operator == "=":
            about_marked = bool(value)
        elif operator == "!=":
            about_marked = not value
        else:
            raise ValueError(
                "Restricted is searched with = or !=, not with %s" % operator
            )
        tasks = (
            self.sudo()
            .with_context(active_test=False)
            .search([("restricted", "=", True)])
        )
        domain = [(model_field, "=", self._name), (id_field, "in", tasks.ids)]
        return domain if about_marked else ["!"] + expression.normalize_domain(domain)

    def _restricted_outsiders(self, partners):
        """Those of partners outside the Restricted tasks group, when this is
        a marked task; nobody without one."""
        if not self:
            return partners.browse()
        return partners - self._restricted_members().partner_id

    @api.model
    def _restricted_user_is_member(self):
        """Whether the current user belongs to the Restricted tasks group."""
        return self.env.user in self._restricted_members()

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        """The portal pages search tasks as superuser once their address
        carries a token, even one never checked against the project. There a
        visitor outside the group finds no marked task."""
        if (
            self.env.context.get("restricted_portal")
            and not self._restricted_user_is_member()
        ):
            args = expression.AND([args, [("restricted", "=", False)]])
        return super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )

    def _portal_ensure_token(self):
        """A marked task has no portal link: whoever held it would read the
        task as superuser, member or not."""
        if self._filter_restricted():
            return None
        return super()._portal_ensure_token()

    def _sign_token(self, pid):
        """Nor a signature to post on it from the portal: Odoo signs over the
        task's token, the same empty value on every marked task, so a
        signature made for one would post on all of them as superuser. An
        empty signature matches none."""
        if self._filter_restricted():
            return ""
        return super()._sign_token(pid)

    def _get_depends_tracked_fields(self):
        """A marked task reports none of its changes to the tasks it blocks:
        Odoo would post them, with its name, on those tasks."""
        if self._filter_restricted():
            return set()
        return super()._get_depends_tracked_fields()

    def _restricted_address(self, message):
        """Leave on a message about this marked task only the addressees it
        allows: the members of the group, and the recipients a person typed
        into it. The chatter composer and the full composer pass those in the
        context key `restricted_typed_partner_ids`, and so must any program
        that addresses someone outside the group on purpose. Any other
        addressee outside the group is removed, and the removal is logged.
        Without a marked task there is nothing to do."""
        if not self:
            return
        self.ensure_one()
        typed = self.env["res.partner"].browse(
            self.env.context.get("restricted_typed_partner_ids", [])
        )
        removed = self._restricted_outsiders(message.sudo().partner_ids) - typed
        if removed:
            message.sudo().partner_ids -= removed
            _logger.info(
                "Message %s is about a restricted task; addressees outside the "
                "Restricted tasks group removed: %s",
                message.id,
                removed.ids,
            )

    def _restricted_recipients(self, message):
        """Who may receive what a message about this marked task sends: the
        members of the group and the partners the message is addressed to."""
        self.ensure_one()
        return self._restricted_members().partner_id | message.sudo().partner_ids

    def _restricted_filter_recipients(self, message, recipients_data):
        """The notification recipients of a message about this marked task
        that it allows; all of them without a marked task."""
        if not self:
            return recipients_data
        allowed_ids = self._restricted_recipients(message).ids
        return [
            recipient for recipient in recipients_data if recipient["id"] in allowed_ids
        ]

    def _restricted_filter_mail(self, mail):
        """Send an e-mail about this marked task only to the recipients it
        allows. Without a marked task there is nothing to do."""
        if not self:
            return
        mail._restricted_send_only_to(self._restricted_recipients(mail.mail_message_id))

    def _restricted_unsubscribe_outsiders(self):
        if not self:
            return
        self.env["mail.followers"].sudo().search(
            [
                ("res_model", "=", self._name),
                ("res_id", "in", self.ids),
                ("partner_id", "not in", self._restricted_members().partner_id.ids),
            ]
        ).unlink()

    def _restricted_revoke_outsiders(self):
        """Take from non-members what still reaches the tasks: their
        subscriptions; the notifications through which those who can log in
        could still read the tasks' messages (those of a partner without a
        user only record what was sent); the replies elsewhere to those
        messages, which Discuss shows with their parent; the e-mails about
        those messages that are not delivered yet; the tasks' portal link;
        and the download links and public flag of the tasks' attachments."""
        if not self:
            return
        self._restricted_unsubscribe_outsiders()
        messages = (
            self.env["mail.message"]
            .sudo()
            .search([("model", "=", self._name), ("res_id", "in", self.ids)])
        )
        self.env["mail.message"].sudo().search(
            [
                ("parent_id", "in", messages.ids),
                "|",
                ("model", "!=", self._name),
                ("res_id", "not in", self.ids),
            ]
        ).write({"parent_id": False})
        self.env["mail.notification"].sudo().with_context(active_test=False).search(
            [
                ("mail_message_id", "in", messages.ids),
                (
                    "res_partner_id",
                    "not in",
                    self._restricted_members().partner_id.ids,
                ),
                ("res_partner_id.user_ids", "!=", False),
            ]
        ).unlink()
        undelivered = (
            self.env["mail.mail"]
            .sudo()
            .search(
                [
                    ("mail_message_id", "in", messages.ids),
                    ("state", "in", ["outgoing", "exception"]),
                ]
            )
        )
        for mail in undelivered:
            mail.mail_message_id._restricted_task()._restricted_filter_mail(mail)
        self.sudo().write({"access_token": False})
        self.env["ir.attachment"].sudo().search(
            [("res_model", "=", self._name), ("res_id", "in", self.ids)]
        ).write({"access_token": False, "public": False})

    @api.model
    def _restricted_tasks_involving(self, users):
        """The marked tasks, archived ones included, that users are assigned
        to or follow."""
        tasks = self.sudo().with_context(active_test=False)
        if not users:
            return tasks.browse()
        return tasks.search(
            [
                ("restricted", "=", True),
                "|",
                ("user_ids", "in", users.ids),
                ("message_partner_ids", "in", users.partner_id.ids),
            ]
        )

    def _restricted_involved(self, users):
        """Those of users who are assigned to or follow any of these tasks."""
        return users.filtered(
            lambda user: user in self.user_ids
            or user.partner_id in self.message_partner_ids
        )

    @api.model
    def _restricted_tasks_with_activities(self, users):
        """The marked tasks, archived ones included, where users have
        activities."""
        tasks = self.sudo().with_context(active_test=False)
        if not users:
            return tasks.browse()
        return tasks.search(
            [("restricted", "=", True), ("activity_ids.user_id", "in", users.ids)]
        )

    def _restricted_leaver_activities_message(self, users):
        """Why users cannot leave the group while they have activities on
        these marked tasks, and what to do first."""
        return _(
            "Only members of the Restricted tasks group can have activities on "
            "restricted tasks. Leaving the group: %(users)s, with activities on "
            "%(tasks)s. Assign those activities to a member or mark them as "
            "done first.",
            users=", ".join((users & self.activity_ids.user_id).mapped("name")),
            tasks=", ".join('"%s"' % name for name in self.mapped("name")),
        )

    @api.model
    def _restricted_remove_users(self, users):
        """Take users who left the group off the marked tasks they are
        assigned to or follow, with an internal note on each. The
        notifications they received stay (spec, leaving the group). The note
        is the record of the change, so the write is not tracked, and nothing
        but the explicit unsubscription removes them as followers."""
        tasks = self._restricted_tasks_involving(users)
        for task in tasks:
            task.message_post(
                body=escape(
                    _(
                        "Taken off this restricted task after leaving the "
                        "Restricted tasks group: %(users)s.",
                        users=", ".join(
                            task._restricted_involved(users).mapped("name")
                        ),
                    )
                ),
                subtype_xmlid="mail.mt_note",
            )
        tasks.with_context(tracking_disable=True).write(
            {"user_ids": [Command.unlink(user.id) for user in users]}
        )
        tasks._restricted_unsubscribe_outsiders()

    @api.model
    def _restricted_leave_warning(self, users):
        """The warning shown before users leave the group: saving is refused
        while they have activities on marked tasks; otherwise it takes them
        off the marked tasks they are on. None when neither applies."""
        activity_tasks = self._restricted_tasks_with_activities(users)
        tasks = self._restricted_tasks_involving(users)
        if activity_tasks:
            message = activity_tasks._restricted_leaver_activities_message(users)
        elif tasks:
            message = _(
                "Leaving the group: %(users)s. When you save, they will be taken "
                "off the restricted tasks they are assigned to or follow, with an "
                "internal note on each. Tasks affected: %(count)s.",
                users=", ".join(tasks._restricted_involved(users).mapped("name")),
                count=len(tasks),
            )
        else:
            return None
        return {"title": _("Restricted tasks"), "message": message}

    @api.model
    @contextmanager
    def _restricted_leavers_removed(self):
        """Take whoever leaves the Restricted tasks group within the block off
        its marked tasks, and refuse the leaving while they have activities on
        any of them."""
        members = self._restricted_members()
        yield
        leavers = members - self._restricted_members()
        activity_tasks = self._restricted_tasks_with_activities(leavers)
        if activity_tasks:
            raise ValidationError(
                activity_tasks._restricted_leaver_activities_message(leavers)
            )
        self._restricted_remove_users(leavers)

    def _message_subscribe(self, partner_ids=None, subtype_ids=None, customer_ids=None):
        restricted = self._filter_restricted()
        super(ProjectTask, self - restricted)._message_subscribe(
            partner_ids=partner_ids, subtype_ids=subtype_ids, customer_ids=customer_ids
        )
        member_partner_ids = self._restricted_members().partner_id.ids
        return super(ProjectTask, restricted)._message_subscribe(
            partner_ids=[pid for pid in partner_ids or [] if pid in member_partner_ids],
            subtype_ids=subtype_ids,
            customer_ids=customer_ids,
        )

    def _message_auto_subscribe(self, updated_values, followers_existing_policy="skip"):
        res = super()._message_auto_subscribe(
            updated_values, followers_existing_policy=followers_existing_policy
        )
        self._filter_restricted()._restricted_unsubscribe_outsiders()
        return res
