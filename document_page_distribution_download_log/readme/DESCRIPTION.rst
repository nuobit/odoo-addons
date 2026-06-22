This module records **per-recipient download evidence** for distributed
document page versions. It is the download-log counterpart of
``document_page_distribution``: while that module owns the person + version
coverage (``document.page.history.recipient``), this module logs each real
access/download of a version's PDF by a covered recipient, and exposes the
download coverage as quality-audit evidence.

For every ``(version, recipient)`` coverage line it adds a download summary
(downloaded, first/last download date, download count) and a detail of every
real access. A download is only ever recorded against an **existing** recipient
line of the same version and person; this module never creates coverage nor
invents recipients (that remains the responsibility of
``document_page_distribution``).

**How it works**

* Saving a document page stores its content as a new version
  (``document.page.history``); the page itself always shows the head version.
* Each time a version's content is saved, the single document link in it is
  rewritten from the raw ``/web/content/<attachment>`` form to a version-aware
  download route that carries the version id.
* Opening that link checks the user's read access to the page, records the
  download against the recipient's coverage line of that exact version, and
  redirects to the standard ``/web/content`` file download.

**Audit contract**

The download log is **append-only**. Evidence rows are written only by the
system, through the download controller, on the recipient's behalf; the access
rights are **read-only for every role, the Document Manager included**
(``perm_read`` only). No user can create, edit or delete a download record, so
the trail cannot be tampered with — which is the point of a compliance log.
Visibility follows the document's own Security groups: a user sees the download
evidence of the documents they are allowed to read, and a Document Manager sees
all of it.
