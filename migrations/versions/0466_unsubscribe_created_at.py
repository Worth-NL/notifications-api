"""
Create Date: 2024-07-02 08:50:23.266628
"""

from alembic import op
from sqlalchemy import Column, DateTime


revision = "0466_unsubscribe_created_at"
down_revision =  "0465_user_research_email"


def upgrade():
    op.add_column("unsubscribe_request_report", Column("created_at", DateTime(), nullable=True))


def downgrade():
    op.drop_column("unsubscribe_request_report", "created_at")
