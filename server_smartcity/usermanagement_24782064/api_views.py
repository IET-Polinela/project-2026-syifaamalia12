from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer
from drf_spectacular.utils import extend_schema

User = get_user_model()


@extend_schema(exclude=True)
class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = RegisterSerializer