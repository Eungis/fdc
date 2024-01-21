from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Make database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./product.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        # the second parameter only has to be passed whenever using SQLite database
        "check_same_thread": False
    },
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
