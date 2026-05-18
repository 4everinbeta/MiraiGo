"""Initial search run tables."""

from alembic import op
import sqlalchemy as sa


revision = "20260412_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "search_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("search_id", sa.String(length=64), nullable=False),
        sa.Column("query", sa.String(length=500), nullable=False),
        sa.Column("inventories", sa.JSON(), nullable=False),
        sa.Column("request_payload", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("search_id"),
    )
    op.create_index("ix_search_runs_search_id", "search_runs", ["search_id"])

    op.create_table(
        "provider_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("search_run_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("inventory_type", sa.String(length=32), nullable=False),
        sa.Column("configured", sa.Boolean(), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("cache_hit", sa.Boolean(), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["search_run_id"], ["search_runs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_provider_runs_search_run_id", "provider_runs", ["search_run_id"])


def downgrade() -> None:
    op.drop_index("ix_provider_runs_search_run_id", table_name="provider_runs")
    op.drop_table("provider_runs")
    op.drop_index("ix_search_runs_search_id", table_name="search_runs")
    op.drop_table("search_runs")
