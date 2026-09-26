This module makes Odoo 14.0 accept WebP images and keep them as they are, the
way Odoo 17.0 does. A WebP written to an image field (``fields.Image``, the
stored ``image_1920`` … ``image_128`` family, an attachment) is stored
untouched, its resolution is checked against the same 50 megapixel limit as
the other formats, and it is served back as ``image/webp``.

It is a backport of the Odoo 17.0 code, adapted only where the 14.0 API
differs: ``ImageProcess`` recognises the RIFF/WEBP header and never hands the
file to PIL, ``get_webp_size`` reads the dimensions from the header,
``is_image_size_above`` compares WebP sizes, the base64 magic-word map knows
WebP and the ``guess_mimetype`` signature table has a WebP entry.

The patch is applied to ``odoo.tools`` when the module is loaded
(``post_load``), so it is process-wide: every model, and every database served
by the same Odoo process, gets the behaviour once the module is installed on
one database. Uninstalling the module removes nothing until the Odoo service
restarts.
