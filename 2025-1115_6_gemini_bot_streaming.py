"""
================================================================================
[강의용 시각화 자료] 6단계: Gemini 봇 스트리밍 구조도
================================================================================

이 코드는 Streamlit과 Google GenAI SDK를 사용하여 "실시간 스트리밍" 챗봇을 구현합니다.
전체 데이터 흐름은 다음과 같습니다:

[사용자 (User)]
      |
      | 1. 메시지 입력 (st.chat_input)
      v
[Streamlit 앱] ----------------------------------------+
|                                                      |
|  2. 대화 기록(History)에 사용자 메시지 추가          |
|     (st.session_state.history)                       |
|                                                      |
|  3. Google Gemini API 호출 (스트리밍 모드)           |
|     client.models.generate_content_stream(history)   |
|                                                      |
+------------------------------------------------------+
      |
      | 4. 요청 (Request)
      v
[Google Gemini AI 서버]
      |
      | 5. 응답 스트림 (Response Stream) - 조각(Chunk) 단위 전송
      |    "안녕" -> "하세" -> "요!"
      v
[Streamlit 앱] ----------------------------------------+
|                                                      |
|  6. 반복문(for chunk in stream)으로 조각 수신        |
|                                                      |
|  7. 화면 갱신 (message_placeholder.markdown)         |
|     "안녕▌" -> "안녕하세요▌" -> "안녕하세요!"        |
|                                                      |
|  8. 대화 기록(History)에 전체 응답 추가              |
+------------------------------------------------------+

================================================================================
[핵심 코드 설명]
1. st.sidebar: API 키를 입력받는 사이드바 영역
2. @st.cache_resource: 클라이언트 연결을 한 번만 수행하도록 최적화
3. st.session_state.history: 대화 내용을 저장하는 리스트 (문맥 유지)
4. generate_content_stream(): 한 번에 답을 받지 않고, 타자기처럼 실시간으로 받음
================================================================================
"""

# 6_gemini_bot_streaming.py
#
# [스트리밍 수정] generate_content_stream() 올바른 사용법
#
# 실행 (API 키 필요):
# 1. (터미널) pip install google-genai
# 2. (터미널) streamlit run 6_gemini_bot_streaming.py

import streamlit as st
from google import genai
import os
import time

# --- 1. API 키 설정 ---
with st.sidebar:
    st.subheader("🔑 Google API 키 설정")
    api_key = st.text_input(
        "Google AI Studio API Key를 입력하세요.", 
        type="password",
        help="[Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키를 발급받으세요."
    )
    if not api_key:
        st.error("API 키를 입력해야 챗봇이 작동합니다.")
        st.stop()

# --- 2. Gemini 클라이언트 로드 (캐싱) ---
@st.cache_resource
def load_client(key):
    print("--- [알림] Gemini 클라이언트(Client)를 로드합니다... (앱 실행 시 1번만) ---")
    try:
        client = genai.Client(api_key=key)
        print("--- 클라이언트 로드 완료 ---")
        return client
    except Exception as e:
        st.error(f"클라이언트 로드 중 오류 발생: {e}")
        st.stop()

client = load_client(api_key)
MODEL_NAME = 'gemini-2.5-flash'

# --- 3. 채팅 기록(History) 초기화 ---
if "history" not in st.session_state:
    st.session_state.history = []
    print("새로운 채팅 기록(history list)을 시작합니다.")

st.title("Gemini 봇 (최신 스트리밍 - 6단계)")

# --- 4. 이전 대화 기록 표시 ---
for message in st.session_state.history:
    role = "ai" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["parts"][0]["text"])

# --- 5. 새 사용자 입력 처리 (스트리밍) ---
if prompt := st.chat_input("메시지를 입력하세요..."):
    
    # 1. 사용자 메시지 표시 및 history에 추가
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.history.append({"role": "user", "parts": [{"text": prompt}]})

    # 2. Gemini의 스트리밍 응답 처리
    with st.chat_message("ai"):
        message_placeholder = st.empty()
        
        with st.spinner("Gemini가 생각 중입니다... 🤔"):
            try:
                # 핵심: generate_content_stream() 메소드 사용
                response_stream = client.models.generate_content_stream(
                    model=MODEL_NAME,
                    contents=st.session_state.history
                )
                
                full_response = ""
                
                # 스트림 청크를 순회하며 실시간 표시
                for chunk in response_stream:
                    # chunk.text가 None이거나 빈 문자열일 수 있으므로 체크
                    chunk_text = chunk.text if hasattr(chunk, 'text') and chunk.text else ""
                    if chunk_text:
                        full_response += chunk_text
                        message_placeholder.markdown(full_response + "▌")
                
                # 최종 응답 표시 (커서 제거)
                message_placeholder.markdown(full_response)
                print(f"스트리밍 응답 완료. 총 길이: {len(full_response)}")

                # history에 전체 응답 추가
                st.session_state.history.append({
                    "role": "model",
                    "parts": [{"text": full_response}]
                })

            except AttributeError as e:
                st.error(f"청크 속성 오류: {e}")
                print(f"AttributeError 상세: {e}")
                print(f"청크 타입: {type(chunk)}")
                print(f"청크 내용: {chunk}")
            except Exception as e:
                st.error(f"응답 생성 중 오류: {e}")
                print(f"오류 상세: {e}")
                import traceback
                traceback.print_exc()