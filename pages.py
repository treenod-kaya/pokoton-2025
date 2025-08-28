# pages.py - 페이지별 렌더링 로직

import streamlit as st
from components import (
    render_system_status, render_development_tools, 
    render_progress_indicator, render_team_member_form, render_team_member_list
)
from database import get_project_by_id

def render_welcome_page():
    """환영 페이지 (프로젝트 미선택 시)"""
    st.info("📁 사이드바에서 프로젝트를 선택하거나 새로 생성해주세요.")
    
    # 진행 상황 표시
    render_progress_indicator("H2")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📝 완료된 개발 단계
        
        #### ✅ H1. 환경 세팅 (완료)
        - Streamlit 프로젝트 구조 세팅
        - SQLite 초기화 스크립트 작성
        - 모듈화된 파일 구조 완성
        
        #### 🔄 H2. 팀원 입력 (진행중)
        - 프로젝트 선택 & 팀원 입력 화면
        - 팀원 입력 폼 + 테이블 표시
        - 모듈 분리 및 컴포넌트화
        """)
    
    with col2:
        st.markdown("""
        ### 🗂️ 현재 파일 구조
        ```
        pokoton-2025/
        ├── config.py       # 설정 상수
        ├── models.py       # 데이터 모델
        ├── init_db.py      # DB 초기화
        ├── database.py     # CRUD 함수
        ├── components.py   # UI 컴포넌트 ✨
        ├── pages.py        # 페이지 렌더링 ✨
        ├── app.py          # 메인 앱 (간소화) ✨
        ├── requirements.txt
        └── pokoton.db      # SQLite DB
        ```
        
        ### 🚀 다음 개발 단계
        - ✅ H1: 환경 세팅 완료
        - 🔄 H2: 팀원 입력 (현재)
        - ⏳ H3: 업무 입력 화면
        - ⏳ H4: 시뮬레이션 로직
        - ⏳ H5: 결과 시각화
        """)
    
    # 시스템 상태 확인
    st.markdown("---")
    render_system_status()
    
    # 개발 도구
    render_development_tools()

def render_project_main_page():
    """프로젝트 메인 페이지 (프로젝트 선택 후)"""
    st.success("🎉 프로젝트가 선택되었습니다!")
    
    # 진행 상황 표시
    render_progress_indicator("H2")
    
    # 현재 프로젝트 정보
    project_info = get_project_by_id(st.session_state.current_project_id)
    if project_info:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("프로젝트 ID", project_info['id'])
        with col2:
            st.metric("프로젝트명", project_info['name'])
        with col3:
            st.metric("생성일", project_info['created_at'][:10] if project_info['created_at'] else "")
    
    st.markdown("---")
    
    # H2 단계: 팀원 관리
    render_team_member_form()
    
    st.markdown("---")
    
    render_team_member_list()
    
    st.markdown("---")
    
    # 다음 단계 안내
    st.info("""
    ### 📋 H3 단계 예정: 업무 입력 화면
    - 업무명, 난이도(1~5), 예상 소요 시간 입력 폼
    - 업무 목록 테이블 표시
    - 업무 수정/삭제 기능
    """)
    
    # 개발 도구
    render_development_tools()

def render_h3_preview_page():
    """H3 단계 미리보기 페이지 (준비중)"""
    st.header("📝 H3. 업무 입력 화면 (준비중)")
    st.info("H2 단계 완료 후 구현 예정입니다.")
    
    # 예상 UI 미리보기
    st.markdown("""
    ### 🎯 H3에서 구현할 기능들
    
    #### 1. 업무 입력 폼
    - 업무명 (텍스트 입력)
    - 난이도 (1~5 선택)
    - 예상 소요 시간 (숫자 입력)
    
    #### 2. 업무 목록 표시
    - 등록된 업무들을 테이블로 표시
    - 수정/삭제 기능
    
    #### 3. 데이터 검증
    - 필수 필드 검증
    - 난이도 범위 체크
    - 예상 시간 양수 체크
    """)
    
    # Mock-up UI
    with st.expander("🎨 예상 UI 미리보기", expanded=False):
        st.markdown("**업무 입력 폼 (예시)**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("업무명", placeholder="예: 로그인 기능 개발", disabled=True)
        with col2:
            st.selectbox("난이도", options=[1,2,3,4,5], index=2, disabled=True)
        with col3:
            st.number_input("예상 시간", value=8.0, disabled=True)
        
        st.button("업무 추가", disabled=True)
        
        st.markdown("**업무 목록 테이블 (예시)**")
        st.dataframe({
            "ID": [1, 2, 3],
            "업무명": ["로그인 기능 개발", "메인 페이지 디자인", "데이터베이스 설계"],
            "난이도": ["⭐⭐⭐", "⭐⭐", "⭐⭐⭐⭐"],
            "예상시간": ["16.0h", "12.0h", "20.0h"]
        })

def render_error_page(error_message: str):
    """에러 페이지"""
    st.error("❌ 오류가 발생했습니다")
    st.code(error_message)
    
    st.markdown("""
    ### 🔧 문제 해결 방법
    1. 페이지를 새로고침해보세요
    2. 다른 프로젝트를 선택해보세요
    3. 개발 도구에서 데이터베이스 상태를 확인해보세요
    """)
    
    if st.button("🔄 페이지 새로고침"):
        st.rerun()