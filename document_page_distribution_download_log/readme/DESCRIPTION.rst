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
