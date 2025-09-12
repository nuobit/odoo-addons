from odoo import fields, models


class HelloWorld(models.Model):
    """Example model demonstrating basic Odoo model structure."""

    _name = "hello.world"
    _description = "Hello World Example"
    _order = "name"

    # Basic fields demonstrating different types
    name = fields.Char(
        string="Greeting Name",
        required=True,
        help="The name to greet",
    )
    message = fields.Text(
        string="Message",
        default="Hello World!",
        help="The greeting message",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Set to False to archive this record",
    )
    priority = fields.Selection(
        selection=[
            ("low", "Low"),
            ("normal", "Normal"),
            ("high", "High"),
        ],
        string="Priority",
        default="normal",
        help="Priority level of this greeting",
    )
    greeting_count = fields.Integer(
        string="Greeting Count",
        default=0,
        help="Number of times this greeting has been used",
    )

    # Computed field example
    display_name_custom = fields.Char(
        string="Custom Display Name",
        compute="_compute_display_name_custom",
        help="Custom computed display name",
    )

    def _compute_display_name_custom(self):
        """Compute custom display name."""
        for record in self:
            record.display_name_custom = f"[{record.priority.upper()}] {record.name}"

    def action_increment_count(self):
        """Action method to increment greeting count."""
        for record in self:
            record.greeting_count += 1

    def action_reset_count(self):
        """Action method to reset greeting count."""
        for record in self:
            record.greeting_count = 0