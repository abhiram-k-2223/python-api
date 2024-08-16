from fastapi import FastAPI,Response,status,HTTPException, Depends
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models
import time
from sqlalchemy.orm import Session
from .database import engine,get_db
from .routers import user,post,auth

models.Base.metadata.create_all(bind = engine)

app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(host = 'localhost',database = 'python-api',user = 'postgres',password = 'abhi2305',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("database connection was successful")
        break
    except Exception as e:
        print("connecting to database failed")
        print("error:",e)
        time.sleep(2)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {'message':'em vai bunty etla unnav'}

