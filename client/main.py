from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import UniqueConstraint, create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
import requests
from sqlalchemy.orm import sessionmaker, Session

from producer import publish

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db/main_service"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    with db as db:
        yield db


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String, nullable=False)


class ProductUser(Base):
    __tablename__ = "product_user"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    product_id = Column(Integer)
    UniqueConstraint("user_id", "product_id", name="user_product_unique")


app = FastAPI()


@app.get("/", status_code=200)
def root():
    return {"message": "root of client service"}


@app.get("/api/products/", status_code=200)
def products(db: Session = Depends(get_db)):
    products = db.query(Product).all()

    return {"data": products, "status": 200}


@app.post("/api/product/{id}/", status_code=200)
def like(id: int, db: Session = Depends(get_db)):
    req = requests.get("http://docker.for.mac.localhost:8900/api/user")
    last_id = db.query(ProductUser).all()
    if len(last_id) >= 1:
        last_id = last_id[-1].id + 1
    else:
        last_id = 1
    product_check = (
        db.query(ProductUser)
        .filter(
            ProductUser.user_id == req.json().get("id"), ProductUser.product_id == id
        )
        .first()
    )
    if product_check:
        raise HTTPException(
            detail="User has already liked this product", status_code=400
        )
    product_user = ProductUser(id=last_id, user_id=req.json().get("id"), product_id=id)
    db.add(product_user)
    db.commit()
    publish("product_liked", {"id": id})
    return {"message": "successs"}
