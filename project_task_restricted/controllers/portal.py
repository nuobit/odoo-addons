# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.project.controllers import portal


class ProjectCustomerPortal(portal.ProjectCustomerPortal):
    @http.route()
    def portal_my_project(self, project_id=None, access_token=None, **kw):
        # the page lists the project's tasks as superuser when its address
        # carries a token
        request.context = dict(request.context, restricted_portal=True)
        return super().portal_my_project(
            project_id=project_id, access_token=access_token, **kw
        )

    @http.route()
    def portal_my_project_task(
        self, project_id=None, task_id=None, access_token=None, **kw
    ):
        # the page reads the task as superuser when its address carries a token
        task = request.env["project.task"].browse(task_id).exists()
        if task._filter_restricted() and not task._restricted_user_is_member():
            return request.redirect("/my")
        return super().portal_my_project_task(
            project_id=project_id, task_id=task_id, access_token=access_token, **kw
        )
