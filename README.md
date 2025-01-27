# SKN06-4th-2team


## <흑흑요리사>

### 팀원

| 강채연 | 김동명| 박창규 | 백하은| 홍준 |
| --- | --- | --- | --- | --- |
| ![IE001847808_STD](https://github.com/user-attachments/assets/c2f2176b-7c40-4769-b3a4-7dbef5565109) |![돌아이](https://github.com/user-attachments/assets/eac6eb13-7166-409a-9f04-defaeb629cfe)|![100](https://github.com/user-attachments/assets/89f5e5ed-6412-44bf-99e9-13bef9668415)|![강록이형](https://github.com/user-attachments/assets/3f3a4698-0df0-4028-8a9c-d8ced265a568)|![눈감성재](https://github.com/user-attachments/assets/19d76aae-223c-44b1-9fb9-57fd0991293f)|
| 백엔드 | 산출물 정리 및 작성 |웹사이트 구축, 프론트엔드|모델 성능 개선, 프론트엔드| 백엔드 |

</br>

## 1. 프로젝트 소개  
### **주제**  
**블루리본 서베이 챗봇 및 웹사이트**  

### **주제 선택 이유**  
-  최근 '흑백요리사', '백종원의 레미제라블', '냉장고를 부탁해 시즌2' 등 요리 관련 경연 프로그램이 다시 뜨거운 인기를 끌고 있다. 이에 따라 대중에게 다양한 음식 정보를 구체적으로 제공하여, 이들의 요리 경험에 대한 수요를 충족시킬 수 있는 챗봇을 서비스하려 한다.
-   블루리본 서베이는 대한민국에서 신뢰받는 식당 평가 매체로 품질 높은 정보를 제공하는 것으로 알려져 있다. 이 정보를 바탕으로 사용자들에게 다양한 요구를 충족시킬 수 있는 개인화된 추천 알고리즘을 구현할 수 있다.
- 수 많은 식당 중에서 적합한 선택을 하는 것은 시간과 노력이 많이 드는 일이지만 챗봇과 웹 서비스를 통해 효율적으로 정보를 제공함으로써 사용자의 의사결정을 지원할 수 있다. 이를 통해 바쁜 현대인들에게 실질적인 가치를 제공한다.

---

### **Stacks**
|![image](https://github.com/user-attachments/assets/227d16b4-9c5a-4b00-b00c-fcb6986cbf2c)| ![image](https://github.com/user-attachments/assets/49987c99-cb3c-47f1-b20c-087f3035c517)|![image](https://github.com/user-attachments/assets/7734ac1a-06a8-4d7f-9b5b-f7ec5f7c1c34)|![image](https://github.com/user-attachments/assets/374c9758-19bb-43d6-b714-6e537a2456a6)|![image](https://github.com/user-attachments/assets/cd8aaea2-3c3b-42c0-94f8-92cad18b1ec7)|![image](https://github.com/user-attachments/assets/bea1e19d-d49c-4893-b50e-781b6b61f36d)|![image](https://github.com/user-attachments/assets/27a58958-1248-42fb-93ac-eb7bf1b9563a)|![image](https://github.com/user-attachments/assets/ac9b86bc-c77f-40ee-a2ce-bbecb871cbc4)|![image](https://github.com/user-attachments/assets/89f04315-09b8-4d0e-9681-e4db82ccaa7f)|![image](https://github.com/user-attachments/assets/8e51d64c-1221-42d7-9646-eee2a656d3df)|
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|python|RAG|OpenAI|Github|HTML|CSS|Javascript|django|Bootstrap|AWS|






## 2. 주요 기능  
1. **레스토랑 정보 검색:**  
- 이름, 위치, 메뉴, 평점, 리뷰 등 상세 정보 제공  

2. **맞춤형 레스토랑 추천:**  
- 사용자 선호도 및 검색 이력 기반 추천  

3. **자연어 질의응답:**  
- 사용자가 입력한 질문에 정확하고 자연스러운 답변   

---


## 3. 성능 개선 및 평가지표 추가

### 성능개선 과정 및 결과

1. **모델 및 파라미터 튜닝**

- retriever 개선
"k" : 감소시켜 더 집중된 문서 반환
"lambda_mult" : 다양성 보다 관련성을 높임
```
    retriever = vector_store.as_retriever(
       search_type="mmr",
       search_kwargs={
           "k": 20,
           "fetch_k": 200,
           "lambda_mult": 0.7,
       }
   )
```

3. **prompt 개선**
- 요구사항 명세서 기반 prompt 수정

```
  prompt_template = ChatPromptTemplate.from_messages([
       ("system", dedent("""
           당신은 한국의 식당을 추천하고 정보를 제공하는 인공지능 비서입니다.
           아래 [context]에 제공된 정보만 사용하여 질문에 답변하세요. 
           [context]에 없는 정보에 대해서는 "문맥에 없습니다"라고 답변하세요.

           요청 유형에 따른 답변 지침:
           1. **단일 검색 요청**: 키워드, 카테고리, 가격, 리본개수 등 특정 조건에 맞는 단일 식당 정보를 제공하세요.
           - 예시: "리본개수가 2개인 식당은?"
           - 답변: "리본개수가 2개인 식당은 식당 A입니다."

           2. **비교 요청**: 2개 이상의 식당 정보를 비교하여 명확히 제공하세요.
           - 예시: "리본개수가 2개인 식당과 3개인 식당을 비교해주세요."
           - 답변 형식:
               - 식당 A: 리본개수 2, 가격 2만원, 카테고리 한식
               - 식당 B: 리본개수 3, 가격 3만원, 카테고리 프랑스 요리

           지침:
           - 질문에 '리본개수', '평점', '몇 개'라는 키워드가 포함된 경우, [context]에서 "리본개수" 항목을 확인하세요.
           - 리본개수는 평점과 동일한 의미를 가지며, 이를 기준으로 답변하세요.
           - 질문의 모든 조건(예: 가격, 카테고리, 리본개수)을 충족하도록 답변을 작성하세요.
           - 간결하고 명확하게 작성하세요.
           [context]
           {context}
       """)),
       ("human", "질문: {question}")
   ])
```

3. **데이터셋 품질 개선**
- 테스트 데이터 다양화: 테스트 데이터의 질문의 유형과 난이도를 다양하게 포함하도록 확장

```
  initial_test_data = [
       {"question": "예약 가능한 한식당 추천해줘.", "expected_answer": "식당 A가 예약 가능합니다."},
       {"question": "리본개수가 2개인 식당을 추천해주세요.", "expected_answer": "리본 개수가 2개인 식당은 식당 B입니다."},
       {"question": "프랑스식을 추천해주세요.", "expected_answer": "프랑스 요리를 제공하는 식당은 식당 C입니다."},
       {"question": "홍보각 식당의 정보를 알려주세요", "expected_answer": "홍보각 식당은 서울에 위치한 유명 식당입니다."},
       {"question": "평점이 4 이상인 한식당과 프랑스 요리 식당을 비교해주세요.", 
       "expected_answer": "한식당 A: 평점 4.5, 가격 2만원\n프랑스 요리 식당 B: 평점 4.3, 가격 3만원"},
       {"question": "리본개수가 4개 이상이고 평점이 4.5 이상인 식당을 추천해주세요.", "expected_answer": "..."}
   ]
```

### 평가지표 추가

```
- metrics = [
       LLMContextRecall(llm=eval_llm),
       LLMContextPrecisionWithReference(llm=eval_llm),
       Faithfulness(llm=eval_llm),
       AnswerRelevancy(llm=eval_llm, embeddings=eval_embedding)
   ]
```
</br>

|LLM_context_recall|LLM_context_precision_with_reference|Faithfulness|Answer_relevancy|
|---|---|---|---|
|문맥재현율|정밀도|신뢰도|답변관련성|
|0.8313|0.3611|0.6520|0.3766|

---

## 4. 요구사항 정의서  

![요구사항 정의서](https://github.com/user-attachments/assets/1d6b47f6-08cc-47e8-81f7-cfbb3e9545bd)

---

## 5. 화면 설계서  
- **홈 화면:**
- 챗봇 서비스 소개, 회원가입, 로그인 화면 구성
  </br>
    
![bluerb_chatbot](https://github.com/user-attachments/assets/a3ce9d4d-e478-4fb3-985f-6239e293ecbb)

- **챗 화면:**  
- 챗 서비스 제공 화면 구성
</br>

![Chatting](https://github.com/user-attachments/assets/ee09d065-62a3-4e01-a6fe-0c6e68fe0785)


---

## 6. 시스템 구성도  
</br>

![System_architecture](https://github.com/user-attachments/assets/e5893ba3-956a-45a8-bea8-30a82e1064ce)


## 7. 테스트 계획서 및 테스트 결과 보고서  

### 테스트 계획서
</br>

![테스트 계획서_서버](https://github.com/user-attachments/assets/8f76a38d-0b0c-4fc7-bf28-24ccbdd37bdf)

</br>

![테스트 계획서_챗봇](https://github.com/user-attachments/assets/0b0e58e7-89a2-4349-a6c3-dc4eead58f89)

</br>

**동시접속평가 요약**
![동시 접속 평가](https://github.com/user-attachments/assets/7ea620c5-073e-4062-809a-ecd642464d05)

### 테스트 결과 보고서
#### 1. Test 결과
> **배포 가능**
> 
> URL : http://127.0.0.1:8000/
> 
> APP : manage.py, app.py
>
</br>

#### 2. Test 기간
2025.01.17. - 2025.01.20.

</br>


#### 3. Test 단말
> Web
> Win 11 - Chrome, Edge / MAC - Chrome, Edge
>

</br>

#### 4. 주요 Feature
> 회원에게 제공하는 챗봇 서비스
> [블루리본서베이] 기반

</br>

#### 5. 참고내용
> 블루리본 서베이는 꾸준히 업데이트 되기 때문에 2025년 최근 등재 된 식당 정보는 누락될 수 있습니다.
> 
> AWS 의 프리티어 사용하여 100명 이상 동시 접속 시 일부 사용자에게 약간의 지연이 발생합니다

#### 6. 추가 문의
흑흑 요리사

## 8. 팀원 회고
> 강채연 : 졸리당 ~
> </br>
> 김동명 : 수고많으셨습니다 끝내주네요 진짜 팔까요
> </br>
> 박창규 : 졸리네요..~
> </br>
> 백하은 : 어렵당 ~
> </br>
> 홍준   : 감사합니다.



