"""
Create Date: 2024-10-29 13:00:22.856730
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# was meant to be 0468_add_notifications_trgm_normto_cref_idxs but accidentally committed as this
revision = "0472_"
down_revision =  "0471_svc_join_approved_tmp"


def upgrade():
    with op.get_context().autocommit_block():
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        op.create_index(
            "ix_notifications_client_reference_trgm",
            "notifications",
            ["client_reference"],
            unique=False,
            postgresql_using="gin",
            postgresql_ops={"client_reference": "gin_trgm_ops"},
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_notifications_normalised_to_trgm",
            "notifications",
            ["normalised_to"],
            unique=False,
            postgresql_using="gin",
            postgresql_ops={"normalised_to": "gin_trgm_ops"},
            postgresql_concurrently=True,
        )


def downgrade():
    op.drop_index(
        "ix_notifications_normalised_to_trgm",
        table_name="notifications",
        postgresql_using="gin",
        postgresql_ops={"normalised_to": "gin_trgm_ops"},
        postgresql_concurrently=True,
    )
    op.drop_index(
        "ix_notifications_client_reference_trgm",
        table_name="notifications",
        postgresql_using="gin",
        postgresql_ops={"client_reference": "gin_trgm_ops"},
        postgresql_concurrently=True,
    )
    # not reversing CREATE EXTENSION as it may have been present already
