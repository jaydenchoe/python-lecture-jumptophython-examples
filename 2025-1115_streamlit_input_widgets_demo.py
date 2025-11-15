import streamlit as st

st.title("입력 위젯 데모")

st.header("기본 입력 위젯")

if st.button("버튼"):
    st.write("버튼 눌림")

name = st.text_input("텍스트 입력")
if name:
    st.write("입력됨:", name)

age = st.number_input("숫자 입력", min_value=0, max_value=120, value=20)
st.write("나이:", age)

value = st.slider("슬라이더", 0, 100, 50)
st.write("슬라이더 값:", value)

option = st.selectbox("옵션 선택", ["A","B","C"])
st.write("선택됨:", option)

options = st.multiselect("여러 개 선택", ["A","B","C","D"])
st.write("선택 목록:", options)

radio_val = st.radio("라디오 버튼", ["옵션1","옵션2"])
st.write("라디오 선택:", radio_val)

check = st.checkbox("동의")
st.write("체크 상태:", check)

toggle_val = st.toggle("토글")
st.write("토글 상태:", toggle_val)

uploaded = st.file_uploader("파일 업로드")
if uploaded:
    st.write("업로드됨:", uploaded.name)

st.header("폼 입력")

with st.form("my_form"):
    f_name = st.text_input("폼 이름")
    f_age = st.number_input("폼 나이", 0, 120, 30)
    submitted = st.form_submit_button("제출")

if submitted:
    st.write("폼 결과:", f_name, f_age)
