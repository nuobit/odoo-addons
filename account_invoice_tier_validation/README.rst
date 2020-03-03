.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=======================
Invoice Tier Validation
=======================

This module extends the functionality of Invoices to support a tier
validation process.

Installation
============

This module depends on ``base_tier_validation``. You can find it at
`OCA/server-ux <https://github.com/OCA/server-ux>`_

Configuration
=============

To configure this module, you need to:

#. Go to *Settings > Technical > Tier Validations > Tier Definition*.
#. Create as many tiers as you want for Account Invoice model.

Usage
=====

To use this module, you need to:

#. Create an Invoice triggering at least one "Tier Definition".
#. Click on *Request Validation* button.
#. Under the tab *Reviews* have a look to pending reviews and their statuses.
#. Once all reviews are validated click on *Confirm Invoice*.

Additional features:

* You can filter the Invoices requesting your review through the filter *Needs my
  review*.
* User with rights to confirm the Invoice (validate all tiers that would
  be generated) can directly do the operation, this is, there is no need for
  her/him to request a validation.


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

Do not contact contributors directly about support or help with technical issues.

