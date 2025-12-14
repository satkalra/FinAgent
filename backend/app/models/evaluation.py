"""Evaluation model for storing AI response quality evaluations."""
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Evaluation(Base):
    """Evaluation model to store quality evaluations for AI responses."""

    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 star rating
    quality_score = Column(Float, nullable=True)  # 0-100 quality score
    accuracy_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    helpfulness_score = Column(Float, nullable=True)
    tool_usage_quality = Column(Float, nullable=True)  # Quality of tool usage
    feedback_text = Column(Text, nullable=True)
    evaluator_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    message = relationship("Message", back_populates="evaluations")
    conversation = relationship("Conversation", back_populates="evaluations")

    def __repr__(self):
        return f"<Evaluation(id={self.id}, rating={self.rating}, message_id={self.message_id})>"
