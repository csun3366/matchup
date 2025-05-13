from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Member

def home(request):
    return render(request, 'home.html')

def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("You have been logged in!"))
            return redirect('home')
        else:
            messages.success(request, ("帳號或密碼錯誤!"))
            return redirect('login')
    else:
        return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out!"))
    return redirect('home')


def register_user(request):
    pass

def input(request):
    if request.method == "POST":
        pass
    else:
        return render(request, 'input.html')