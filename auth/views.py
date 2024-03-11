from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from django.shortcuts import redirect

class RegisterView(APIView):
    template_name = 'register.html'

    def get(self, request):
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
    

class LoginView(APIView):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username and password:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    refresh = RefreshToken.for_user(user)

                    
                    # Get the URL for the dashboard
                    dashboard_url = reverse('dashboard')
                
                    # Return a redirect response to the dashboard
                    return redirect(dashboard_url)
                else:
                    return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
