# app.py - 포코톤 메인 애플리케이션 (간소화된 진입점)

import streamlit as st
from config import STREAMLIT_CONFIG
from init_db import initialize_database
from components import ProjectSelector, ProjectInfo
from pages import render_welcome_page, render_project_main_page, render_error_page

# 페이지 설정
st.set_page_config(
    page_title=STREAMLIT_CONFIG["page_title"],
    page_icon=STREAMLIT_CONFIG["page_icon"],
    layout=STREAMLIT_CONFIG["layout"]
)

# 데이터베이스 자동 초기화
try:
    initialize_database(with_sample_data=False)
except Exception as e:
    st.error(f"데이터베이스 초기화 중 오류 발생: {e}")

# 세션 상태 초기화
if 'current_project_id' not in st.session_state:
    st.session_state.current_project_id = None
if 'current_project_name' not in st.session_state:
    st.session_state.current_project_name = None

def main():
    """메인 애플리케이션 함수"""
    
    # 메인 제목
    st.title("📋 포코톤 - AI 기반 프로젝트 일정 관리 시뮬레이션")
    st.markdown("### 🚀 스프린트 중심의 체계적인 업무 관리와 Round Robin 알고리즘을 통한 최적화된 팀원 분배")
    
    try:
        # 사이드바 - 프로젝트 관리
        ProjectSelector.render()
        ProjectInfo.render()
        
        # 메인 컨텐츠 라우팅
        if st.session_state.current_project_id:
            render_project_main_page()
        else:
            render_welcome_page()
    
    except Exception as e:
        render_error_page(str(e))




if __name__ == "__main__":
    main()