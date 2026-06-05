from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas


# CRUD functions keep database logic out of the HTTP route handlers.
# CRUD means Create, Read, Update, Delete.
# The API layer handles HTTP details; this file handles database details.
def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    # Build a SELECT query:
    # - select(models.User) means "select rows from the users table"
    # - offset(skip) skips rows for pagination
    # - limit(limit) caps how many rows are returned
    # - order_by(models.User.id) keeps the response in a stable order
    statement = select(models.User).offset(skip).limit(limit).order_by(models.User.id)

    # db.scalars(statement) returns model objects instead of raw database rows.
    return list(db.scalars(statement))


def get_user(db: Session, user_id: int) -> models.User | None:
    # db.get is the simplest way to find one row by primary key.
    # It returns None if no user exists with that id.
    return db.get(models.User, user_id)


def get_user_by_email(db: Session, email: str) -> models.User | None:
    # This shows a custom WHERE query instead of lookup by primary key.
    statement = select(models.User).where(models.User.email == email)
    return db.scalar(statement)


def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    # model_dump converts the validated Pydantic schema into a normal dict.
    # ** unpacks that dict into keyword arguments for the User model.
    user = models.User(**payload.model_dump())

    # Add marks the object as something SQLAlchemy should insert.
    db.add(user)

    # Commit actually writes the insert to the database.
    commit_or_raise(db)

    # refresh loads generated values like id and timestamps after commit.
    db.refresh(user)
    return user


def replace_user(
    db: Session,
    user: models.User,
    payload: schemas.UserPut,
) -> models.User:
    # PUT means complete replacement: every field from the schema is applied.
    for field, value in payload.model_dump().items():
        # setattr(user, "full_name", "New Name") is like user.full_name = "New Name".
        setattr(user, field, value)
    commit_or_raise(db)
    db.refresh(user)
    return user


def patch_user(
    db: Session,
    user: models.User,
    payload: schemas.UserPatch,
) -> models.User:
    # PATCH means partial update: exclude_unset ignores fields not sent by client.
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    commit_or_raise(db)
    db.refresh(user)
    return user


def delete_user(db: Session, user: models.User) -> None:
    # Delete marks the object for removal, then commit applies the deletion.
    db.delete(user)
    db.commit()


def list_posts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    owner_id: int | None = None,
) -> list[models.Post]:
    statement = select(models.Post).offset(skip).limit(limit).order_by(models.Post.id)

    # Optional query filter: /posts?owner_id=1
    # If owner_id is not provided, all posts are returned.
    if owner_id is not None:
        statement = statement.where(models.Post.owner_id == owner_id)
    return list(db.scalars(statement))


def get_post(db: Session, post_id: int) -> models.Post | None:
    # Same primary-key lookup pattern as get_user.
    return db.get(models.Post, post_id)


def create_post(db: Session, payload: schemas.PostCreate) -> models.Post:
    # The route already checks that owner_id belongs to an existing user.
    post = models.Post(**payload.model_dump())
    db.add(post)
    commit_or_raise(db)
    db.refresh(post)
    return post


def replace_post(
    db: Session,
    post: models.Post,
    payload: schemas.PostPut,
) -> models.Post:
    # Same replacement pattern as users, but applied to posts.
    for field, value in payload.model_dump().items():
        setattr(post, field, value)
    commit_or_raise(db)
    db.refresh(post)
    return post


def patch_post(
    db: Session,
    post: models.Post,
    payload: schemas.PostPatch,
) -> models.Post:
    # Only fields present in the JSON body are changed.
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    commit_or_raise(db)
    db.refresh(post)
    return post


def delete_post(db: Session, post: models.Post) -> None:
    db.delete(post)
    db.commit()


def commit_or_raise(db: Session) -> None:
    # Roll back failed transactions so the session can be reused safely.
    # The API layer catches IntegrityError and turns it into a clear HTTP error.
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
