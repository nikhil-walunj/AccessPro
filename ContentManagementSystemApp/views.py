from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterationForm, LoginForm
from .models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings

# Register view
import random
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse

# Step 1: Register view (store in session, send OTP) 
def registerView(request):
    if request.method == 'POST':
        form = UserRegisterationForm(request.POST) 
        if form.is_valid():
            # Save data in session temporarily
            request.session['user_data'] = form.cleaned_data 
            otp = random.randint(100000, 999999)
            request.session['otp'] = str(otp)

            # Send OTP via email
            send_mail(
                subject='Your OTP for Registration',
                message=f'Your OTP is: {otp}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[form.cleaned_data['email']],
                fail_silently=False,
            )
            return redirect('verify_otp')  # Redirect to OTP page
    else:
        form = UserRegisterationForm()
    return render(request, 'register.html', {'form': form})  

# Step 2: OTP verification view 
def verifyOTPView(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        print("Entered OTP:", entered_otp)
        print("Session OTP:", request.session.get('otp'))
        if entered_otp == request.session.get('otp'):
            data = request.session.get('user_data')
            if data:
                user = User(
                    email=data['email'],
                    full_name=data['full_name'],
                    role=data['role']
                )
                user.set_password(data['password1'])
                user.save()
                messages.success(request, "Account created successfully!")
                # Clear session data
                request.session.flush()
                return redirect('login')
        messages.error(request, "Invalid OTP. Please try again.")
    return render(request, 'verify_otp.html')

import datetime
# Login view
def loginView(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                request.session['last_activity']=str(datetime.datetime.now())
                request.session.set_expiry(180)
                response=redirect('dashboard')
                request.session['email']=email
                response.set_cookie('Emailis',email)
                response.set_cookie('time',datetime.datetime.now())
                return response
            else:
                return redirect('login')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form}) 

# Dashboard view (placeholder) 
@login_required
def dashboardView(request): 
    users = User.objects.filter(is_admin=False, is_superuser=False) 
    request.session['last_activity']=str(datetime.datetime.now())
    request.session.set_expiry(180)
    request.session['email'] = request.user.email
    return render(request, 'dashboard.html', {'users': users})

def edituser(request, user_id):
    user_obj = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = UserRegisterationForm(request.POST, instance=user_obj,is_update=True)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('dashboard')
    else:
        form = UserRegisterationForm(instance=user_obj,is_update=True)
    return render(request, 'edituser.html', {'form': form})

def deleteuser(request, user_id):
    user_obj = User.objects.get(id=user_id)
    if request.user.role == 'Admin':
        user_obj.delete()
        messages.success(request, 'User deleted successfully!')
    return redirect('dashboard')

# Logout view
def logoutView(request):
    logout(request)
    return redirect('login')

import random
from django.contrib import messages 
from django.core.mail import send_mail 

def forgotpassword(request):
    if request.method == 'POST':
        email= request.POST.get('email')

        users=User.objects.filter(email=email)
        if users.exists():
            user=users.first()
            otp=random.randint(100000,999999)
            request.session['reset_otp']=otp
            request.session['reset_email']=email
            request.session['otp_purpose']="login"

            subject = "Your Password Reset OTP"  
            message = f"Dear {user.full_name},\n\nYour OTP for passsword reset is: {otp}\n\nPlease enter proper OTP to reset password and It will be valid for 5 minute.\n\nBest Regards,\nYour Support Team."

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return redirect('verifyotp')
        
        else:
            messages.error(request,"Email not found! Please enter a registered email.")
            return render(request,'forgotpassword.html')
    
    return render(request,'forgotpassword.html')
        
def verifyotp(request):
    if request.method == 'POST':
        enterotp=request.POST.get('otp')
        storedotp=request.session.get('reset_otp')
        otppurpose=request.session.get('otp_purpose','')

        if storedotp and enterotp == str(storedotp):
            if otppurpose == 'login':
                return redirect('resetpassword')
            elif otppurpose == 'payment':
                return redirect('paypalsuccess')
            else:
                return redirect('home')
            
        else:
            messages.error(request,'Invalid OTP! Please Try Again.')  

    return render(request,'verifyotp.html')  
        
def resetpassword(request):
    if request.method == 'POST':
        newpassword=request.POST['new_password']
        confirmpassword=request.POST['confirm_password']
        email=request.session.get('reset_email')

        if newpassword == confirmpassword:
            try:
                user = User.objects.get(email=email)
                user.set_password(newpassword)
                user.save()

                # Clear session data: 
                del request.session['reset_otp']
                del request.session['reset_email']

                messages.success(request,"Password reset successfull! You can login now!")
                return redirect('login')
            
            except User.DoesNotExist:
                messages.error(request,"Something went wrong!! Try Again!!")
                return redirect('forgotpassword')
        else:
            messages.error(request,'Password do not match !! Try Again!!')
            return render(request,'resetpassword.html')
        
    return render(request,'resetpassword.html')