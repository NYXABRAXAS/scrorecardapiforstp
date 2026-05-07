"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rule_master",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("product_type", sa.String(length=50), nullable=False),
        sa.Column("dealer_id", sa.String(length=100), nullable=True),
        sa.Column("rule_code", sa.String(length=100), nullable=False),
        sa.Column("rule_name", sa.String(length=255), nullable=False),
        sa.Column("rule_type", sa.String(length=50), nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=False),
        sa.Column("operator", sa.String(length=20), nullable=False),
        sa.Column("field_value", sa.String(length=255), nullable=False),
        sa.Column("score_value", sa.Numeric(10, 2), nullable=True),
        sa.Column("score_component", sa.String(length=50), nullable=True),
        sa.Column("decision_action", sa.String(length=50), nullable=True),
        sa.Column("reason_code", sa.String(length=100), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rule_code", "version", "tenant_id", "product_type", "dealer_id"),
    )
    op.create_index(op.f("ix_rule_master_dealer_id"), "rule_master", ["dealer_id"], unique=False)
    op.create_index(op.f("ix_rule_master_id"), "rule_master", ["id"], unique=False)
    op.create_index(op.f("ix_rule_master_is_active"), "rule_master", ["is_active"], unique=False)
    op.create_index(op.f("ix_rule_master_product_type"), "rule_master", ["product_type"], unique=False)
    op.create_index(op.f("ix_rule_master_rule_code"), "rule_master", ["rule_code"], unique=False)
    op.create_index(op.f("ix_rule_master_rule_type"), "rule_master", ["rule_type"], unique=False)
    op.create_index(op.f("ix_rule_master_tenant_id"), "rule_master", ["tenant_id"], unique=False)

    op.create_table(
        "scorecard_result",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("product_type", sa.String(length=50), nullable=False),
        sa.Column("lead_id", sa.String(length=100), nullable=False),
        sa.Column("final_score", sa.Numeric(10, 2), nullable=False),
        sa.Column("decision", sa.String(length=50), nullable=False),
        sa.Column("underwriting_required", sa.Boolean(), nullable=False),
        sa.Column("reject_flag", sa.Boolean(), nullable=False),
        sa.Column("journey_action", sa.String(length=50), nullable=False),
        sa.Column("bureau_risk", sa.String(length=50), nullable=False),
        sa.Column("score_breakup", sa.JSON(), nullable=False),
        sa.Column("triggered_rules", sa.JSON(), nullable=False),
        sa.Column("reason_codes", sa.JSON(), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scorecard_result_id"), "scorecard_result", ["id"], unique=False)
    op.create_index(op.f("ix_scorecard_result_lead_id"), "scorecard_result", ["lead_id"], unique=False)
    op.create_index(
        op.f("ix_scorecard_result_product_type"), "scorecard_result", ["product_type"], unique=False
    )
    op.create_index(
        op.f("ix_scorecard_result_request_hash"), "scorecard_result", ["request_hash"], unique=False
    )
    op.create_index(op.f("ix_scorecard_result_tenant_id"), "scorecard_result", ["tenant_id"], unique=False)

    op.create_table(
        "rule_audit_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("actor", sa.String(length=100), nullable=True),
        sa.Column("before", sa.JSON(), nullable=True),
        sa.Column("after", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rule_audit_log_id"), "rule_audit_log", ["id"], unique=False)
    op.create_index(op.f("ix_rule_audit_log_rule_id"), "rule_audit_log", ["rule_id"], unique=False)

    op.create_table(
        "scorecard_execution_audit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lead_id", sa.String(length=100), nullable=False),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("product_type", sa.String(length=50), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("matched_rules", sa.JSON(), nullable=False),
        sa.Column("skipped_rules", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_scorecard_execution_audit_id"), "scorecard_execution_audit", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_scorecard_execution_audit_lead_id"),
        "scorecard_execution_audit",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_scorecard_execution_audit_product_type"),
        "scorecard_execution_audit",
        ["product_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_scorecard_execution_audit_request_hash"),
        "scorecard_execution_audit",
        ["request_hash"],
        unique=False,
    )
    op.create_index(
        op.f("ix_scorecard_execution_audit_tenant_id"),
        "scorecard_execution_audit",
        ["tenant_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("scorecard_execution_audit")
    op.drop_table("rule_audit_log")
    op.drop_table("scorecard_result")
    op.drop_table("rule_master")

