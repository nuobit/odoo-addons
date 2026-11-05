On 17.0 the *Dynamic Ratio* checkbox belonged to `barcodes_gs1_label`. A
database migrated from 17.0 with OpenUpgrade keeps the units it marked:
OpenUpgrade keeps the column of a field that a module no longer defines, and
installing this module takes that column up again. Outside OpenUpgrade, an
update of `barcodes_gs1_label` drops that column, and with it the units it
marked, unless this module is installed in that same update or before it.
