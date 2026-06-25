# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError, UserError
from odoo.tests.common import SavepointCase


class TestDocumentPageDistribution(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, mail_notify_force_send=False))
        cls.company = cls.env.company
        cls.internal = cls.env.ref("base.group_user")
        cls.group_manager = cls.env.ref("document_page.group_document_manager")
        cls.group_a = cls.env["res.groups"].create({"name": "DPD Group A"})
        cls.group_b = cls.env["res.groups"].create({"name": "DPD Group B"})
        # activate languages used by the multi-language test
        cls.env["res.lang"]._activate_lang("es_ES")
        cls.env["res.lang"]._activate_lang("ca_ES")
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.manager = Users.create(
            {
                "name": "Manager",
                "login": "dpd_mgr",
                "email": "mgr@example.com",
                "lang": "en_US",
                "groups_id": [
                    (6, 0, [cls.internal.id, cls.group_manager.id, cls.group_a.id])
                ],
            }
        )
        cls.reader_es = Users.create(
            {
                "name": "Reader ES",
                "login": "dpd_es",
                "email": "es@example.com",
                "lang": "es_ES",
                "groups_id": [(6, 0, [cls.internal.id, cls.group_a.id])],
            }
        )
        cls.reader_ca = Users.create(
            {
                "name": "Reader CA",
                "login": "dpd_ca",
                "email": "ca@example.com",
                "lang": "ca_ES",
                "groups_id": [(6, 0, [cls.internal.id, cls.group_a.id])],
            }
        )
        cls.reader_b = Users.create(
            {
                "name": "Reader B",
                "login": "dpd_b",
                "email": "b@example.com",
                "groups_id": [(6, 0, [cls.internal.id, cls.group_b.id])],
            }
        )
        cls.user_no_email = Users.create(
            {
                "name": "No Email",
                "login": "dpd_noemail",
                "email": False,
                "groups_id": [(6, 0, [cls.internal.id, cls.group_a.id])],
            }
        )
        cls.user_inactive = Users.create(
            {
                "name": "Inactive",
                "login": "dpd_inactive",
                "email": "inactive@example.com",
                "active": False,
                "groups_id": [(6, 0, [cls.internal.id, cls.group_a.id])],
            }
        )
        cls.page = cls.env["document.page"].create(
            {
                "name": "Test Procedure",
                "type": "content",
                "content": "<p>First version</p>",
                "draft_summary": "Initial release",
                "groups_id": [(6, 0, [cls.group_a.id])],
            }
        )
        # assign the default distribution template explicitly (the module ships
        # it but does not auto-seed it on the company)
        cls.template = cls.env.ref(
            "document_page_distribution.mail_template_document_page_distribution"
        )
        cls.company.document_page_distribution_template_id = cls.template

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _open_wizard(self, user=None):
        user = user or self.manager
        action = self.page.with_user(user).action_distribute()
        return (
            self.env["document.page.distribute"]
            .with_user(user)
            .with_context(**action["context"])
            .create({})
        )

    def _distribute(self, user=None, only_partners=None):
        wizard = self._open_wizard(user)
        if only_partners is not None:
            for line in wizard.line_ids:
                line.selected = line.partner_id in only_partners
        wizard.action_confirm()
        return wizard

    def _recipients(self):
        return self.page.history_head.recipient_ids

    # ------------------------------------------------------------------
    # coverage
    # ------------------------------------------------------------------
    def test_coverage_resolution(self):
        users = self.page._get_distribution_coverage_users()
        self.assertIn(self.manager, users)
        self.assertIn(self.reader_es, users)
        self.assertIn(self.reader_ca, users)
        self.assertIn(self.user_no_email, users)  # in coverage, sent later as no_email
        self.assertNotIn(self.reader_b, users)  # other group
        self.assertNotIn(self.user_inactive, users)  # archived

    def test_coverage_empty_groups_blocks(self):
        self.page.groups_id = [(5, 0, 0)]
        with self.assertRaises(UserError):
            self.page.with_user(self.manager).action_distribute()

    def test_template_not_configured_blocks(self):
        self.company.document_page_distribution_template_id = False
        with self.assertRaises(UserError):
            self.page.with_user(self.manager).action_distribute()

    # ------------------------------------------------------------------
    # permissions
    # ------------------------------------------------------------------
    def test_distribute_denied_for_non_manager_ui(self):
        with self.assertRaises(AccessError):
            self.page.with_user(self.reader_es).action_distribute()

    def test_distribute_denied_for_non_manager_rpc(self):
        # calling the engine directly (RPC-style) must also be blocked
        with self.assertRaises(AccessError):
            self.page.with_user(self.reader_es)._distribute_send(
                self.page.history_head,
                self._recipients(),
                self.template,
            )

    def test_log_hidden_outside_document_groups(self):
        # the distribution log mirrors the document visibility: a document
        # user not sharing the document groups cannot read it through RPC
        self._distribute(only_partners=self.reader_es.partner_id)
        recipient_ids = self._recipients().ids
        doc_user = self.env.ref("knowledge.group_document_user")
        Users = self.env["res.users"].with_context(no_reset_password=True)
        outsider = Users.create(
            {
                "name": "Outsider",
                "login": "dpd_outsider",
                "email": "outsider@example.com",
                "groups_id": [(6, 0, [self.internal.id, doc_user.id, self.group_b.id])],
            }
        )
        insider = Users.create(
            {
                "name": "Insider",
                "login": "dpd_insider",
                "email": "insider@example.com",
                "groups_id": [(6, 0, [self.internal.id, doc_user.id, self.group_a.id])],
            }
        )
        Recipient = self.env["document.page.history.recipient"]
        Send = self.env["document.page.history.recipient.send"]
        domain = [("document_page_id", "=", self.page.id)]
        self.assertFalse(Recipient.with_user(outsider).search(domain))
        self.assertFalse(Send.with_user(outsider).search(domain))
        with self.assertRaises(AccessError):
            Recipient.with_user(outsider).browse(recipient_ids).read(["email"])
        self.assertTrue(Recipient.with_user(insider).search(domain))
        self.assertTrue(Send.with_user(insider).search(domain))

    # ------------------------------------------------------------------
    # sending
    # ------------------------------------------------------------------
    def test_distribute_creates_recipients_and_sends(self):
        self._distribute()
        recipients = self._recipients()
        # every coverage candidate has a recipient line (incl. no_email)
        partners = recipients.mapped("partner_id")
        self.assertIn(self.reader_es.partner_id, partners)
        self.assertIn(self.user_no_email.partner_id, partners)
        self.assertNotIn(self.reader_b.partner_id, partners)
        # no_email line exists but has no send
        no_email_rec = recipients.filtered(
            lambda r: r.partner_id == self.user_no_email.partner_id
        )
        self.assertEqual(no_email_rec.state, "no_email")
        self.assertFalse(no_email_rec.send_ids)
        # a sendable recipient got a real send + an email notification
        es_rec = recipients.filtered(
            lambda r: r.partner_id == self.reader_es.partner_id
        )
        self.assertTrue(es_rec.send_ids)
        notif = es_rec.send_ids.mail_notification_id
        self.assertEqual(notif.notification_type, "email")
        self.assertEqual(es_rec.state, "queued")  # ready -> queued

    def test_inbox_user_still_receives_email(self):
        self.reader_es.notification_type = "inbox"
        self._distribute(only_partners=self.reader_es.partner_id)
        es_rec = self._recipients().filtered(
            lambda r: r.partner_id == self.reader_es.partner_id
        )
        notif = es_rec.send_ids.mail_notification_id
        self.assertEqual(notif.notification_type, "email")
        self.assertTrue(notif)

    def test_no_followers_subscribed(self):
        self._distribute()
        followers = self.page.message_follower_ids.mapped("partner_id")
        self.assertNotIn(self.reader_es.partner_id, followers)
        self.assertNotIn(self.reader_ca.partner_id, followers)

    def test_multilang_one_message_per_language(self):
        before = self.page.message_ids
        self._distribute(
            only_partners=self.reader_es.partner_id | self.reader_ca.partner_id
        )
        new_messages = self.page.message_ids - before
        notes = new_messages.filtered(lambda m: m.message_type == "notification")
        # one chatter message per effective language (es_ES, ca_ES)
        self.assertEqual(len(notes), 2)

    def test_message_shows_version_and_summary(self):
        self._distribute(only_partners=self.reader_es.partner_id)
        message = self.page.message_ids.filtered(
            lambda m: m.message_type == "notification"
        )[:1]
        self.assertIn(self.page.name, message.body)
        self.assertIn("Initial release", message.body)

    def test_message_email_from_uses_template(self):
        self.company.email = "docs@example.com"
        self._distribute(only_partners=self.reader_es.partner_id)
        message = self.page.message_ids.filtered(
            lambda m: m.message_type == "notification"
        )[:1]
        self.assertIn("docs@example.com", message.email_from)

    # ------------------------------------------------------------------
    # redistribution & preselection
    # ------------------------------------------------------------------
    def test_redistribute_new_send_same_recipient_no_new_version(self):
        versions_before = len(self.page.history_ids)
        self._distribute(only_partners=self.reader_es.partner_id)
        self._distribute(only_partners=self.reader_es.partner_id)
        es_rec = self._recipients().filtered(
            lambda r: r.partner_id == self.reader_es.partner_id
        )
        self.assertEqual(len(es_rec), 1)
        self.assertEqual(len(es_rec.send_ids), 2)
        self.assertEqual(len(self.page.history_ids), versions_before)

    def test_preselection_excludes_already_sent(self):
        # queued recipients are not preselected by default on the next round
        self._distribute(only_partners=self.reader_es.partner_id)
        wizard = self._open_wizard()
        es_line = wizard.line_ids.filtered(
            lambda line: line.partner_id == self.reader_es.partner_id
        )
        self.assertFalse(es_line.selected)
        # a never-sent candidate stays preselected
        ca_line = wizard.line_ids.filtered(
            lambda line: line.partner_id == self.reader_ca.partner_id
        )
        self.assertTrue(ca_line.selected)

    def test_confirm_blocks_if_version_changed(self):
        wizard = self._open_wizard()
        # a new version is published while the wizard is open
        self.page.write({"content": "<p>Second version</p>"})
        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_security_change_keeps_past_audit(self):
        self._distribute(only_partners=self.reader_es.partner_id)
        es_rec = self._recipients().filtered(
            lambda r: r.partner_id == self.reader_es.partner_id
        )
        sends_before = len(es_rec.send_ids)
        # remove the group afterwards: the past send is preserved
        self.page.groups_id = [(6, 0, [self.group_b.id])]
        self.assertEqual(len(es_rec.send_ids), sends_before)
        self.assertTrue(es_rec.exists())

    # ------------------------------------------------------------------
    # historical versions
    # ------------------------------------------------------------------
    def test_old_version_keeps_recipients_and_sends(self):
        # distribute the first version
        self._distribute(only_partners=self.reader_es.partner_id)
        v1 = self.page.history_head
        v1_rec = v1.recipient_ids.filtered(
            lambda r: r.partner_id == self.reader_es.partner_id
        )
        self.assertTrue(v1_rec)
        self.assertTrue(v1_rec.send_ids)
        sends_before = len(v1_rec.send_ids)

        # publish a new version: history_head moves to v2
        self.page.write({"content": "<p>Second version</p>"})
        self.page.invalidate_cache()
        v2 = self.page.history_head
        self.assertNotEqual(v1, v2)

        # the old version still owns its recipients and their sends
        self.assertIn(v1_rec, v1.recipient_ids)
        self.assertTrue(v1_rec.exists())
        self.assertEqual(len(v1_rec.send_ids), sends_before)

        # the document's "current" distribution reflects v2 (empty), not v1
        self.assertFalse(self.page.current_recipient_ids)
        self.assertNotIn(v1_rec, self.page.current_recipient_ids)

        # the historical sends stay reachable through the per-recipient action
        action = v1_rec.action_open_sends()
        self.assertEqual(action["res_model"], "document.page.history.recipient.send")
        sends = self.env["document.page.history.recipient.send"].search(
            action["domain"]
        )
        self.assertEqual(sends, v1_rec.send_ids)

    def test_distribution_count_per_version(self):
        # a distributed version reports its own recipient count...
        self._distribute(only_partners=self.reader_es.partner_id)
        v1 = self.page.history_head
        self.assertTrue(v1.distribution_count > 0)
        self.assertEqual(v1.distribution_count, len(v1.recipient_ids))
        # ...and a newer, undistributed version keeps its own count at 0
        self.page.write({"content": "<p>Second version</p>"})
        self.page.invalidate_cache()
        v2 = self.page.history_head
        self.assertNotEqual(v1, v2)
        self.assertEqual(v2.distribution_count, 0)
        self.assertTrue(v1.distribution_count > 0)

    # ------------------------------------------------------------------
    # review follow-ups (#2630)
    # ------------------------------------------------------------------
    def test_failed_states_are_represelected(self):
        # a recipient whose last status is a failure is preselected again
        self._distribute(only_partners=self.reader_es.partner_id)
        es_rec = self._recipients().filtered(
            lambda r: r.partner_id == self.reader_es.partner_id
        )
        notif = es_rec.send_ids.mail_notification_id
        self.assertTrue(notif)
        for status, expected in (
            ("bounce", "bounce"),
            ("exception", "error"),
            ("canceled", "canceled"),
        ):
            notif.notification_status = status
            es_rec.invalidate_cache()
            self.assertEqual(es_rec.state, expected)
            wizard = self._open_wizard()
            es_line = wizard.line_ids.filtered(
                lambda line: line.partner_id == self.reader_es.partner_id
            )
            self.assertTrue(
                es_line.selected, "state %s must be re-preselected" % status
            )

    def test_blank_lang_user_grouped_as_en_us(self):
        # a user with no language is treated and grouped as en_US
        self.reader_es.lang = False
        self.assertFalse(self.reader_es.lang)
        before = self.page.message_ids
        self._distribute(
            only_partners=self.manager.partner_id | self.reader_es.partner_id
        )
        notes = (self.page.message_ids - before).filtered(
            lambda m: m.message_type == "notification"
        )
        # blank lang grouped with the en_US manager -> a single message
        self.assertEqual(len(notes), 1)
        es_rec = self._recipients().filtered(
            lambda r: r.partner_id == self.reader_es.partner_id
        )
        self.assertTrue(es_rec.send_ids)

    def test_async_notification_status_reflected_in_state(self):
        # a later asynchronous status change reaches the line summary
        self._distribute(only_partners=self.reader_es.partner_id)
        es_rec = self._recipients().filtered(
            lambda r: r.partner_id == self.reader_es.partner_id
        )
        self.assertEqual(es_rec.state, "queued")  # ready -> queued
        notif = es_rec.send_ids.mail_notification_id
        self.assertTrue(notif)
        notif.notification_status = "bounce"
        es_rec.invalidate_cache()
        self.assertEqual(es_rec.state, "bounce")

    def test_cancel_wizard_creates_no_records(self):
        # opening the wizard and not confirming must not persist anything
        Recipient = self.env["document.page.history.recipient"]
        Send = self.env["document.page.history.recipient.send"]
        domain = [("document_page_id", "=", self.page.id)]
        self.assertEqual(Recipient.search_count(domain), 0)
        self.assertEqual(Send.search_count(domain), 0)
        self._open_wizard()  # built but never confirmed == cancelled
        self.assertEqual(Recipient.search_count(domain), 0)
        self.assertEqual(Send.search_count(domain), 0)
