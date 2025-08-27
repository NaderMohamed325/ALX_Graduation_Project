

from django.urls import path


from .views import (
    DeleteProfileView,
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
    UpdateProfileView,
    TaskListCreateView,
    TaskDetailView,
    TaskCompleteView,
    TaskIncompleteView,
)
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('profile/delete/', DeleteProfileView.as_view(), name='delete_profile'),
    path('tasks/', TaskListCreateView.as_view(), name='task_list_create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/complete/', TaskCompleteView.as_view(), name='task_complete'),
    path('tasks/<int:pk>/incomplete/', TaskIncompleteView.as_view(), name='task_incomplete'),
]
