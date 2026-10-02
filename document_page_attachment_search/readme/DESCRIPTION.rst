By default, the OCA module ``document_page`` exposes a search field on the
``content`` of a page that only matches against the page HTML body. When users
attach files to a page (PDF, docx, xlsx, OpenDocument...), the text inside those
files is not reachable from that search even though Odoo's
``attachment_indexation`` already extracts and stores it in
``ir.attachment.index_content``.

This module extends the ``content`` search of ``document.page`` so that the same
query also matches the indexed text of the files attached to the page.

Behavior:

* The existing search box keeps working as before; the default search field keeps
  matching the revision summary and is widened to also match the page body and the
  text of its attachments, so typing a term and pressing Enter searches them
  directly.
* For text operators (``like``, ``ilike``, ``=like``, ``=ilike``) the search
  domain is widened to also match pages that have an attachment
  (``ir.attachment`` with ``res_model=document.page``) whose indexed content
  contains the query. The page is resolved from the attachment's ``res_id``.
* For other operators (``=``, ``!=``, ``not ilike``, etc.) the original behavior
  is preserved untouched: combining attachment matches with equality or negation
  would change the semantics of the original search.
* This is implemented with a single inherited search view that widens the default
  field's ``filter_domain`` (``position="attributes"``) to also search the page
  content; no search fields are moved, added or removed, and the OCA search box
  stays the single entry point.
* When a page is created or its content is saved, any file embedded in the body
  (``/web/content/<id>`` or ``/web/image/<id>``) that is not yet linked to a
  record is anchored to that page (its ``res_id`` is set). A file embedded before
  the page's first save (``res_id=0``) therefore becomes searchable on the next
  save, with no manual step.
* A file still linked to an existing ``document.page`` (via ``res_model`` /
  ``res_id``) cannot be deleted. This avoids leaving a dead ``/web/content`` link
  in the page body and keeps the content search consistent.

Scope:

* Any file attached to the page is searchable, whether embedded in the body or
  attached through the chatter. The match relies on the native ``res_model`` /
  ``res_id`` link that Odoo maintains, not on parsing the page HTML, so it is
  unaffected by modules that rewrite the links of the body.
* A file uploaded into a page that has not been saved yet gets ``res_id=0``; it
  becomes searchable once the page is saved (the save anchors it, see above) or
  after the post-migration linking of the usage section. An anchored file stays
  searchable until it is deleted, also when the body no longer links it.
