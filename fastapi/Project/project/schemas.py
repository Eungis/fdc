from __future__ import annotations

from pydantic import BaseModel


class Seller(BaseModel):
    username: str
    email: str
    password: str


class DisplaySeller(BaseModel):
    username: str
    email: str

    class Config:
        from_attributes = True


class Product(BaseModel):
    name: str
    description: str
    price: int


class DisplayProduct(BaseModel):
    # make price field confidential

    name: str
    description: str
    seller: DisplaySeller

    class Config:
        # enable adding it to any route which we want
        from_attributes = True
