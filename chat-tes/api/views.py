from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
import json
import markdown2  # ✅ 마크다운을 HTML로 변환
from django.utils.safestring import mark_safe  # ✅ mark_safe 추가
from time import sleep
from .llm import chat, add_message_to_history
# def chat_message(request, message):
#     """
#     대화를 수행하는 API 엔드포인트.
#     path parameter로 사용자의 메시지를 받아서 AI의 응답을 반환한다.
#     session을 이용해 대화 기록을 관리한다.
#     """
#     print("==========", chat)
#     # session에서 대화내역(history)를 불러오기. (없으면-처음시작 빈 배열반환.)
#     history = request.session.get("chatting_history", [])

#     # llm에게 메세지 전송
#     response = chat.send_message(message, history)

#     # history에 message, response을 저장. (max_length가 넘으면 오래된 순으로 메세지 삭제)
#     add_message_to_history(history, ("human", message))
#     add_message_to_history(history, ("ai", response))

#     # session에 변경된 대화내역(history) 업데이트.
#     request.session["chatting_history"] = history

#     # JsonResponse(dict): HttpResponse 타입
#     # dict를 JSON 응답으로 만들어서 응답.
#     return JsonResponse({'response': response})


def chat_view(request):
    raw_history = request.session.get("chatting_history", [])
    history = []
    for item in raw_history:
        if isinstance(item, list) and len(item) == 2:  # ✅ 기존 리스트 기반 튜플 데이터 변환
            history.append((item[0], mark_safe(markdown2.markdown(item[1]))))  # ✅ 불러올 때도 HTML 변환
        elif isinstance(item, dict):  # ✅ 딕셔너리 데이터 변환
            human_msg = mark_safe(markdown2.markdown(item["message"]))
            ai_msg = mark_safe(markdown2.markdown(item["response"]))
            history.append(("human", human_msg))
            history.append(("ai", ai_msg))

    print("🔍 변환된 history 구조:", history)  # ✅ 디버깅용 로그 추가
    name = request.user.name if request.user.is_authenticated else "익명 사용자"

    if request.method == "POST":
        user_message = request.POST.get("message", "").strip()

        if user_message:
            # ✅ AI 응답이 이미 저장된 경우 중복 추가 방지
            last_ai_response = history[-1][1] if history and history[-1][0] == "ai" else None
            response = chat.send_message(user_message, history).strip()

            if response and response.lower() != "response" and response != last_ai_response:
                add_message_to_history(history, ("human", user_message))
                add_message_to_history(history, ("ai", response))
                request.session["chatting_history"] = history

        return redirect("api:chat")  # ✅ POST 요청 후 리다이렉트 (새로고침 문제 해결)

    return render(request, "chat.html", {"history": history, "name": name})


@csrf_exempt
def chat_message_api(request):
    if request.method == "POST":
        data = json.loads(request.body)  
        user_message = data.get("message", "").strip()
        history = request.session.get("chatting_history", [])

        if not user_message:
            return JsonResponse({"error": "Invalid request"}, status=400)

        # ✅ AI 응답 생성
        response = chat.send_message(user_message, history).strip()
        response_html = mark_safe(markdown2.markdown(response))  # ✅ 마크다운 변환

        # ✅ 중복 방지: 세션의 마지막 메시지와 비교
        if history and history[-1][0] == "ai" and history[-1][1] == response_html:
            return JsonResponse({"error": "Duplicate response"}, status=400)

        # ✅ 중복 저장 방지: 이제 여기서만 history에 추가
        add_message_to_history(history, ("human", user_message))
        add_message_to_history(history, ("ai", response_html))
        request.session["chatting_history"] = history

        def generate_response():
            for char in response_html:
                yield char
                sleep(0.02)

        return StreamingHttpResponse(generate_response(), content_type="text/html")

