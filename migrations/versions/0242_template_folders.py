"""

Revision ID: 0242_template_folders
Revises: 0241_another_letter_org
Create Date: 2018-10-26 16:00:40.173840

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0242_template_folders"
down_revision = "0241_another_letter_org"


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "template_folder",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["template_folder.id"],
        ),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["services.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "template_folder_map",
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_folder_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["template_folder_id"],
            ["template_folder.id"],
        ),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["templates.id"],
        ),
        sa.PrimaryKeyConstraint("template_id"),
    )


def downgrade():
    op.drop_table("template_folder_map")
    op.drop_table("template_folder")
    # ### end Alembic commands ###
