from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from schemas import PaymentRequest, TransactionResponse, BalanceResponse
from models.models import Transaction as TransactionModel, Users as UserModel
from typing import List

router = APIRouter()

def process_payment(card_number: str, expiry_date: str, cvv: int, amount: float) -> bool:
    # Payment gateway communication logic, fake for now
    # check card info，execute payment，return result
    return True

@router.post("/payments/charge", response_model=TransactionResponse)
async def charge_payment(payment_request: PaymentRequest, db: Session = Depends(get_db)):
    # suppose process_payment is true
    payment_success = process_payment(
        card_number=payment_request.card_number,
        expiry_date=payment_request.expiry_date,
        cvv=payment_request.cvv,
        amount=payment_request.amount
    )

    if not payment_success:
        # failed payment respond with error
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Payment failed")

    # create transaction record
    new_transaction = TransactionModel(
        card_number=payment_request.card_number,
        expiry_date=payment_request.expiry_date,
        cvv=payment_request.cvv,
        amount=payment_request.amount,
        user_id=payment_request.user_id,
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
async def get_balance(user_id: int, db: Session = Depends(get_db)):
    # calculate and return current balance
    transactions = db.query(TransactionModel).filter(
        TransactionModel.user_id == user_id,
        TransactionModel.status == "processed"
    ).all()
    total_balance = sum(t.amount for t in transactions)
    return BalanceResponse(total_balance=total_balance)

@router.get("/payments/transactions", response_model=List[TransactionResponse])
async def get_transactions(user_id: int, db: Session = Depends(get_db)):
    # search and return all transaction of users
    transactions = db.query(TransactionModel).filter(
        TransactionModel.user_id == user_id
    ).all()
    return [TransactionResponse(
        transaction_id=t.id,
        user_id=t.user_id,
        amount=t.amount,
        status=t.status
    ) for t in transactions]