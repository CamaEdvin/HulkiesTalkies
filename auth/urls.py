from django.urls import path
from .views import RegisterView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user_registration'),
    path('login/', LoginView.as_view(), name='login'),
]
