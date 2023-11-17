from httpx import AsyncClient
import pytest
from main import app
from unittest.mock import patch
from datetime import datetime

@pytest.mark.asyncio
@patch('routers.payment.validate_card')
@patch('routers.payment.check_funds_and_fraud')
async def test_charge_payment(mock_check_funds, mock_validate):
    mock_validate.return_value = {"success": "true", "details": "Card is valid"}
    mock_check_funds.return_value = {"success": "true", "details": "Funds available"}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/payments/charge", json={
            "card_number": "1234567890123456",
            "expiry_date": datetime.now().isoformat(),
            "cvv": "123",
            "amount": 100.00,
            "user_id": "1"
        })

        if response.status_code != 200:
            print("Response:", response.json())

        assert response.status_code == 200
        response_data = response.json()
        assert 'transaction_id' in response_data
        assert 'user_id' in response_data
        assert 'amount' in response_data
        assert 'status' in response_data
        assert response_data['user_id'] == "1"
        assert response_data['amount'] == 100.00
        assert response_data['status'] == 'processed'


@pytest.mark.asyncio
async def test_get_balance():
    test_user_id = 1

    # Mocking database interaction
    with patch('sqlalchemy.orm.Session.query') as mock_query:
        mock_query.return_value.filter.return_value.all.return_value = [
            # Mocked transactions
            MockTransaction(amount=100.00), 
            MockTransaction(amount=200.00)
        ]

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/payments/balance?user_id={test_user_id}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['total_balance'] == 300.00

@pytest.mark.asyncio
async def test_get_transactions():
    test_user_id = "1"

    with patch('sqlalchemy.orm.Session.query') as mock_query:
        mock_query.return_value.filter.return_value.all.return_value = [
            MockTransaction(id=1, amount=100.00, user_id=test_user_id, status='processed'),
            MockTransaction(id=2, amount=200.00, user_id=test_user_id, status='processed')
        ]

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/payments/transactions?user_id={test_user_id}")

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2
        assert response_data[0]['transaction_id'] == 1
        assert response_data[1]['transaction_id'] == 2

# Helper class for mocking transactions
class MockTransaction:
    def __init__(self, id=None, user_id=None, amount=None, status=None):
        self.id = id
        self.user_id = user_id
        self.amount = amount
        self.status = status