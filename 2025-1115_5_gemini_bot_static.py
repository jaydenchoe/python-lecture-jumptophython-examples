# 5_gemini_bot_static.py
#
# [오류 수정]
# 1. (63행) history를 표시할 때 .text (객체)가 아닌 ["text"] (딕셔너리)로 접근합니다.
# 2. (77행) history에 모델 응답을 object가 아닌 dict로 변환하여 추가합니다.
#
# 실행 (API 키 필요):
# 1. (터미널) pip install google-genai
# 2. (터미널) streamlit run 5_gemini_bot_static.py

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

# --- 3. 채팅 기록(History) 초기화 (st.session_state) ---
if "history" not in st.session_state:
    st.session_state.history = []
    print("새로운 채팅 기록(history list)을 시작합니다.")

st.title("Gemini 봇 (최신 문법) (5단계)")

# --- 4. 이전 대화 기록 표시 ---
# [버그 수정 1] .text -> ["text"]
# st.session_state.history 에는 딕셔너리만 저장되므로, 
# 딕셔너리 문법으로 접근해야 합니다.
for message in st.session_state.history:
    role = "ai" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["parts"][0]["text"]) # <--- [수정됨]

# --- 5. 새 사용자 입력 처리 (최신 문법) ---
if prompt := st.chat_input("메시지를 입력하세요..."):
    
    # 1. 사용자 메시지 표시 및 history list에 추가 (dict)
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.history.append({"role": "user", "parts": [{"text": prompt}]})

    # 2. Gemini에게 응답 요청
    with st.chat_message("ai"):
        with st.spinner("Gemini가 생각 중입니다... 🤔"):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=st.session_state.history
                )
                
                response_text = response.text
                st.markdown(response_text)
                
                # [버그 수정 2] object -> dict
                # response.candidates[0].content (객체)를 그대로 넣는 대신,
                # API 규격에 맞는 딕셔너리 형태로 변환하여 추가합니다.
                model_response_content = response.candidates[0].content
                st.session_state.history.append({
                    "role": model_response_content.role,
                    "parts": [{"text": model_response_content.parts[0].text}]
                }) # <--- [수정됨]
            
            except Exception as e:
                st.error(f"응답 생성 중 오류: {e}")