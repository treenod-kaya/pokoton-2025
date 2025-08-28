# pages.py - 페이지별 렌더링 로직

import streamlit as st
from components import (
    TeamMemberForm, TeamMemberList, TaskForm, TaskList,
    SimulationRunner, SimulationResults, SimulationAnalysis, SimulationVisualization, SimulationExport,
    SprintForm, SprintList, SprintTaskDistribution,
    DemoGuide, FeatureHighlight, TaskDistributionSimulator
)
from database import get_project_by_id
from demo_data import render_demo_section

def render_welcome_page():
    """환영 페이지 (프로젝트 미선택 시)"""
    
    # 메인 소개 섹션
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1>🎯 포코톤에 오신 것을 환영합니다!</h1>
        <h3>AI 기반 프로젝트 일정 관리 및 업무 분배 시뮬레이션 플랫폼</h3>
        <p style="font-size: 1.2em; color: #666; margin-top: 1rem;">
            스프린트 중심의 체계적인 업무 관리와 Round Robin 알고리즘을 통한 최적화된 팀원 분배를 경험해보세요.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 시작하기 안내
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("📁 **시작하기**: 사이드바에서 프로젝트를 선택하거나 새로 생성해주세요.")
    
    # 추가 기능 하이라이트
    FeatureHighlight.render()

def render_project_main_page():
    """프로젝트 메인 페이지 (프로젝트 선택 후)"""
    st.success("🎉 프로젝트가 선택되었습니다!")
    
    
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
    
    # 탭으로 팀원 관리, 업무 관리, 스프린트 관리, 업무 분배, 시뮬레이션 분리
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 팀원 관리", "📋 업무 관리", "🚀 스프린트 관리", "📊 시뮬레이션 A", "📊 시뮬레이션 B"])
    
    with tab1:
        # H3 단계: 팀원 관리
        TeamMemberForm.render()
        st.markdown("---")
        TeamMemberList.render()
    
    with tab2:
        # H4 단계: 업무 관리
        # 업무 수정 모드인지 확인
        if st.session_state.get('editing_task_id'):
            from database import get_task_by_id
            task_data = get_task_by_id(st.session_state.editing_task_id)
            if task_data:
                TaskForm.render(task_data=task_data, is_edit_mode=True)
            else:
                st.error("선택한 업무를 찾을 수 없습니다.")
                del st.session_state.editing_task_id
                st.rerun()
        else:
            TaskForm.render()
        
        st.markdown("---")
        TaskList.render()
    
    with tab3:
        # 스프린트 관리
        # 스프린트 수정 모드인지 확인
        if st.session_state.get('editing_sprint_id'):
            from database import get_sprint_by_id
            sprint_data = get_sprint_by_id(st.session_state.editing_sprint_id)
            if sprint_data:
                SprintForm.render(sprint_data=sprint_data, is_edit_mode=True)
            else:
                st.error("선택한 스프린트를 찾을 수 없습니다.")
                del st.session_state.editing_sprint_id
                st.rerun()
        else:
            SprintForm.render()
        
        st.markdown("---")
        SprintList.render()
    
    with tab4:
        # 새로운 업무 분배 시뮬레이션 (핵심 기능)
        TaskDistributionSimulator.render()
    
    with tab5:
        # 기존 시뮬레이션 (상세 분석용)
        SimulationRunner.render()
        st.markdown("---")
        SimulationResults.render()
        st.markdown("---")
        SprintTaskDistribution.render()
        st.markdown("---")
        SimulationVisualization.render()
        st.markdown("---")
        SimulationExport.render()
        st.markdown("---")
        SimulationAnalysis.render()
    
    st.markdown("---")
    

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