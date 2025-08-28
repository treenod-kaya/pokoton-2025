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
    
    # 기존 프로젝트 선택 (H3 개선)
    projects = get_all_projects()
    if projects:
        st.sidebar.markdown("#### 📂 기존 프로젝트 선택")
        
        # 프로젝트 카드 형태로 표시
        for project in projects:
            summary = get_project_summary(project['id'])
            
            # 현재 선택된 프로젝트 표시
            is_selected = st.session_state.get('current_project_id') == project['id']
            
            with st.sidebar.container():
                if is_selected:
                    st.markdown(f"""
                    <div style="border: 2px solid #1f77b4; border-radius: 8px; padding: 10px; margin: 5px 0; background-color: #e8f4f8;">
                        <strong>🟢 {project['name']}</strong><br/>
                        <small>팀원: {summary['team_count']}명 | 업무: {summary['task_count']}개</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    if st.button(f"📁 {project['name']}", key=f"select_project_{project['id']}", help=f"팀원: {summary['team_count']}명, 업무: {summary['task_count']}개"):
                        st.session_state.current_project_id = project['id']
                        st.session_state.current_project_name = project['name']
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
    """팀원 입력 폼 컴포넌트 (H3 개선)"""
    st.header("👥 팀원 관리")
    
    # H3: 더 나은 입력 폼 디자인
    with st.container():
        st.subheader("새 팀원 추가")
        
        # 2행 레이아웃으로 개선
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            member_name = st.text_input(
                "팀원명 *", 
                placeholder="예: 김개발", 
                key="member_name",
                help="팀원의 실명 또는 닉네임을 입력하세요"
            )
        with row1_col2:
            member_role = st.selectbox(
                "역할 *",
                options=["프론트엔드 개발자", "백엔드 개발자", "풀스택 개발자", "UI/UX 디자이너", "기획자", "QA 엔지니어", "데이터 분석가", "프로젝트 매니저", "기타"],
                index=None,
                placeholder="역할을 선택하세요",
                key="member_role"
            )
        
        row2_col1, row2_col2, row2_col3 = st.columns(3)
        with row2_col1:
            member_hours = st.number_input(
                "일일 가용시간", 
                min_value=0.5, 
                max_value=24.0, 
                value=8.0, 
                step=0.5,
                key="member_hours",
                help="하루에 이 프로젝트에 투입 가능한 시간"
            )
        with row2_col2:
            member_skill = st.selectbox(
                "숙련도",
                options=["초급", "중급", "고급", "전문가"],
                index=1,  # 중급이 기본값
                key="member_skill"
            )
        with row2_col3:
            member_cost = st.number_input(
                "시간당 비용 (만원)",
                min_value=0.0,
                max_value=50.0,
                value=5.0,
                step=0.5,
                key="member_cost",
                help="시간당 인건비 (만원 단위)"
            )
        
        # 추가 버튼
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("👨‍💻 팀원 추가", key="add_member", type="primary", use_container_width=True):
                if member_name and member_name.strip() and member_role:
                    try:
                        add_team_member(
                            st.session_state.current_project_id, 
                            member_name.strip(), 
                            member_role, 
                            member_hours,
                            member_skill,
                            member_cost
                        )
                        st.success(f"✅ 팀원 '{member_name}'({member_role})가 추가되었습니다!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 팀원 추가 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.error("⚠️ 팀원명과 역할을 입력해주세요.")

def render_team_member_list():
    """팀원 목록 표시 컴포넌트 (H3 개선)"""
    members = get_team_members(st.session_state.current_project_id)
    
    if members:
        st.subheader(f"📋 현재 팀원 현황 ({len(members)}명)")
        
        # H3: 카드 형태로 팀원 표시
        cols = st.columns(min(len(members), 3))  # 최대 3개 컬럼
        
        for i, member in enumerate(members):
            with cols[i % 3]:
                # 숙련도별 색상 매핑
                skill_colors = {
                    "초급": "#FFE4E1",
                    "중급": "#E6F3FF", 
                    "고급": "#E6FFE6",
                    "전문가": "#FFF2E6"
                }
                skill_color = skill_colors.get(member.get('skill_level', '중급'), "#F0F0F0")
                
                # 팀원 카드
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: {skill_color};">
                    <h4 style="margin: 0 0 10px 0;">👤 {member['name']}</h4>
                    <p style="margin: 5px 0;"><strong>역할:</strong> {member['role']}</p>
                    <p style="margin: 5px 0;"><strong>가용시간:</strong> {member['available_hours_per_day']:.1f}시간/일</p>
                    <p style="margin: 5px 0;"><strong>숙련도:</strong> {member.get('skill_level', '중급')}</p>
                    <p style="margin: 5px 0;"><strong>비용:</strong> {member.get('hourly_cost', 5.0):.1f}만원/시간</p>
                    <p style="margin: 5px 0; color: #666;"><small>등록일: {member['created_at'][:10] if member['created_at'] else ''}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                # 개별 삭제 버튼
                if st.button(f"🗑️ 삭제", key=f"delete_{member['id']}", help=f"{member['name']} 삭제"):
                    if delete_team_member(member['id']):
                        st.success(f"✅ {member['name']}이(가) 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error("❌ 팀원 삭제에 실패했습니다.")
        
        st.markdown("---")
        
        # H3: 팀 요약 정보
        total_hours = sum(m['available_hours_per_day'] for m in members)
        total_cost = sum(m.get('hourly_cost', 5.0) * m['available_hours_per_day'] for m in members)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 팀원 수", f"{len(members)}명")
        with col2:
            st.metric("일일 총 가용시간", f"{total_hours:.1f}시간")
        with col3:
            st.metric("일일 총 비용", f"{total_cost:.1f}만원")
        with col4:
            avg_skill = len([m for m in members if m.get('skill_level') in ['고급', '전문가']]) / len(members) * 100
            st.metric("고급 인력 비율", f"{avg_skill:.0f}%")
            
        # 테이블 형태도 제공 (토글)
        with st.expander("📊 상세 테이블 보기"):
            members_df = pd.DataFrame([
                {
                    "ID": m["id"],
                    "팀원명": m["name"],
                    "역할": m["role"],
                    "숙련도": m.get('skill_level', '중급'),
                    "일일 가용시간": f"{m['available_hours_per_day']:.1f}h",
                    "시간당 비용": f"{m.get('hourly_cost', 5.0):.1f}만원",
                    "일일 총 비용": f"{m.get('hourly_cost', 5.0) * m['available_hours_per_day']:.1f}만원",
                    "등록일": m["created_at"][:10] if m["created_at"] else ""
                } for m in members
            ])
            
            st.dataframe(members_df, use_container_width=True, hide_index=True)
            
    else:
        st.info("👥 아직 추가된 팀원이 없습니다. 위에서 팀원을 추가해주세요.")

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
                st.markdown(f'<p style="color:#808080;">⚪ {step_key}<br/>{step_name}</p>', unsafe_allow_html=True)