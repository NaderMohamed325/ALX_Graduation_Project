from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            response = Response({
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)

            # Store token in HttpOnly cookie
            response.set_cookie(
                key="auth_token",
                value=token.key,
                httponly=True,
                secure=False,     # set to True in production
                samesite="Lax"
            )
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        user = None
        if username:
            user = authenticate(username=username, password=password)
        elif email:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)

            response = Response({
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)

            # Store token in HttpOnly cookie
            response.set_cookie(
                key="auth_token",
                value=token.key,
                httponly=True,
                secure=False,     # set to True in production
                samesite="Lax"
            )
            return response

        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenAuthentication(TokenAuthentication):
    """
    Custom authentication to read the token from HttpOnly cookies.
    """
    def authenticate(self, request):
        token = request.COOKIES.get("auth_token")
        if not token:
            return None
        return self.authenticate_credentials(token)


class ProfileView(APIView):
    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "user": UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)
