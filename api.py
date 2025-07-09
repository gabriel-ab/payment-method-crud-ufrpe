from typing import Optional
from uuid import UUID, uuid4
import os

from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import create_model, ValidationError
from sqlmodel import SQLModel, Field, create_engine, select, Session
from contextlib import asynccontextmanager

def patch(model: type[SQLModel]) -> type[SQLModel]:
    fields = model.model_fields.copy()
    for f in fields.values():
        f.required = False
        f.default = None

    return create_model(
        f"{model.__name__}Optional",
        **{n: (Optional[f.annotation], f) for n, f in fields.items()}
    )

class PaymentMethodBase(SQLModel):
    owner_name: str = Field(max_length=100, description="Name of the card owner")
    card_number: str = Field(min_length=16, max_length=16, description="16-digit card number", schema_extra=dict(pattern="\d{16}"))
    expiration_date: str = Field(max_length=7, description="MM/YYYY format", schema_extra=dict(pattern="\d{2}/\d{4}"))
    security_code: str = Field(min_length=3, max_length=3, description="3-digit security code")


class PaymentMethodCreate(PaymentMethodBase):
    user: UUID = Field(index=True, description="UUID of the user")


class PaymentMethodPatch(patch(PaymentMethodBase)):
    pass

class PaymentMethod(PaymentMethodCreate, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True, index=True, description="Unique identifier for the payment method")



DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
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
def create_payment_method(payment: PaymentMethodCreate, session: Session = Depends(get_session)):
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
    user: UUID, uuid: UUID, payment_update: PaymentMethodPatch, session: Session = Depends(get_session)
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
