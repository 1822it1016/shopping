import jwt
from django.conf import settings
from django.http import JsonResponse
from .models import User
from rest_framework import status


class JWTAuthMiddleware:
    def __init__(self, get_response):
        """
        Initializes the middleware with the given get_response function.

        :param get_response: The next middleware or view in the request chain.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Middleware for validating JWT tokens.

        :param request: The HTTP request object.
        :return: The HTTP response object.
        """
        # Skip authentication for specific paths: login, signup, and any admin-related paths.
        if request.path in ['/user-management/login', '/user-management/signup'] or 'admin' in request.path:
            # If the request is for login, signup, or admin paths, proceed without JWT validation.
            return self.get_response(request)

        # Get the Authorization header from the request.
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                # Extract the token from the Authorization header (expected format: "Bearer <token>").
                token = auth_header.split(' ')[1]

                # Decode the JWT token using the secret key from settings.
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

                # Retrieve the user associated with the ID in the token payload.
                user = User.objects.get(id=payload['user_id'])
                if not user:
                    return JsonResponse({"msg": "Invalid token provided user not present in Database"}, status=status.HTTP_400_BAD_REQUEST)
            # Attach the user to the request object for use in views.
            except (jwt.ExpiredSignatureError, jwt.DecodeError):
                # Return a 401 error if the token is expired or invalid.
                return JsonResponse({"detail": "Invalid token provided"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                # Return a 401 error if the user associated with the token does not exist.
                return JsonResponse({"detail": "Invalid token provided"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Return a 401 error if no Authorization header is provided.
            return JsonResponse({"detail": "Token not provided, please provide token in header"},
                                status=status.HTTP_401_UNAUTHORIZED)

        # Proceed to the next middleware or view if the token is valid.
        response = self.get_response(request)
        return response
