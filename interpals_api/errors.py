"""
The project error tree.
"""

class InterpalsAPIError(Exception):
    """
    Base InterpalsAPI error.
    """
    pass


class SessionError(InterpalsAPIError):
    """
    General session error.
    """
    pass


class APIError(InterpalsAPIError):
    """
    General API error.
    """
    pass


class NoCSRFTokenError(SessionError):
    """
    CSRF token not found on session create.
    """
    pass


class WrongUsernameOrPasswordError(SessionError):
    """
    Invalid credentials on session create.
    """
    pass


class TooManyLoginAttemptsError(SessionError):
    """
    Too many attempts on session create.
    """
    pass


class APITimeoutError(APIError):
    """
    Timeout error in API call.
    """
    pass


class APIAuthError(APIError):
    """
    Authorization error in API call.
    """
    pass


class APIRedirectError(APIError):
    """
    Redirect error in API call.
    """
    pass
