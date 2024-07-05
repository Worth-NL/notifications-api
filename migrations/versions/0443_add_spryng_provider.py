"""

Revision ID: 0443_add_spryng_provider
Revises: 0442_new_sms_allowance_n_rate
Create Date: 2024-05-07 13:05:00.000000

"""

import uuid
from datetime import datetime

from alembic import op


revision = "0443_add_spryng_provider"
down_revision = "0442_new_sms_allowance_n_rate"


identifier = "spryng"
provider_id = str(uuid.uuid4())


def upgrade():
    op.execute(
        f"INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active, version, supports_international) values ('{provider_id}', '{identifier.capitalize()}', '{identifier}', 30, 'sms', true, 1, true)"
    )


def downgrade():
    op.execute(f"DELETE FROM provider_details WHERE identifier = '{identifier}'")
