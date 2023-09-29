"""empty message

Revision ID: 0421_add_notifynl_templates
Revises: 0420_add_notifynl_templates
Create Date: 2023-09-29 14:17:01.963181

"""

from alembic import op
from flask import current_app

# revision identifiers, used by Alembic.
revision = "0421_add_notifynl_templates"
down_revision = "0420_add_notifynl_templates"


templates = [
    # Reply-to email address
    {
        "id": "2e542078-1b7e-4640-ab44-57e5db6b3bf3",
        "name": "Verify email reply-to address for a service on NotifyNL",
        "type": "email",
        "subject": "Your NotifyNL reply-to email address",
        "content": """Hi,\n\n
                    This address has been provided as a reply-to email address for a NotifyNL account.\n
                    Any replies from users to emails they receive through NotifyNL will come back to this email address.\n\n
                    This is just a quick check to make sure the address is valid.\n\n
                    No need to reply.
                    """,
    },
    # Service is live
    {
        "id": "ec92ba79-222b-46f1-944a-79b3c072234d",
        "name": "Automated \"You''re now live\" message on NotifyNL",
        "type": "email",
        "subject": "((service name)) is now live on NotifyNL",
        "content": """Hi ((name)),\n\n((service name)) is now live on NotifyNL.""",
    },
]


def upgrade():
    op.get_bind()
    insert = """INSERT INTO {} (id, name, template_type, created_at, content, archived, service_id,
                                subject, created_by_id, version, process_type, hidden)
                VALUES ('{}', '{}', '{}', current_timestamp, '{}', False, '{}', '{}', '{}', 1, 'normal', False)
            """

    template_redacted_insert = """INSERT INTO template_redacted (template_id, redact_personalisation,
                                                                updated_at, updated_by_id)
                                    VALUES ('{}', False, current_timestamp, '{}')
                                """

    for template in templates:
        for table_name in ["templates", "templates_history"]:
            op.execute(
                insert.format(
                    table_name,
                    template["id"],
                    template["name"],
                    template["type"],
                    template["content"],
                    current_app.config["NOTIFY_SERVICE_ID"],
                    template["subject"],
                    current_app.config["NOTIFY_USER_ID"],
                )
            )

        op.execute(
            template_redacted_insert.format(
                template["id"],
                current_app.config["NOTIFY_USER_ID"],
            )
        )


def downgrade():
    op.get_bind()

    for template in templates:
        op.execute("DELETE FROM notifications WHERE template_id = '{}'".format(template["id"]))
        op.execute("DELETE FROM notification_history WHERE template_id = '{}'".format(template["id"]))
        op.execute("DELETE FROM template_redacted WHERE template_id = '{}'".format(template["id"]))
        op.execute("DELETE FROM templates WHERE id = '{}'".format(template["id"]))
        op.execute("DELETE FROM templates_history WHERE id = '{}'".format(template["id"]))
