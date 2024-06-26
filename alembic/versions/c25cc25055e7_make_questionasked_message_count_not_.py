"""Make QuestionAsked.message_count not nullable

Revision ID: c25cc25055e7
Revises: 68e73e211893
Create Date: 2024-04-06 19:33:22.608328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c25cc25055e7'
down_revision: Union[str, None] = '68e73e211893'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('questions_asked', 'messages_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('questions_asked', 'messages_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
