# account/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.forms import forms

## 확장 User 모델 
# - AbstractUser로 구현: 기본 User(username, password)에 필드들을 추가하는 방식
# - AbstractUser 상속. 필드들 정의(username, password빼고 정의)


class User(AbstractUser):
    # groups와 user_permissions 필드에 고유한 related_name 설정
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
    
    # 필드 추가
    name = models.CharField(max_length=255, blank=True, default="")
    email = models.EmailField(max_length=255, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)  
    def __str__(self):
        return f"username: {self.username}, name: {self.name}"
