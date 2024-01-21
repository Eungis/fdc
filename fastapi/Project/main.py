from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy.orm import Session
from project import schemas, models
from project.database import SessionLocal, engine

app = FastAPI()

models.Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/product")
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

    new_product = models.Product(name=request.name, description=request.description, price=request.price)
    db.add(new_product)
    db.commit()
    # reload the latest attributes of object
    db.refresh(new_product)

    return request
