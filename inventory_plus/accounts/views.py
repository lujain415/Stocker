from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from accounts.forms import SignUpForm
from inventory.utils import notify_manager  # لو utils في inventory

def register_user_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # مهم عشان يقدر يدخل مباشرة
            user.save()
            
            notify_manager(
                subject='مستخدم جديد',
                message=f'تم تسجيل مستخدم جديد: {user.username}'
            )

            messages.success(request, "تم إنشاء الحساب بنجاح", "alert-success")
            return redirect("accounts:sign_in")
    else:
        form = SignUpForm()
    
    return render(request, "accounts/signup.html", {"form": form})



'''def sign_up(request: HttpRequest):

    if request.method == "POST":
        try:
            new_user = User.objects.create_user(
                username=request.POST["username"],
                password=request.POST["password"],
                email=request.POST["email"],
                first_name=request.POST["first_name"],
                last_name=request.POST["last_name"]
            )
            new_user.save()
            messages.success(request, "Registered User Successfully", "alert-success")
            return redirect("accounts:sign_in")
        except Exception as e:
            print(e)

    return render(request, "accounts/signup.html", {})

'''
def sign_in(request: HttpRequest):

    if request.method == "POST":
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user:
            login(request, user)
            messages.success(request, "Logged in successfully", "alert-success")
            return redirect(request.GET.get("next", "/"))
        else:
            messages.error(request, "Please try again. Your credentials are wrong", "alert-danger")

    return render(request, "accounts/signin.html")


def log_out(request: HttpRequest):
    logout(request)
    messages.success(request, "Logged out successfully", "alert-warning")
    return redirect(request.GET.get("next", "/"))

