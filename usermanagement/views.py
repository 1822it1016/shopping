from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.conf import settings
from .models import User
from .serializers import UserLoginSerializer, UserSerializer


class SignupView(APIView):
    def post(self, request):
        """
        Handles POST requests for user signup.

        This method creates a new user with the provided data if valid.

        :param request: The HTTP request object containing user data.
        :return: A Response indicating success or failure.
        """
        # Deserialize the incoming user data.
        serializer = UserSerializer(data=request.data)

        # Validate and save the user if the data is valid.
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Return validation errors if the data is invalid.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        """
        Handles POST requests for user login.

        This method authenticates a user using their email and password, and generates a JWT token on successful login.

        :param request: The HTTP request object containing login credentials.
        :return: A Response containing the JWT token or an error message.
        """
        # Deserialize the incoming login data.
        serializer = UserLoginSerializer(data=request.data)

        # Validate the login data.
        if serializer.is_valid():
            # Retrieve the user by email.
            user = User.objects.filter(email=request.data["email"]).first()

            # Check if the user exists and the password is correct.
            if user is None or not user.check_password(request.data["password"]):
                # Return a 401 error if the credentials are invalid.
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate a JWT token with the user's ID.
            token = jwt.encode({"user_id": str(user.id)}, settings.SECRET_KEY, algorithm="HS256")

            # Return the JWT token and a success message.
            return Response({"token": token, "msg": "Login Done"}, status=status.HTTP_200_OK)

        # Return validation errors if the login data is invalid.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
