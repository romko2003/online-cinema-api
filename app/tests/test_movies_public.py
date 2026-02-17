from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_movies_list_empty_ok(client):
    r = await client.get("/api/v1/movies")
    assert r.status_code == 200, r.text

    data = r.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_movie_detail_not_found(client):
    # random UUID should not exist
    r = await client.get("/api/v1/movies/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404, r.text
    assert r.json()["detail"] == "Movie not found"
