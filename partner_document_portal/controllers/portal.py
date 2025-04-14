# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo import _, fields, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class DocumentPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "document_count" in counters:  # _getCountersAlwaysDisplayed to always show
            domain = self._prepare_document_domain()
            values["document_count"] = (
                request.env["partner.document"].search_count(domain)
                if request.env["partner.document"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )
        return values

    @http.route(
        ["/my/documents/<int:document_id>/download"],
        type="http",
        auth="public",
        website=True,
    )
    def _download_partner_document(
        self, document_id, access_token=None, download=False, **kw
    ):
        try:
            partner_sudo = self._document_check_access(
                "partner.document", document_id, access_token=access_token
            )
            attachment = (
                request.env["ir.attachment"]
                .sudo()
                .search(
                    [
                        ("res_model", "=", "partner.document"),
                        ("res_id", "=", partner_sudo.id),
                        ("id", "!=", False),
                    ],
                    limit=1,
                )
            )
            mimetype = attachment.mimetype or "application/octet-stream"

            return request.make_response(
                base64.b64decode(partner_sudo.datas),
                headers=[
                    ("Content-Type", mimetype),
                    (
                        "Content-Disposition",
                        f'attachment; filename="{partner_sudo.datas_fname}"'
                        if download
                        else f'inline; filename="{partner_sudo.datas_fname}"',
                    ),
                ],
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

    @http.route(
        ["/my/documents/template/<int:template_file_id>/download"],
        type="http",
        auth="public",
        website=True,
    )
    def _download_document_template_file(
        self, template_file_id, access_token=None, download=False, **kw
    ):
        try:
            template_file_sudo = self._document_check_access(
                "partner.document.template.file",
                template_file_id,
                access_token=access_token,
            )
            attachment = (
                request.env["ir.attachment"]
                .sudo()
                .search(
                    [
                        ("res_model", "=", "partner.document.template.file"),
                        ("res_id", "=", template_file_sudo.id),
                        ("id", "!=", False),
                    ],
                    limit=1,
                )
            )
            mimetype = attachment.mimetype or "application/octet-stream"

            return request.make_response(
                base64.b64decode(template_file_sudo.datas),
                headers=[
                    ("Content-Type", mimetype),
                    (
                        "Content-Disposition",
                        f'attachment; filename="{template_file_sudo.datas_fname}"'
                        if download
                        else f'inline; filename="{template_file_sudo.datas_fname}"',
                    ),
                ],
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

    def _prepare_document_domain(self):
        return [("partner_id", "=", request.env.user.partner_id.id)]

    def _prepare_searchbar_sortings(self):
        return {
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "name": {"label": _("Name"), "order": "name"},
        }

    @http.route(
        ["/my/documents", "/my/documents/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_documents(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        Document = request.env["partner.document"]
        domain = self._prepare_document_domain()

        searchbar_sortings = self._prepare_searchbar_sortings()
        if not sortby or sortby not in searchbar_sortings:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]
        document_count = Document.search_count(domain)
        pager = portal_pager(
            url="/my/documents",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=document_count,
            page=page,
            step=self._items_per_page,
        )
        documents = (
            Document.search(
                domain, order=order, limit=self._items_per_page, offset=pager["offset"]
            )
            if Document.check_access_rights("read", raise_exception=False)
            else Document
        )
        request.session["my_documents_history"] = documents.ids[:100]

        values.update(
            {
                "date": date_begin,
                "date_end": date_end,
                "documents": documents,
                "page_name": "document",
                "default_url": "/my/documents",
                "pager": pager,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("partner_document_portal.portal_my_documents", values)

    @http.route(
        ["/my/documents/<int:document_id>"], type="http", auth="public", website=True
    )
    def portal_my_document_detail(self, document_id, access_token=None, **kw):
        try:
            document_sudo = self._document_check_access(
                "partner.document", document_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        values = self._document_get_page_view_values(document_sudo, access_token, **kw)
        return request.render("partner_document_portal.portal_document_page", values)

    def _document_get_page_view_values(self, document, access_token, **kwargs):
        values = {
            "page_name": "DOCUMENTS",
            "document": document,
        }
        return self._get_page_view_values(
            document, access_token, values, "my_document_history", False, **kwargs
        )

    @http.route(
        ["/my/documents/update_document/<int:document_id>"],
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
        csrf=False,
    )
    def update_document(self, document_id, **post):
        description = post.get("description")
        expiration_date = post.get("expiration_date")
        file = post.get("attachment")
        partner_document = request.env["partner.document"].sudo().browse(document_id)
        vals = {}
        if description != partner_document.description:
            vals["description"] = description
        if expiration_date != fields.Date.to_string(partner_document.expiration_date):
            vals["expiration_date"] = expiration_date
        if partner_document.validated and (file or vals):
            vals["validated"] = False
        if vals:
            partner_document.write(vals)
        if file:
            try:
                partner_document.write(
                    {
                        "datas_fname": file.filename,
                        "datas": base64.b64encode(file.read()).decode("ascii"),
                    }
                )
            except Exception:
                return request.redirect(
                    f"/my/documents/{document_id}?error=attachment_failed"
                )
        return request.redirect("/my/documents")
