from unittest.mock import AsyncMock, patch
import pytest
from routers.helpers import validate_card, check_funds_and_fraud

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_validate_card(mock_post):
    mock_post.return_value = AsyncMock(status_code=200, json=lambda: {"success": "true", "details": "Card is valid"})
    response = await validate_card("1234567890123456")
    assert response == {"success": "true", "details": "Card is valid"}

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_check_funds_and_fraud(mock_post):
    mock_post.return_value = AsyncMock(status_code=200, json=lambda: {"success": "true", "details": "Funds available"})
    response = await check_funds_and_fraud("1234567890123456", 100.00)
    assert response == {"success": "true", "details": "Funds available"}
