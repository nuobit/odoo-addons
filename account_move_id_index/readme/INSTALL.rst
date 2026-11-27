Installing the module builds both indexes. While PostgreSQL builds an index, it
blocks writes on that table, for a time that grows with the size of the table.

Uninstalling the module drops both indexes.
