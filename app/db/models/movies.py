from __future__ import annotations

import uuid as uuid_lib
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import (
    DECIMAL,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# IMPORTANT:
# Table(...) expects sqlalchemy.Column, NOT mapped_column.
movie_genres = Table(
    "movie_genres",
    Base.metadata,
    sa.Column("movie_id", sa.ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("genre_id", sa.ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)

movie_directors = Table(
    "movie_directors",
    Base.metadata,
    sa.Column("movie_id", sa.ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("director_id", sa.ForeignKey("directors.id", ondelete="CASCADE"), primary_key=True),
)

movie_stars = Table(
    "movie_stars",
    Base.metadata,
    sa.Column("movie_id", sa.ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("star_id", sa.ForeignKey("stars.id", ondelete="CASCADE"), primary_key=True),
)


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    movies: Mapped[list["Movie"]] = relationship(
        secondary=movie_genres,
        back_populates="genres",
    )


class Star(Base):
    __tablename__ = "stars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)

    movies: Mapped[list["Movie"]] = relationship(
        secondary=movie_stars,
        back_populates="stars",
    )


class Director(Base):
    __tablename__ = "directors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)

    movies: Mapped[list["Movie"]] = relationship(
        secondary=movie_directors,
        back_populates="directors",
    )


class Certification(Base):
    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    movies: Mapped[list["Movie"]] = relationship(back_populates="certification")


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (
        UniqueConstraint("name", "year", "time", name="uq_movie_name_year_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    uuid: Mapped[uuid_lib.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid_lib.uuid4,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    time: Mapped[int] = mapped_column(Integer, nullable=False)  # minutes

    imdb: Mapped[float] = mapped_column(Float, nullable=False)
    votes: Mapped[int] = mapped_column(Integer, nullable=False)

    meta_score: Mapped[float | None] = mapped_column(Float)
    gross: Mapped[float | None] = mapped_column(Float)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    price: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    certification_id: Mapped[int] = mapped_column(
        ForeignKey("certifications.id", ondelete="RESTRICT"),
        nullable=False,
    )

    certification: Mapped["Certification"] = relationship(back_populates="movies")

    genres: Mapped[list["Genre"]] = relationship(
        secondary=movie_genres,
        back_populates="movies",
    )
    directors: Mapped[list["Director"]] = relationship(
        secondary=movie_directors,
        back_populates="movies",
    )
    stars: Mapped[list["Star"]] = relationship(
        secondary=movie_stars,
        back_populates="movies",
    )
