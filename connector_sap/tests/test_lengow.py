# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from . import common

_logger = logging.getLogger(__name__)


# TODO:Use freezegun
class TestLengow(common.TestLengowConnector):

    def test_lengow_01(self):
        # ARRANGE
        p1 = self.browse_ref("base.main_company")

        backend = self.env["lengow.backend"].create(
            {
                "name": "Test backend",
                "company_id": p1.id,
                "user_id": self.user1(p1).id,
                "access_token": '47ee4346bf5b0734bb3c239ab24555bbe0e5a2a00e48fd6a9a04195704de241c',
                "secret": '87e3ac91030ae16c2e8971404ddf308bd168ab53f493903fb03318fdf3cc80f9',
                # **self.fake_credentials,
            }
        )

        with backend.work_on("lengow.sale.order") as work:
            adapter = work.component(usage="backend.adapter")

        # r1w_values = {
        #     "name": "Room type r1",
        # }
        # _aaa=('leroy',14645)
        # r1w_id = adapter.read(_aaa)
        # print(adapter._prepare_parameters({'a':1, 'b':2,'c':3}, ['a','b','c'], ['d']))
        r1w_id = adapter._exec('orders', **{'marketplace_order_date_from': '2022-03-01',
                                            })
        # print(r1w_id)

        # params= [("marketplace","in",["leroymerlin","decathlon"])]
        # params={
        #     "marketplace_order_id":["4UT0-000009","4UT0-000008"],
        #     "marketplace":"leroymerlin"
        # }
        # print(adapter.read(params))
        # params = [("marketplace_order_id", "=", "4UT0-000071"),
        #           ("marketplace", "in", ["decathlon", "leroymerlin"])]
        # params = [("marketplace_order_id", "in", ["4UT0-000071","4UT0-000037"]),("marketplace","in",["decathlon","leroymerlin"])]
        # print(adapter.search_read(params))

        # print(adapter.read("leroymerlin", "4UT0-000037"))
        # print(r1w_id)
        # [("marketplace_order_id", "in", ["4UT0-000009", "4UT0-000008"]),
        #  ("marketplace", "in", ["lesssroymerlin", "decathlon"])]
        # domain=[('a','=',1),('b','!=',False),('c','in',[1,2,3,4])]

        # print(adapter._domain_to_normalized_dict(domain))

    # def test_access_with_bad_token(self):
    #     p1 = self.browse_ref("base.main_company")
    #
    #     backend = self.env["lengow.backend"].create(
    #         {
    #             "name": "Test backend",
    #             "company_id": p1.id,
    #             "user_id": self.user1(p1).id,
    #             "access_token": '9e',
    #             "secret": 'f3df392231bb7941414d0ec58ec9eb260865f4f1f7c88d0b53c748b26d4bd387',
    #             # **self.fake_credentials,
    #         }
    #     )
    #
    #     with backend.work_on("lengow.sale.order") as work:
    #         adapter = work.component(usage="backend.adapter")
    #
    #
    #     # self.assertRaises(ConnectionError('f"Error trying to log in\n{r.text}"'),  adapter._exec('get_token'))
    #     # r1w_id = adapter._exec('get_token', **{'imported_from': '2021-10-10'})
    #     # adapter._exec('get_token', **{'imported_from': '2021-10-10'})
    #     # # self.assertRaises('connectionError')
    #
    #     with self.assertRaises(
    #             ConnectionError, msg="Error trying to log in"
    #     ):
    #         adapter._exec('get_token')
    #
    #
    # def test_access_with_token_ok(self):
    #     p1 = self.browse_ref("base.main_company")
    #
    #     backend = self.env["lengow.backend"].create(
    #         {
    #             "name": "Test backend",
    #             "company_id": p1.id,
    #             "user_id": self.user1(p1).id,
    #             "access_token": '9e2172a84d3af37bdc616afa50f71d94758791c881c545cdaa7f6783884a976b',
    #             "secret": 'f3df392231bb7941414d0ec58ec9eb260865f4f1f7c88d0b53c748b26d4bd387',
    #             # **self.fake_credentials,
    #         }
    #     )
    #     with backend.work_on("lengow.sale.order") as work:
    #         adapter = work.component(usage="backend.adapter")
    #
    #     self.assertIsNotNone(adapter._exec('get_token'))
    #
    # def test_get_orders_ok(self):
    #     p1 = self.browse_ref("base.main_company")
    #
    #     backend = self.env["lengow.backend"].create(
    #         {
    #             "name": "Test backend",
    #             "company_id": p1.id,
    #             "user_id": self.user1(p1).id,
    #             "access_token": '9e2172a84d3af37bdc616afa50f71d94758791c881c545cdaa7f6783884a976b',
    #             "secret": 'f3df392231bb7941414d0ec58ec9eb260865f4f1f7c88d0b53c748b26d4bd387',
    #             # **self.fake_credentials,
    #         }
    #     )
    #     with backend.work_on("lengow.sale.order") as work:
    #         adapter = work.component(usage="backend.adapter")
    #
    #     self.assertIsNotNone(adapter._exec('orders'))

    # def test_get_orders_empty(self):
    #     p1 = self.browse_ref("base.main_company")
    #
    #     backend = self.env["lengow.backend"].create(
    #         {
    #             "name": "Test backend",
    #             "company_id": p1.id,
    #             "user_id": self.user1(p1).id,
    #             "access_token": '9e2172a84d3af37bdc616afa50f71d94758791c881c545cdaa7f6783884a976b',
    #             "secret": 'f3df392231bb7941414d0ec58ec9eb260865f4f1f7c88d0b53c748b26d4bd387',
    #             # **self.fake_credentials,
    #         }
    #     )
    #     with backend.work_on("lengow.sale.order") as work:
    #         adapter = work.component(usage="backend.adapter")
    #
    #     self.assertIsNone(adapter._exec('orders',  **{'imported_from': '2023-10-10'}))
