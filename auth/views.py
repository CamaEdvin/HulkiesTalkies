from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import UserSerializer
from django.views.generic import View
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.generic import TemplateView


class RegisterView(APIView):
    template_name = 'register.html'

    def get(self, request):
        # Render the register.html template
        return render(request, self.template_name)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
