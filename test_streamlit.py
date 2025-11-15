import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("테스트 페이지")

st.write("텍스트 출력 테스트")
st.write({"a":1,"b":2})

df = pd.DataFrame({"x":[1,2,3],"y":[10,20,30]})
st.write("데이터프레임")
st.write(df)

fig = plt.figure()
plt.plot(df["x"], df["y"])
st.write("matplotlib 차트")
st.write(fig)

name = st.text_input("이름 입력")
if name:
    st.write(f"{name} 반가워")

if st.button("버튼 테스트"):
    st.write("버튼 눌림")

uploaded = st.file_uploader("파일 업로드 테스트")
if uploaded:
    st.write(uploaded.name)
