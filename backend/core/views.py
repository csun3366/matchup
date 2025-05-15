from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
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
            return redirect('home')
        else:
            messages.success(request, ("帳號或密碼錯誤!"))
            return redirect('login')
    else:
        return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('home')


def register_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()       # 建立 User 並加密密碼
            login(request, user)     # 可選，自動登入
            return redirect('home')  # 或任何成功頁面
        else:
            # 加入欄位錯誤訊息到 messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

            # 或也可以加入非欄位錯誤
            for error in form.non_field_errors():
                messages.error(request, error)
            return redirect('register')
    else:
        return render(request, 'register.html')

def input(request):
    if request.method == "POST":
        pass
    else:
        return render(request, 'input.html')