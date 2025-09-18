from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies.user import get_payload
from src.api.schemas.mock import Product, Order
from src.db.roles import UserRole


router = APIRouter()


MOCK_PRODUCTS: list[Product] = [
    Product(id=1, name="Keyboard", price=49.99),
    Product(id=2, name="Mouse", price=19.99),
]

MOCK_ORDERS: list[Order] = [
    Order(id=1, product_id=1, quantity=2),
    Order(id=2, product_id=2, quantity=1),
]


@router.get("/products", response_model=List[Product], summary="Mock: список товаров")
async def list_products(payload: Annotated[dict, Depends(get_payload)]):
    return MOCK_PRODUCTS


@router.get(
    "/orders",
    response_model=List[Order],
    summary="Mock: список заказов, доступно только аутентифицированным пользователям",
)
async def list_orders(payload: Annotated[dict, Depends(get_payload)]):
    return MOCK_ORDERS
