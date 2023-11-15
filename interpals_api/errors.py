class InterpalsAPIError(Exception):
    pass


class SessionError(InterpalsAPIError):
    pass


class APIError(InterpalsAPIError):
    pass


class NoCSRFTokenError(SessionError):
    pass


class WrongUsernameOrPasswordError(SessionError):
    pass


class TooManyLoginAttemptsError(SessionError):
    pass


class APITimeoutError(APIError):
    pass


class APIAuthError(APIError):
    pass


class APIRedirectError(APIError):
    pass
