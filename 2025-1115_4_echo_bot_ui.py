# 4_echo_bot_ui.py
#
# 실행: streamlit run 4_echo_bot_ui.py
#
# 3단계의 '세션 상태'를 응용하여, '숫자' 대신 '대화 기록 리스트'를
# 저장합니다. 그리고 챗봇 전용 UI를 사용합니다.

import streamlit as st

st.title("Echo 봇 (메아리 봇) (4단계)")
st.write("챗봇 UI와 대화 기록 세션을 배웁니다.")

# --- [핵심 1] 세션 상태 초기화 (채팅 기록용) ---
# "messages" 라는 키(key)로 빈 리스트를 만듭니다.
# 이 리스트에 사용자와 봇의 대화를 계속 추가할 것입니다.
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- [핵심 2] 이전 대화 기록 표시 ---
# 스크립트가 다시 실행될 때마다, 세션에 저장된 '전체' 대화 기록을
# 처음부터 끝까지 다시 그립니다.
for msg in st.session_state.messages:
    # st.chat_message : 채팅 버블(말풍선)을 만듭니다.
    # msg["role"] (user 또는 ai)에 따라 다른 아이콘을 표시합니다.
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"]) # 마크다운으로 내용을 표시합니다.

# --- [핵심 3] 새 사용자 입력 처리 ---
# st.chat_input : 화면 하단에 고정된 채팅 입력창을 만듭니다.
# 사용자가 메시지를 입력하고 Enter를 치면, 그 내용이 'prompt' 변수에
# 저장되고 스크립트가 다시 실행됩니다.
if prompt := st.chat_input("메시지를 입력하세요..."):
    
    # 1. 사용자의 메시지를 세션에 저장하고 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. "Echo" (봇)의 응답을 세션에 저장하고 화면에 표시
    response = f"'{prompt}'라고 하셨네요! (메아리)"
    st.session_state.messages.append({"role": "ai", "content": response})
    with st.chat_message("ai"):
        st.markdown(response)

print("스크립트가 다시 실행되었습니다!")