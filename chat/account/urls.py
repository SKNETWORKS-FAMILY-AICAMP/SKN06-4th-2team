# account/urls.py
from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path("register", views.create, name="register"),
    path("login", views.user_login, name="login"),
    path("logout", views.user_logout, name="logout"),
    path("detail", views.user_detail, name="detail"),
    path('password_change', views.password_change, name='password_change'),
    path('update', views.user_update, name='update'),
    path('delete', views.user_delete, name="delete"),
    path('find_username', views.find_username, name='find_username'),
    path('find_password', views.find_password, name='find_password'),  # 이메일 입력
    path('reset-password/<uidb64>/<token>', views.password_reset_confirm, name='password_reset_confirm'),  # 링크 클릭
    path('reset-password/done', views.password_reset_complete, name='password_reset_complete'),  # 완료 페이지
]