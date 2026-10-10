This module extends l10n_es with generic pieces the official Spanish
localization does not ship:

* Split of the exempt output VAT into "con derecho a deducción" /
  "sin derecho a deducción" variants.
* The complete non-deductible input VAT family: goods variants
  (bienes corrientes / bienes de inversión) for the official 4%, 10%
  and 21% non-deductible templates, plus the intra-community and
  reverse-charge non-deductible cases, wired into the official
  intra-community and IRPF 15 fiscal positions.
* VAT group flags (`is_vat`) on the official tax groups and
  consistency checks on taxes and journal entries.
