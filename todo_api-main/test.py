from schemas import UserSignup, PaymentRequest
from datetime import datetime, timedelta

# test UserSignup
def test_user_signup():
    user_data = {
        "username": "testuser",
        "password": "password123",
        "email": "test@example.com",
        "business_name": "Test Business"
    }
    user = UserSignup(**user_data)
    print(user.json())

# test PaymentRequest
def test_payment_request():
    payment_data = {
        "card_number": "1234567812345678",
        "expiry_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "cvv": 123,
        "amount": 100.0,
        "user_id": 1
    }
    payment_request = PaymentRequest(**payment_data)
    print(payment_request.json())

if __name__ == "__main__":
    test_user_signup()
    test_payment_request()
