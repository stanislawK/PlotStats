"""add ScanFailure model

Revision ID: 3d80c6723fbc
Revises: 9bc5ae3dee69
Create Date: 2024-03-31 17:06:32.539104

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "3d80c6723fbc"
down_revision = "9bc5ae3dee69"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "scanfailure",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("search_id", sa.Integer(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["search_id"],
            ["search.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_scanfailure_status_code"), "scanfailure", ["status_code"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_scanfailure_status_code"), table_name="scanfailure")
    op.drop_table("scanfailure")
    # ### end Alembic commands ###
