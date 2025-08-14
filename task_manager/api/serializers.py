from rest_framework.serializers import ModelSerializer

from .models import Task
from django.contrib.auth.models import User

class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']