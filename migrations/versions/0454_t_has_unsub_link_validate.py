"""
Create Date: 2024-06-01 16:35:30.12345
"""

from alembic import op


revision = "0454_t_has_unsub_link_validate"
down_revision =  "0453_t_has_unsub_link_constraint"


def upgrade():
    # These only acquire a SHARE UPDATE EXCLUSIVE lock.
    op.execute("ALTER TABLE templates VALIDATE CONSTRAINT ck_templates_has_unsubscribe_link_not_null_check")


def downgrade():
    # non-reversible
    pass
