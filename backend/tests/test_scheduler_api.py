import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.schedule import GenerateRequest

@pytest.mark.asyncio
async def test_exclude_professors_in_generate_request() -> None:
    req = GenerateRequest(
        subject_claves=["MAT-101"],
        exclude_professors=["Prof A", "Prof B"]
    )
    assert req.exclude_professors == ["Prof A", "Prof B"]

@pytest.mark.asyncio
async def test_get_professors_endpoint(
    async_client: AsyncClient,
    auth_headers: dict[str, str]
) -> None:
    # Requires /api/v1/schedules/professors to return list of distinct professors
    response = await async_client.get("/api/v1/schedules/professors", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
