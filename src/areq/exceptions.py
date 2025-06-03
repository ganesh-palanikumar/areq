import httpx
import requests.exceptions
from .models import AreqRequest, AreqResponse, create_areq_request, create_areq_response

SupportedHttpxError = httpx.HTTPError | httpx.InvalidURL


class AreqException(requests.exceptions.RequestException):
    """
    Base class for all Areq exceptions.
    Wraps an underlying httpx error.
    """

    underlying_exception: SupportedHttpxError
    request: AreqRequest | None = None
    response: AreqResponse | None = None

    def __init__(self, error: SupportedHttpxError, *args, **kwargs):
        """
        Initializes the AreqException.

        Args:
            error: The underlying httpx error.
            *args: Arguments to pass to the parent requests.exceptions.RequestException.
            **kwargs: Keyword arguments for the parent.
        """
        self.underlying_exception = error

        # Ensure self.request is an AreqRequest instance
        httpx_req_obj = getattr(error, "request", None)
        self.request = create_areq_request(httpx_req_obj)

        # Ensure self.response is an AreqResponse instance
        httpx_resp_obj = getattr(error, "response", None)
        self.response = create_areq_response(httpx_resp_obj)

        # Pass message and request to parent RequestException
        if not args:
            args_to_parent = (str(error),)
        else:
            args_to_parent = args

        kwargs_to_parent = kwargs.copy()
        if "request" not in kwargs_to_parent:
            kwargs_to_parent["request"] = self.request

        super().__init__(*args_to_parent, **kwargs_to_parent)
        self.__cause__ = error


class AreqHTTPError(AreqException, requests.exceptions.HTTPError):
    """
    Wraps an httpx.HTTPStatusError, mimicking requests.exceptions.HTTPError.
    """

    response: AreqResponse | None = (
        None  # Overrides requests.HTTPError.response for type
    )

    def __init__(self, error: httpx.HTTPStatusError):
        # Convert httpx response to AreqResponse
        areq_response = create_areq_response(error.response)

        # Initialize AreqException (which sets self.request and self.underlying_exception)
        # and requests.exceptions.HTTPError
        super().__init__(
            error, response=areq_response
        )  # Calls AreqException then HTTPError
        self.response = areq_response  # Ensure self.response is the AreqResponse

        # Note: self.request is set by AreqException's __init__
        # self.__cause__ is set by AreqException's __init__


class AreqConnectionError(AreqException, requests.exceptions.ConnectionError):
    def __init__(
        self,
        error: (
            httpx.ConnectError
            | httpx.ReadError
            | httpx.WriteError
            | httpx.NetworkError
            | httpx.RemoteProtocolError
            | httpx.ProtocolError
            | httpx.LocalProtocolError
        ),
    ):
        super().__init__(error)  # Passes error message and request to parent


class AreqTimeout(AreqException, requests.exceptions.Timeout):
    def __init__(self, error: httpx.TimeoutException):
        super().__init__(error)


class AreqConnectTimeout(
    AreqTimeout, AreqConnectionError, requests.exceptions.ConnectTimeout
):
    """
    Represents a connection timeout error in areq.

    This class uses multiple inheritance to maintain compatibility with both areq's
    exception hierarchy and requests' exception hierarchy. The inheritance chain is:

    AreqConnectTimeout
    ├── AreqTimeout (areq's timeout base)
    │   └── AreqException (areq's base)
    │       └── requests.RequestException
    ├── AreqConnectionError (areq's connection error base)
    │   └── AreqException (areq's base)
    │       └── requests.RequestException
    └── requests.ConnectTimeout (requests' connect timeout)
        ├── requests.Timeout
        │   └── requests.RequestException
        └── requests.ConnectionError
            └── requests.RequestException

    The MRO ensures that:
    1. AreqException is initialized first (via AreqTimeout or AreqConnectionError)
    2. requests.ConnectTimeout is initialized next
    3. Each base class's __init__ is called exactly once
    4. The final exception type is compatible with both areq and requests

    This design allows areq exceptions to be caught by both areq-specific and
    requests-specific exception handlers, making it a true drop-in replacement.
    """

    def __init__(self, error: httpx.ConnectTimeout | httpx.PoolTimeout):
        """
        Initialize the AreqConnectTimeout exception.

        Args:
            error: The underlying httpx timeout error.
        """
        # Initialize AreqException first with the error object
        AreqException.__init__(self, error)
        # Then initialize requests.ConnectTimeout with just the message
        requests.exceptions.ConnectTimeout.__init__(self, str(error))


class AreqReadTimeout(AreqTimeout, requests.exceptions.ReadTimeout):
    def __init__(self, error: httpx.ReadTimeout):
        super().__init__(error)  # AreqTimeout -> AreqException -> requests.Timeout


