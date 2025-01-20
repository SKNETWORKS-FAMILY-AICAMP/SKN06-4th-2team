from django.urls import path
from .views import chat_message_api, chat_view

app_name = 'api'

urlpatterns = [
    path('chat/', chat_view, name='chat'),
    path('chat/api/', chat_message_api, name='chat_message_api'),  # ✅ 비동기 API 추가
]
