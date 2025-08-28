# components.py - 재사용 가능한 UI 컴포넌트

import streamlit as st
import pandas as pd
from database import (
    create_project, get_all_projects, get_project_by_id,
    add_team_member, get_team_members, delete_team_member,
    add_task, get_tasks, delete_task,
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

def render_task_form():
    """업무 입력 폼 컴포넌트 (H4)"""
    st.header("📋 업무 관리")
    
    # 현재 프로젝트의 팀원 목록 가져오기 (담당자 선택용)
    team_members = get_team_members(st.session_state.current_project_id)
    member_options = ["미지정"] + [m["name"] for m in team_members]
    
    with st.container():
        st.subheader("새 업무 추가")
        
        # 첫 번째 행: 기본 정보
        col1, col2, col3 = st.columns(3)
        with col1:
            item_name = st.text_input("업무명 *", placeholder="예: 로그인 API 개발", key="task_item_name")
        with col2:
            priority = st.selectbox("우선순위", options=[1, 2, 3, 4, 5], index=2, key="task_priority")
        with col3:
            assignee = st.selectbox("담당자", options=member_options, index=0, key="task_assignee")
        
        # 두 번째 행: 분류 정보
        col1, col2, col3 = st.columns(3)
        with col1:
            attribute = st.selectbox(
                "속성", 
                options=["기능 개발", "버그 수정", "리팩토링", "테스트", "문서화", "기타"],
                index=0, key="task_attribute"
            )
        with col2:
            # 기존 빌드 목록 (세션 상태로 관리)
            if 'build_types' not in st.session_state:
                st.session_state.build_types = [
                    "Sprint 1.0", "Sprint 1.1", "Sprint 1.2", 
                    "v1.0.0", "v1.1.0", "v2.0.0",
                    "2024-Q4", "2025-Q1", "Hot Fix"
                ]
            
            build_options = st.session_state.build_types + ["+ 새 빌드 추가"]
            selected_build = st.selectbox(
                "적용 빌드",
                options=build_options,
                index=0,
                key="task_build_select"
            )
            
            # 새 빌드 추가 선택 시
            if selected_build == "+ 새 빌드 추가":
                new_build = st.text_input(
                    "새 빌드명",
                    placeholder="예: Sprint 2.0, v3.0.0",
                    key="new_build_input"
                )
                if new_build and new_build.strip():
                    if st.button("빌드 추가", key="add_build_btn"):
                        if new_build.strip() not in st.session_state.build_types:
                            st.session_state.build_types.append(new_build.strip())
                            st.success(f"'{new_build}' 빌드가 추가되었습니다!")
                            st.rerun()
                        else:
                            st.warning("이미 존재하는 빌드명입니다.")
                build_type = new_build if new_build and new_build.strip() else ""
            else:
                build_type = selected_build
        with col3:
            part_division = st.selectbox(
                "파트 구분",
                options=["프론트엔드", "백엔드", "데이터베이스", "인프라", "기획", "디자인", "QA"],
                index=0, key="task_part_division"
            )
        
        # 세 번째 행: 상세 내용
        content = st.text_area("업무 내용", placeholder="업무에 대한 자세한 설명을 입력하세요...", key="task_content")
        
        # 네 번째 행: 시간 추정
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            story_points_leader = st.number_input("스토리 포인트", min_value=0, max_value=50, value=0, key="task_story_points")
        with col2:
            duration_leader = st.number_input("예상 기간(리더)", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="task_duration_leader")
        with col3:
            duration_assignee = st.number_input("예상 기간(담당자)", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="task_duration_assignee")
        with col4:
            final_hours = st.number_input("최종 예상시간", min_value=0.0, max_value=500.0, value=8.0, step=0.5, key="task_final_hours")
        
        # 다섯 번째 행: AI 판단 및 연결성
        col1, col2 = st.columns(2)
        with col1:
            ai_judgment = st.text_input("AI 판단", placeholder="AI 분석 결과...", key="task_ai_judgment")
        with col2:
            connectivity = st.text_input("업무 연결성", placeholder="관련 업무 ID나 설명...", key="task_connectivity")
        
        # 추가 버튼
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("📝 업무 추가", key="add_task", type="primary", use_container_width=True):
                if item_name and item_name.strip():
                    try:
                        add_task(
                            project_id=st.session_state.current_project_id,
                            attribute=attribute,
                            build_type=build_type,
                            part_division=part_division,
                            priority=priority,
                            item_name=item_name.strip(),
                            content=content,
                            assignee=assignee if assignee != "미지정" else "",
                            story_points_leader=story_points_leader,
                            duration_leader=duration_leader,
                            duration_assignee=duration_assignee,
                            final_hours=final_hours,
                            ai_judgment=ai_judgment,
                            connectivity=connectivity
                        )
                        st.success(f"✅ 업무 '{item_name}'가 추가되었습니다!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 업무 추가 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.error("⚠️ 업무명을 입력해주세요.")

def render_task_list():
    """업무 목록 표시 컴포넌트 (H4)"""
    tasks = get_tasks(st.session_state.current_project_id)
    
    if tasks:
        st.subheader(f"📊 업무 현황 ({len(tasks)}개)")
        
        # H4: 업무 테이블 표시
        import pandas as pd
        
        tasks_df = pd.DataFrame([
            {
                "ID": task["id"],
                "업무명": task["item_name"],
                "속성": task.get("attribute", ""),
                "빌드": task.get("build_type", ""),
                "파트": task.get("part_division", ""),
                "우선순위": task.get("priority", 3),
                "담당자": task.get("assignee", "미지정"),
                "스토리포인트": task.get("story_points_leader", 0),
                "리더예상": f"{task.get('duration_leader', 0):.1f}h",
                "담당자예상": f"{task.get('duration_assignee', 0):.1f}h", 
                "최종시간": f"{task.get('final_hours', 0):.1f}h",
                "AI판단": task.get("ai_judgment", "")[:20] + "..." if len(task.get("ai_judgment", "")) > 20 else task.get("ai_judgment", ""),
                "연결성": task.get("connectivity", ""),
                "등록일": task["created_at"][:10] if task["created_at"] else ""
            } for task in tasks
        ])
        
        st.dataframe(tasks_df, use_container_width=True, hide_index=True)
        
        # 업무 삭제 기능
        with st.expander("🗑️ 업무 삭제"):
            task_to_delete = st.selectbox(
                "삭제할 업무 선택",
                options=[t["id"] for t in tasks],
                format_func=lambda x: next(t["item_name"] for t in tasks if t["id"] == x),
                index=None,
                placeholder="삭제할 업무를 선택하세요"
            )
            
            if task_to_delete and st.button("업무 삭제", key="delete_task", type="secondary"):
                if delete_task(task_to_delete):
                    st.success("✅ 업무가 삭제되었습니다.")
                    st.rerun()
                else:
                    st.error("❌ 업무 삭제에 실패했습니다.")
    else:
        st.info("📝 아직 추가된 업무가 없습니다. 위에서 업무를 추가해주세요.")

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