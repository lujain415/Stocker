from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.forms import SignUpForm


def register_user_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inventory:all_products_view')
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


def sign_in(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('inventory:all_products_view')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/signin.html')


def log_out(request: HttpRequest):
    logout(request)
    messages.success(request, "Logged out successfully", "alert-warning")
    return redirect(request.GET.get("next", "/"))


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        request.user.username = username
        request.user.email = email
        request.user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("accounts:profile_view")

    return render(request, "accounts/edit_profile.html")
