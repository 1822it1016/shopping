import uuid
from django.test import TestCase
from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework.test import APIRequestFactory
from .views import SignupView, LoginView


class UserAuthenticationTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('usermanagement.serializers.UserSerializer.save')
    def test_signup_view(self, mock_save):
        # Arrange
        mock_save.return_value = MagicMock(id=uuid.uuid4(), name="Test User", email="test@example.com")
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
        url = '/signup'  # Use the direct URL path
        request = self.factory.post(url, data, format='json')

        # Act
        view = SignupView.as_view()  # Instantiate the view
        response = view(request)

        # Assert
        mock_save.assert_called_once()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Test User")
        self.assertEqual(response.data["email"], "test@example.com")

    @patch('usermanagement.models.User.objects.filter')
    def test_login_view_success(self, mock_filter):
        # Arrange
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        mock_filter.return_value.first.return_value = mock_user
        mock_user.id = uuid.uuid4()
        data = {
            "email": "test@example.com",
            "password": "password123"
        }
        url = '/login'
        request = self.factory.post(url, data, format='json')

        view = LoginView.as_view()
        response = view(request)

        mock_filter.assert_called_once_with(email="test@example.com")
        mock_user.check_password.assert_called_once_with("password123")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["msg"], "Login Done")

    @patch('usermanagement.models.User.objects.filter')
    def test_login_view_invalid_credentials(self, mock_filter):
        # Arrange
        mock_filter.return_value.first.return_value = None  # No user found
        data = {
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
        url = '/login'
        request = self.factory.post(url, data, format='json')

        view = LoginView.as_view()
        response = view(request)

        mock_filter.assert_called_once_with(email="wrong@example.com")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid credentials")

    @patch('usermanagement.models.User.objects.filter')
    def test_login_view_wrong_password(self, mock_filter):
        # Arrange
        mock_user = MagicMock()
        mock_user.check_password.return_value = False
        mock_filter.return_value.first.return_value = mock_user
        data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        url = '/login'
        request = self.factory.post(url, data, format='json')

        view = LoginView.as_view()
        response = view(request)

        mock_filter.assert_called_once_with(email="test@example.com")
        mock_user.check_password.assert_called_once_with("wrongpassword")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid credentials")
