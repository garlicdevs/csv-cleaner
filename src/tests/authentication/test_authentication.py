from django.test import TestCase, RequestFactory
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from authentication.authentications import ApiKeyAuthentication


class CustomApiKeyAuthTests(TestCase):
    def setUp(self):
        # Initialize the RequestFactory and the authentication class
        self.factory = RequestFactory()
        self.authenticator = ApiKeyAuthentication()

    def test_authentication_success(self):
        """Test that the authentication succeeds with the correct API key."""
        request = self.factory.get("/test", HTTP_X_API_KEY=settings.API_KEY)
        user_auth_tuple = self.authenticator.authenticate(request)
        self.assertIsNotNone(user_auth_tuple)
        self.assertEqual(user_auth_tuple[0], "AuthenticatedApiKeyUser")

    def test_authentication_failure_missing_header(self):
        """Test that the authentication fails if the API key header is missing."""
        request = self.factory.get("/test")
        with self.assertRaises(AuthenticationFailed):
            self.authenticator.authenticate(request)

    def test_authentication_failure_invalid_header(self):
        """Test that the authentication fails if the API key is incorrect."""
        request = self.factory.get("/test", HTTP_X_API_KEY="invalid")
        with self.assertRaises(AuthenticationFailed):
            self.authenticator.authenticate(request)

