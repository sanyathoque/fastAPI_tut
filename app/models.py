from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    # Store timestamps in UTC so the API does not depend on server timezone.
    # This is used when new rows are created or updated.
    return datetime.now(timezone.utc)


# Database table for people/accounts that can own posts.
class User(Base):
    # Actual database table name.
    __tablename__ = "users"

    # Mapped[...] tells SQLAlchemy the Python type for each database column.
    # mapped_column(...) describes the database behavior for that column.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # unique=True means two users cannot share the same email.
    # index=True makes lookups by email faster.
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # created_at is set when the row is first inserted.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
    )

    # updated_at changes whenever SQLAlchemy updates this row.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now(),
    )

    # One user can have many posts. Deleting a user deletes their posts too.
    posts: Mapped[list["Post"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )


# Database table for content owned by a user.
class Post(Base):
    # Actual database table name.
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)

    # Text is better than String here because post content can be longer.
    content: Mapped[str] = mapped_column(Text)
    published: Mapped[bool] = mapped_column(Boolean, default=False)

    # owner_id links this post to users.id.
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now(),
    )

    # The other side of User.posts. This lets code access post.owner.
    owner: Mapped[User] = relationship(back_populates="posts")
