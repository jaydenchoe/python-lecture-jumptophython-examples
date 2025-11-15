# 2_caching.py
#
# 실행: streamlit run 2_caching.py
#
# 1단계에서 코드가 매번 다시 실행되는 것을 확인했습니다.
# 만약 10초 걸리는 작업이 있다면, 버튼을 누를 때마다 10초가 걸릴 겁니다.
# @st.cache_resource를 사용해 이 문제를 해결합니다.

import streamlit as st
import time

# --- [새로 추가된 부분 1] ---
# @st.cache_resource : '리소스' (ML 모델, DB 연결 등)를 캐시합니다. [cite: 2645]
# 이 함수는 앱 실행 후 *단 한 번만* 실행되고, 그 결과(반환값)를
# Streamlit이 저장(캐시)해 둡니다.
@st.cache_resource
def load_heavy_resource():
    # 터미널에 로그를 찍어, 이 함수가 언제 실행되는지 확인합니다.
    print("--- [경고] 10초 걸리는 무거운 작업 시작! ---")
    time.sleep(10) # 10초간 대기 (예: 모델 로딩 시간)
    print("--- 로딩 완료! ---")
    # 이 딕셔너리 객체를 캐시합니다.
    return {"status": "Loaded", "time": time.time()}
# --- [끝] ---

st.title("캐싱(Caching) 이해하기 (2단계)")

# --- [새로 추가된 부분 2] ---
# 캐시된 함수를 호출합니다.
#
# 1. 첫 실행 시: load_heavy_resource() 함수가 실행되고, 10초간 멈춥니다.
# 2. 버튼 클릭 시: (스크립트는 다시 실행되지만) 이 함수는 실행되지 않고
#    캐시된 {"status": "Loaded", ...} 값을 즉시 반환합니다.
#    -> 터미널에 "--- [경고] ---" 로그가 찍히지 않는 것을 확인하세요!
resource = load_heavy_resource()

st.write(f"무거운 리소스 로딩 결과: {resource}")
# --- [끝] ---

if st.button("캐싱 테스트 버튼"):
    st.write("버튼 클릭! (10초 안 걸리고 바로 반응해야 성공)")

print("스크립트가 다시 실행되었습니다!")