# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import WordPressCase

RETRY_PATTERN = {1: (5, 15), 5: (20, 40), 10: (45, 75), 15: (240, 360)}


class TestQueueJobFunctions(WordPressCase):
    def test_channels_are_registered_under_root(self):
        channels = self.env["queue.job.channel"].search(
            [("name", "in", ["wordpress_export_batch", "wordpress_export_record"])],
            order="name",
        )
        self.assertEqual(
            channels.mapped("complete_name"),
            ["root.wordpress_export_batch", "root.wordpress_export_record"],
        )

    def test_export_batch_lands_on_its_channel_with_20_attempts(self):
        binding_model = self.env["wordpress.ir.attachment"]
        job = self._new_job(
            "wordpress.ir.attachment",
            "export_batch",
            lambda: binding_model.with_delay().export_batch(self.backend),
        )
        self.assertEqual(job.channel, "root.wordpress_export_batch")
        self.assertEqual(job.max_retries, 20)
        self.assertEqual(job.job_function_id._parse_retry_pattern(), RETRY_PATTERN)

    def test_export_record_lands_on_its_channel_with_20_attempts(self):
        binding_model = self.env["wordpress.ir.attachment"]
        job = self._new_job(
            "wordpress.ir.attachment",
            "export_record",
            lambda: binding_model.with_delay().export_record(
                self.backend, self.attachment
            ),
        )
        self.assertEqual(job.channel, "root.wordpress_export_record")
        self.assertEqual(job.max_retries, 20)
        self.assertEqual(job.job_function_id._parse_retry_pattern(), RETRY_PATTERN)
