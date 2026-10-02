Post-migration reindexing:

When pages and their files are imported in bulk (a migration), the attachments
may be created with their ``index_content`` left empty, so the search cannot
match them yet. Recompute it once, reusing Odoo's own indexing and without
rewriting the page content (so no new revision is created), from a shell::

    odoo-bin shell -c <odoo.conf> -d <database>
    >>> env["document.page"].reindex_attachment_content(
    ...     batch_size=500, only_missing=True)
    >>> env.cr.commit()

``batch_size`` caps how many attachments are processed per run (re-run until
``processed`` is ``0``); ``only_missing`` limits the work to attachments whose
``index_content`` is still empty. The call returns a summary
``{"processed", "skipped", "no_text"}``; ``no_text`` lists the ``(id, name)`` of
attachments that yielded no extractable text (scanned PDFs, or PDFs indexed
without ``pdfminer.six``).

Post-migration linking:

Pages imported in bulk may have body-embedded files left with ``res_id=0`` (for
example, files embedded before the page was first saved). New edits anchor them
automatically, but to relink the ones already in the database in a single pass,
from a shell::

    odoo-bin shell -c <odoo.conf> -d <database>
    >>> env["document.page"].search([])._anchor_orphan_attachments()
    >>> env.cr.commit()

Each orphan attachment gets its ``res_id`` set to the page whose current body
references it. Attachments that no longer appear in any page body (files removed
or replaced) are intentionally left untouched.
