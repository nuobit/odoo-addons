# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentPage(models.Model):
    _inherit = "document.page"

    mgmtsystem_master_folder = fields.Selection(
        selection=[
            ("procedure", "Procedures"),
            ("environmental_aspect", "Environmental Aspects"),
            ("work_instruction", "Work Instructions"),
            ("manual", "Manuals"),
        ],
        string="Master Folder Of",
        copy=False,
        help="Management system menu that lists the pages of this category. Each "
        "company has at most one master folder per menu, plus at most one without "
        "company. The Create button of the menu files the new page in the master "
        "folder of the selected company, or in the one without company when the "
        "selected company has none.",
    )

    @api.constrains("type", "company_id", "mgmtsystem_master_folder", "active")
    def _check_mgmtsystem_master_folder(self):
        for page in self.filtered("mgmtsystem_master_folder"):
            if page.type != "category":
                raise ValidationError(
                    _(
                        'The page "%s" is not a category: only a category can be '
                        "a master folder.",
                        page.name,
                    )
                )
            if not page.active:
                raise ValidationError(
                    _(
                        'The category "%(folder)s" is the master folder of %(menu)s. '
                        'Clear its "Master Folder Of" field before archiving it.',
                        folder=page.name,
                        menu=page._get_mgmtsystem_master_folder_label(
                            page.mgmtsystem_master_folder
                        ),
                    )
                )
            # sudo: the category that already has the mark may belong to a
            # company the user has not selected
            other_folders = self.sudo().search(
                [
                    ("id", "!=", page.id),
                    (
                        "mgmtsystem_master_folder",
                        "=",
                        page.mgmtsystem_master_folder,
                    ),
                    ("company_id", "=", page.company_id.id),
                ]
            )
            if other_folders:
                menu = page._get_mgmtsystem_master_folder_label(
                    page.mgmtsystem_master_folder
                )
                folders = ", ".join(other_folders.mapped("name"))
                if page.company_id:
                    raise ValidationError(
                        _(
                            'The category "%(folder)s" is already the master '
                            'folder of %(menu)s for the company "%(company)s".',
                            folder=folders,
                            menu=menu,
                            company=page.company_id.name,
                        )
                    )
                else:
                    raise ValidationError(
                        _(
                            'The category "%(folder)s" is already the master '
                            "folder of %(menu)s without company.",
                            folder=folders,
                            menu=menu,
                        )
                    )

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        menu = self.env.context.get("mgmtsystem_master_folder_menu")
        if menu and "parent_id" in fields_list:
            values["parent_id"] = self._get_mgmtsystem_master_folder(menu).id
        return values

    @api.model
    def _get_mgmtsystem_master_folder(self, menu):
        """Return the master folder of the menu for the selected company, or the
        one without company when the selected company has none."""
        company = self.env.company
        folders = self.search(
            [
                ("mgmtsystem_master_folder", "=", menu),
                ("company_id", "in", [company.id, False]),
            ]
        )
        company_folders = folders.filtered(lambda folder: folder.company_id == company)
        shared_folders = folders - company_folders
        candidates = company_folders or shared_folders
        if not candidates:
            raise UserError(
                _(
                    'The company "%(company)s" has no master folder of %(menu)s.',
                    company=company.name,
                    menu=self._get_mgmtsystem_master_folder_label(menu),
                )
            )
        elif len(candidates) > 1:
            raise UserError(
                _(
                    "Several categories are the master folder of %(menu)s: "
                    "%(folders)s. Leave the mark on only one per company.",
                    menu=self._get_mgmtsystem_master_folder_label(menu),
                    folders=", ".join(candidates.mapped("name")),
                )
            )
        return candidates

    @api.model
    def _get_mgmtsystem_master_folder_label(self, menu):
        selection = self._fields["mgmtsystem_master_folder"]._description_selection(
            self.env
        )
        return dict(selection)[menu]
