# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Job Queue User",
    "summary": "Read-only access to the job queue",
    "version": "14.0.1.0.0",
    "category": "Generic Modules",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/nuobit/odoo-addons",
    "license": "LGPL-3",
    "depends": [
        "queue_job",
    ],
    "data": [
        "security/queue_job_user_security.xml",
        "security/ir.model.access.csv",
        "views/queue_job_menus.xml",
    ],
}
