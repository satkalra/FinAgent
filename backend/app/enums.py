"""Enums for FinAgent."""

import enum


class MessageRole(str, enum.Enum):
    """Enum for message roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
