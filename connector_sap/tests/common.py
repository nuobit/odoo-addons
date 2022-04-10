# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.tests.common import SavepointComponentCase

_logger = logging.getLogger(__name__)


class TestLengowConnector(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # disable jobs
        # TODO: it breaks the folio creation with error:
        #   psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint
        #       "mail_followers_mail_followers_res_partner_res_model_id_uniq"

        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,  # no jobs thanks
            )
        )

        cls.user1 = lambda self, lengow: cls.env["res.users"].create(
            {
                "name": "User backend 1",
                "login": "userbackend1",
                "company_id": lengow.company_id.id,
                "groups_id": [
                    (
                        6,
                        0,
                        [

                            cls.env.ref("base.group_user").id,
                            cls.env.ref("connector.group_connector_manager").id,

                        ],
                    )
                ],
            }
        )

        cls.user1 = lambda self, lengow: cls.env.ref("base.user_root")
