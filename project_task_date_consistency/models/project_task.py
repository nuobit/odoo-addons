# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import timedelta

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"
    date_start = fields.Datetime()
    date_end = fields.Datetime()
    date_deadline = fields.Date()

    def _check_consistency_update(self, values):  # noqa: C901
        if "date_start" in values:
            values["date_start"] = fields.Datetime.to_datetime(values["date_start"])
        if "date_end" in values:
            values["date_end"] = fields.Datetime.to_datetime(values["date_end"])
        if "date_deadline" in values:
            values["date_deadline"] = fields.Date.to_date(values["date_deadline"])
        if (
            "date_start" in values
            and "date_end" in values
            and "date_deadline" not in values
        ):
            if values["date_end"]:
                values["date_deadline"] = values["date_end"].date()
        elif (
            "date_start" not in values
            and "date_end" in values
            and "date_deadline" in values
        ):
            if values["date_end"] and self.date_start and self.date_end:
                duration = self.date_end - self.date_start
                values["date_start"] = (
                    fields.Datetime.to_datetime(values["date_end"]) - duration
                )
        elif "date_start" in values and "date_end" not in values:
            if values["date_start"] and self.date_start and self.date_end:
                duration = self.date_end - self.date_start
                values["date_end"] = (
                    fields.Datetime.to_datetime(values["date_start"]) + duration
                )
                if "date_deadline" not in values:
                    values["date_deadline"] = values["date_end"].date()
        elif (
            "date_start" in values
            and "date_end" not in values
            and "date_deadline" not in values
        ):
            if values["date_start"] and self.date_start and self.date_end:
                duration = self.date_end - self.date_start
                values["date_end"] = (
                    fields.Datetime.to_datetime(values["date_start"]) + duration
                )
                values["date_deadline"] = values["date_end"].date()
        elif (
            "date_start" not in values
            and "date_end" in values
            and "date_deadline" not in values
        ):
            if values["date_end"]:
                if self.date_start and self.date_end:
                    duration = self.date_end - self.date_start
                    values["date_start"] = (
                        fields.Datetime.to_datetime(values["date_end"]) - duration
                    )
                values["date_deadline"] = values["date_end"].date()
        elif (
            "date_start" not in values
            and "date_end" not in values
            and "date_deadline" in values
        ):
            if not values["date_deadline"]:
                if self.date_end:
                    values["date_deadline"] = self.date_end.date()
            else:
                if self.date_end:
                    values["date_end"] = fields.Datetime.to_datetime(
                        values["date_deadline"]
                    )
                    values["date_end"] += timedelta(
                        seconds=self.date_end.second,
                        minutes=self.date_end.minute,
                        hours=self.date_end.hour,
                    )
                    if self.date_start:
                        duration = self.date_end - self.date_start
                        values["date_start"] = (
                            fields.Datetime.to_datetime(values["date_end"]) - duration
                        )

    def write(self, values):
        self._check_consistency_update(values)
        result = super().write(values)
        return result
