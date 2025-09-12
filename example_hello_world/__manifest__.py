{
    "name": "Example Hello World",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "Example module demonstrating basic Odoo structure",
    "description": """
Example Hello World Module
===========================

This is an example module that demonstrates:

* Basic Odoo module structure
* Model creation with fields
* Views (form, tree, action, menu)
* Basic data records
* Following OCA coding guidelines

This module is meant as a template and learning resource.
It can be safely removed from production environments.
    """,
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        "views/hello_world_views.xml",
        "data/hello_world_data.xml",
    ],
    "demo": [],
    "installable": False,  # Set to False to prevent accidental installation
    "application": False,
    "auto_install": False,
}