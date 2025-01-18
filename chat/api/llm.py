import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from cachetools import LRUCache
from time import sleep
from dotenv import load_dotenv
from textwrap import dedent
import traceback

load_dotenv()


class Chatting:
    """
    대화형 AI 채팅 클래스.
    GPT 모델을 사용하여 사용자와 대화를 수행하고, 대화 기록을 관리합니다.
    """
    def __init__(self, vector_store, cache_size=100, rate_limit=1):
        self.rate_limit = rate_limit  # API 호출 속도 제한 (초)
        self.cache = LRUCache(maxsize=cache_size)  # 검색 결과 캐싱

        # 모델과 벡터 스토어 설정
        self.model = ChatOpenAI(model="gpt-4o-mini")
        self.retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 20,
                "fetch_k": 200,
                "lambda_mult": 0.7,
            }
        )

        # 프롬프트 템플릿 설정 (초기화 시 한 번만 정의)
        self.prompt_template = dedent("""
        당신은 한국의 식당을 추천하고 정보를 제공하는 인공지능 비서입니다.
        반드시 아래 [context]에 제공된 정보만 사용해 답변하세요. 
        [context]에 없는 정보에 대해서는 "문맥에 없습니다"라고 답변하세요.

        참고:
        - '리본개수', '평점', '몇 개' 키워드가 포함된 질문은 [context]의 "리본개수" 항목을 확인해 답변하세요.
        - 리본개수는 평점과 동일한 의미를 가지므로 이를 바탕으로 답변을 작성하세요.
        - 모든 답변은 간결하고 명확하게 작성하세요.
        [context]
        {context}

        질문: {question}
        답변:
        """)

    def get_cached_relevant_documents(self, query):
        """
        검색 요청에 대해 캐싱 및 API 호출 속도 제한 적용.
        """
        if query in self.cache:
            return self.cache[query]
        try:
            sleep(self.rate_limit)  # API 호출 간 딜레이
            docs = self.retriever.invoke(query)
            context = "\n\n".join([doc.page_content for doc in docs])
            self.cache[query] = context
            return context
        except Exception as e:
            print(f"Error during document retrieval: {e}")
            traceback.print_exc()
            return "검색 결과를 가져오는 중 문제가 발생했습니다."

    def send_message(self, message, history=None):
        """
        사용자 메시지를 처리하고 AI 응답을 반환합니다.
        """
        try:
            # 검색된 context와 사용자 질문을 프롬프트에 삽입
            context = self.get_cached_relevant_documents(message)
            prompt = self.prompt_template.format(context=context, question=message)

            # 응답 생성
            response = self.model.invoke(prompt)

            # 응답을 텍스트로 변환
            response_text = str(response.content)  # 텍스트 추출

            # 대화 기록 업데이트
            if history is not None:
                add_message_to_history(history, {"message": message, "response": response_text})

            return response_text  # 텍스트만 반환
        except Exception as e:
            print(f"Error during chat response generation: {e}")
            traceback.print_exc()
            return "응답을 생성하는 중 문제가 발생했습니다. 다시 시도해주세요."


def add_message_to_history(history, message, max_history=20):
    """
    Message를 history에 추가하는 유틸리티 메서드.
    """
    while len(history) >= max_history:
        history.pop(0)
    history.append(message)


# 벡터 스토어 및 임베딩 모델 설정
COLLECTION_NAME = "bluer_db_openai"
PERSIST_DIRECTORY = "vector_store/chroma/bluer_db"
EMBEDDING_MODEL_NAME = 'text-embedding-3-small'

embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
vector_store = Chroma(
    embedding_function=embedding_model,
    collection_name=COLLECTION_NAME,
    persist_directory=PERSIST_DIRECTORY
)

# Chatting 클래스 초기화
chat = Chatting(vector_store=vector_store)
