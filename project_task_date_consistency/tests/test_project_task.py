# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo.tests import SavepointCase


class TestDateConsistency(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestDateConsistency, cls).setUpClass()

        cls.task = cls.env["project.task"].create(
            {
                "name": "task1",
            }
        )

    def test_date_consistency_in_task(self):
        """
        PRE:
            - task1 exists
            - task1 time_deadline,time_start, time_end are empty
        ACT:
            - Combinations of fields are randomly generated
        POST:
            - All dates are consistent
        """

        tests = [
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {"date_start": datetime.datetime(2021, 11, 11, 8, 8, 8)}
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_start,
                    datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "Test-1.1.0: insert date_start Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {"date_end": datetime.datetime(2021, 11, 11, 8, 8, 8)}
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_end,
                    datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "Test-1.2.0: insert date_end Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {"date_end": datetime.datetime(2021, 11, 11, 8, 8, 8)}
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2021, 11, 11),
                    "Test-1.2.1: modify date_deadline Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {"date_deadline": datetime.date(2021, 11, 11)}
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2021, 11, 11),
                    "Test-1.3.0: modify date_deadline Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_end": datetime.datetime(2021, 11, 11, 8, 8, 8),
                        "date_deadline": datetime.date(2021, 11, 25),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_end,
                    datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "Test-1.4.0: modify date_end Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_end": datetime.datetime(2021, 11, 11, 8, 8, 8),
                        "date_deadline": datetime.date(2021, 11, 25),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2021, 11, 25),
                    "Test-1.4.1: modify date_deadline Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                        "date_end": datetime.datetime(2021, 12, 21, 8, 8, 8),
                        "date_deadline": datetime.date(2021, 11, 25),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_start,
                    datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "Test-1.5.0: modify date_start Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                        "date_end": "2021-12-21 08:08:08",
                        "date_deadline": datetime.date(2021, 11, 25),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_end,
                    datetime.datetime(2021, 12, 21, 8, 8, 8),
                    "Test-1.5.1: modify date_end Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                        "date_end": datetime.datetime(2021, 12, 21, 8, 8, 8),
                        "date_deadline": datetime.date(2021, 11, 25),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2021, 11, 25),
                    "Test-1.5.2: modify date_deadline Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                        "date_deadline": datetime.date(2022, 2, 22),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_start,
                    datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "Test-1.6.0: modify date_start Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                        "date_deadline": datetime.date(2021, 11, 25),
                    }
                ),
                "assert": lambda x: self.assertFalse(
                    x.date_end, "Test-1.6.1: date_end has values. Expected False"
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                        "date_deadline": datetime.date(2021, 11, 25),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2021, 11, 25),
                    "Test-1.6.2: modify date_deadline Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                        "date_end": datetime.datetime(2021, 12, 21, 8, 8, 8),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_start,
                    datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "Test-1.7.0: modify date_start Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                        "date_end": datetime.datetime(2021, 12, 21, 8, 8, 8),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_end,
                    datetime.datetime(2021, 12, 21, 8, 8, 8),
                    "Test-1.7.1: modify date_start Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                        "date_end": datetime.datetime(2021, 12, 21, 8, 8, 8),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2021, 12, 21),
                    "Test-1.7.2: modify date_deadline Fails",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": False,
                    }
                ),
                "assert": lambda x: self.assertFalse(
                    x.date_start, "Test-2.1.0: date_start fails, expected:False"
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": False,
                    }
                ),
                "assert": lambda x: self.assertFalse(
                    x.date_end, "Test-2.1.1: date_end fails, expected:False"
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": False,
                    }
                ),
                "assert": lambda x: self.assertFalse(
                    x.date_deadline, "Test-2.1.2: date_deadline fails, expected:False"
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2022, 5, 5, 8, 8, 8),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_start,
                    datetime.datetime(2022, 5, 5, 8, 8, 8),
                    "Test-2.1.3: write date_start fails",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2022, 5, 5, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2022, 5, 5, 8, 8, 8),
                    }
                ),
                "assert": lambda x: self.assertFalse(
                    x.date_end, "Test-2.1.4: date_end fails, expected:False"
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {"date_start": datetime.datetime(2022, 5, 5, 8, 8, 8)}
                ),
                "assert": lambda x: self.assertFalse(
                    x.date_deadline, "Test-2.1.5: date_deadline fails, expected:False"
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": False,
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                    }
                ),
                "assert": lambda x: self.assertFalse(
                    x.date_start, "Test-2.2.0: date_start fails, expected:False"
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": False,
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_end,
                    datetime.datetime(2024, 12, 12, 8, 8, 8),
                    "Test-2.2.1: date_end fails, expected:False",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": False,
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2024, 12, 12),
                    "Test-2.2.2: date_deadline fails",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2022, 5, 5, 8, 8, 8),
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                    },
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_start,
                    datetime.datetime(2022, 5, 5, 8, 8, 8),
                    "Test-2.2.3: write date_start fails",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2022, 5, 5, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2022, 5, 5, 8, 8, 8),
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_end,
                    datetime.datetime(2024, 12, 12, 8, 8, 8),
                    "Test-2.2.4: date_end fails, expected:False",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2022, 5, 5, 8, 8, 8),
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2024, 12, 12),
                    "Test-2.2.5: date_deadline fails, expected:False",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": False,
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                        "date_deadline": datetime.date(2022, 1, 1),
                    }
                ),
                "assert": lambda x: self.assertFalse(
                    x.date_start, "Test-2.3.0: date_start fails, expected:False"
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": False,
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                        "date_deadline": datetime.date(2022, 1, 1),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_end,
                    datetime.datetime(2024, 12, 12, 8, 8, 8),
                    "Test-2.3.1: date_end fails",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": False,
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                        "date_deadline": datetime.date(2022, 1, 1),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2022, 1, 1),
                    "Test-2.3.2: date_deadline fails",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2022, 5, 5, 8, 8, 8),
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                        "date_deadline": datetime.date(2022, 1, 1),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_start,
                    datetime.datetime(2022, 5, 5, 8, 8, 8),
                    "Test-2.3.3: date_start fails",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2022, 5, 5, 8, 8, 8),
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                        "date_deadline": datetime.date(2022, 1, 1),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_end,
                    datetime.datetime(2024, 12, 12, 8, 8, 8),
                    "Test-2.3.4: date_start fails",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2021, 11, 11, 8, 8, 8),
                    "date_end": False,
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_start": datetime.datetime(2022, 5, 5, 8, 8, 8),
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                        "date_deadline": datetime.date(2022, 1, 1),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2022, 1, 1),
                    "Test-2.3.5: date_deadline fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": datetime.datetime(2022, 2, 22, 8, 8, 8),
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2024, 12, 12),
                    "Test-2.4.0: date_deadline fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": datetime.datetime(2022, 2, 22, 8, 8, 8),
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {
                        "date_end": datetime.datetime(2024, 12, 12, 8, 8, 8),
                        "date_deadline": datetime.date(2015, 1, 1),
                    }
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2015, 1, 1),
                    "Test-2.5.0: date_deadline fails",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": datetime.datetime(2022, 2, 22, 8, 8, 8),
                    "date_deadline": False,
                },
                "act": lambda x: x.write({"date_end": False}),
                "assert": lambda x: self.assertFalse(
                    x.date_end, "Test-2.6.0: date_end fails"
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2022, 2, 22, 6, 6, 6),
                    "date_end": datetime.datetime(2022, 2, 22, 8, 8, 8),
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {"date_end": datetime.datetime(2022, 2, 23, 8, 8, 8)}
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_start,
                    datetime.datetime(2022, 2, 23, 6, 6, 6),
                    "Test-2.7.0: date_start fail.",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2022, 2, 22, 6, 6, 6),
                    "date_end": datetime.datetime(2022, 2, 22, 8, 8, 8),
                    "date_deadline": False,
                },
                "act": lambda x: x.write(
                    {"date_end": datetime.datetime(2022, 2, 23, 8, 8, 8)}
                ),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2022, 2, 23),
                    "Test-2.7.1: date_deadline fail.",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2022, 2, 22, 6, 6, 6),
                    "date_end": datetime.datetime(2022, 2, 22, 8, 8, 8),
                    "date_deadline": False,
                },
                "act": lambda x: x.write({"date_deadline": datetime.date(2022, 7, 7)}),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2022, 7, 7),
                    "Test-2.8.0: date_deadline fail.",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2022, 2, 22, 6, 6, 6),
                    "date_end": datetime.datetime(2022, 2, 22, 8, 8, 8),
                    "date_deadline": False,
                },
                "act": lambda x: x.write({"date_deadline": datetime.date(2022, 7, 7)}),
                "assert": lambda x: self.assertEqual(
                    x.date_deadline,
                    datetime.date(2022, 7, 7),
                    "Test-2.8.0: date_deadline fail.",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2022, 2, 22, 6, 6, 6),
                    "date_end": datetime.datetime(2022, 2, 22, 8, 8, 8),
                    "date_deadline": False,
                },
                "act": lambda x: x.write({"date_deadline": datetime.date(2022, 7, 7)}),
                "assert": lambda x: self.assertEqual(
                    x.date_end,
                    datetime.datetime(2022, 7, 7, 8, 8, 8),
                    "Test-2.8.1: date_end fail.",
                ),
            },
            {
                "arrange": {
                    "date_start": datetime.datetime(2022, 2, 22, 6, 6, 6),
                    "date_end": datetime.datetime(2022, 2, 22, 8, 8, 8),
                    "date_deadline": False,
                },
                "act": lambda x: x.write({"date_deadline": datetime.date(2022, 7, 7)}),
                "assert": lambda x: self.assertEqual(
                    x.date_start,
                    datetime.datetime(2022, 7, 7, 6, 6, 6),
                    "Test-2.8.2: date_start fail.",
                ),
            },
            {
                "arrange": {
                    "date_start": False,
                    "date_end": datetime.datetime(2022, 2, 22, 8, 8, 8),
                    "date_deadline": False,
                },
                "act": lambda x: x.write({"date_deadline": datetime.date(2022, 7, 7)}),
                "assert": lambda x: self.assertEqual(
                    x.date_end,
                    datetime.datetime(2022, 7, 7, 8, 8, 8),
                    "Test-2.9.1: date_end fail.",
                ),
            },
        ]

        for t in tests:
            if "arrange" in t:
                self.task.write(t["arrange"])
            if "act" in t:
                t["act"](self.task)
            with self.subTest():
                t.get("assert", t.get("actassert"))(self.task)
