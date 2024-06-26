"""Add on delete cascade

Revision ID: 73ca65768b17
Revises: eccafef95a24
Create Date: 2024-04-21 16:59:01.202520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73ca65768b17'
down_revision: Union[str, None] = 'eccafef95a24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('messages_sender_id_fkey', 'messages', type_='foreignkey')
    op.drop_constraint('messages_conversation_id_fkey', 'messages', type_='foreignkey')
    op.create_foreign_key(None, 'messages', 'participants', ['sender_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'messages', 'conversations', ['conversation_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.create_foreign_key('messages_conversation_id_fkey', 'messages', 'conversations', ['conversation_id'], ['id'])
    op.create_foreign_key('messages_sender_id_fkey', 'messages', 'participants', ['sender_id'], ['id'])
    # ### end Alembic commands ###
