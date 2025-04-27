# Error Code Rule

## Format
Each error code follows the format: `[Letter][Module][Sequence]`
Example: `A01XX`
- `Letter`: Module identifier (1 character)
- `Module`: Category identifier (2 digits)
- `Sequence`: Error sequence number (2 digits)

## Module Prefixes (Letter)
- `A`: Common errors (general system errors)
- `B`: Account related (user, tenant, authentication)
- `C`: Model provider related (AI models, providers)
- `D`: Application related (app management)
- `E`: Workflow related (workflow execution)
- `F`: Conversation related (chat, messages)

## Module Numbers (2 digits)
- `00`: System level (system errors, internal errors)
- `01`: Authentication & Authorization
- `02`: Input/Parameter validation
- `03`: Resource related (not found, already exists)
- `04`: Operation related (create, update, delete)
- `05`: Rate limiting & Quota
- `06`: External service/integration
- `07`: Data processing & validation
- `08`: Configuration related
- `09`: Security related
- `10`: Business logic related

## Example Implementation
```python
class CommonErrorCode(BaseErrorCode):
    """
    Common errors (Category A)
    
    Module categories:
    00: System level errors
    01: Authentication & Authorization
    02: Input/Parameter validation
    03: Resource related
    04: Operation related
    05: Rate limiting & Quota
    """
    # System level errors (00)
    INTERNAL_SERVER_ERROR = ("A0001", "Internal Server Error")
    SERVICE_UNAVAILABLE = ("A0002", "Service temporarily unavailable")
    
    # Authentication & Authorization (01)
    UNAUTHORIZED = ("A0101", "Unauthorized")
    PERMISSION_DENIED = ("A0102", "Permission Denied")
    TOKEN_EXPIRED = ("A0103", "Token has expired")
    
    # Input/Parameter validation (02)
    INVALID_ARGUMENT = ("A0201", "Invalid argument")
    INVALID_FORMAT = ("A0202", "Invalid data format")
    MISSING_REQUIRED_FIELD = ("A0203", "Missing required field")
    
    # Resource related (03)
    RESOURCE_NOT_FOUND = ("A0301", "Resource not found")
    RESOURCE_ALREADY_EXISTS = ("A0302", "Resource already exists")
    
    # Rate limiting (05)
    RATE_LIMIT_EXCEEDED = ("A0501", "Too many requests")
    QUOTA_EXCEEDED = ("A0502", "Quota exceeded")
```

## Guidelines
1. **Consistency**: Use consistent naming and categorization across all modules
2. **Clarity**: Error messages should be clear and descriptive
3. **Documentation**: Always include category comments and descriptions
4. **Extensibility**: Leave room for future error codes in each category
5. **Uniqueness**: Ensure error codes are unique across all modules

## Best Practices
1. Keep error messages user-friendly and actionable
2. Use appropriate HTTP status codes with error responses
3. Include relevant error details without exposing sensitive information
4. Consider internationalization requirements
5. Document all error codes in API documentation

## Error Code Structure
- First character (Letter): Identifies the module
- Next two digits (Module): Identifies the category within the module
- Last two digits (Sequence): Sequential number within the category

## Note
- Error codes should be immutable once in production
- Deprecated error codes should not be reused
- Consider backwards compatibility when updating error codes
- Regular review and cleanup of unused error codes