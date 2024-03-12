"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import advanced_alchemy
from advanced_alchemy.types import GUID, ORA_JSONB, DateTimeUTC
from sqlalchemy import Text
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    with op.get_context().autocommit_block():
        schema_upgrades()


def downgrade():
    with op.get_context().autocommit_block():
        schema_downgrades()


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}


def schema_upgrades():
    """schema upgrade migrations go here."""
    ${upgrades if upgrades else "pass"}


def schema_downgrades():
    """schema downgrade migrations go here."""
    ${downgrades if downgrades else "pass"}