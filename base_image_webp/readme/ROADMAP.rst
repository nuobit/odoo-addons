* WebP is accepted on every image field of every model in the process (the
  patch is global), not only on product images.
* No WebP resizing: the stored ``image_1024``, ``image_512``, ``image_256`` and
  ``image_128`` fields and ``/web/image?width=…`` return the full file, as in
  Odoo 17.0 (the filestore keeps a single copy).
* A WebP inside a PDF report prints blank: wkhtmltopdf cannot render WebP and
  the JPEG companion of Odoo 17.0 is not ported.
* Uninstalling does not remove the patch until the Odoo service restarts, and
  a service serving several databases is patched for all of them once one of
  them installs the module.
* Do not add ``webp`` to the ``base.image_autoresize_extensions`` system
  parameter: the attachment auto-resize cannot process WebP (as in Odoo 17.0).
* The ``guess_mimetype`` signature table only acts when ``python-magic`` is
  not installed; there, as in Odoo 17.0, a RIFF file that is not WebP (WAV,
  AVI) is typed ``image/webp``.
* The unsaved preview of the backend image widget types its data URI as
  ``image/png`` (the 14.0 widget map has no WebP entry); browsers render it by
  sniffing the bytes, and the saved image is served as ``image/webp``.
