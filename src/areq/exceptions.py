from collections import OrderedDict
from typing import Type, TypeVar, Union

import httpx
import requests.exceptions

from .models import AreqRequest, AreqResponse, create_areq_request, create_areq_response

SupportedHttpxError = httpx.HTTPError | httpx.InvalidURL

T = TypeVar("T", bound=httpx.HTTPError | httpx.InvalidURL)

ErrorType = Union[
    httpx.HTTPStatusError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
    httpx.TooManyRedirects,
    httpx.DecodingError,
    httpx.CookieConflict,
    httpx.ConnectError,
    httpx.ReadError,
    httpx.WriteError,
    httpx.RemoteProtocolError,
    httpx.ProtocolError,
    httpx.NetworkError,
    httpx.TransportError,
    httpx.TimeoutException,
    httpx.InvalidURL,
]


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
    """
    Wraps httpx connection errors, mimicking requests.exceptions.ConnectionError.
    """

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
    """
    Wraps httpx timeout errors, mimicking requests.exceptions.Timeout.
    """

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
    │       └── requests.ConnectionError
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
    """
    Wraps httpx read timeout errors, mimicking requests.exceptions.ReadTimeout.
    """

    def __init__(self, error: httpx.ReadTimeout):
        super().__init__(error)  # AreqTimeout -> AreqException -> requests.Timeout


class AreqTooManyRedirects(AreqException, requests.exceptions.TooManyRedirects):
    """
    Wraps httpx too many redirects errors, mimicking requests.exceptions.TooManyRedirects.
    """

    response: AreqResponse | None = None  # Can be None

    def __init__(self, error: httpx.TooManyRedirects):
        # httpx.TooManyRedirects doesn't have a response attribute
        super().__init__(error)  # Just pass the error, no response


class AreqInvalidURL(AreqException, requests.exceptions.InvalidURL):
    """
    Wraps httpx invalid url errors, mimicking requests.exceptions.InvalidURL.
    """

    def __init__(self, error: httpx.InvalidURL):
        # InvalidURL is now directly supported by AreqException via SupportedHttpxError
        super().__init__(error)


class AreqMissingSchema(AreqInvalidURL, requests.exceptions.MissingSchema):
    """
    Wraps httpx missing schema errors, mimicking requests.exceptions.MissingSchema.
    requests has a separate MissingSchema exception, but httpx bundles it with InvalidURL.
    The only way we can find if its a missing schema error is to check the message.
    """

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
    """
    Wraps httpx ssl errors, mimicking requests.exceptions.SSLError.
    """

    # requests.SSLError inherits ConnectionError
    def __init__(
        self, error: httpx.ConnectError
    ):  # Specifically for ConnectErrors that are SSL related
        super().__init__(
            error
        )  # AreqConnectionError -> AreqException -> requests.ConnectionError


class AreqProxyError(AreqConnectionError, requests.exceptions.ProxyError):
    """
    Wraps httpx proxy errors, mimicking requests.exceptions.ProxyError.
    """

    # requests.ProxyError inherits ConnectionError
    def __init__(
        self, error: httpx.ConnectError
    ):  # Specifically for ConnectErrors that are Proxy related
        super().__init__(error)


class AreqContentDecodingError(AreqException, requests.exceptions.ContentDecodingError):
    """
    Wraps httpx content decoding errors, mimicking requests.exceptions.ContentDecodingError.
    """

    def __init__(self, error: httpx.DecodingError):
        # httpx.DecodingError doesn't have a 'response' attribute.
        # requests.ContentDecodingError can take response=, but we'll omit it.
        super().__init__(error)


# --- Factory Function ---


def _convert_httpx_invalid_url_to_areq_exception(
    error: httpx.InvalidURL,
) -> AreqException:
    """
    Converts an httpx.InvalidURL instance into an appropriate AreqException subclass.
    """
    message = str(error).lower()
    if any(
        msg in message
        for msg in ["missing url scheme", "invalid url scheme", "missing schema"]
    ):
        return AreqMissingSchema(error)
    return AreqInvalidURL(error)


def _convert_httpx_connect_timeout_to_areq_exception(
    error: httpx.ConnectError,
) -> AreqException:
    """
    Converts an httpx.ConnectTimeout instance into an appropriate AreqException subclass.
    """
    message = str(error).lower()
    if "ssl" in message or "tls" in message:
        return AreqSSLError(error)
    if "proxy" in message:  # Basic heuristic
        return AreqProxyError(error)
    return AreqConnectionError(error)


mapper = OrderedDict(
    {
        # Most specific types first
        httpx.HTTPStatusError: AreqHTTPError,
        httpx.ConnectTimeout: AreqConnectTimeout,
        httpx.ReadTimeout: AreqReadTimeout,
        httpx.WriteTimeout: AreqTimeout,
        httpx.PoolTimeout: AreqConnectTimeout,
        httpx.TooManyRedirects: AreqTooManyRedirects,
        httpx.DecodingError: AreqContentDecodingError,
        httpx.CookieConflict: AreqException,
        # Connection-related errors
        httpx.ConnectError: _convert_httpx_connect_timeout_to_areq_exception,
        httpx.ReadError: AreqConnectionError,
        httpx.WriteError: AreqConnectionError,
        httpx.RemoteProtocolError: AreqConnectionError,
        httpx.ProtocolError: AreqConnectionError,
        httpx.LocalProtocolError: AreqConnectionError,
        # Network and transport errors
        httpx.NetworkError: AreqConnectionError,
        httpx.TransportError: AreqException,
        # Timeout base class
        httpx.TimeoutException: AreqTimeout,
        # URL validation
        httpx.InvalidURL: _convert_httpx_invalid_url_to_areq_exception,
    }
)


def is_error_type(
    error: httpx.HTTPError | httpx.InvalidURL, error_type: Type[T]
) -> bool:
    """Type guard to check error type and help type checker understand the type."""
    return isinstance(error, error_type)


def convert_httpx_to_areq_exception(
    error: httpx.HTTPError | httpx.InvalidURL,
) -> AreqException:
    """
    Converts an httpx error instance into an appropriate AreqException subclass.

    Args:
        error: The httpx error to convert

    Returns:
        An appropriate AreqException subclass instance

    Note:
        If the error type is not found in the mapper, returns a base AreqException
    """
    for error_type, converter in mapper.items():
        if isinstance(error, error_type):
            # After isinstance check, we know error is of type error_type
            return converter(error)  # type: ignore[arg-type]

    # Absolute fallback for any httpx.HTTPError not specifically mapped
    return AreqException(error)
