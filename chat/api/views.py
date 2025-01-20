from django.contrib.auth.decorators import login_required  # ✅ 로그인한 사용자만 접근 가능
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
import json
import markdown2  # ✅ 마크다운을 HTML로 변환
from django.utils.safestring import mark_safe  # ✅ mark_safe 추가
from time import sleep
from .llm import chat, add_message_to_history

@login_required
def chat_view(request):
    """챗봇 메인 페이지"""
    raw_history = request.session.get("chatting_history", [])
    history = []

    for item in raw_history:
        if isinstance(item, list) and len(item) == 2:
            history.append((item[0], mark_safe(markdown2.markdown(item[1]))))  
        elif isinstance(item, dict):  
            human_msg = mark_safe(markdown2.markdown(item["message"]))
            ai_msg = mark_safe(markdown2.markdown(item["response"]))
            history.append(("human", human_msg))  # ✅ 수정: "name" 대신 "human"으로 일관성 유지
            history.append(("ai", ai_msg))

    print("🔍 변환된 history 구조:", history)  
    user_name = request.user.name if request.user.is_authenticated else "익명 사용자"

    if request.method == "POST":
        user_message = request.POST.get("message", "").strip()

        if user_message:
            last_ai_response = history[-1][1] if history and history[-1][0] == "ai" else None
            response = chat.send_message(user_message, history).strip()

            if response and response.lower() != "response" and response != last_ai_response:
                add_message_to_history(history, ("human", user_message))  # ✅ "name" -> "human"
                add_message_to_history(history, ("ai", response))
                request.session["chatting_history"] = history

        return redirect("api:chat")

    return render(request, "chat.html", {"history": history, "user_name": user_name})

@csrf_exempt
def chat_message_api(request):
    """비동기 요청을 처리하는 API"""
    if request.method == "POST":
        data = json.loads(request.body)  
        user_message = data.get("message", "").strip()
        history = request.session.get("chatting_history", []).copy()
        user_name = request.user.name if request.user.is_authenticated else "익명 사용자"

        if not user_message:
            return JsonResponse({"error": "Invalid request"}, status=400)

        response = chat.send_message(user_message, history).strip()
        response_html = mark_safe(markdown2.markdown(response))  

        if history and history[-1][0] == "ai" and history[-1][1] == response_html:
            return JsonResponse({"error": "Duplicate response"}, status=400)

        add_message_to_history(history, ("human", user_message))  # ✅ "name" -> "human"
        add_message_to_history(history, ("ai", response_html))
        request.session["chatting_history"] = history

        def generate_response():
            for char in response_html:
                yield char
                sleep(0.02)

        return StreamingHttpResponse(generate_response(), content_type="text/html")
