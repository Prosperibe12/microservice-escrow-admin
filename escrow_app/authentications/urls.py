from django.urls import path 
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from escrow_app.authentications import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password_reset_request/', views.PasswordResetRequest.as_view(), name='password_reset_request'),
    path('password_reset_confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', views.PasswordChange.as_view(), name='password_reset_complete'),
    path('logout/', views.LogoutView.as_view(), name='logout')
]