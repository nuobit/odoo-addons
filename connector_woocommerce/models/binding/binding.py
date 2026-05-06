# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

# Max attempts for a job before it transitions to ``state='failed'``.
# Combined with ``retry_pattern`` on every queue.job.function of this
# connector (``{1: 10, 5: 30, 10: 60, 15: 300}``) this yields a retry
# window of ~33 minutes. OCA queue_job default is 5 which clipped the
# progression at the first bucket (10s × 4 ≈ 40s).
MAX_RETRIES_NETWORK = 20


class WoocommerceBinding(models.AbstractModel):
    _name = "woocommerce.binding"
    _inherit = "connector.extension.external.binding"
    _description = "WooCommerce Binding"

    backend_id = fields.Many2one(
        comodel_name="woocommerce.backend",
        string="WooCommerce Backend",
        required=True,
        ondelete="restrict",
    )

    _sql_constraints = [
        (
            "internal_uniq",
            "unique(backend_id, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
    ]

    def with_delay(
        self,
        priority=None,
        eta=None,
        max_retries=None,
        description=None,
        channel=None,
        identity_key=None,
    ):
        if max_retries is None:
            max_retries = MAX_RETRIES_NETWORK
        return super().with_delay(
            priority=priority,
            eta=eta,
            max_retries=max_retries,
            description=description,
            channel=channel,
            identity_key=identity_key,
        )
