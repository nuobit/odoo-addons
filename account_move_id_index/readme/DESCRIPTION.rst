This module adds a database index on the journal entry of payments and of bank
statement lines: the ``move_id`` column of the ``account_payment`` and
``account_bank_statement_line`` tables. Odoo declares both indexes itself from
version 16.0.

Whenever a reconciliation changes the journal items of an entry, Odoo looks up
the payments and the bank statement lines of that entry, to recompute whether
they are reconciled. Without these indexes each lookup reads the whole table, so
validating a reconciliation slows down as the tables grow.
