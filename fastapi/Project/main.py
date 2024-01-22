from fastapi import FastAPI
from project import models
from project.database import engine
from project.routers import product, seller

app = FastAPI(
    title="Products API",
    description="Get details for all the products on our website.",
    terms_of_service="http://www.google.com",
    contact={"Developer name": "Eungis", "website": "http://www.google.com", "email": "demo@gmail.com"},
    license_info={"name": "XYZ", "url": "http://www.google.com"},
    # docs_url="/documentation" # change the router of docs url. Default = docs
)
app.include_router(product.router)
app.include_router(seller.router)

models.Base.metadata.create_all(engine)
