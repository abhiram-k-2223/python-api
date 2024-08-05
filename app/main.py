from fastapi import FastAPI,Response,status,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

class Post(BaseModel):
    title:str
    content:str
    rating:Optional[int] = None
    published:bool = True

my_posts = [{"title":"friendship day scenario",
             "content":"em ra bunty friendship day anta iyyala party edhi malla","id":1},
             
             {
                 "title":"title of the post 2",
                 "content":"content of the post 2",
                 "id":2
             }]

@app.get("/")
def root():
    return {'message':'em vai bunty etla unnav'}

@app.get('/posts')
def posts():
    print("all posts are shown")
    return {"data":my_posts}

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = 'Post not found' )
    print(post)
    return {"post detail": post}

@app.post("/post",status_code = status.HTTP_201_CREATED)
def post(post:Post):
    post_dict = post.model_dump()
    post_dict['id'] = randrange(0,100000)
    my_posts.append(post_dict)
    return {"data":post}

def find_index_post(id):
    for i,p in enumerate(my_posts):
        if p['id'] == id:
            return i

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, response: Response):
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = 'Post not found')

    my_posts.pop(index)
    return "post is removed"


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')

    post_dict = post.model_dump()
    post_dict['id'] = id
    my_posts[index] = post_dict

    return {"data": post_dict}
