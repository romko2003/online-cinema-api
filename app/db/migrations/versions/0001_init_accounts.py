import sqlalchemy as sa
from alembic import op

revision = "0001_init_accounts"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "name",
            sa.Enum("USER", "MODERATOR", "ADMIN", name="usergroupenum"),
            unique=True,
            nullable=False,
        ),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("user_groups.id"), nullable=False),
    )

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("first_name", sa.String(100)),
        sa.Column("last_name", sa.String(100)),
        sa.Column("avatar", sa.String(255)),
        sa.Column("gender", sa.Enum("MAN", "WOMAN", name="genderenum")),
        sa.Column("date_of_birth", sa.Date()),
        sa.Column("info", sa.Text()),
    )


def downgrade() -> None:
    op.drop_table("user_profiles")
    op.drop_table("users")
    op.drop_table("user_groups")
