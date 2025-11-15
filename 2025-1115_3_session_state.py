# 3_session_state.py
#
# 실행: streamlit run 3_session_state.py
#
# 2단계에서 '느린 로딩'은 해결했습니다.
# 하지만 스크립트가 다시 실행될 때마다 '변수'도 초기화됩니다.
# 챗봇이 대화 내용을 기억하게 하려면? st.session_state를 사용합니다.

import streamlit as st

st.title("세션 상태(Session State) 이해하기 (3단계)")

# --- [일반 변수 (잘못된 예)] ---
st.subheader("1. 일반 변수 (버튼 누를 때마다 1로 초기화됨)")
normal_counter = 0
if st.button("일반 변수 +1"):
    normal_counter += 1
st.write(f"현재 값: {normal_counter}")


# --- [세션 변수 (올바른 예)] ---
st.subheader("2. 세션 변수 (값을 기억함)")

# [핵심 1] 세션 상태 초기화
# 'st.session_state'는 파이썬 딕셔너리(dict)처럼 작동합니다. [cite: 2393]
# "session_counter"라는 키(key)가 세션에 없으면(즉, 첫 실행이면) 0으로 초기화합니다. [cite: 2390]
if "session_counter" not in st.session_state:
    st.session_state.session_counter = 0

# [핵심 2] 세션 상태 사용
# 버튼을 누르면 '세션에 저장된' 값을 1 증가시킵니다.
if st.button("세션 변수 +1"):
    st.session_state.session_counter += 1

# [핵심 3] 세션 상태 표시
# 버튼을 누를 때마다 스크립트가 다시 실행되어도, st.session_state 값은
# 유지되므로 숫자가 계속 증가하는 것을 볼 수 있습니다! [cite: 2396]
st.write(f"현재 값: {st.session_state.session_counter}")

print("스크립트가 다시 실행되었습니다!")