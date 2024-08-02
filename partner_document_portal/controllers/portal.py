# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
from odoo import _, http
from odoo.http import request
from odoo.exceptions import AccessError, MissingError

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class DocumentPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "document_count" in counters:
            values["document_count"] = (
                request.env["partner.document"].search_count([])
                if request.env["partner.document"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )
        return values

    def _prepare_document_domain(self):
        return []

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

    @http.route(["/my/documents/<int:document_id>"], type="http", auth="public", website=True)
    def portal_my_document_detail(
        self, document_id, access_token=None, **kw
    ):
        try:
            document_sudo = self._document_check_access("partner.document", document_id, access_token)
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

    @http.route(['/my/documents/upload'], type='http', auth='user', website=True)
    def portal_upload_document(self, **kw):
        values = self._prepare_portal_layout_values()
        return request.render('partner_document_portal.portal_upload_document', values)

    @http.route(['/my/documents/upload/submit'], type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def portal_upload_document_submit(self, **kw):
        Document = request.env['partner.document']
        file = request.httprequest.files.get('file')
        datas = base64.b64encode(file.read()) if file else None

        document_data = {
            'description': kw.get('description'),
            'expiration_date': kw.get('expiration_date'),
            'document_type_id': int(kw.get('document_type_id')),
            'datas': datas,
        }
        document = Document.create(document_data)
        return request.redirect('/my/documents')

    @http.route(['/my/documents/update_document'], type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def update_document(self, **post):
        document_id = int(post.get('document_id'))
        description = post.get('description')
        expiration_date = post.get('expiration_date')
        document = request.env['partner.document'].sudo().browse(document_id)
        document.write({
            'description': description,
            'expiration_date': expiration_date,
        })
        file = post.get('attachment')
        if file:
            # TODO: How to create a attachment??
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': base64.b64encode(file.read()).decode('ascii'),
                'res_model': 'partner.document',
                'res_id': document_id,
                'type': 'binary',
            })
            document.write({'datas': [(4, attachment.datas)]})

        return request.redirect('/my/documents/%s' % document_id)

    @http.route(['/my/documents/delete/<int:document_id>'], type='http', auth='user', website=True)
    def portal_delete_document(self, document_id, **kw):
        Document = request.env['partner.document']
        try:
            document = Document.browse(document_id)
            if not document.exists() or document.validated:
                raise AccessError("You cannot delete this document.")
            document.unlink()
        except (AccessError, MissingError):
            return request.redirect('/my/documents')
        return request.redirect('/my/documents')
