By default, the OCA module ``document_page`` exposes a search field on the
``content`` of a page that only matches against the page HTML body. When users
attach files to a page (PDF, docx, xlsx, OpenDocument...), the text inside those
files is not reachable from that search even though Odoo's
``attachment_indexation`` already extracts and stores it in
``ir.attachment.index_content``.

This module extends the ``content`` search of ``document.page`` so that the same
query also matches the indexed text of the files attached to the page.

Behavior:

* The search box starts with a *Document* entry: typing a term and pressing Enter
  finds the documents whose title, summary or content contains it, the text of
  their files included. The *Summary* and *Content* entries keep their own
  meaning and stay available.
* For text operators (``like``, ``ilike``, ``=like``, ``=ilike``) the search
  domain is widened to also match pages that have an attachment
  (``ir.attachment`` with ``res_model=document.page``) whose indexed content
  contains the query. The page is resolved from the attachment's ``res_id``.
* For other operators (``=``, ``!=``, ``not ilike``, etc.) the original behavior
  is preserved untouched: combining attachment matches with equality or negation
  would change the semantics of the original search.
* When a page is created or its content is saved, the files embedded in the body
  (``/web/content/<id>`` or ``/web/image/<id>``) that are not yet linked to a
  record and were uploaded by the user who saves are anchored to that page (their
  ``res_id`` is set); the save of a system administrator anchors them whoever
  uploaded them. A file embedded before the page's first save (``res_id=0``)
  therefore becomes searchable when its uploader saves the page, with no manual
  step.
* A file of the document saved in its content is kept with the versions of the
  document, also after a later version takes it out of the content: while the
  document exists, only a system administrator can delete it, attach it to
  another record or change its content. The image of the page and the files
  attached through the chatter can be deleted as usual.

Scope:

* Any file attached to the page is searchable, whether embedded in the body or
  attached through the chatter. The match relies on the native ``res_model`` /
  ``res_id`` link that Odoo maintains, not on parsing the page HTML, so it is
  unaffected by modules that rewrite the links of the body.
* A file uploaded into a page that has not been saved yet gets ``res_id=0``; it
  becomes searchable once the page is saved (the save anchors it, see above) or
  after the post-migration linking of the usage section. An anchored file stays
  searchable until it is deleted, also when the body no longer links it.
