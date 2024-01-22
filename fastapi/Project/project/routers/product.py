from typing import List
from fastapi import status, HTTPException
from fastapi.params import Depends
from fastapi import APIRouter
from sqlalchemy.orm import Session
from project import schemas, models
from project.database import get_db

router = APIRouter(prefix="/product", tags=["Products"])


@router.get("/", response_model=List[schemas.DisplayProduct])
def products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products


@router.get("/{id}", response_model=schemas.DisplayProduct)
def product(id, db: Session = Depends(get_db)):
    """Set response_model=schemas.DisplayProduct:

    DisplayProduct's config has been set `from_attributes=True`, which enable
    creating from arbitrary class instances by reading the instance attributes corresponding to the
    model field name.

    => return DisplayProduct.model_validate(response) # in this function, response=product.
    """
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/", status_code=status.HTTP_201_CREATED)  # code 201
def add(request: schemas.Product, db: Session = Depends(get_db)):
    # A newly constructed Session may be said to be in the "begin" state. In this state,
    # the Session has not established any connection or transactional state with any of the Engine opjects
    # that may be associated with it.
    # The Session then receives requests to operate upon a database connection. Typically, this means it is called
    # upon to execute SQL statements using a particular Engine, which may be via Session.query(), Session.execute(),
    # or within a flush operation of pending data, which occurs when such state exists and Session.commit() or
    # Session.flush() is called.

    # Transactions and Connection Management
    # source link: https://docs.sqlalchemy.org/en/13/orm/session_transaction.html#transactions-and-connection-management

    new_product = models.Product(
        name=request.name, description=request.description, price=request.price, seller_id=1  # tmp seller
    )
    db.add(new_product)
    db.commit()

    # reload the latest attributes of object
    db.refresh(new_product)
    return request


@router.delete("/{id}")
def delete(id, db: Session = Depends(get_db)):
    db.query(models.Product).filter(models.Product.id == id).delete(synchronize_session=False)
    db.commit()
    return {f"Entry (product with id {id}) deleted."}


@router.put("/{id}")
def update(id, request: schemas.Product, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id)
    if not product.first():
        pass
    product.update(request.dict())
    db.commit()
    return {f"Product with id {id} was updated."}
