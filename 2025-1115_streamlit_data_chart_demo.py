import streamlit as st
import pandas as pd
import numpy as np

st.title("데이터 요소와 차트 요소 데모")

st.header("데이터 요소")

df = pd.DataFrame({
    "x": [1,2,3],
    "y": [10,20,30]
})
st.write("st.dataframe")
st.dataframe(df)

st.write("st.table")
st.table(df)

st.write("st.json")
st.json({"name":"jayden","items":[1,2,3]})

st.write("st.metric")
st.metric(label="일일 사용자", value="1000명", delta="+10%")

st.header("차트 요소")

chart_data = pd.DataFrame({
    "a": [1,2,3,4],
    "b": [10,30,20,40]
})

st.write("st.bar_chart")
st.bar_chart(chart_data)

st.write("st.line_chart")
st.line_chart(chart_data)

st.write("st.area_chart")
st.area_chart(chart_data)
