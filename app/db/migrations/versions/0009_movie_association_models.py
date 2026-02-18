"""movie association tables as declarative models

Revision ID: 20260217_0001
Revises: <PUT_PREVIOUS_REVISION_HERE>
Create Date: 2026-02-17
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# IMPORTANT: replace with your actual previous revision
revision = "20260217_0001"
down_revision = "<PUT_PREVIOUS_REVISION_HERE>"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names(schema="public")


def upgrade() -> None:
    # If these tables already exist (created earlier via inline Table),
    # we do not need to recreate them. This migration exists to formalize
    # them as "first-class" models in the codebase.
    if not _table_exists("movie_genres"):
        op.create_table(
            "movie_genres",
            sa.Column(
                "movie_id",
                sa.Integer(),
                sa.ForeignKey("movies.id", ondelete="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
            sa.Column(
                "genre_id",
                sa.Integer(),
                sa.ForeignKey("genres.id", ondelete="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
        )
        op.create_index("ix_movie_genres_movie_id", "movie_genres", ["movie_id"])
        op.create_index("ix_movie_genres_genre_id", "movie_genres", ["genre_id"])

    if not _table_exists("movie_directors"):
        op.create_table(
            "movie_directors",
            sa.Column(
                "movie_id",
                sa.Integer(),
                sa.ForeignKey("movies.id", ondelete="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
            sa.Column(
                "director_id",
                sa.Integer(),
                sa.ForeignKey("directors.id", ondelete="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
        )
        op.create_index("ix_movie_directors_movie_id", "movie_directors", ["movie_id"])
        op.create_index(
            "ix_movie_directors_director_id", "movie_directors", ["director_id"]
        )

    if not _table_exists("movie_stars"):
        op.create_table(
            "movie_stars",
            sa.Column(
                "movie_id",
                sa.Integer(),
                sa.ForeignKey("movies.id", ondelete="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
            sa.Column(
                "star_id",
                sa.Integer(),
                sa.ForeignKey("stars.id", ondelete="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
        )
        op.create_index("ix_movie_stars_movie_id", "movie_stars", ["movie_id"])
        op.create_index("ix_movie_stars_star_id", "movie_stars", ["star_id"])


def downgrade() -> None:
    # Only drop if exists (safe downgrade).
    if _table_exists("movie_stars"):
        op.drop_index("ix_movie_stars_star_id", table_name="movie_stars")
        op.drop_index("ix_movie_stars_movie_id", table_name="movie_stars")
        op.drop_table("movie_stars")

    if _table_exists("movie_directors"):
        op.drop_index("ix_movie_directors_director_id", table_name="movie_directors")
        op.drop_index("ix_movie_directors_movie_id", table_name="movie_directors")
        op.drop_table("movie_directors")

    if _table_exists("movie_genres"):
        op.drop_index("ix_movie_genres_genre_id", table_name="movie_genres")
        op.drop_index("ix_movie_genres_movie_id", table_name="movie_genres")
        op.drop_table("movie_genres")
