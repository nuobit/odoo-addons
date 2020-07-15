.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
POS data validation
===================

The POS module is ignoring EXPLICITLY the propagation of errors coming from the backend.
It causes a data inconsistency because the POS are making changes that are not rolled back.

This modules makes the following validations to minimize the effect of ignoring the errors:

* Using the same serial number twice
* Selling without stock

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




