from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Schemas describe the JSON shape that FastAPI accepts and returns.
# They are separate from SQLAlchemy models so API validation stays explicit.
class UserBase(BaseModel):
    # Shared fields used by multiple user schemas.
    # Keeping them here avoids repeating the same fields in Create, Put, and Read.

    # EmailStr validates that the value looks like an email address.
    email: EmailStr

    # Field(...) adds validation rules.
    # Here, full_name cannot be empty and cannot be longer than 255 characters.
    full_name: str = Field(min_length=1, max_length=255)

    # Default is true, so the frontend can omit this when creating a user.
    is_active: bool = True


class UserCreate(UserBase):
    # POST /users uses the same required fields as UserBase.
    pass


class UserPut(UserBase):
    # PUT replaces the complete user, so all base fields are required.
    pass


class UserPatch(BaseModel):
    # PATCH updates only the fields the frontend sends, so everything is optional.
    # The "| None" part means the field can be missing or null.
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None


class UserRead(UserBase):
    # Response schema includes database-generated fields.
    id: int
    created_at: datetime
    updated_at: datetime

    # Allows Pydantic to read attributes from SQLAlchemy model instances.
    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    # Shared post fields used by create, update, and response schemas.
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)

    # New posts default to drafts unless the frontend sends published: true.
    published: bool = False


class PostCreate(PostBase):
    # The frontend must say which user owns the post.
    owner_id: int


class PostPut(PostBase):
    # PUT replaces the complete post, including ownership.
    owner_id: int


class PostPatch(BaseModel):
    # PATCH supports partial post edits.
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, min_length=1)
    published: bool | None = None
    owner_id: int | None = None


class PostRead(PostBase):
    # Response schema mirrors the post table fields the frontend needs.
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    # Same idea as UserRead: allows returning SQLAlchemy Post objects directly.
    model_config = ConfigDict(from_attributes=True)


class Message(BaseModel):
    # Small response body for delete confirmations and similar messages.
    message: str
