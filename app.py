import streamlit as st

st.title("Hello Streamlit!")
st.write("Streamlit Community Cloud 배포 테스트 앱입니다.")

if st.button("클릭해보세요!"):
    st.success("배포가 성공적으로 완료되었습니다! 🎉")
