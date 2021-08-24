.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

====================
Report PDF CSS reset
====================

This module enables you with the capability to reset the default
paddings on the pdf minimal_layout template

Usage
=====

return self.env.ref('module.report_name') \
    .with_context(no_paddings=True).report_action(self, data=data)

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
