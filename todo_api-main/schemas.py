from pydantic import BaseModel, EmailStr, constr, validator
from datetime import datetime

class UserSignup(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)
    email: EmailStr
    business_name: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    business_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PaymentRequest(BaseModel):
    card_number: str
    expiry_date: datetime
    cvv: str
    amount: float
    user_id: str

    @validator('card_number')
    def validate_card_number(cls, value):
        # Add custom validation for card number if needed
        assert len(value) in [15, 16], 'Card number must be 15 or 16 digits long'
        return value

    @validator('expiry_date', pre=True)
    def validate_expiry_date(cls, value):
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                raise ValueError(f"Cannot parse {value} as datetime")
        return value

    @validator('amount')
    def validate_amount(cls, value):
        # Ensure the amount is positive
        assert value > 0, 'Amount must be positive'
        return value

class TransactionResponse(BaseModel):
    transaction_id: int
    user_id: str
    amount: float
    status: str

class BalanceResponse(BaseModel):
    total_balance: float
