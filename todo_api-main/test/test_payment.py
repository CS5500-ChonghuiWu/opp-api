from httpx import AsyncClient
import pytest
from main import app  # Import your FastAPI app
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
