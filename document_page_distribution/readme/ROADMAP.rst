* The log says that an email was delivered to a recipient, not that the
  recipient read or accepted the document: the module records no read or
  acceptance evidence.
* Every recipient receives an email, also the users whose notification
  preference is to handle the notifications inside Odoo: the log relies on the
  delivery status of an email.
* A document without groups in its *Security* tab cannot be distributed: the
  users in scope are taken from those groups.
* A user without a language receives the email in English.
* The users in scope are computed again when the wizard is confirmed. A user
  added to a group while the wizard is open gets a line in the log without
  having been shown in the wizard, and a user removed from the groups in the
  meantime is not sent the email, even if selected.
* The behaviour with *Document Page Approval* installed is not covered by the
  tests of this module.
* Odoo deletes the notification of a delivered email some time after the send.
  From then on the send keeps its last delivery status: a later bounce of that
  email no longer reaches the log.
