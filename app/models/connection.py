from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Connection(Base):
    __tablename__ = "connections"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    addressee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Connection status
    status = Column(String, nullable=False, default="pending")  # pending, accepted, rejected, blocked
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], backref="sent_connections")
    addressee = relationship("User", foreign_keys=[addressee_id], backref="received_connections")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('requester_id', 'addressee_id', name='unique_connection'),
        CheckConstraint('requester_id != addressee_id', name='no_self_connection'),
    )
