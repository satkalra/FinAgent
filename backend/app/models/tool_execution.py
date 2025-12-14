"""Tool execution model for tracking agent tool usage."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ToolExecution(Base):
    """Tool execution model to track tool usage by the agent."""

    __tablename__ = "tool_executions"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_name = Column(String(100), nullable=False, index=True)
    tool_input = Column(JSON, nullable=False)  # Store as JSON
    tool_output = Column(Text, nullable=True)  # Store result as text/JSON string
    execution_time_ms = Column(Integer, nullable=True)  # Time taken to execute tool
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    message = relationship("Message", back_populates="tool_executions")

    def __repr__(self):
        return f"<ToolExecution(id={self.id}, tool={self.tool_name}, success={self.success})>"
