from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_movies_schema"
down_revision = "0004_password_reset_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "genres",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), unique=True, nullable=False),
    )

    op.create_table(
        "stars",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), unique=True, nullable=False),
    )

    op.create_table(
        "directors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), unique=True, nullable=False),
    )

    op.create_table(
        "certifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), unique=True, nullable=False),
    )

    op.create_table(
        "movies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("time", sa.Integer(), nullable=False),
        sa.Column("imdb", sa.Float(), nullable=False),
        sa.Column("votes", sa.Integer(), nullable=False),
        sa.Column("meta_score", sa.Float()),
        sa.Column("gross", sa.Float()),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price", sa.DECIMAL(10, 2), nullable=False, server_default="0.00"),
        sa.Column("certification_id", sa.Integer(), sa.ForeignKey("certifications.id"), nullable=False),
        sa.UniqueConstraint("name", "year", "time", name="uq_movie_name_year_time"),
    )

    op.create_table(
        "movie_genres",
        sa.Column("movie_id", sa.Integer(), sa.ForeignKey("movies.id"), primary_key=True),
        sa.Column("genre_id", sa.Integer(), sa.ForeignKey("genres.id"), primary_key=True),
    )

    op.create_table(
        "movie_directors",
        sa.Column("movie_id", sa.Integer(), sa.ForeignKey("movies.id"), primary_key=True),
        sa.Column("director_id", sa.Integer(), sa.ForeignKey("directors.id"), primary_key=True),
    )

    op.create_table(
        "movie_stars",
        sa.Column("movie_id", sa.Integer(), sa.ForeignKey("movies.id"), primary_key=True),
        sa.Column("star_id", sa.Integer(), sa.ForeignKey("stars.id"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("movie_stars")
    op.drop_table("movie_directors")
    op.drop_table("movie_genres")
    op.drop_table("movies")
    op.drop_table("certifications")
    op.drop_table("directors")
    op.drop_table("stars")
    op.drop_table("genres")
