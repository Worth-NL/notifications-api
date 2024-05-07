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
        f"INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active, version) values ('{provider_id}', '{identifier.capitalize()}', '{identifier}', 30, 'sms', true, 1)"
    )

    op.execute(
        f"INSERT INTO provider_rates (id, valid_from, rate, provider_id) VALUES ('{uuid.uuid4()}', '{datetime.utcnow()}', 1.0, '{provider_id}')"
    )


def downgrade():
    op.execute(f"DELETE FROM provider_rates WHERE provider_id = '{provider_id}'")
    op.execute(f"DELETE FROM provider_details WHERE id = '{provider_id}'")
