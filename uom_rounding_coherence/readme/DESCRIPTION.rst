This module adds validation to ensure that Unit of Measure (UoM) rounding
precision is coherent with the conversion ratio to the reference unit,
preventing precision loss during conversions.

When converting quantities between UoMs in the same category, a non-reference
UoM whose rounding is too coarse relative to its conversion factor will lose
precision beyond the reference UoM's rounding.

**Example Problem:**

If the reference UoM has rounding 0.001 and a secondary UoM with ratio 1.141
has rounding 0.01, each conversion can introduce up to ±0.004 error in
reference units — enough to accumulate visible discrepancies over multiple
transactions.

**The Validation:**

The module performs two checks:

1. **Conversion ratio coherence**: the UoM's rounding step, converted to
   reference units (rounding / factor), must not exceed the reference UoM's
   rounding. This prevents precision loss during conversions.

2. **Stock quant coherence**: when changing a UoM's rounding, the module checks
   that all existing stock quant quantities for products using that UoM fit
   within the new rounding. This prevents making the rounding coarser than the
   data allows (e.g., changing from 0.001 to 0.01 when quants with 3 decimals
   already exist in stock).
