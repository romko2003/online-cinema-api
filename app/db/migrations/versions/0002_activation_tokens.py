import sqlalchemy as sa
from alembic import op

revision = "0002_activation_tokens"
down_revision = "0001_init_accounts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "activation_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("token", sa.String(255), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("activation_tokens")
