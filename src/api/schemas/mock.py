from pydantic import BaseModel, Field, EmailStr


class Product(BaseModel):
    id: int = Field(ge=1)
    name: str
    price: float = Field(ge=0)


class Order(BaseModel):
    id: int = Field(ge=1)
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=1)


class Customer(BaseModel):
    id: int = Field(ge=1)
    email: EmailStr
    full_name: str


