import streamlit as st
import datetime

# 페이지 설정
st.set_page_config(
    page_title="간단한 Streamlit 앱",
    page_icon="🚀",
    layout="wide"
)

# 메인 제목
st.title("🚀 Streamlit Community Cloud 배포 테스트")

# 환영 메시지
st.markdown("### 안녕하세요! 이것은 배포 테스트용 간단한 Streamlit 앱입니다.")

# 현재 시간 표시
current_time = datetime.datetime.now()
st.info(f"현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

# 간단한 상호작용 요소들
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 텍스트 입력")
    user_name = st.text_input("이름을 입력하세요:", placeholder="홍길동")
    if user_name:
        st.success(f"안녕하세요, {user_name}님!")

with col2:
    st.subheader("🎨 색상 선택")
    color = st.color_picker("좋아하는 색상을 선택하세요:", "#FF6B6B")
    st.markdown(f'<div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center; color: white; font-weight: bold;">선택한 색상</div>', unsafe_allow_html=True)

# 간단한 차트
st.subheader("📊 샘플 차트")
import pandas as pd
import numpy as np

# 샘플 데이터 생성
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['A', 'B', 'C']
)

st.line_chart(chart_data)

# 사이드바
st.sidebar.title("🔧 설정")
st.sidebar.markdown("이것은 사이드바입니다.")

# 슬라이더
number = st.sidebar.slider("숫자를 선택하세요:", 0, 100, 50)
st.sidebar.write(f"선택한 숫자: {number}")

# 체크박스
if st.sidebar.checkbox("고급 옵션 표시"):
    st.sidebar.write("고급 옵션이 활성화되었습니다!")

# 푸터
st.markdown("---")
st.markdown("### 🎉 배포가 성공적으로 완료되었습니다!")
st.markdown("이 앱이 정상적으로 표시된다면 Streamlit Community Cloud 배포가 성공한 것입니다.")
