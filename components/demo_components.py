# components/demo_components.py - 데모 관련 UI 컴포넌트

import streamlit as st
from demo_data import get_demo_script

class DemoGuide:
    """데모 가이드 컴포넌트"""
    
    @staticmethod
    def render():
        """데모 가이드 렌더링"""
        st.header("🎭 데모 가이드")
        
        # 데모 개요
        st.markdown("""
        ### 🎯 데모 목적
        포코톤의 핵심 기능을 **5분 내**에 체험할 수 있도록 구성된 완전한 데모 시나리오입니다.
        """)
        
        # 빠른 체험 버튼들
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 빠른 시작", type="primary", use_container_width=True):
                st.session_state.demo_step = "quick_start"
                st.rerun()
        
        with col2:
            if st.button("📖 상세 가이드", use_container_width=True):
                st.session_state.demo_step = "detailed_guide"
                st.rerun()
        
        with col3:
            if st.button("🎬 데모 스크립트", use_container_width=True):
                st.session_state.demo_step = "demo_script"
                st.rerun()
        
        # 선택된 데모 단계에 따라 내용 표시
        demo_step = st.session_state.get('demo_step', 'overview')
        
        if demo_step == "quick_start":
            DemoGuide._render_quick_start()
        elif demo_step == "detailed_guide":
            DemoGuide._render_detailed_guide()
        elif demo_step == "demo_script":
            DemoGuide._render_demo_script()
        else:
            DemoGuide._render_overview()
    
    @staticmethod
    def _render_overview():
        """데모 개요"""
        st.markdown("---")
        st.subheader("📋 데모 개요")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### 🎯 데모 시나리오
            1. **샘플 프로젝트 생성** (30초)
            2. **데이터 탐색** (2분)
            3. **시뮬레이션 실행** (1분)
            4. **결과 분석** (1분 30초)
            
            **총 소요시간: 약 5분**
            """)
        
        with col2:
            st.markdown("""
            #### 📊 포함된 데이터
            - 👥 **5명의 팀원** (다양한 역할)
            - 🚀 **3개의 스프린트** (실제 일정)
            - 📋 **10개의 업무** (현실적 시나리오)
            - 📈 **완전한 분석** 데이터
            """)
        
        # 주요 기능 하이라이트
        st.markdown("### ✨ 체험 가능한 주요 기능")
        
        features = [
            {"icon": "🎯", "title": "스프린트 기반 관리", "desc": "실제 개발 스프린트 환경과 동일한 업무 관리"},
            {"icon": "🔄", "title": "Round Robin 분배", "desc": "공정하고 균형적인 자동 업무 분배 알고리즘"},
            {"icon": "📊", "title": "실시간 시각화", "desc": "Bar Chart, 간트 차트, 균형도 지표 등 다양한 시각화"},
            {"icon": "📤", "title": "데이터 Export", "desc": "CSV, Excel 형태로 분석 결과 내보내기"},
            {"icon": "🛡️", "title": "품질 보장", "desc": "데이터 유효성 검증 및 에러 처리 시스템"},
            {"icon": "🎨", "title": "직관적 UI", "desc": "사용하기 쉬운 탭 기반 인터페이스"}
        ]
        
        cols = st.columns(2)
        for i, feature in enumerate(features):
            with cols[i % 2]:
                st.markdown(f"""
                **{feature['icon']} {feature['title']}**  
                {feature['desc']}
                """)
    
    @staticmethod
    def _render_quick_start():
        """빠른 시작 가이드"""
        st.markdown("---")
        st.subheader("🚀 빠른 시작 가이드")
        
        steps = [
            {
                "number": "1️⃣",
                "title": "샘플 데이터 생성",
                "content": "메인 화면에서 **'🎭 샘플 데이터 생성'** 버튼을 클릭하세요.",
                "time": "30초"
            },
            {
                "number": "2️⃣", 
                "title": "프로젝트 선택",
                "content": "자동으로 생성된 **'🚀 포코톤 데모 프로젝트'**가 선택됩니다.",
                "time": "즉시"
            },
            {
                "number": "3️⃣",
                "title": "데이터 탐색",
                "content": "**팀원 관리**, **업무 관리**, **스프린트 관리** 탭을 둘러보세요.",
                "time": "2분"
            },
            {
                "number": "4️⃣",
                "title": "시뮬레이션 실행",
                "content": "**시뮬레이션** 탭에서 **'🚀 Round Robin 시뮬레이션 실행'** 버튼을 클릭하세요.",
                "time": "1분"
            },
            {
                "number": "5️⃣",
                "title": "결과 확인",
                "content": "**시각화** 및 **Export** 섹션에서 다양한 분석 결과를 확인하세요.",
                "time": "1분 30초"
            }
        ]
        
        for step in steps:
            with st.container():
                col1, col2, col3 = st.columns([1, 8, 1])
                with col1:
                    st.markdown(f"### {step['number']}")
                with col2:
                    st.markdown(f"**{step['title']}**")
                    st.markdown(step['content'])
                with col3:
                    st.markdown(f"⏱️ {step['time']}")
                st.markdown("---")
    
    @staticmethod
    def _render_detailed_guide():
        """상세 가이드"""
        st.markdown("---")
        st.subheader("📖 상세 데모 가이드")
        
        # 탭별 상세 설명
        guide_tabs = st.tabs(["👥 팀원", "📋 업무", "🚀 스프린트", "🎯 시뮬레이션", "📊 시각화"])
        
        with guide_tabs[0]:
            st.markdown("""
            ### 👥 팀원 관리 탭
            
            #### 📋 확인할 내용
            - **5명의 팀원**: 김개발, 박프론트, 이디자인, 최기획, 정QA
            - **다양한 역할**: 백엔드, 프론트엔드, 디자이너, PM, QA
            - **일일 가용시간**: 6~8시간 (역할별 차이)
            
            #### 🔍 주목할 점
            - 역할별 **전문성**을 고려한 시간 배정
            - 실제 개발팀과 **동일한 구성**
            - **균형잡힌** 팀 구조
            """)
        
        with guide_tabs[1]:
            st.markdown("""
            ### 📋 업무 관리 탭
            
            #### 📋 확인할 내용
            - **10개의 현실적 업무**: DB 설계부터 배포까지
            - **다양한 우선순위**: 1~5단계 설정
            - **상세한 업무 내용**: 실제 개발 시나리오
            
            #### 🔍 주목할 점
            - **스프린트별** 업무 분류
            - **연결성** 설정으로 업무 간 의존관계 표현
            - **AI 판단** 필드의 컨텍스트 정보
            """)
        
        with guide_tabs[2]:
            st.markdown("""
            ### 🚀 스프린트 관리 탭
            
            #### 📋 확인할 내용
            - **Sprint 1.0**: 기초설계 (2주)
            - **Sprint 1.1**: 핵심개발 (2주)  
            - **v1.0.0**: 정식릴리즈 (1주)
            
            #### 🔍 주목할 점
            - **현실적인 일정**: 총 5주 프로젝트
            - **명확한 목표**: 스프린트별 핵심 목적
            - **단계적 진행**: 설계 → 개발 → 릴리즈
            """)
        
        with guide_tabs[3]:
            st.markdown("""
            ### 🎯 시뮬레이션 탭
            
            #### 📋 확인할 내용
            - **프로젝트 요약**: 팀원 수, 업무 수, 총 시간
            - **분배 결과**: 팀원별 할당 현황
            - **스프린트별 분배**: 각 스프린트 업무 할당
            
            #### 🔍 주목할 점
            - **자동 유효성 검증**: 실행 전 데이터 체크
            - **즉시 결과**: 클릭 한 번으로 완료
            - **상세한 분석**: 활용률, 균형도 등
            """)
        
        with guide_tabs[4]:
            st.markdown("""
            ### 📊 시각화 탭
            
            #### 📋 확인할 내용
            - **팀원별 업무량**: Bar Chart로 한눈에 비교
            - **간트 차트**: 전체 프로젝트 타임라인
            - **불균형 지표**: 활용률 분포 및 편차
            
            #### 🔍 주목할 점
            - **인터랙티브**: 호버, 확대/축소 가능
            - **색상 구분**: 팀원/역할별 시각적 구분
            - **자동 분석**: AI 기반 권장사항 제시
            """)
    
    @staticmethod
    def _render_demo_script():
        """데모 스크립트"""
        st.markdown("---")
        st.subheader("🎬 프레젠테이션용 데모 스크립트")
        
        # 스크립트 다운로드 버튼
        script_content = get_demo_script()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📄 데모 스크립트 다운로드",
                data=script_content,
                file_name="pokoton_demo_script.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        # 스크립트 미리보기
        with st.expander("📖 스크립트 미리보기", expanded=True):
            st.markdown(script_content)

class FeatureHighlight:
    """기능 하이라이트 컴포넌트"""
    
    @staticmethod
    def render():
        """기능 하이라이트 렌더링"""
        st.markdown("---")
        st.header("✨ 포코톤 주요 기능")
        
        # 3개 컬럼으로 주요 기능 표시
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🎯 스마트 분배
            - **Round Robin 알고리즘**
            - 공정한 업무 분배
            - 팀원별 가용시간 고려
            - 우선순위 기반 할당
            """)
        
        with col2:
            st.markdown("""
            ### 📊 실시간 분석
            - **직관적 시각화**
            - 간트 차트 타임라인
            - 활용률 모니터링
            - 불균형 자동 감지
            """)
        
        with col3:
            st.markdown("""
            ### 🚀 효율성 극대화
            - **원클릭 시뮬레이션**
            - CSV/Excel Export
            - 스프린트 기반 관리
            - 에러 방지 시스템
            """)