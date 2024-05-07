"""

Revision ID: 0443_add_spryng_provider
Revises: 0442_new_sms_allowance_n_rate
Create Date: 2024-05-07 13:05:00.000000

"""

import uuid

from alembic import op


revision = "0443_add_spryng_provider"
down_revision = "0442_new_sms_allowance_n_rate"


def upgrade():
    op.execute(
        "INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active) values ('{}', 'Spryng', 'spryng', 30, 'sms', true)".format(
            str(uuid.uuid4())
        )
    )

    op.execute(
        "UPDATE provider_rates set provider_id = (select id from provider_details where identifier = 'spryng') where provider = 'spryng'"
    )

    op.execute(
        "UPDATE provider_statistics set provider_id = (select id from provider_details where identifier = 'spryng') where provider = 'spryng'"
    )


def downgrade():
    op.execute("DELETE FROM provider_statistics WHERE provider = 'spryng'")
    op.execute("DELETE FROM provider_rates WHERE provider = 'spryng'")
    op.execute("DELETE FROM provider_details WHERE identifier = 'spryng'")
