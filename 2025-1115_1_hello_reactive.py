# 1_hello_reactive.py
#
# 1. 설치 (터미널에서 딱 한 번 실행):
#    pip install streamlit
#
# 2. 실행 (터미널에서):
#    streamlit run 1_hello_reactive.py
#
# 3. 브라우저에서 웹 앱을 확인하고, 터미널에서 print() 로그를 확인하세요.

import streamlit as st

# st.title() : 웹페이지에 큰 제목을 씁니다.
st.title("Streamlit 맛보기 (1단계)")

# st.write() : 웹페이지에 텍스트, 숫자, 데이터 등을 씁니다.
st.write("Streamlit은 파이썬 코드만으로 웹 앱을 만듭니다.")

# st.button() : 웹페이지에 버튼을 만듭니다.
# 버튼을 '클릭하면' True가 되어 if 문이 실행됩니다.
if st.button("여기를 눌러보세요"):
    st.write("버튼이 클릭되었습니다!")

# --- [핵심] 반응형 프로그래밍 ---
# 이 print문은 터미널(검은창)에 출력됩니다.
# 1. 앱을 처음 실행하면 "스크립트가 다시 실행되었습니다!"가 터미널에 1번 찍힙니다.
# 2. 웹에서 "여기를 눌러보세요" 버튼을 클릭할 때마다,
#    터미널에 "스크립트가 다시 실행되었습니다!"가 *계속* 찍히는 것을 확인하세요!
#
# 이것이 Streamlit의 '반응형' 핵심입니다. [cite: 2069]
print("스크립트가 다시 실행되었습니다!")