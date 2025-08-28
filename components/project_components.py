# components/project_components.py - 프로젝트 관련 UI 컴포넌트

import streamlit as st
from database import create_project, get_all_projects, get_project_summary

class ProjectSelector:
    """프로젝트 선택/생성 컴포넌트 클래스"""
    
    @staticmethod
    def render():
        """프로젝트 선택/생성 컴포넌트 렌더링"""
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
            
            # 프로젝트 카드 형태로 표시
            for project in projects:
                summary = get_project_summary(project['id'])
                
                # 현재 선택된 프로젝트 표시
                is_selected = st.session_state.get('current_project_id') == project['id']
                
                with st.sidebar.container():
                    if is_selected:
                        # 선택된 프로젝트 카드 (다크 모드 대응)
                        st.markdown(f"""
                        <style>
                        .selected-project-{project['id']} {{
                            border: 2px solid #1f77b4;
                            border-radius: 8px;
                            padding: 10px;
                            margin: 5px 0;
                            background-color: #e8f4f8;
                            color: #333333;
                        }}
                        
                        /* 다크 모드 */
                        @media (prefers-color-scheme: dark) {{
                            .selected-project-{project['id']} {{
                                background-color: #1a2332;
                                color: #ffffff;
                                border-color: #4da6ff;
                            }}
                        }}
                        
                        .selected-project-{project['id']} strong,
                        .selected-project-{project['id']} small {{
                            color: inherit;
                        }}
                        </style>
                        
                        <div class="selected-project-{project['id']}">
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

class ProjectInfo:
    """현재 선택된 프로젝트 정보 컴포넌트 클래스"""
    
    @staticmethod
    def render():
        """현재 선택된 프로젝트 정보 표시"""
        if st.session_state.get('current_project_id'):
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