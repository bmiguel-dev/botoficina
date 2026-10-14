from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.database import db  

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.initiate_tables()
    yield
    

app = FastAPI(lifespan=lifespan)