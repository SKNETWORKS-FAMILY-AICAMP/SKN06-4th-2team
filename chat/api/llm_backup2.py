import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate, ChatMessagePromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from langchain_community.tools import TavilySearchResults
from langchain_core.documents import Document

from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from ragas import EvaluationDataset, RunConfig, evaluate
from ragas.metrics import LLMContextRecall, Faithfulness, LLMContextPrecisionWithReference, AnswerRelevancy

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper


from textwrap import dedent
from operator import itemgetter

from dotenv import load_dotenv
load_dotenv()

import traceback

########################################################
# vector_db에서 데이터 불러오기
########################################################

COLLECTION_NAME = "bluer_db_openai"
PERSIST_DIRECTORY = "../vector_store/chroma/bluer_db"
EMBEDDING_MODEL_NAME = 'text-embedding-3-small'
embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)

vector_store = Chroma(
    embedding_function=embedding_model,
    collection_name=COLLECTION_NAME,
    persist_directory=PERSIST_DIRECTORY
)



class Chatting:
    """
    대화형 AI 채팅 클래스.
    
    GPT 모델을 사용하여 사용자와 대화를 수행하고, 대화 기록을 관리한다.
    """

    def __init__(self):

        model = ChatOpenAI(model="gpt-4o-mini")
        
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 50,
                "fetch_k": 200,
                "lambda_mult": 0.5,               
                                    }
            )
        

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", dedent("""
                당신은 한국의 식당을 소개하는 인공지능 비서입니다. 
                반드시 질문에 대해서 [context]에 주어진 내용을 바탕으로 답변을 해주세요. 
                질문에 '리본개수', '평점', '몇 개'라는 키워드가 포함된 경우, [context]에서 "리본개수" 항목을 확인해 답변하세요.
                리본개수는 평점과 같은 의미를 가집니다.
                [context]
                {context}
            """)),
            ("human", "{question}")
        ])

        def content_from_doc(docs:list[Document]):
            return "\n\n".join([d.page_content for d in docs])

        output_parser = StrOutputParser()


        self.chain = (
            {
                "context": RunnableLambda(lambda inputs: retriever.get_relevant_documents(inputs["query"])),
                "question": RunnableLambda(lambda inputs: {"question": inputs["query"]})
            } 
            | prompt_template 
            | model 
            | output_parser
        )

    def send_message(self, message:str, history:list):
        """
        사용자 메시지를 처리하고 AI 응답을 반환.
        Parameter:
            message: str 사용자가 입력한 메시지
            history: list - 사용자와 AI간의 이전까지의 대화 기록

        Returns:
            str: AI의 응답 메시지
        """
        try:
            response = self.chain.invoke({"history": history, "query": message})
            return response
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            traceback.print_exc()
            raise
    


def add_message_to_history(history:list[tuple[str, str]], message:tuple[str, str], max_history=20):
    """
    Message를 history에 추가하는 util 메소드.
    파라미터로 받은 history에 message를 추가한다.
    max_history 개수를 넘어가면 오래된 것 부터 지운다.
    Parameter:
        history: list - 대화 기록
        message: tuple - (speaker, message) 형태의 메시지
        max_history: int - 저장할 최대 대화 기록 개수
    """
    while len(history) >= max_history:
        history.pop(0)
    history.append(message)
        
        