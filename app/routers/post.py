from .. import schemas,models
from fastapi import FastAPI,Response,status,HTTPException, Depends,APIRouter
from sqlalchemy.orm import Session
from ..database import engine,get_db
from typing import List

router = APIRouter(
    prefix='/posts',
    tags = ['Posts']
)

@router.get('/',response_model = List[schemas.Post])
def posts(db:Session = Depends(get_db)):
    #cursor.execute("""select *from posts""")
    #posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts

@router.get("/{id}",response_model = schemas.Post)
def get_post(id: int, response: Response,db:Session = Depends(get_db),):
    # cursor.execute("""select *from posts where id = %s""",(str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = 'Post not found' )
    return post

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def post(post: schemas.PostCreate,db:Session = Depends(get_db)):
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
    return new_post

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
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

@router.put("/{id}",response_model = schemas.Post)
def update_post(id: int, post: schemas.PostCreate,db:Session = Depends(get_db)):
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

    return post_query.first()