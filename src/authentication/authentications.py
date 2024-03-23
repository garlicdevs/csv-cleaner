from typing import Tuple, Optional

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request


class ApiKeyAuthentication(BaseAuthentication):
    """
    Custom API Key Authentication
    Verifies that the incoming request contains a valid API Key in the headers.
    """

    # Define the header name where the API Key is expected
    api_key_header: str = "X-API-KEY"

    def authenticate(self, request: Request) -> Tuple[str, Optional[None]]:
        """
        Perform API Key authentication.

        Args:
            request (Request): The incoming request object.

        Returns:
            Tuple[str, Optional[None]]: A tuple containing the authenticated user (None in this case) and a token.

        Raises:
            AuthenticationFailed: If the API Key is missing or invalid.
        """
        # Retrieve the API Key from the request headers
        api_key = request.headers.get(self.api_key_header)

        # Validate the presence of the API Key
        if api_key is None:
            raise AuthenticationFailed("API Key header missing.")

        # Verify the API Key's value
        if api_key != settings.API_KEY:  # Assuming the valid API Key is stored in Django's settings
            raise AuthenticationFailed("Unauthorized: Incorrect API Key.")

        # Authentication successful, but no associated user (use a generic identifier)
        return ("AuthenticatedApiKeyUser", None)
