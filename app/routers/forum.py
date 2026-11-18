"""
CQ Silvopastoral Dashboard — Forum Router
Version: 2.0 (Workshop Edition)

Endpoints:
  GET  /forum/posts           — list all posts (with replies), newest-first
  POST /forum/posts           — create a new top-level post
  POST /forum/posts/{id}/replies — reply to an existing post

All endpoints require a valid JWT (registered users only).
Only the author's display name is returned — no email, no role info.
"""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Session as DBSession

from app.database import Base, get_db
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/forum", tags=["forum"])


# ---------------------------------------------------------------------------
# SQLAlchemy models
# ---------------------------------------------------------------------------

class ForumPost(Base):
    __tablename__ = "forum_posts"

    id         = Column(Integer, primary_key=True, index=True)
    author_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    body       = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author  = relationship("User", foreign_keys=[author_id], lazy="joined")
    replies = relationship(
        "ForumReply",
        back_populates="post",
        order_by="ForumReply.created_at",
        lazy="joined",
        cascade="all, delete-orphan",
    )


class ForumReply(Base):
    __tablename__ = "forum_replies"

    id         = Column(Integer, primary_key=True, index=True)
    post_id    = Column(Integer, ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=False)
    author_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    body       = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    post   = relationship("ForumPost", back_populates="replies")
    author = relationship("User", foreign_keys=[author_id], lazy="joined")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ReplyCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=2000)


class PostCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)


class ReplyOut(BaseModel):
    id:          int
    post_id:     int
    author_name: str
    body:        str
    created_at:  datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_safe(cls, reply: ForumReply) -> "ReplyOut":
        """Return only the display name — no email, no role."""
        return cls(
            id=reply.id,
            post_id=reply.post_id,
            author_name=reply.author.full_name if reply.author else "Unknown",
            body=reply.body,
            created_at=reply.created_at,
        )


class PostOut(BaseModel):
    id:          int
    author_name: str
    body:        str
    created_at:  datetime
    replies:     List[ReplyOut] = []

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_safe(cls, post: ForumPost) -> "PostOut":
        """Return only display names — no emails, no roles."""
        return cls(
            id=post.id,
            author_name=post.author.full_name if post.author else "Unknown",
            body=post.body,
            created_at=post.created_at,
            replies=[ReplyOut.from_orm_safe(r) for r in post.replies],
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/posts", response_model=List[PostOut])
def list_posts(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all forum posts, newest-first, with their replies.
    Requires authentication — registered users only.
    Only author display names are returned, never emails or roles.
    """
    posts = (
        db.query(ForumPost)
        .order_by(ForumPost.created_at.desc())
        .all()
    )
    return [PostOut.from_orm_safe(p) for p in posts]


@router.post("/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new top-level forum post.
    Requires authentication.
    """
    post = ForumPost(
        author_id=current_user.id,
        body=payload.body.strip(),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return PostOut.from_orm_safe(post)


@router.post("/posts/{post_id}/replies", response_model=ReplyOut, status_code=status.HTTP_201_CREATED)
def create_reply(
    post_id: int,
    payload: ReplyCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reply to an existing forum post.
    Requires authentication.
    """
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    reply = ForumReply(
        post_id=post_id,
        author_id=current_user.id,
        body=payload.body.strip(),
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return ReplyOut.from_orm_safe(reply)
