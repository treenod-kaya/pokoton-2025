# components.py - 재사용 가능한 UI 컴포넌트

import streamlit as st
import pandas as pd
from database import (
    create_project, get_all_projects, get_project_by_id,
    add_team_member, get_team_members, delete_team_member,
    get_project_summary
)

def render_project_selector():
    """프로젝트 선택/생성 컴포넌트"""
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

def render_project_info():
    """현재 선택된 프로젝트 정보 표시"""
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

def render_system_status():
    """시스템 상태 확인 컴포넌트"""
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
            from config import STREAMLIT_CONFIG
            st.success(f"✅ 설정 로딩 완료")
            st.caption(f"앱 제목: {STREAMLIT_CONFIG['page_title'][:20]}...")
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

def render_team_member_form():
    """팀원 입력 폼 컴포넌트 (H2)"""
    st.header("👥 팀원 관리")
    
    with st.expander("➕ 새 팀원 추가", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            member_name = st.text_input("팀원명", placeholder="예: 김개발", key="member_name")
        with col2:
            member_role = st.text_input("역할", placeholder="예: 백엔드 개발자", key="member_role")
        with col3:
            member_hours = st.number_input(
                "일일 가용시간", 
                min_value=0.5, 
                max_value=24.0, 
                value=8.0, 
                step=0.5,
                key="member_hours"
            )
        
        if st.button("팀원 추가", key="add_member", type="primary"):
            if member_name.strip() and member_role.strip():
                try:
                    add_team_member(
                        st.session_state.current_project_id, 
                        member_name.strip(), 
                        member_role.strip(), 
                        member_hours
                    )
                    st.success(f"팀원 '{member_name}'가 추가되었습니다!")
                    st.rerun()
                except Exception as e:
                    st.error(f"팀원 추가 중 오류가 발생했습니다: {str(e)}")
            else:
                st.error("팀원명과 역할을 입력해주세요.")

def render_team_member_list():
    """팀원 목록 표시 컴포넌트 (H2)"""
    members = get_team_members(st.session_state.current_project_id)
    
    if members:
        st.subheader(f"현재 팀원 ({len(members)}명)")
        
        # 팀원 테이블
        members_df = pd.DataFrame([
            {
                "ID": m["id"],
                "팀원명": m["name"],
                "역할": m["role"],
                "일일 가용시간": f"{m['available_hours_per_day']:.1f}h",
                "등록일": m["created_at"][:10] if m["created_at"] else ""
            } for m in members
        ])
        
        st.dataframe(members_df, use_container_width=True, hide_index=True)
        
        # 팀원 삭제 기능
        with st.expander("🗑️ 팀원 삭제"):
            member_to_delete = st.selectbox(
                "삭제할 팀원 선택",
                options=[m["id"] for m in members],
                format_func=lambda x: next(m["name"] for m in members if m["id"] == x),
                index=None,
                placeholder="삭제할 팀원을 선택하세요"
            )
            
            if member_to_delete and st.button("팀원 삭제", key="delete_member", type="secondary"):
                if delete_team_member(member_to_delete):
                    st.success("팀원이 삭제되었습니다.")
                    st.rerun()
                else:
                    st.error("팀원 삭제에 실패했습니다.")
    else:
        st.info("아직 추가된 팀원이 없습니다. 위에서 팀원을 추가해주세요.")

def render_development_tools():
    """개발 도구 컴포넌트"""
    with st.expander("🔧 개발 도구", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📝 샘플 데이터 생성"):
                try:
                    from init_db import insert_sample_data
                    insert_sample_data()
                    st.success("샘플 데이터가 생성되었습니다!")
                    st.rerun()
                except Exception as e:
                    st.error(f"샘플 데이터 생성 실패: {e}")
        
        with col2:
            if st.button("🔄 데이터베이스 상태 확인"):
                try:
                    from init_db import check_database_status
                    check_database_status()
                    st.success("콘솔에서 데이터베이스 상태를 확인하세요.")
                except Exception as e:
                    st.error(f"상태 확인 실패: {e}")

def render_progress_indicator(current_step: str):
    """진행 단계 표시 컴포넌트"""
    steps = {
        "H1": "환경 세팅",
        "H2": "팀원 입력", 
        "H3": "업무 입력",
        "H4": "시뮬레이션",
        "H5": "결과 표시"
    }
    
    st.markdown("### 📊 개발 진행 상황")
    
    cols = st.columns(len(steps))
    for i, (step_key, step_name) in enumerate(steps.items()):
        with cols[i]:
            if step_key == current_step:
                st.success(f"🟢 {step_key}\n{step_name}")
            elif step_key < current_step:
                st.info(f"✅ {step_key}\n{step_name}")
            else:
                st.markdown(f'<p style="color:gray;">⚪ {step_key}<br/>{step_name}</p>', unsafe_allow_html=True)