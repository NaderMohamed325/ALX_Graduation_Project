
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"user": UserSerializer(user).data}, status=201)
        return Response(serializer.errors, status=400)
