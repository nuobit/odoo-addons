# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged

from ..models.binding.binding import MAX_RETRIES_NETWORK


@tagged("post_install", "-at_install")
class TestWithDelayMaxRetries(TransactionCase):
    """The ``retry_pattern`` declared on every woocommerce ``queue.job.function``
    (``{1: 10, 5: 30, 10: 60, 15: 300}``) is designed for up to ~20 attempts.
    OCA queue_job's ``DEFAULT_MAX_RETRIES`` is 5, which clipped every
    woocommerce job at the first bucket (10s x 4 = ~40s window) and turned the
    longer buckets (30s, 60s, 300s) into dead code.

    This test suite pins the override on ``WoocommerceBinding.with_delay`` that
    defaults ``max_retries`` to ``MAX_RETRIES_NETWORK`` (20) so the declared
    pattern actually runs, giving a ~33-minute retry window per job.
    """

    def test_default_max_retries_matches_woocommerce_constant(self):
        """Without an explicit ``max_retries=``, the woocommerce binding must
        inject ``MAX_RETRIES_NETWORK`` (20) instead of the OCA default (5)."""
        delayable = self.env["woocommerce.sale.order"].with_delay()
        self.assertEqual(delayable.delayable.max_retries, MAX_RETRIES_NETWORK)

    def test_explicit_max_retries_is_respected(self):
        """An explicit ``max_retries=N`` on the call site must win over the
        woocommerce default — e.g. for one-shot diagnostic enqueues."""
        delayable = self.env["woocommerce.sale.order"].with_delay(max_retries=7)
        self.assertEqual(delayable.delayable.max_retries, 7)

    def test_explicit_zero_max_retries_is_respected(self):
        """``max_retries=0`` means infinite retries in queue_job — the
        woocommerce default must not silently replace it with 20."""
        delayable = self.env["woocommerce.sale.order"].with_delay(max_retries=0)
        self.assertEqual(delayable.delayable.max_retries, 0)

    def test_other_kwargs_forwarded(self):
        """The override must pass ``priority``, ``eta``, ``description``,
        ``channel`` and ``identity_key`` through to the parent ``with_delay``
        untouched."""
        delayable = self.env["woocommerce.sale.order"].with_delay(
            priority=42,
            description="probe",
            channel="root.woocommerce_export_batch",
            identity_key="probe-identity",
        )
        self.assertEqual(delayable.delayable.priority, 42)
        self.assertEqual(delayable.delayable.description, "probe")
        self.assertEqual(delayable.delayable.channel, "root.woocommerce_export_batch")
        self.assertEqual(delayable.delayable.identity_key, "probe-identity")
        # And the injected default is still there alongside them.
        self.assertEqual(delayable.delayable.max_retries, MAX_RETRIES_NETWORK)

    def test_default_applied_to_multiple_binding_models(self):
        """The override lives on the abstract ``woocommerce.binding`` model, so
        every concrete binding (partners, products, sale orders, etc.)
        must inherit the same default without per-model wiring."""
        for model in (
            "woocommerce.res.partner",
            "woocommerce.product.template",
            "woocommerce.product.product",
            "woocommerce.sale.order",
        ):
            with self.subTest(model=model):
                delayable = self.env[model].with_delay()
                self.assertEqual(delayable.delayable.max_retries, MAX_RETRIES_NETWORK)

    def test_non_woocommerce_model_keeps_oca_default(self):
        """The override must be scoped to woocommerce bindings — generic Odoo
        models (e.g. ``res.partner``) keep the OCA ``DEFAULT_MAX_RETRIES``
        behaviour of ``max_retries=None`` until ``with_delay`` wires it to
        ``DEFAULT_MAX_RETRIES`` at Job construction time."""
        delayable = self.env["res.partner"].with_delay()
        self.assertIsNone(delayable.delayable.max_retries)
