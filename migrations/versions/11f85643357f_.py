"""empty message

Revision ID: 11f85643357f
Revises: 725061a99504
Create Date: 2023-10-29 16:45:52.836965

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "11f85643357f"
down_revision = "725061a99504"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("todo", schema=None) as batch_op:
        batch_op.add_column(sa.Column("completed", sa.Boolean(), nullable=True))
        
    with op.batch_alter_table("todo", schema=None) as batch_op:
        batch_op.execute("UPDATE todo SET completed = False WHERE completed IS NULL;")
        batch_op.alter_column("completed", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("todo", schema=None) as batch_op:
        batch_op.drop_column("completed")

    # ### end Alembic commands ###
