For each marketplace mapping of a Lengow backend (*Connectors > Lengow >
Backends*, tab *Mappings*), select the **Contact name source**: the field of
the Lengow order addresses the contact name is read from, for both the billing
and the delivery address.

* *First name + Last name* (default): the name is built from the
  ``first_name``/``last_name`` pair. Correct for most marketplaces. Some of
  them reuse ``full_name`` as a mutable delivery label (rewritten on late
  re-synchronizations, e.g. with a carrier or pick-up point label), which is
  why that field is ignored under this source.
* *Full name*: the name is read from ``full_name``. Needed for the few
  marketplaces that publish the contact name only there and leave first/last
  name empty.

The name is read strictly from the selected source: if it comes empty on an
order, the order's import job fails with a message describing which name
fields came filled and how to reconfigure the mapping. After changing the
selection, import the affected orders again from the backend (*Import
specific orders*): an already-failed job carries the data prepared at
download time, so requeuing it keeps the old values.
