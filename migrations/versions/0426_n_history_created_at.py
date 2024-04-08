"""

Revision ID: 0426_n_history_created_at
Revises: 0425_notify_user_name.py
Create Date: 2023-09-17 15:17:58.545277

"""
from alembic import op
import sqlalchemy as sa


revision = "0426_n_history_created_at"
down_revision = "0425_notify_user_name.py"


def upgrade():
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_notification_history_created_at",
            "notification_history",
            ["created_at"],
            unique=False,
            postgresql_concurrently=True,
        )


def downgrade():
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_notification_history_created_at", table_name="notification_history", postgresql_concurrently=True
        )
