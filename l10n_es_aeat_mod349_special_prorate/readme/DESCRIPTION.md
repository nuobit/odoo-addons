This module wires the special prorate purchase taxes
(`l10n_es_special_prorate`) into the AEAT 349 model tax map, so the
intra-community acquisitions of goods and services carried by those
taxes are reported under keys A and I.

It is the 349 counterpart of `l10n_es_aeat_mod303_special_prorate` and
`l10n_es_aeat_sii_oca_special_prorate`, and installs automatically when
both `l10n_es_special_prorate` and `l10n_es_aeat_mod349` are installed.
