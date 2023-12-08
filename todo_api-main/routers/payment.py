from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from routers.helpers import validate_card, check_funds_and_fraud
from db.database import get_db
from schemas import PaymentRequest, TransactionResponse, BalanceResponse
from models.models import Transaction as TransactionModel, Users as UserModel
from typing import List
from datetime import datetime

router = APIRouter()

@router.post("/payments/charge", response_model=TransactionResponse)
async def charge_payment(payment_request: PaymentRequest, db: Session = Depends(get_db)):
    # Validate the card
    card_validation_result = await validate_card(payment_request.card_number)

    if card_validation_result.get("success") == "false":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card validation failed")

    # Check funds and fraud
    funds_and_fraud_result = await check_funds_and_fraud(payment_request.card_number, payment_request.amount)

    if funds_and_fraud_result.get("success") == "false":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Funds and fraud check failed")

    if payment_request.expiry_date < datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card expired")
    # Payment process is successful
    payment_success = True

    if not payment_success:
        # failed payment respond with error
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Payment failed")

    # create transaction record
    new_transaction = TransactionModel(
        user_id=payment_request.user_id,
        amount=payment_request.amount,
        status="processed" if payment_success else "failed"
    )
    
    # add the transaction record to db
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    # return response
    return TransactionResponse(
        transaction_id=new_transaction.id,
        user_id=new_transaction.user_id,
        amount=new_transaction.amount,
        status=new_transaction.status
    )


@router.get("/payments/balance", response_model=BalanceResponse)
async def get_balance(user_id: str, db: Session = Depends(get_db)):
    # calculate and return current balance
    transactions = db.query(TransactionModel).filter(
        TransactionModel.user_id == user_id,
        TransactionModel.status == "processed"
    ).all()
    total_balance = sum(t.amount for t in transactions)
    return BalanceResponse(total_balance=total_balance)

@router.get("/payments/transactions", response_model=List[TransactionResponse])
async def get_transactions(user_id: str, db: Session = Depends(get_db)):
    # search and return all transactions of user
    transactions = db.query(TransactionModel).filter(
        TransactionModel.user_id == user_id
    ).all()
    return [TransactionResponse(
        transaction_id=t.id,
        user_id=t.user_id,
        amount=t.amount,
        status=t.status
    ) for t in transactions]
