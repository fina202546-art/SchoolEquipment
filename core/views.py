from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import User, Equipment, BorrowRequest
from .forms import EquipmentForm, BorrowForm  # BorrowForm をインポートしていることを確認

# --- 静的ページ ---
def home_view(request):
    return render(request, 'home.html')

def contact_view(request):
    return render(request, 'contact.html')

def rules_view(request):
    return render(request, 'rules.html')

# --- メインダッシュボード ---
@login_required
def dashboard(request):
    if request.user.role == 'admin':
        items = Equipment.objects.all()
        requests = BorrowRequest.objects.all().order_by('-date_requested')
        return render(request, 'admin_dash.html', {'items': items, 'requests': requests})
    else:
        # 学生：参考用としてすべての備品（貸出中・故障含む）を表示
        search_query = request.GET.get('search', '')
        if search_query:
            items = Equipment.objects.filter(name__icontains=search_query)
        else:
            items = Equipment.objects.all()
        return render(request, 'student_dash.html', {'items': items})

# --- 2段階登録（PHAP方式） ---
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        request.session['reg_data'] = {
            'username': username,
            'email': email,
            'password': password,
            'role': role
        }

        if role == 'admin':
            return redirect('security_question')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='student'
            )
            login(request, user)
            return redirect('dashboard')
    return render(request, 'register.html')

def security_question_view(request):
    reg_data = request.session.get('reg_data')
    if not reg_data:
        return redirect('register')

    error = None
    if request.method == 'POST':
        answer = request.POST.get('answer', '').strip().upper()
        if answer == "PHAP":
            user = User.objects.create_user(
                username=reg_data['username'],
                email=reg_data['email'],
                password=reg_data['password'],
                role='admin'
            )
            login(request, user)
            del request.session['reg_data']
            return redirect('dashboard')
        else:
            error = "回答が正しくありません。管理者として登録することはできません。"

    return render(request, 'security_question.html', {'error': error})

# --- 備品管理（CRUD） ---
@login_required
def add_equipment(request):
    if request.user.role != 'admin':
        return redirect('dashboard')

    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES)  # データと画像を処理
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        else:
            print(form.errors)
    else:
        form = EquipmentForm()

    return render(request, 'form.html', {'form': form, 'title': '備品を登録 (Thêm thiết bị)'})

@login_required
def update_equipment(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    if request.user.role != 'admin':
        return redirect('dashboard')

    if request.method == 'POST':
        # 重要：request.FILES と instance=item が必須
        form = EquipmentForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EquipmentForm(instance=item)

    return render(request, 'form.html', {'form': form, 'title': '備品情報を更新 (Cập nhật)'})

@login_required
def delete_equipment(request, pk):
    if request.user.role == 'admin':
        get_object_or_404(Equipment, pk=pk).delete()
    return redirect('dashboard')

# --- 貸出 / 返却管理 ---
@login_required
def borrow_item(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)

    if request.method == 'POST':
        form = BorrowForm(request.POST)
        if form.is_valid():
            BorrowRequest.objects.create(
                equipment=equipment,
                student=request.user,
                reason=form.cleaned_data['reason'],
                status='pending'
            )
            equipment.status = 'borrowed'  # 承認待ちのため一時ロック
            equipment.save()
            return redirect('dashboard')
    else:
        form = BorrowForm()

    return render(request, 'borrow_confirm.html', {'form': form, 'equipment': equipment})

@login_required
def approve_request(request, pk):
    if request.user.role == 'admin':
        req = get_object_or_404(BorrowRequest, pk=pk)
        req.status = 'approved'
        req.save()

        # 備品を正式に貸出状態へ
        req.equipment.status = 'borrowed'
        req.equipment.save()

    return redirect('dashboard')

@login_required
def reject_request(request, pk):
    if request.user.role == 'admin':
        req = get_object_or_404(BorrowRequest, pk=pk)
        req.status = 'rejected'
        req.save()

        # 備品を利用可能状態へ戻す
        req.equipment.status = 'available'
        req.equipment.save()

    return redirect('dashboard')

@login_required
def return_item(request, pk):
    if request.user.role == 'admin':
        borrow_req = get_object_or_404(BorrowRequest, pk=pk)
        borrow_req.status = 'returned'
        borrow_req.save()

        # 重要：備品を「利用可能」に戻す
        equipment = borrow_req.equipment
        equipment.status = 'available'
        equipment.save()

    return redirect('dashboard')

@login_required
def borrow_history(request):
    if request.user.role == 'admin':
        history = BorrowRequest.objects.all().order_by('-date_requested')
    else:
        history = BorrowRequest.objects.filter(student=request.user).order_by('-date_requested')

    return render(request, 'history.html', {'history': history})
