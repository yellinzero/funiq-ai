from app.core.errors.base import BaseErrorCode


class ConversationErrorCode(BaseErrorCode):
    """
    Conversation related errors (Category F)
    """
    # Resource related (03)
    CONVERSATION_NOT_FOUND = ("F0301", "Conversation not found with the specified ID")
    
    # Operation related (04)
    CONVERSATION_CREATE_ERROR = ("F0401", "Failed to create conversation - Please check the provided configuration")
    CONVERSATION_UPDATE_ERROR = ("F0402", "Failed to update conversation - Please check the provided changes")
    CONVERSATION_DELETE_ERROR = ("F0403", "Failed to delete conversation - Please ensure no active dependencies exist")
    
    # Business logic/Status related (10)
    CONVERSATION_NOT_ACTIVE = ("F1001", "The requested conversation is not active")
