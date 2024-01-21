import sys
import uvicorn
from fastapi import FastAPI, Form
from pydantic import BaseModel, Field, HttpUrl
from typing import Set, List
from uuid import UUID
from datetime import date, datetime, time, timedelta


class Event(BaseModel):
    event_id: UUID
    start_date: date
    start_time: datetime
    end_time: datetime
    repeat_time: time
    execute_after: timedelta


class Profile(BaseModel):
    name: str
    email: str
    age: int


class Image(BaseModel):
    url: HttpUrl
    name: str


class Product(BaseModel):
    name: str = Field(example="phone")
    price: int = Field(
        # For documentation
        title="Price of the item",
        description="This would be the price of the item being added.",
        gt=0,
    )
    discount: int
    discounted_price: float
    # accept only unique items
    tags: Set[str] = Field(example="['electronics', 'computers']", default_factory=[])
    # nesting pydantic model
    images: List[Image]

    class Config:
        # provide information of example data
        json_schema_extra = {
            "example": {
                "name": "Phone",
                "price": 100,
                "discount": 10,
                "discounted_price": 0,
                "tags": ["electronics", "computers"],
                "images": [
                    {"url": "http://www.google.com", "name": "phone image"},
                    {"url": "http://www.google.com", "name": "phone image side view"},
                ],
            }
        }


class Offer(BaseModel):
    name: str
    description: str
    price: float
    # deepy nested models
    products: List[Product]


class User(BaseModel):
    name: str
    email: str


app = FastAPI()


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}


@app.post("/addevent")
def addevent(event: Event):
    return {event}


@app.post("/addoffer")
def addoffer(offer: Offer):
    return {offer}


@app.post("/purchase")
def purchase(user: User, product: Product):
    return {user, product}


@app.post("/addproduct")
def addproduct(product: Product):
    product.discounted_price = product.price - (product.price * product.discount) / 100
    return product


@app.get("/")
def index():
    return "Hello there!"


# id here is a `Path Parameter` with Type
@app.get("/property/{id}")
def property(id: int):
    return {f"This is a property page for property {id}"}


# ordering of routes - handle them in the correct order
@app.get("/user/admin")
def admin():
    return {"This is admin page"}


@app.get("/user/{username}")
def profile(username: str):
    return {f"This is a profile page for user: {username}"}


# id here is a `Query Parameter`
# how to pass the query parameter? 27.0.0.1:8000/products?id=10&price=200
@app.get("/products")
def products(id: int = None, price: int = None):
    return {f"Product with an id: {id}; price: {price}"}


# combination of path and query parameter
@app.get("/profile/{userid}/comments")
def new_profile(userid: int, commentid: int):
    return {f"Profile page for user with user id {userid} and comment with {commentid}"}


# request body
@app.post("/adduser")
def adduser(profile: Profile):
    return {profile}


if __name__ == "__main__":
    APP_ENV = sys.argv[1]

    # uvicorn main:app --reload
    uvicorn.run("main:app", host="0.0.0.0", port="8000", workers=1, reload=True, log_config="./log.ini")

    # # use gunicorn as process manager
    # command = "gunicorn main:app --preload --workers 2 --worker-class uvicorn.workers.UvicornWorker" \
    #           "-c ./config.py --log-config "
    # if APP_ENV == "production":
    #     command += "./production/log.ini"
    # else:
    #     command += "./development/log.ini"
    # os.system(command)
