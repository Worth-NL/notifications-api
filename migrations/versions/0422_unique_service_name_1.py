"""

Revision ID: 0422_unique_service_name_1
Revises: 0421_add_notifynl_templates
Create Date: 2023-08-24 16:26:03.488048

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0422_unique_service_name_1"
down_revision = "0421_add_notifynl_templates"


def upgrade():
    op.add_column("services", sa.Column("normalised_service_name", sa.String(), nullable=True, unique=True))
    op.add_column("services_history", sa.Column("normalised_service_name", sa.String(), nullable=True))


def downgrade():
    op.drop_column("services", "normalised_service_name")
    op.drop_column("services_history", "normalised_service_name")
