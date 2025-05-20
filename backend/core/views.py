from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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

@login_required
def input(request):
    if request.method == "POST":
        username = request.user.username
        self_ig = request.POST.get("self_ig")
        other_ig = request.POST.get("other_ig")
        print("username: " + str(request.user.username))
        print("self_ig: " + str(self_ig))
        print("other_ig: " + str(other_ig))
        # 步驟1: 先處理這個username的舊資料
        print("[INFO] Update old matched mermber ... ")
        if Member.objects.filter(username=username).exists():
            member = Member.objects.get(username=username)
            if member.is_matched:
                old_self_ig = member.self_ig
                old_other_ig = member.other_ig
                if Member.objects.filter(self_ig=old_other_ig, other_ig=old_self_ig).exclude(username=username).exists():
                    old_match_members = Member.objects.filter(self_ig=old_other_ig, other_ig=old_self_ig).exclude(username=username)
                    for m in old_match_members:
                        m.is_matched = False
                        m.save()

        # 步驟2: 再處理這個username的新資料
        print("[INFO] Update new mermber ... ")
        is_matched = False
        if Member.objects.exclude(username=username).filter(self_ig=other_ig, other_ig=self_ig).exists():
            # 如果配對成功 更新對方is_matched
            print("配對成功!!!")
            match_members = Member.objects.exclude(username=username).filter(self_ig=other_ig, other_ig=self_ig)
            is_matched = True
            for m in match_members:
                m.is_matched = is_matched
                m.save()
        else:
            print("配對失敗!!!")
            is_matched = False

        # 步驟3: 最後更新或創建這個username的物件
        member, created = Member.objects.update_or_create(
            username=username,
            defaults={
                'self_ig': self_ig,
                'other_ig': other_ig,
                'is_matched' : is_matched
            }
        )
        return render(request, 'status.html', {
            'has_input' : True,
            'is_matched': is_matched,
            'self_ig' : self_ig,
            'other_ig' : other_ig
        })
    else:
        return render(request, 'input.html')

@login_required
def status(request):
    username = request.user.username
    if Member.objects.filter(username=username).exists():
        member = Member.objects.get(username=username)
        return render(request, 'status.html', {
            'has_input' : True,
            'is_matched': member.is_matched,
            'self_ig' : member.self_ig,
            'other_ig' : member.other_ig
        })
    else:
        return render(request, 'status.html', {
            'has_input' : False,
            'is_matched': False,
            'self_ig' : "",
            'other_ig' : ""
        })