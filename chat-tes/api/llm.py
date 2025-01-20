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
    def __init__(self, vector_store, cache_size=100, rate_limit=0.1):
        self.rate_limit = rate_limit  # API 호출 속도 제한 (초)
        self.cache = LRUCache(maxsize=cache_size)  # 검색 결과 캐싱
        # print(vector_store._collection.count() ) # vectory가 비어있는지 확인
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
    아래 [context]와 [history]에 제공된 정보만 사용하여 질문에 답변하세요.  
    [context]나 [history]에 없는 정보에 대해서는 반드시 **"문맥에 없습니다"**라고 답변하세요.  

    ---

    ### **[대화 규칙]**
    1. **제공된 정보만 사용**  
        - [context]나 [history]에 없는 정보는 절대 유추하지 마세요.
        - 없는 정보에 대해서는 **"문맥에 없습니다"**라고 답변하세요.

    2. **마크다운 형식으로 답변**  
        - **가게 이름**은 `**굵게 강조**`하세요.  
        - 세부 정보는 `- 항목별 리스트` 형식으로 정리하세요.  
        - 전화번호, 가격대, 위치 등의 정보는 `**강조**`하여 구분하세요.  
        - **리본개수(평점)는 항상 포함**하여 답변하세요.  

    3. **질문 유형에 따른 답변 지침**
        - **단일 검색 요청**: 키워드, 카테고리, 가격, 리본개수 등 특정 조건에 맞는 단일 식당 정보를 제공하세요.  
            - 예시 1: "리본개수가 2개인 식당은?"  
            - 예시 2: "리본개수가 두 개인 식당은?"  
            - 답변: "**리본개수가 2개인 식당은** 식당 A입니다."
        - **비교 요청**: 2개 이상의 식당 정보를 비교하여 명확히 제공하세요.  
            - 예시: "리본개수가 2개인 식당과 3개인 식당을 비교해주세요."  
            - 답변 형식:  
                - **식당 A**: 리본개수 2, 가격 **2만원**, 카테고리 **한식**  
                - **식당 B**: 리본개수 3, 가격 **3만원**, 카테고리 **프랑스 요리**  

    4. **이전 대화 연속성 유지**
        - 질문에 **"두 곳 중", "이 중에서", "가장 좋은 곳", "둘 다"** 등의 표현이 등장할 경우, [history]에서 **가장 최근에 등장한 두 개의 가게 이름**을 찾아서 [context]에서 해당 가게 정보를 검색한 후 답변하세요.
        - "리본개수"를 명확히 인식할 수 있도록 숫자(1, 2, 3)뿐만 아니라 한글 표현(한 개, 두 개, 세 개)도 동일하게 처리하세요.

    ---

    ### **[이전 대화]**
    {history}

    ### **[현재 참고 가능한 정보]**
    {context}

    ---

    ### **질문**: {question}  
    ### **답변**:
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
            context = self.get_cached_relevant_documents(message)

            history_text = ""
            for h in history:
                if h[0] == "human":
                    history_text += f"\n사용자: {h[1]}"
                else:
                    history_text += f"\nAI: {h[1]}"

            prompt = self.prompt_template.format(history=history_text, context=context, question=message)

            response = self.model.invoke(prompt)

            response_text = str(response.content)  # 텍스트 변환

            return response_text  # 🔹 history 저장은 API 함수에서만!
        except Exception as e:
            print(f"Error during chat response generation: {e}")
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
