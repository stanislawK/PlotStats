"""add favorite search

Revision ID: 9bc5ae3dee69
Revises: e8a730aa8d16
Create Date: 2024-01-26 19:57:51.615475

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "9bc5ae3dee69"
down_revision = "e8a730aa8d16"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "search", "distance_radius", existing_type=sa.INTEGER(), nullable=True
    )
    op.add_column("user", sa.Column("favorite_search_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "user", "search", ["favorite_search_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "user", type_="foreignkey")  # type: ignore
    op.drop_column("user", "favorite_search_id")
    op.alter_column(
        "search", "distance_radius", existing_type=sa.INTEGER(), nullable=False
    )
    # ### end Alembic commands ###
