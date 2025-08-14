
from django.contrib import admin
from django.urls import path
from django.urls import include

from .views import RegisterView
urlpatterns = [
path('register/', RegisterView.as_view()),
]
