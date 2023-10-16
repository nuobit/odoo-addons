# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo.addons.component.core import AbstractComponent
from odoo.addons.queue_job.exception import RetryableJobError

from ..common.database import session_pg_advisory_unlock, session_pg_try_advisory_lock


class BaseConnectorComponent(AbstractComponent):
    _inherit = "base.connector"

    def session_advisory_lock_or_retry(self, lock, retry_seconds=1):
        """Acquire a Postgres session advisory lock or retry job

        When the lock cannot be acquired, it raises a
        :exc:`odoo.addons.queue_job.exception.RetryableJobError` so the job
        is retried after n ``retry_seconds``.

        Usage example:

        .. code-block:: python

            lock_name = 'import_record({}, {}, {}, {})'.format(
                self.backend_record._name,
                self.backend_record.id,
                self.model._name,
                self.external_id,
            )
            self.session_advisory_lock_or_retry(lock_name, retry_seconds=2)

        See :func:`odoo.addons.connector.connector.session_pg_try_advisory_lock` for
        details.

        :param lock: The lock name. Can be anything convertible to a
           string.  It needs to represent what should not be synchronized
           concurrently, usually the string will contain at least: the
           action, the backend name, the backend id, the model name, the
           external id
        :param retry_seconds: number of seconds after which a job should
           be retried when the lock cannot be acquired.
        """
        if not session_pg_try_advisory_lock(self.env, lock):
            raise RetryableJobError(
                "Could not acquire advisory lock",
                seconds=retry_seconds,
                ignore_retry=True,
            )

    def session_pg_advisory_unlock(
        self,
        lock,
    ):
        return session_pg_advisory_unlock(self.env, lock)
