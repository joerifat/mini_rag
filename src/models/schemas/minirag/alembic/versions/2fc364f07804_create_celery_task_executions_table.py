"""create celery task executions table

Revision ID: 2fc364f07804
Revises: 3a2f1ed49b61
Create Date: 2026-08-31 11:17:49.493433
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2fc364f07804"
down_revision: Union[str, None] = "3a2f1ed49b61"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "Celery_task_execution",
        sa.Column("execution_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_name", sa.String(), nullable=False),
        sa.Column("task_args_hash", sa.String(length=64), nullable=False),
        sa.Column("celery_task_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("execution_id"),
    )

    op.create_index(
        "ixz_celery_task_id",
        "Celery_task_execution",
        ["celery_task_id"],
        unique=False,
    )

    op.create_index(
        "ixz_task_execution_created_at",
        "Celery_task_execution",
        ["created_at"],
        unique=False,
    )

    op.create_index(
        "ixz_task_execution_status",
        "Celery_task_execution",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ixz_task_name_args_celery_hash",
        "Celery_task_execution",
        ["task_name", "task_args_hash", "celery_task_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ixz_task_name_args_celery_hash",
        table_name="Celery_task_execution",
    )

    op.drop_index(
        "ixz_task_execution_status",
        table_name="Celery_task_execution",
    )

    op.drop_index(
        "ixz_task_execution_created_at",
        table_name="Celery_task_execution",
    )

    op.drop_index(
        "ixz_celery_task_id",
        table_name="Celery_task_execution",
    )

    op.drop_table("Celery_task_execution")