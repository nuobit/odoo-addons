This module needs the ``pdfminer.six`` Python package in Odoo's Python
environment to extract the text of PDF files::

    pip install pdfminer.six

It is tested with release 20251107, which needs Python 3.9 or later; on an
older Python, pip installs the newest release that supports it.

Restart Odoo after installing it. The manifest declares the dependency by the
name the package is imported with, ``pdfminer``: Odoo refuses to install the
module when that name cannot be imported.

Do not install the package named ``pdfminer``: it is the original, abandoned
project, and Odoo extracts no text from PDF files with it. It writes into the
same ``pdfminer`` folder as ``pdfminer.six``, so if it is installed, uninstall
it and then reinstall ``pdfminer.six`` with ``pip install --force-reinstall``.

``attachment_indexation`` is installed with this module. Files uploaded before
``attachment_indexation`` or ``pdfminer.six`` was installed are not indexed
retroactively: see the post-migration reindexing of the usage section.
