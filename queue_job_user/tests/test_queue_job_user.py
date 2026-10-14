# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import exceptions
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestQueueJobUser(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env["res.users"].create(
            {
                "name": "Job Queue User",
                "login": "queue_job_user",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("queue_job_user.group_queue_job_user").id,
                        ],
                    )
                ],
            }
        )
        cls.manager = cls.env["res.users"].create(
            {
                "name": "Job Queue Manager",
                "login": "queue_job_manager",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("queue_job.group_queue_job_manager").id,
                        ],
                    )
                ],
            }
        )
        cls.channel_group = cls.env["res.groups"].create({"name": "Test channel"})
        cls.env["ir.model.access"].create(
            {
                "name": "test channel",
                "model_id": cls.env.ref("queue_job.model_queue_job").id,
                "group_id": cls.channel_group.id,
                "perm_read": True,
            }
        )
        cls.env["ir.rule"].create(
            {
                "name": "Test channel",
                "model_id": cls.env.ref("queue_job.model_queue_job").id,
                "groups": [(4, cls.channel_group.id)],
                "domain_force": "[('channel', '=', 'root.test')]",
            }
        )
        cls.writer_group = cls.env["res.groups"].create({"name": "Test channel writer"})
        cls.env["ir.model.access"].create(
            {
                "name": "test channel writer",
                "model_id": cls.env.ref("queue_job.model_queue_job").id,
                "group_id": cls.writer_group.id,
                "perm_read": True,
                "perm_write": True,
            }
        )
        cls.env["ir.rule"].create(
            {
                "name": "Test channel writer",
                "model_id": cls.env.ref("queue_job.model_queue_job").id,
                "groups": [(4, cls.writer_group.id)],
                "domain_force": "[('channel', '=', 'root.test')]",
                "perm_read": False,
                "perm_write": True,
                "perm_create": False,
                "perm_unlink": False,
            }
        )
        cls.writer = cls.env["res.users"].create(
            {
                "name": "Test channel writer",
                "login": "test_channel_writer",
                "groups_id": [
                    (6, 0, [cls.env.ref("base.group_user").id, cls.writer_group.id])
                ],
            }
        )

    def test_user_search(self):
        jobs = self.env["queue.job"]
        jobs += (
            self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        )
        jobs += (
            self.env["res.partner"]
            .with_user(self.manager)
            .with_delay(channel="root.test")
            .create({"name": "test"})
            .db_record()
        )
        self.assertEqual(
            self.env["queue.job"].with_user(self.user).search([("id", "in", jobs.ids)]),
            jobs,
        )

    def test_user_read(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        self.env["queue.job"].flush()
        model = self.env["queue.job"].with_user(self.user)
        for view_type in ("form", "tree"):
            fields = model.fields_view_get(view_type=view_type)["fields"]
            self.assertTrue(fields)
            self.env["queue.job"].invalidate_cache()
            values = model.browse(job.id).read(list(fields))[0]
            self.assertFalse(set(fields) - set(values))

    def test_user_write(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        with self.assertRaises(exceptions.AccessError):
            job.with_user(self.user).priority = 30

    def test_user_create(self):
        with self.assertRaises(exceptions.AccessError):
            self.env["queue.job"].with_user(self.user).with_context(
                _job_edit_sentinel=self.env["queue.job"].EDIT_SENTINEL,
            ).create(
                {
                    "uuid": "test",
                    "user_id": self.user.id,
                    "state": "failed",
                    "model_name": "queue.job",
                    "method_name": "write",
                    "args": (),
                }
            )

    def test_user_unlink(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        with self.assertRaises(exceptions.AccessError):
            job.with_user(self.user).unlink()

    def test_user_requeue(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        job.state = "failed"
        with self.assertRaises(exceptions.AccessError):
            job.with_user(self.user).requeue()
        self.assertEqual(job.state, "failed")

    def test_user_done(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        with self.assertRaises(exceptions.AccessError):
            job.with_user(self.user).button_done()
        self.assertEqual(job.state, "pending")

    def test_user_cancelled(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        with self.assertRaises(exceptions.AccessError):
            job.with_user(self.user).button_cancelled()
        self.assertEqual(job.state, "pending")

    def test_user_sudo_cancelled(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        job.with_user(self.user).sudo().button_cancelled()
        self.assertEqual(job.state, "cancelled")

    def test_manager_cancelled(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        job.with_user(self.manager).button_cancelled()
        self.assertEqual(job.state, "cancelled")

    def test_manager_requeue(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        job.state = "failed"
        job.with_user(self.manager).requeue()
        self.assertEqual(job.state, "pending")

    def test_manager_done(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        job.with_user(self.manager).button_done()
        self.assertEqual(job.state, "done")

    def test_rule_cancelled(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        with self.assertRaises(exceptions.AccessError):
            job.with_user(self.writer).button_cancelled()
        self.assertEqual(job.state, "pending")

    def test_writer_cancelled(self):
        job = (
            self.env["res.partner"]
            .with_delay(channel="root.test")
            .create({"name": "test"})
            .db_record()
        )
        job.with_user(self.writer).button_cancelled()
        self.assertEqual(job.state, "cancelled")

    def test_user_writer_cancelled(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        channel_job = (
            self.env["res.partner"]
            .with_delay(channel="root.test")
            .create({"name": "test"})
            .db_record()
        )
        self.writer.write(
            {"groups_id": [(4, self.env.ref("queue_job_user.group_queue_job_user").id)]}
        )
        with self.assertRaises(exceptions.AccessError):
            job.with_user(self.writer).button_cancelled()
        self.assertEqual(job.state, "pending")
        channel_job.with_user(self.writer).button_cancelled()
        self.assertEqual(channel_job.state, "cancelled")

    def test_user_menus(self):
        menu_ids = (
            self.env["ir.ui.menu"]
            .with_user(self.user)
            .load_menus(False)["all_menu_ids"]
        )
        self.assertIn(self.env.ref("queue_job.menu_queue_job").id, menu_ids)
        self.assertNotIn(self.env.ref("queue_job.menu_queue_job_channel").id, menu_ids)
        self.assertNotIn(self.env.ref("queue_job.menu_queue_job_function").id, menu_ids)

    def test_manager_menus(self):
        menu_ids = (
            self.env["ir.ui.menu"]
            .with_user(self.manager)
            .load_menus(False)["all_menu_ids"]
        )
        self.assertIn(self.env.ref("queue_job.menu_queue_job").id, menu_ids)
        self.assertIn(self.env.ref("queue_job.menu_queue_job_channel").id, menu_ids)
        self.assertIn(self.env.ref("queue_job.menu_queue_job_function").id, menu_ids)

    def test_user_actions(self):
        toolbar = (
            self.env["queue.job"]
            .with_user(self.user)
            .fields_view_get(view_type="tree", toolbar=True)["toolbar"]
        )
        action_ids = [action["id"] for action in toolbar["action"]]
        self.assertNotIn(self.env.ref("queue_job.action_requeue_job").id, action_ids)
        self.assertNotIn(self.env.ref("queue_job.action_set_jobs_done").id, action_ids)
        self.assertNotIn(
            self.env.ref("queue_job.action_set_jobs_cancelled").id, action_ids
        )

    def test_manager_actions(self):
        toolbar = (
            self.env["queue.job"]
            .with_user(self.manager)
            .fields_view_get(view_type="tree", toolbar=True)["toolbar"]
        )
        action_ids = [action["id"] for action in toolbar["action"]]
        self.assertIn(self.env.ref("queue_job.action_requeue_job").id, action_ids)
        self.assertIn(self.env.ref("queue_job.action_set_jobs_done").id, action_ids)
        self.assertIn(
            self.env.ref("queue_job.action_set_jobs_cancelled").id, action_ids
        )

    def test_manager_user(self):
        self.assertTrue(self.manager.has_group("queue_job_user.group_queue_job_user"))

    def test_user_rule_search(self):
        jobs = self.env["queue.job"]
        jobs += (
            self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        )
        jobs += (
            self.env["res.partner"]
            .with_delay(channel="root.test")
            .create({"name": "test"})
            .db_record()
        )
        self.user.write({"groups_id": [(4, self.channel_group.id)]})
        self.assertEqual(
            self.env["queue.job"].with_user(self.user).search([("id", "in", jobs.ids)]),
            jobs,
        )

    def test_rule_search(self):
        job = self.env["res.partner"].with_delay().create({"name": "test"}).db_record()
        channel_job = (
            self.env["res.partner"]
            .with_delay(channel="root.test")
            .create({"name": "test"})
            .db_record()
        )
        channel_user = self.env["res.users"].create(
            {
                "name": "Test channel user",
                "login": "test_channel_user",
                "groups_id": [
                    (6, 0, [self.env.ref("base.group_user").id, self.channel_group.id])
                ],
            }
        )
        self.assertEqual(
            self.env["queue.job"]
            .with_user(channel_user)
            .search([("id", "in", (job + channel_job).ids)]),
            channel_job,
        )
