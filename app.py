# app.py - 포코톤 메인 애플리케이션

import streamlit as st
import pandas as pd
from config import STREAMLIT_CONFIG, TASK_ATTRIBUTES, PART_DIVISIONS, PRIORITY_LEVELS, DEFAULT_VALUES
from database import (
    create_project, get_all_projects, get_project_by_id,
    add_team_member, get_team_members,
    add_task, get_tasks,
    get_project_summary
)
from init_db import initialize_database

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
    st.title("📋 포코톤 - 일정 관리 시뮬레이션 (H1 환경 세팅 완료)")
    st.markdown("### 🚀 Streamlit + SQLite 기반 프로젝트 관리 시스템")
    
    # 사이드바 - 프로젝트 관리
    render_sidebar()
    
    # 메인 컨텐츠
    if st.session_state.current_project_id:
        render_main_content()
    else:
        render_welcome_screen()

def render_sidebar():
    """사이드바 렌더링"""
    st.sidebar.title("🎯 프로젝트 관리")
    
    # 프로젝트 생성
    with st.sidebar.expander("➕ 새 프로젝트 생성", expanded=False):
        new_project_name = st.text_input("프로젝트명", placeholder="예: 웹사이트 리뉴얼 프로젝트")
        if st.button("프로젝트 생성", key="create_project"):
            if new_project_name.strip():
                try:
                    project_id = create_project(new_project_name.strip())
                    st.session_state.current_project_id = project_id
                    st.session_state.current_project_name = new_project_name.strip()
                    st.success(f"프로젝트 '{new_project_name}'가 생성되었습니다!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
            else:
                st.error("프로젝트명을 입력해주세요.")
    
    # 기존 프로젝트 선택
    projects = get_all_projects()
    if projects:
        st.sidebar.markdown("#### 📂 기존 프로젝트 선택")
        
        project_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in projects}
        selected_project_key = st.sidebar.selectbox(
            "프로젝트 선택",
            options=list(project_options.keys()),
            index=None,
            placeholder="프로젝트를 선택하세요"
        )
        
        if selected_project_key:
            selected_project_id = project_options[selected_project_key]
            if st.session_state.current_project_id != selected_project_id:
                st.session_state.current_project_id = selected_project_id
                project_info = get_project_by_id(selected_project_id)
                st.session_state.current_project_name = project_info['name']
                st.rerun()
    else:
        st.sidebar.info("아직 생성된 프로젝트가 없습니다.")
    
    # 현재 프로젝트 정보 표시
    if st.session_state.current_project_id:
        st.sidebar.success(f"📌 현재 프로젝트: **{st.session_state.current_project_name}**")
        
        # 프로젝트 요약 정보
        summary = get_project_summary(st.session_state.current_project_id)
        st.sidebar.markdown(
            f"""
            **프로젝트 현황**
            - 팀원 수: {summary['team_count']}명
            - 업무 수: {summary['task_count']}개
            - 총 예상시간: {summary['total_estimated_hours']:.1f}시간
            - 일일 총 가용시간: {summary['total_daily_capacity']:.1f}시간
            """
        )
    else:
        st.sidebar.warning("프로젝트를 선택하거나 새로 생성해주세요.")

def render_welcome_screen():
    """환영 화면 렌더링"""
    st.info("📁 사이드바에서 프로젝트를 선택하거나 새로 생성해주세요.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📝 H1 단계 완료 사항
        ✅ **Streamlit 프로젝트 구조 세팅**
        - config.py: 설정 파일
        - models.py: 데이터 모델
        - init_db.py: DB 초기화 스크립트
        - database.py: CRUD 함수
        - app.py: 메인 애플리케이션
        
        ✅ **SQLite 초기화 스크립트**
        - 자동 DB 생성 및 테이블 생성
        - 샘플 데이터 옵션
        - 상태 확인 기능
        """)
    
    with col2:
        st.markdown("""
        ### 🗂️ 파일 구조
        ```
        pokoton-2025/
        ├── config.py       # 설정 상수
        ├── models.py       # 데이터 모델
        ├── init_db.py      # DB 초기화
        ├── database.py     # CRUD 함수
        ├── app.py          # 메인 앱
        ├── requirements.txt
        └── pokoton.db      # SQLite DB
        ```
        
        ### 🚀 다음 단계 (H2)
        - DB 스키마 & CRUD 완성 ✅
        - 프로젝트 선택 기능 ✅
        - 팀원 입력 화면 (준비중)
        """)
    
    # 시스템 상태 확인
    st.markdown("---")
    st.subheader("🔍 시스템 상태 확인")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 데이터베이스 연결 테스트
        try:
            from database import db
            conn_test = db.get_connection()
            conn_test.close()
            st.success("✅ 데이터베이스 연결 성공")
        except Exception as e:
            st.error(f"❌ 데이터베이스 연결 실패: {e}")
    
    with col2:
        # 설정 파일 로딩 테스트
        try:
            st.success(f"✅ 설정 로딩 완료")
            st.caption(f"DB 경로: {STREAMLIT_CONFIG['page_title']}")
        except Exception as e:
            st.error(f"❌ 설정 로딩 실패: {e}")
    
    with col3:
        # 프로젝트 목록 테스트
        try:
            projects = get_all_projects()
            st.success(f"✅ 프로젝트 조회 완료")
            st.caption(f"총 {len(projects)}개 프로젝트")
        except Exception as e:
            st.error(f"❌ 프로젝트 조회 실패: {e}")

def render_main_content():
    """메인 컨텐츠 렌더링 (H2에서 구현 예정)"""
    st.success("🎉 프로젝트가 선택되었습니다!")
    st.info("📋 H2 단계에서 팀원 입력 화면을 구현할 예정입니다.")
    
    # 현재 프로젝트 정보 표시
    project_info = get_project_by_id(st.session_state.current_project_id)
    if project_info:
        st.markdown(f"""
        **선택된 프로젝트 정보**
        - ID: {project_info['id']}
        - 이름: {project_info['name']}
        - 생성일: {project_info['created_at']}
        """)
    
    # 임시 개발 도구
    with st.expander("🔧 개발 도구 (H1 테스트용)", expanded=False):
        if st.button("샘플 데이터 생성 테스트"):
            try:
                from init_db import insert_sample_data
                insert_sample_data()
                st.success("샘플 데이터가 생성되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"샘플 데이터 생성 실패: {e}")

if __name__ == "__main__":
    main()