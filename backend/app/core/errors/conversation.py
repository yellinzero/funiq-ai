from app.core.errors.base import BaseErrorCode


class ConversationErrorCode(BaseErrorCode):
    """
    Conversation related error codes
    """
    CONVERSATION_NOT_FOUND = ("D0601", "Conversation not found with the specified ID")
    CONVERSATION_DELETE_ERROR = ("D0602", "Failed to delete conversation - Please ensure no active dependencies exist")
    CONVERSATION_CREATE_ERROR = ("D0603", "Failed to create conversation - Please check the provided configuration")

    CONVERSATION_NOT_ACTIVE = ("D0604", "The requested conversation is not active")

    CONVERSATION_UPDATE_ERROR = ("D0605", "Failed to update conversation - Please check the provided changes")
