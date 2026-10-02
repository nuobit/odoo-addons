#. Open a document page as a document manager.
#. In the *Security* tab, set the groups that may read the document.
#. Press *Distribute* in the form header. The wizard lists the users in scope
   with their state. A user that cannot read the document or has no email
   address cannot be selected.
#. Select the recipients and press *Send*. The emails leave with the next run
   of the mail queue of Odoo; until then the state of the recipient is
   *Queued*.
#. Each distribution is logged as a note in the document's chatter. The
   *Distribution* tab of the document lists the recipients of the current
   version with their state (queued, sent, bounced, error, ...). Above the
   list, *Distribution* says how many of them the version has been sent to,
   as a fraction: *3/10* means 3 of 10. The form of every version keeps the
   same information, and the list of versions shows it in the column
   *Distribution*.

Pressing *Distribute* again on the same version resends the email to the
selected recipients as a reminder; it does not create a new document version.
The recipients whose last email is queued or sent are not selected by default.
