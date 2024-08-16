from fastapi import FastAPI,Response,status,HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models
import time
from .import models
from sqlalchemy.orm import Session
from .database import engine,get_db

models.Base.metadata.create_all(bind = engine)

app = FastAPI()


class Post(BaseModel):
    title:str
    content:str
    published:bool = True

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

@app.get("/")
def root():
    return {'message':'em vai bunty etla unnav'}

@app.get('/sqlalchemy')
def test_posts(db:Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"status":posts}

@app.get('/posts')
def posts(db:Session = Depends(get_db)):
    #cursor.execute("""select *from posts""")
    #posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data":posts}

@app.get("/posts/{id}")
def get_post(id: int, response: Response,db:Session = Depends(get_db)):
    # cursor.execute("""select *from posts where id = %s""",(str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = 'Post not found' )
    return {"message":post}

@app.post("/post", status_code=status.HTTP_201_CREATED)
def post(post: Post,db:Session = Depends(get_db)):
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) 
    #     VALUES (%s, %s, %s) RETURNING *""",
    #     (post.title, post.content, post.published)
    # )
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, response: Response,db:Session = Depends(get_db)):
    # cursor.execute(
    #     """delete from posts where id = %s returning *""",(str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = 'Post not found')
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post,db:Session = Depends(get_db)):
    # cursor.execute(
    #     """UPDATE posts SET title = %s, content = %s, published = %s 
    #        WHERE id = %s RETURNING *""",
    #     (post.title, post.content, post.published, id)
    # )
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    post_query.update(post.model_dump(),synchronize_session=False)
    db.commit()

    return {"data": post_query.first()}
