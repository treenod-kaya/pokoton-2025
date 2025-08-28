# pages.py - 페이지별 렌더링 로직

import streamlit as st
from components import (
    SystemStatus, DevelopmentTools, ProgressIndicator,
    TeamMemberForm, TeamMemberList, TaskForm, TaskList,
    SimulationRunner, SimulationResults, SimulationAnalysis, SimulationVisualization, SimulationExport,
    SprintForm, SprintList, SprintTaskDistribution
)
from database import get_project_by_id

def render_welcome_page():
    """환영 페이지 (프로젝트 미선택 시)"""
    st.info("📁 사이드바에서 프로젝트를 선택하거나 새로 생성해주세요.")
    
    # 진행 상황 표시
    ProgressIndicator.render("H7")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📝 완료된 개발 단계
        
        #### ✅ H1. 환경 세팅 (완료)
        - Streamlit 프로젝트 구조 세팅
        - SQLite 초기화 스크립트 작성
        - 모듈화된 파일 구조 완성
        
        #### ✅ H2. 팀원 입력 (완료)
        - 프로젝트 선택 & 팀원 입력 화면
        - 팀원 입력 폼 + 테이블 표시
        - 모듈 분리 및 컴포넌트화
        
        #### ✅ H3. 업무 입력 (완료)
        - 13개 필드 업무 관리 시스템
        - 업무 입력/수정/삭제 CRUD
        - 우선순위 및 담당자 지정
        
        #### ✅ H4. 업무 관리 (완료)
        - 업무 상세 정보 관리
        - 스토리 포인트 및 시간 추정
        - 업무 연결성 및 AI 판단
        
        #### ✅ H5. 시뮬레이션 (완료)
        - Round Robin 분배 알고리즘
        - 팀원별 업무량 및 일정 계산
        - 시뮬레이션 결과 분석
        
        #### ✅ H6. 결과 시각화 (완료)
        - 팀원별 업무량 Bar Chart
        - 프로젝트 간트 차트
        - 불균형 지표 시각화
        
        #### ✅ H7. Export & 품질 보강 (완료)
        - CSV/Excel 결과 Export
        - 기본 에러 처리 및 유효성 검증
        - 데이터 무결성 보장
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
        - ✅ H2: 팀원 입력 완료
        - ✅ H3: 업무 입력 완료
        - ✅ H4: 업무 관리 완료
        - ✅ H5: 시뮬레이션 완료
        - ✅ H6: 결과 시각화 완료
        - ✅ H7: Export & 품질 보강 완료
        - ⏳ H8: 최종 완성 및 배포
        """)
    
    # 시스템 상태 확인
    st.markdown("---")
    SystemStatus.render()
    
    # 개발 도구
    DevelopmentTools.render()

def render_project_main_page():
    """프로젝트 메인 페이지 (프로젝트 선택 후)"""
    st.success("🎉 프로젝트가 선택되었습니다!")
    
    # 진행 상황 표시
    ProgressIndicator.render("H7")
    
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
    
    # 탭으로 팀원 관리, 업무 관리, 스프린트 관리, 시뮬레이션 분리
    tab1, tab2, tab3, tab4 = st.tabs(["👥 팀원 관리", "📋 업무 관리", "🚀 스프린트 관리", "🎯 시뮬레이션"])
    
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
        # H5 단계: 시뮬레이션
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
    
    # 다음 단계 안내
    st.info("""
    ### 🎉 H7 단계 완료: Export & 품질 보강
    - ✅ CSV/Excel 결과 Export 기능
    - ✅ 시뮬레이션 실행 전 데이터 유효성 검증
    - ✅ 에러 처리 및 사용자 친화적 오류 메시지
    - ✅ 통합 분석 리포트 다운로드
    
    ### 🚀 다음 단계 예정: H8 최종 완성
    - 실제 날짜 기반 간트 차트
    - 성능 최적화 및 안정성 개선
    - 사용자 매뉴얼 및 배포 준비
    """)
    
    # 개발 도구
    DevelopmentTools.render()

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