from .. import schemas,models
from fastapi import Response,status,HTTPException, Depends,APIRouter
from sqlalchemy.orm import Session
from ..database import engine,get_db
from typing import List
from . import oauth2
from typing import Optional

router = APIRouter(
    prefix='/posts',
    tags = ['Posts']
)

# @router.get("/myposts", response_model=List[schemas.Post])
# def current_user_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
#     print("Current User ID:", current_user.id)  # Debugging print statement
#     posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
#     user = db.query(models.User).filter(models.User.id == current_user.id).first()
#     print(user.id)
#     print("Posts:", posts)  # Debugging print statement
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found for the current user.")
#     return posts

@router.get('/',response_model = List[schemas.Post])
def posts(db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user),limit:int = 10,skip:int = 0,search:Optional[str] = ""):
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found for the current user.")
    return posts

@router.get("/{id}",response_model = schemas.Post)
def get_post(id: int, response: Response,db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = 'Post not found' )
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you can only retrieve your posts')
    
    return post

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def post(post: schemas.PostCreate,db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id = current_user.id,**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, response: Response,db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = 'Post not found')
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you can only delete your posts not others')
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}",response_model = schemas.Post)
def update_post(id: int, post: schemas.PostCreate,db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you can only delete your posts not others')
    
    post_query.update(post.model_dump(),synchronize_session=False)
    db.commit()

    return post_query.first()


