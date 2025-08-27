from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import UserSerializer, TaskSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.conf import settings
from django.utils import timezone
from .models import Task
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
import datetime


class AuthRateThrottle(AnonRateThrottle):
    """
    Throttling for auth endpoints to prevent brute force attacks
    """
    rate = '5/min'


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class RegisterView(APIView):
    throttle_classes = [AuthRateThrottle]
    
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
    throttle_classes = [AuthRateThrottle]
    
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
                secure=not settings.DEBUG,  # True in production, False in dev
                samesite="Strict"
            )
            return response

        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Delete the token to force re-login
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        
        # Clear the auth cookie
        response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie("auth_token")
        
        return response


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


class UpdateProfileView(APIView):
    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DeleteProfileView(APIView):
    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskListCreateView(APIView):
    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        # Get tasks for the current user
        qs = Task.objects.filter(user=request.user)
        
        # Filter by completion status
        completed = request.query_params.get('completed')
        if completed is not None:
            if completed.lower() == 'true':
                qs = qs.filter(completed=True)
            elif completed.lower() == 'false':
                qs = qs.filter(completed=False)
                
        # Search by title/description
        search = request.query_params.get('search')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        
        # Ordering
        ordering = request.query_params.get('ordering')
        if ordering:
            if ordering in ['created_at', '-created_at', 'due_date', '-due_date', 'title', '-title']:
                qs = qs.order_by(ordering)
            
        # Paginate results    
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)
        serializer = TaskSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save(user=request.user)
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Task, pk=pk, user=user)

    def get(self, request, pk):
        task = self.get_object(pk, request.user)
        return Response(TaskSerializer(task).data)

    def put(self, request, pk):
        task = self.get_object(pk, request.user)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = self.get_object(pk, request.user)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskCompleteView(APIView):
    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.completed = True
        task.save()
        return Response(TaskSerializer(task).data)


class TaskIncompleteView(APIView):
    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.completed = False
        task.save()
        return Response(TaskSerializer(task).data)