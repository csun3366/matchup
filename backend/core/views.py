from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_datetime
from django.utils.timesince import timesince
from django.utils.timezone import now
from .models import Member

def format_notification_time(timestamp):
    if not timestamp:
        return ''

    now_time = now()
    diff = now_time - timestamp

    if diff < timedelta(minutes=5):
        return '剛剛'
    elif diff < timedelta(hours=24):
        hours = int(diff.total_seconds() // 3600)
        minutes = int((diff.total_seconds() % 3600) // 60)
        if hours >= 1:
            return f"{hours} 小時前"
        else:
            return f"{minutes} 分鐘前"
    else:
        return timestamp.strftime('%Y/%m/%d')

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
                m.add_notification("與" + str(self_ig) + "成功配對了！")
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
        if is_matched:
            member.add_notification("與" + str(other_ig) + "成功配對了！")
            member.save()

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

@login_required
def unread_notification_count(request):
    print(request.user.username)
    if Member.objects.filter(username=request.user.username).exists():
        member = Member.objects.get(username=request.user.username)
        count = member.unread_count()
        return JsonResponse({'count': count})
    else:
        return JsonResponse({'count': 0})

@login_required
def notifications(request):
    if Member.objects.filter(username=request.user.username).exists():
        member = Member.objects.get(username=request.user.username)
        messages = []
        for msg in member.notifications:
            print(msg['text'])
        member.mark_all_as_read()
        member.save()
        for n in member.notifications:
            timestamp = parse_datetime(n['timestamp']) if n.get('timestamp') else None
            messages.append({
                'text': n['text'],
                'time': format_notification_time(timestamp),
                'timestamp': timestamp  # 加入排序用
            })
            # 依照 timestamp 排序，None 的會排在最後
            messages.sort(key=lambda x: x['timestamp'] or parse_datetime('1900-01-01T00:00:00'), reverse=True)
        return JsonResponse({'notifications': messages})
    else:
        return JsonResponse({'notifications': []})