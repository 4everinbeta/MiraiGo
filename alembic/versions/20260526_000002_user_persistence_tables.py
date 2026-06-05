"""User persistence tables."""

from alembic import op
import sqlalchemy as sa


revision = "20260526_000002"
down_revision = "20260412_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user table
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_user_email", "user", ["email"])
    op.create_index("ix_user_full_name", "user", ["full_name"])

    # Create search_history table
    op.create_table(
        "search_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("search_id", sa.String(length=64), nullable=False),
        sa.Column("query", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_search_history_search_id", "search_history", ["search_id"])

    # Create user_preference table
    op.create_table(
        "user_preference",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("default_origin", sa.String(length=100), nullable=True),
        sa.Column("preferred_inventory", sa.JSON(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="USD"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_preference")
    op.drop_index("ix_search_history_search_id", table_name="search_history")
    op.drop_table("search_history")
    op.drop_index("ix_user_full_name", table_name="user")
    op.drop_index("ix_user_email", table_name="user")
    op.drop_table("user")