class AreqTooManyRedirects(AreqException, requests.exceptions.TooManyRedirects):
    response: AreqResponse | None = None  # Can be None

    def __init__(self, error: httpx.TooManyRedirects):
        # httpx.TooManyRedirects doesn't have a response attribute
        super().__init__(error)  # Just pass the error, no response


class AreqInvalidURL(AreqException, requests.exceptions.InvalidURL):
    def __init__(self, error: httpx.InvalidURL):
        # InvalidURL is now directly supported by AreqException via SupportedHttpxError
        super().__init__(error)


class AreqMissingSchema(AreqInvalidURL, requests.exceptions.MissingSchema):
    def __init__(self, error: httpx.InvalidURL):
        # Check if it's a missing schema error
        message = str(error).lower()
        if not any(
            msg in message
            for msg in ["missing url scheme", "invalid url scheme", "missing schema"]
        ):
            raise ValueError("Not a missing schema error")
        super().__init__(error)


class AreqSSLError(AreqConnectionError, requests.exceptions.SSLError):
    # requests.SSLError inherits ConnectionError
    def __init__(
        self, error: httpx.ConnectError
    ):  # Specifically for ConnectErrors that are SSL related
        super().__init__(
            error
        )  # AreqConnectionError -> AreqException -> requests.ConnectionError


class AreqProxyError(AreqConnectionError, requests.exceptions.ProxyError):
    # requests.ProxyError inherits ConnectionError
    def __init__(
        self, error: httpx.ConnectError
    ):  # Specifically for ConnectErrors that are Proxy related
        super().__init__(error)


class AreqContentDecodingError(AreqException, requests.exceptions.ContentDecodingError):
    def __init__(self, error: httpx.DecodingError):
        # httpx.DecodingError doesn't have a 'response' attribute.
        # requests.ContentDecodingError can take response=, but we'll omit it.
        super().__init__(error)


# --- Factory Function ---


def convert_httpx_to_areq_exception(
    error: httpx.HTTPError | httpx.InvalidURL,
) -> AreqException:
    """
    Converts an httpx error instance into an appropriate AreqException subclass.
    """
    if isinstance(error, httpx.InvalidURL):
        message = str(error).lower()
        if any(
            msg in message
            for msg in ["missing url scheme", "invalid url scheme", "missing schema"]
        ):
            return AreqMissingSchema(error)
        return AreqInvalidURL(error)
    if isinstance(error, httpx.HTTPStatusError):
        return AreqHTTPError(error)

    # Timeout Mappings
    if isinstance(error, httpx.ConnectTimeout):
        return AreqConnectTimeout(error)
    if isinstance(error, httpx.ReadTimeout):
        return AreqReadTimeout(error)
    if isinstance(error, httpx.WriteTimeout):  # requests has no specific WriteTimeout
        return AreqTimeout(error)  # Map to generic AreqTimeout
    if isinstance(
        error, httpx.PoolTimeout
    ):  # Pool timeout is a kind of connect timeout
        return AreqConnectTimeout(error)  # Map to AreqConnectTimeout
    if isinstance(error, httpx.TimeoutException):  # Generic base for other timeouts
        return AreqTimeout(error)

    # Connection / Network Error Mappings (excluding timeouts handled above)
    if isinstance(error, httpx.ConnectError):
        message = str(error).lower()
        if "ssl" in message or "tls" in message:
            return AreqSSLError(error)
        if "proxy" in message:  # Basic heuristic
            return AreqProxyError(error)
        return AreqConnectionError(error)

    if isinstance(
        error, (httpx.ReadError, httpx.WriteError)
    ):  # Non-timeout read/write errors
        return AreqConnectionError(error)

    if isinstance(
        error,
        (httpx.RemoteProtocolError, httpx.ProtocolError, httpx.LocalProtocolError),
    ):
        return AreqConnectionError(error)

    # Request Construction / Redirection Mappings
    if isinstance(error, httpx.TooManyRedirects):
        return AreqTooManyRedirects(error)

    # Decoding Error Mapping
    if isinstance(error, httpx.DecodingError):
        return AreqContentDecodingError(error)

    # Other specific httpx errors without direct common requests equivalents
    if isinstance(error, httpx.CookieConflict):
        return AreqException(error)  # Fallback to base AreqException

    # Fallbacks for broader httpx exception types if not caught by specifics
    if isinstance(
        error, httpx.NetworkError
    ):  # Base for ConnectError, ReadError, WriteError
        return AreqConnectionError(error)
    if isinstance(
        error, httpx.TransportError
    ):  # Base for many, including NetworkError, HTTPStatusError
        return AreqException(
            error
        )  # Use base AreqException for generic transport errors

    # Absolute fallback for any httpx.HTTPError not specifically mapped
    return AreqException(error)
