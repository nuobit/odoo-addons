This module integrates Portuguese transport documents functionality between
InvoiceXpress and Vehicle Daily Stock modules.

**Key Features:**

* Seamlessly integrates ``l10n_pt_stock_invoicexpress`` with ``l10n_pt_stock_vehicle_daily``
* Automatically computes license plate information from location data
* Ensures proper license plate handling in stock move location wizards
* Hides redundant license plate fields in the user interface when both modules are installed

**Technical Details:**

The module extends the stock picking model to automatically compute the license plate
from the location's Portuguese license plate field, ensuring data consistency across
both transport document generation (InvoiceXpress) and daily vehicle reporting
(Portuguese Tax Authorities) workflows.

This is an auto-install bridge module that activates automatically when both
parent modules are present in the system.
