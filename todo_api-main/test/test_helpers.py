from starlette.exceptions import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock, Mock
import pytest
from datetime import timedelta
from models.models import Users
from jose import jwt
from routers.helpers import validate_card, check_funds_and_fraud, check_user_authentication
from routers.auth import create_user, login_for_access_token, authenticate_user, create_access_token, get_current_user, Users, CreateUserRequest

# Mock class for database session
class MockSession:
    def add(self, _):
        pass

    def commit(self):
        pass

    def refresh(self, _):
        pass

    def query(self, _):
        return self

    def filter(self, _):
        return self

    def first(self):
        return None

@pytest.mark.asyncio
@patch('routers.auth.bcrypt_context')
async def test_create_user(mock_bcrypt_context):
    mock_bcrypt_context.hash = MagicMock(return_value="hashed_testpass")
    mock_session = MockSession()

    # Create a CreateUserRequest object with the required attributes
    create_user_request = CreateUserRequest(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        surname="User",
        password="testpass",
        role="user"
    )

    user = await create_user(mock_session, create_user_request)

    assert user["username"] == "testuser"
    assert user["user_id"] is not None

@pytest.mark.asyncio
@patch('routers.auth.bcrypt_context')
async def test_authenticate_user(mock_bcrypt_context):
    mock_bcrypt_context.verify = MagicMock(return_value=True)
    user = Users(username="testuser", hashed_password="hashed_testpass")

    mock_session = MockSession()
    mock_session.first = MagicMock(return_value=user)

    authenticated_user = authenticate_user("testuser", "testpass", mock_session)
    assert authenticated_user.username == "testuser"

SECRET_KEY_TEST = 'test_secret_key'
ALGORITHM_TEST = 'HS256'

def test_create_access_token(monkeypatch):
    # Mock jwt.encode to return a fixed token
    def mock_jwt_encode(claims, secret_key, algorithm):
        return 'mocked_token'

    # Use monkeypatch to replace jwt.encode with the mock function
    monkeypatch.setattr(jwt, 'encode', mock_jwt_encode)

    # Call the create_access_token function with the custom secret key and algorithm
    token = create_access_token("testuser", 1, "user", timedelta(minutes=30))

    # Assert that the token matches the expected value
    assert token == 'mocked_token'

@pytest.mark.asyncio
@patch('routers.auth.jwt')
async def test_get_current_user(mock_jwt):
    mock_jwt.decode = MagicMock(return_value={"sub": "testuser", "id": 1, "role": "user"})
    user = await get_current_user("fake-jwt-token")
    assert user["username"] == "testuser"
    assert user["id"] == 1
    assert user["user_role"] == "user"


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

def test_check_user_authentication():
    user = None
    with pytest.raises(HTTPException) as exc_info:
        check_user_authentication(user)
    exception = exc_info.value
    assert exception.status_code == 401
    assert exception.detail == 'Authentication Failed'