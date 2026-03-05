This module extends the stock picking signature functionality in Odoo 16.

While Odoo 16 already includes a signature field on pickings, it is limited to outgoing
deliveries only and lacks metadata tracking. This module adds:

* **Configurable per picking type**: A ``Require Signature`` option on operation types
  lets administrators enable signature requirements for any type of transfer (receipts,
  deliveries, internal transfers).
* **Signature metadata**: ``Signed By`` and ``Signed On`` fields are automatically
  populated when a signature is captured.
* **Validation enforcement**: Transfers with a required signature cannot be validated
  without one.
* **Extended reports**: Signature block added to the Picking Operations report in
  addition to the existing Delivery Slip report.
* **Signature tab**: A dedicated "Signature" notebook tab on the picking form shows
  signature details.
