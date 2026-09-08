.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===============
Invoice batches
===============

Group invoices to easy printing/emailing

Configuration
=============

Go to *Invoicing > Configuration > Settings > Invoice batches* and set, for
each company:

* the default e-mail template of the batch invoices. Address it to the field
  *Batch e-mail recipient* of the invoice
  (``${object.invoice_batch_email_recipient_id.id}`` as recipients): the batch
  e-mail contact of the invoice or, when it is empty, its partner;
* the invoice batch user: the internal user the batch jobs run as. The
  invoices generated from a batch and the e-mails sent from it belong to that
  user (creator, follower, author of the sent messages), so the customer
  replies reach its mailbox. It needs the Billing group, an e-mail address and
  the company among its allowed companies; without a valid user, no invoice
  can be generated from a batch nor e-mailed from one. Processing a batch
  with the e-mail method enabled needs the user of the batch company even
  when none of its invoices is sent by e-mail; printing and factura-e alone
  do not.

Usage
=====

* The invoices generated from a batch are created, followed and e-mailed by
  the invoice batch user of the company, so the customer replies reach its
  mailbox and not the person who launched the batch.
* When a batch invoice is validated, the customer follower Odoo adds is the
  batch e-mail contact of the invoice when it differs from the partner: the
  contact is the one who receives the e-mail. Invoices outside a batch keep
  the native follower.
* The batch has a chatter: whoever creates it follows it, and each processing
  leaves a note with the number of invoices launched per sending method.

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
* Christopher Ormaza <chris.ormaza@forgeflow.com>
