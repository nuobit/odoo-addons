.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

======================
Report qweb PDF chunks
======================

This module temporarily splits all selected documents to print into chunks
and invokes the external Wkhtmltopdf (0.12.5) program for each chunk to avoid
the well known memory problems when printing many documents.

The chunks are concatenated at the end returning a single huge PDF file
as the user expects.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/nuobit/odoo-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Eric Antones <eantones@nuobit.com>
