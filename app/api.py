from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db


# All routes in this file are mounted under /api/v1.
# So @router.get("/users") becomes GET /api/v1/users.
router = APIRouter(prefix="/api/v1")

# Reusable type alias: injects one SQLAlchemy Session into each request handler.
# Depends(get_db) tells FastAPI to run get_db() before the route function.
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/users", response_model=list[schemas.UserRead])
def list_users(
    db: DbSession,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    # GET collection endpoint with simple pagination.
    # Query(ge=0) means skip must be greater than or equal to 0.
    # Query(le=100) means limit cannot be higher than 100.
    return crud.list_users(db, skip=skip, limit=limit)


@router.post(
    "/users",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(payload: schemas.UserCreate, db: DbSession):
    # FastAPI validates payload before this function runs.
    # If the JSON body is invalid, FastAPI automatically returns 422.
    try:
        return crud.create_user(db, payload)
    except IntegrityError as exc:
        # Example: duplicate email violates the unique database constraint.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        ) from exc


@router.get("/users/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, db: DbSession):
    # Path parameters like user_id come from the URL.
    # Example: /api/v1/users/5 gives user_id = 5.
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.put("/users/{user_id}", response_model=schemas.UserRead)
def replace_user(user_id: int, payload: schemas.UserPut, db: DbSession):
    # PUT expects a full user object and replaces all editable fields.
    user = crud.get_user(db, user_id)
    if user is None:
        # Raising HTTPException stops the route and sends this error response.
        raise HTTPException(status_code=404, detail="User not found.")
    try:
        return crud.replace_user(db, user, payload)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        ) from exc


@router.patch("/users/{user_id}", response_model=schemas.UserRead)
def patch_user(user_id: int, payload: schemas.UserPatch, db: DbSession):
    # PATCH accepts a partial JSON body and changes only provided fields.
    # Example body: {"full_name": "Updated Name"}
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    try:
        return crud.patch_user(db, user, payload)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        ) from exc


@router.delete(
    "/users/{user_id}",
    response_model=schemas.Message,
    status_code=status.HTTP_200_OK,
)
def delete_user(user_id: int, db: DbSession):
    # The database relationship also deletes this user's posts.
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    crud.delete_user(db, user)
    return {"message": "User deleted."}


@router.get("/posts", response_model=list[schemas.PostRead])
def list_posts(
    db: DbSession,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    owner_id: int | None = None,
):
    # owner_id is an optional filter: /api/v1/posts?owner_id=1
    return crud.list_posts(db, skip=skip, limit=limit, owner_id=owner_id)


@router.post(
    "/posts",
    response_model=schemas.PostRead,
    status_code=status.HTTP_201_CREATED,
)
def create_post(payload: schemas.PostCreate, db: DbSession):
    # Validate the foreign key early so the frontend receives a clear 404.
    # A post must belong to a real user.
    if crud.get_user(db, payload.owner_id) is None:
        raise HTTPException(status_code=404, detail="Owner not found.")
    return crud.create_post(db, payload)


@router.get("/posts/{post_id}", response_model=schemas.PostRead)
def get_post(post_id: int, db: DbSession):
    # GET one post by id.
    post = crud.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")
    return post


@router.put("/posts/{post_id}", response_model=schemas.PostRead)
def replace_post(post_id: int, payload: schemas.PostPut, db: DbSession):
    # A post can be reassigned to another existing user.
    # First check the post exists, then check the new owner exists.
    post = crud.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")
    if crud.get_user(db, payload.owner_id) is None:
        raise HTTPException(status_code=404, detail="Owner not found.")
    return crud.replace_post(db, post, payload)


@router.patch("/posts/{post_id}", response_model=schemas.PostRead)
def patch_post(post_id: int, payload: schemas.PostPatch, db: DbSession):
    # If owner_id is being changed, make sure the new owner exists.
    # If owner_id was not sent, leave the current owner unchanged.
    post = crud.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")
    if payload.owner_id is not None and crud.get_user(db, payload.owner_id) is None:
        raise HTTPException(status_code=404, detail="Owner not found.")
    return crud.patch_post(db, post, payload)


@router.delete(
    "/posts/{post_id}",
    response_model=schemas.Message,
    status_code=status.HTTP_200_OK,
)
def delete_post(post_id: int, db: DbSession):
    # Delete one post by id.
    post = crud.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")
    crud.delete_post(db, post)
    return {"message": "Post deleted."}
