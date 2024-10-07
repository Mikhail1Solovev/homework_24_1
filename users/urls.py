from django.urls import path
from . import views
from .views import UserRegistrationView, ObtainTokenView

urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', ObtainTokenView.as_view(), name='token_obtain_pair'),
]
