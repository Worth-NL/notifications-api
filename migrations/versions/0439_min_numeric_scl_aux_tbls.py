"""

Revision ID: 0439_min_numeric_scl_aux_tbls
Revises: 0438_sh_swap_check_for_not_null

"""

from sqlalchemy import (
    Numeric,
    case,
    cast,
    column,
    func,
    table,
    update,
)
from alembic import op


revision = "0439_min_numeric_scl_aux_tbls"
down_revision = "0438_sh_swap_check_for_not_null"


def _get_cases(var, max_scale=7):
    # values used in types must be constants so we need
    # to do this slightly ridiculous case statement covering
    # each scale we expect to encounter
    return case(
        {i: cast(var, Numeric(1000, i)) for i in range(max_scale)},
        value=func.min_scale(var),
        else_=var,
    )


def upgrade():
    conn = op.get_bind()
    conn.execute(update(table("letter_rates", column("rate"))).values(rate=_get_cases(column("rate"))))
    conn.execute(update(table("rates", column("rate"))).values(rate=_get_cases(column("rate"))))


def downgrade():
    pass
