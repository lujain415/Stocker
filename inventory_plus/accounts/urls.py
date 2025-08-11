from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    
    path('signin/', views.sign_in, name="sign_in"),
    path('logout/', views.log_out, name="log_out"),
    path("signup/", views.register_user_view, name="sign_up"),
    path("profile/", views.profile_view, name="profile_view"),
    path("edit/", views.edit_profile_view, name="edit_profile"),
]
