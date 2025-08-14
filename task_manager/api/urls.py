

from django.urls import path


from .views import DeleteProfileView, LoginView, ProfileView, RegisterView, UpdateProfileView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('profile/delete/', DeleteProfileView.as_view(), name='delete_profile'),    
]
