from alembic import op
import sqlalchemy as sa

revision = "0008_payments_schema"
down_revision = "0007_orders_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("successful", "canceled", "refunded", name="paymentstatusenum"),
            nullable=False,
            server_default="successful",
        ),
        sa.Column("amount", sa.DECIMAL(10, 2), nullable=False),
        sa.Column("external_payment_id", sa.String(length=255)),
    )
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_order_id", "payments", ["order_id"])
    op.create_index("ix_payments_status", "payments", ["status"])

    op.create_table(
        "payment_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("payment_id", sa.Integer(), sa.ForeignKey("payments.id"), nullable=False),
        sa.Column("order_item_id", sa.Integer(), sa.ForeignKey("order_items.id"), nullable=False),
        sa.Column("price_at_payment", sa.DECIMAL(10, 2), nullable=False),
    )
    op.create_index("ix_payment_items_payment_id", "payment_items", ["payment_id"])
    op.create_index("ix_payment_items_order_item_id", "payment_items", ["order_item_id"])


def downgrade() -> None:
    op.drop_index("ix_payment_items_order_item_id", table_name="payment_items")
    op.drop_index("ix_payment_items_payment_id", table_name="payment_items")
    op.drop_table("payment_items")

    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_order_id", table_name="payments")
    op.drop_index("ix_payments_user_id", table_name="payments")
    op.drop_table("payments")
