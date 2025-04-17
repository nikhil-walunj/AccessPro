from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginView, name='login'),
    path('register/', views.registerView, name='register'),
    path('verify-otp/', views.verifyOTPView, name='verify_otp'),
    # path('resend-otp/', views.resendOTPView, name='resend_otp'),
    path('dashboard/', views.dashboardView, name='dashboard'),
    path('logout/', views.logoutView, name='logout'),
    path('forgotpass/',views.forgotpassword,name='forgotpassword'),
    path('resetpassword/',views.resetpassword,name='resetpassword'),
    path('verifyotp/',views.verifyotp,name='verifyotp'),
    path('edituser/<int:user_id>/', views.edituser, name='edituser'),
    path('deleteuser/<int:user_id>/', views.deleteuser, name='deleteuser'),
]