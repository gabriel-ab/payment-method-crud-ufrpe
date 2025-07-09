from typing import Optional
from uuid import UUID, uuid4
import os

from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import ValidationError
from sqlmodel import SQLModel, Field, create_engine, select, Session
from contextlib import asynccontextmanager


class CreatePaymentMethod(SQLModel):
    user: UUID
    owner_name: str = Field(max_length=100, description="Name of the card owner")
    card_number: str = Field(min_length=16, max_length=16, description="16-digit card number")
    expiration_date: str = Field(max_length=7, regex="\d{2}/\d{4}", description="MM/YYYY format")
    security_code: str = Field(min_length=3, max_length=3, description="3-digit security code")


class PaymentMethod(CreatePaymentMethod, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True, index=True)


class PatchPaymentMethod(SQLModel):
    owner_name: Optional[str] = None
    card_number: Optional[str] = None
    expiration_date: Optional[str] = None
    security_code: Optional[str] = None


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Payment Method API", description="API for managing payment methods", version="1.0.0", lifespan=lifespan
)


@app.post("/payment_method", response_model=PaymentMethod, status_code=status.HTTP_201_CREATED)
def create_payment_method(payment: CreatePaymentMethod, session: Session = Depends(get_session)):
    db_payment = PaymentMethod.model_validate(payment)
    session.add(db_payment)
    session.commit()
    session.refresh(db_payment)
    return db_payment


@app.get("/payment_method", response_model=list[PaymentMethod])
def read_payment_methods(user: UUID, session: Session = Depends(get_session)):
    payments = session.exec(select(PaymentMethod).where(PaymentMethod.user == user)).all()
    return payments


@app.patch("/payment_method", response_model=PaymentMethod)
def update_payment_method(
    user: UUID, uuid: UUID, payment_update: PatchPaymentMethod, session: Session = Depends(get_session)
):
    payment = session.get(PaymentMethod, uuid)
    if not payment or payment.user != user:
        raise HTTPException(status_code=404, detail="Payment method not found")
    try:
        for key, value in payment_update.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(payment, key, value)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


@app.delete("/payment_method", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_method(user: UUID, uuid: UUID, session: Session = Depends(get_session)):
    payment = session.get(PaymentMethod, uuid)
    if not payment or payment.user != user:
        raise HTTPException(status_code=404, detail="Payment method not found")
    session.delete(payment)
    session.commit()
