# account/forms.py
## Form/ModelForm 클래스들을 정의
##  - 입력 폼당 하나씩 생성. 보통 등록폼, 수정폼 두가지를 만든다.

# Form
# class MyForm(forms.Form)

# ModelForm
# class MyForm(forms.ModelForm)

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,  # 사용자 등록/생성 폼
    UserChangeForm     # 사용자  정보 수정 폼. 둘다 ModelForm
)
from .models import User
from django.contrib.auth.forms import AuthenticationForm
# 사용자 가입(등록)시 사용할 Form을 구성 
#                  - UserCreationForm 상속(username, pwd1, pwd2) + 추가항목
class CustomUserCreationForm(UserCreationForm):
    
    class Meta:
        model = User  # User model의 field를 이용해서 form field를 구성
        # fields = "__all__" # 모델의 모든 field들을 사용해서 form field구성
        fields = ["name", "username", "password1", "password2", "birthday", "email"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "size", "placeholder": "사용자 이름"}),
            "username": forms.TextInput(attrs={"class": "size", "placeholder": "아이디"}),
            "password1": forms.PasswordInput(attrs={"class": "size", "placeholder": "비밀번호"}),
            "password2": forms.PasswordInput(attrs={"class": "size", "placeholder": "비밀번호 확인"}),
            "birthday": forms.DateInput(attrs={"class": "size", "type": "date", "placeholder": "생년월일"}),
            "email": forms.EmailInput(attrs={"class": "size", "placeholder": "이메일"}),
        }
        
    # ModelForm에서 기본 검증을 처리
    ## name: required
    ## email: required, email형식 체크
    ## birthday: 날짜 형식 체크
    
    # 사용자 정의 검증 (Form을 만들경우에는 Form에 작성. )
    # - clean(), clean_검증필드명()
    ## name은 두 글자 이상 입력
    def clean_name(self):
        # self.cleaned_data: dict - 기본 검증을 통과한 요청파라미터들.
        name = self.cleaned_data['name']
        if not name:    # name이 None일 경우 처리
            raise forms.ValidationError("Name cannot be empty.")
        if len(name) < 2 :
            raise forms.ValidationError("이름은 2글자 이상 입력하세요.")
        return name # 리턴해주는 값이 View가 사용하는 값.
    
# 회원정보 수정 Form 정의 - UserChangeForm(username) 상속
class CustomUserChangeForm(UserChangeForm):

    password = None  # password변경 페이지 링크가 안나오도록 하기.

    class Meta:
        model = User
        fields = ['name', 'email', 'birthday']
        widgets = {
            'birthday':forms.DateInput(attrs={'type':'date'})
        }
    # name Field 검증 메소드
    def clean_name(self):
        # self.cleaned_data: dict - 기본 검증을 통과한 요청파라미터들.
        name = self.cleaned_data['name']
        if len(name) < 2 :
            raise forms.ValidationError("이름은 2글자 이상 입력하세요.")
        return name # 리턴해주는 값이 View가 사용하는 값.
        
# Django의 기본 로그인 폼(AuthenticationForm)을 커스터마이징하는 역할
class CustomAuthenticationForm(AuthenticationForm): 
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input-field", "placeholder": "아이디"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input-field", "placeholder": "비밀번호"})
    )