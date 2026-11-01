# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.tests.common import TransactionComponentCase


class WordPressCase(TransactionComponentCase):
    """Backend and an attachment without any HTTP call."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        lang = cls.env.ref("base.lang_en")
        cls.backend = cls.env["wordpress.backend"].create(
            {
                "name": "WordPress test backend",
                "url": "http://127.0.0.1:1",
                "username": "odoo.test",
                "application_password": "test",
                "lang_ids": [(6, 0, lang.ids)],
            }
        )
        cls.attachment = cls.env["ir.attachment"].create({"name": "photo.png"})

    def _new_job(self, model_name, method_name, run):
        job_model = self.env["queue.job"]
        domain = [("model_name", "=", model_name), ("method_name", "=", method_name)]
        before = job_model.search(domain)
        run()
        jobs = job_model.search(domain) - before
        self.assertEqual(len(jobs), 1)
        return jobs
