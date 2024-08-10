from fastapi import FastAPI,Response,status,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Post(BaseModel):
    title:str
    content:str
    rating:Optional[int] = None
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

@app.get('/posts')
def posts():
    cursor.execute("""select *from posts""")
    posts = cursor.fetchall()
    return {"data":posts}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute("""select *from posts where id = %s""",(str(id),))
    post = cursor.fetchone()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = 'Post not found' )
    return {"message":post}

@app.post("/post", status_code=status.HTTP_201_CREATED)
def post(post: Post):
    cursor.execute(
        """INSERT INTO posts (title, content, published) 
        VALUES (%s, %s, %s) RETURNING *""",
        (post.title, post.content, post.published)
    )
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, response: Response):
    cursor.execute(
        """delete from posts where id = %s returning *""",(str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = 'Post not found')
    print("the post is now deleted")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s 
           WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, id)
    )
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return {"data": updated_post}
