from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None


def upgrade():
    op.create_table(
        "tasks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_key", sa.String(128), nullable=False),
        sa.Column("input", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("role", sa.String(32)),
        sa.Column("result", sa.Text()),
        sa.Column("score", sa.Float()),
        sa.Column("critique", sa.Text()),
        sa.Column("reusable", sa.Boolean(), nullable=False),
        sa.Column("steps", sa.JSON()),
        sa.Column("retries", sa.Integer(), nullable=False),
        sa.Column("failure_reason", sa.Text()),
        sa.Column("idempotency_key", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        sa.Column("lease_until", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_tasks_status_created_at", "tasks", ["status", "created_at"])
    op.create_index("ix_tasks_owner_key", "tasks", ["owner_key"])
    op.create_table(
        "traces",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("task_id", sa.String(36), nullable=False),
        sa.Column("owner_key", sa.String(128), nullable=False),
        sa.Column("role", sa.String(32)),
        sa.Column("call_type", sa.String(32), nullable=False),
        sa.Column("message", sa.Text()),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("tokens_in", sa.Integer(), nullable=False),
        sa.Column("tokens_out", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_traces_task_id", "traces", ["task_id"])


def downgrade():
    op.drop_table("traces")
    op.drop_table("tasks")
