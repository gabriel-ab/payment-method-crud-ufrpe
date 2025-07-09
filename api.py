from typing import AsyncGenerator
import uuid
import os

from fastapi import FastAPI
from fastcrud import crud_router
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Mapped, mapped_column, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from pydantic import BaseModel

class Base(DeclarativeBase, MappedAsDataclass):
    uuid: Mapped[str] = mapped_column(sa.Uuid, primary_key=True, unique=True, init=False, repr=False, default=uuid.uuid4)

class PaymentMethod(Base):
    __tablename__ = "payment_method"
    user_id: Mapped[str] = mapped_column(sa.Uuid)
    owner: Mapped[str] = mapped_column(sa.String(255))
    number: Mapped[str] = mapped_column(sa.String(16))
    expiry: Mapped[str] = mapped_column(sa.String(5))
    cvc: Mapped[str] = mapped_column(sa.String(3))


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

item_router = crud_router(
    session=get_session,
    model=PaymentMethod,
    create_schema=PaymentMethod,
    update_schema=PaymentMethod,
    path="/payment_method",
    tags=["Payment Methods"],
)

app.include_router(item_router)


