""""added_autoincrements_to_ids"

Revision ID: d519e0d2e7d1
Revises: f08399183feb
Create Date: 2025-07-07 23:40:52.200065

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'd519e0d2e7d1'
down_revision: Union[str, None] = 'f08399183feb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('token_denylist', 'id',
               existing_type=mysql.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('token_denylist', 'exp',
               existing_type=mysql.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('token_denylist', 'exp',
               existing_type=sa.Integer(),
               type_=mysql.BIGINT(),
               existing_nullable=False)
    op.alter_column('token_denylist', 'id',
               existing_type=sa.Integer(),
               type_=mysql.BIGINT(),
               existing_nullable=False,
               autoincrement=True)
    # ### end Alembic commands ###
