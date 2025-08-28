# demo_data.py - 데모용 샘플 데이터 생성

import streamlit as st
from database import (
    create_project, add_team_member, add_task, add_sprint
)
from datetime import date, timedelta

def create_demo_project():
    """데모용 프로젝트 생성"""
    try:
        # 1. 프로젝트 생성
        project_id = create_project("🚀 포코톤 데모 프로젝트")
        
        # 2. 스프린트 생성
        today = date.today()
        sprint_data = [
            {
                "name": "Sprint 1.0 - 기초설계",
                "description": "프로젝트 초기 설계 및 환경 구축",
                "start_date": today.strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=14)).strftime("%Y-%m-%d"),
                "status": "active"
            },
            {
                "name": "Sprint 1.1 - 핵심개발",
                "description": "주요 기능 개발 및 구현",
                "start_date": (today + timedelta(days=15)).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=28)).strftime("%Y-%m-%d"),
                "status": "planned"
            },
            {
                "name": "v1.0.0 - 정식릴리즈",
                "description": "최종 테스트 및 배포 준비",
                "start_date": (today + timedelta(days=29)).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=35)).strftime("%Y-%m-%d"),
                "status": "planned"
            }
        ]
        
        for sprint in sprint_data:
            add_sprint(
                project_id=project_id,
                name=sprint["name"],
                description=sprint["description"],
                start_date=sprint["start_date"],
                end_date=sprint["end_date"],
                status=sprint["status"]
            )
        
        # 3. 팀원 생성
        team_members = [
            {"name": "김개발", "role": "백엔드 개발자", "hours": 8.0},
            {"name": "박프론트", "role": "프론트엔드 개발자", "hours": 7.5},
            {"name": "이디자인", "role": "UI/UX 디자이너", "hours": 7.0},
            {"name": "최기획", "role": "프로젝트 매니저", "hours": 6.0},
            {"name": "정QA", "role": "QA 엔지니어", "hours": 8.0}
        ]
        
        for member in team_members:
            add_team_member(
                project_id=project_id,
                name=member["name"],
                role=member["role"],
                available_hours_per_day=member["hours"]
            )
        
        # 4. 업무 생성
        tasks = [
            # Sprint 1.0 업무들
            {
                "attribute": "기능 개발",
                "build_type": "Sprint 1.0 - 기초설계",
                "part_division": "백엔드",
                "priority": 5,
                "item_name": "데이터베이스 스키마 설계",
                "content": "프로젝트에 필요한 데이터베이스 테이블 구조 설계 및 관계 정의",
                "assignee": "김개발",
                "story_points_leader": 8,
                "duration_leader": 16.0,
                "duration_assignee": 14.0,
                "final_hours": 15.0,
                "ai_judgment": "복잡도 높음, 초기 설계 중요",
                "connectivity": ""
            },
            {
                "attribute": "기능 개발",
                "build_type": "Sprint 1.0 - 기초설계",
                "part_division": "프론트엔드",
                "priority": 4,
                "item_name": "UI 컴포넌트 시스템 구축",
                "content": "재사용 가능한 UI 컴포넌트 라이브러리 구축",
                "assignee": "박프론트",
                "story_points_leader": 5,
                "duration_leader": 12.0,
                "duration_assignee": 10.0,
                "final_hours": 11.0,
                "ai_judgment": "표준화 필요, 디자인 시스템 연계",
                "connectivity": ""
            },
            {
                "attribute": "디자인",
                "build_type": "Sprint 1.0 - 기초설계",
                "part_division": "디자인",
                "priority": 4,
                "item_name": "와이어프레임 및 프로토타입",
                "content": "사용자 경험 흐름 설계 및 인터랙티브 프로토타입 제작",
                "assignee": "이디자인",
                "story_points_leader": 8,
                "duration_leader": 20.0,
                "duration_assignee": 18.0,
                "final_hours": 19.0,
                "ai_judgment": "사용자 중심 설계 중요",
                "connectivity": ""
            },
            
            # Sprint 1.1 업무들
            {
                "attribute": "기능 개발",
                "build_type": "Sprint 1.1 - 핵심개발",
                "part_division": "백엔드",
                "priority": 5,
                "item_name": "API 서버 구현",
                "content": "RESTful API 서버 구현 및 인증 시스템 개발",
                "assignee": "김개발",
                "story_points_leader": 13,
                "duration_leader": 24.0,
                "duration_assignee": 20.0,
                "final_hours": 22.0,
                "ai_judgment": "핵심 로직, 보안 고려 필요",
                "connectivity": "1"
            },
            {
                "attribute": "기능 개발",
                "build_type": "Sprint 1.1 - 핵심개발",
                "part_division": "프론트엔드",
                "priority": 4,
                "item_name": "메인 대시보드 개발",
                "content": "사용자 대시보드 화면 구현 및 데이터 시각화",
                "assignee": "박프론트",
                "story_points_leader": 8,
                "duration_leader": 16.0,
                "duration_assignee": 15.0,
                "final_hours": 15.5,
                "ai_judgment": "사용자 인터페이스 최적화 필요",
                "connectivity": "2"
            },
            {
                "attribute": "기능 개발",
                "build_type": "Sprint 1.1 - 핵심개발",
                "part_division": "프론트엔드",
                "priority": 3,
                "item_name": "업무 관리 화면",
                "content": "업무 생성, 수정, 삭제 기능이 있는 관리 화면",
                "assignee": "박프론트",
                "story_points_leader": 5,
                "duration_leader": 14.0,
                "duration_assignee": 12.0,
                "final_hours": 13.0,
                "ai_judgment": "CRUD 기본 기능",
                "connectivity": ""
            },
            
            # v1.0.0 업무들
            {
                "attribute": "테스트",
                "build_type": "v1.0.0 - 정식릴리즈",
                "part_division": "QA",
                "priority": 5,
                "item_name": "통합 테스트 및 버그 수정",
                "content": "전체 시스템 통합 테스트 및 발견된 버그 수정",
                "assignee": "정QA",
                "story_points_leader": 8,
                "duration_leader": 20.0,
                "duration_assignee": 16.0,
                "final_hours": 18.0,
                "ai_judgment": "품질 보증 중요 단계",
                "connectivity": "4"
            },
            {
                "attribute": "문서화",
                "build_type": "v1.0.0 - 정식릴리즈",
                "part_division": "기획",
                "priority": 3,
                "item_name": "사용자 매뉴얼 작성",
                "content": "최종 사용자를 위한 상세 매뉴얼 및 가이드 작성",
                "assignee": "최기획",
                "story_points_leader": 3,
                "duration_leader": 12.0,
                "duration_assignee": 10.0,
                "final_hours": 11.0,
                "ai_judgment": "사용자 편의성 향상",
                "connectivity": ""
            },
            {
                "attribute": "배포",
                "build_type": "v1.0.0 - 정식릴리즈",
                "part_division": "인프라",
                "priority": 4,
                "item_name": "프로덕션 배포 준비",
                "content": "서버 설정, 도메인 연결, SSL 인증서 설정",
                "assignee": "김개발",
                "story_points_leader": 5,
                "duration_leader": 8.0,
                "duration_assignee": 6.0,
                "final_hours": 7.0,
                "ai_judgment": "배포 안정성 중요",
                "connectivity": "7"
            }
        ]
        
        for task in tasks:
            add_task(
                project_id=project_id,
                attribute=task["attribute"],
                build_type=task["build_type"],
                part_division=task["part_division"],
                priority=task["priority"],
                item_name=task["item_name"],
                content=task["content"],
                assignee=task["assignee"],
                story_points_leader=task["story_points_leader"],
                duration_leader=task["duration_leader"],
                duration_assignee=task["duration_assignee"],
                final_hours=task["final_hours"],
                ai_judgment=task["ai_judgment"],
                connectivity=task["connectivity"]
            )
        
        return project_id, "🎉 데모 프로젝트가 성공적으로 생성되었습니다!"
        
    except Exception as e:
        return None, f"❌ 데모 프로젝트 생성 중 오류가 발생했습니다: {str(e)}"

def render_demo_section():
    """데모 섹션 렌더링"""
    st.markdown("---")
    st.header("🎭 데모 체험하기")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 빠른 시작
        완전히 구성된 샘플 프로젝트를 생성하여 
        포코톤의 모든 기능을 바로 체험해보세요.
        
        **포함된 내용:**
        - 👥 5명의 다양한 역할 팀원
        - 📋 10개의 실제적인 업무
        - 🚀 3개의 스프린트 일정
        - 📊 완전한 시뮬레이션 데이터
        """)
    
    with col2:
        st.markdown("""
        ### 📖 데모 순서
        1. **샘플 데이터 생성** 버튼 클릭
        2. 생성된 **"포코톤 데모 프로젝트"** 선택
        3. 각 탭에서 팀원, 업무, 스프린트 확인
        4. **시뮬레이션** 탭에서 분배 실행
        5. **시각화** 및 **Export** 기능 체험
        """)
    
    # 데모 프로젝트 생성 버튼
    st.markdown("### 🎯 데모 프로젝트 생성")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎭 샘플 데이터 생성", type="primary", use_container_width=True):
            with st.spinner("데모 프로젝트를 생성하고 있습니다..."):
                project_id, message = create_demo_project()
                
                if project_id:
                    st.success(message)
                    st.info("💡 **다음 단계**: 사이드바에서 '🚀 포코톤 데모 프로젝트'를 선택하세요!")
                    
                    # 자동으로 생성된 프로젝트 선택
                    st.session_state.current_project_id = project_id
                    st.session_state.current_project_name = "🚀 포코톤 데모 프로젝트"
                    
                    # 성공 후 페이지 새로고침
                    st.rerun()
                else:
                    st.error(message)

def get_demo_script():
    """데모 스크립트 반환"""
    return """
# 🎭 포코톤 데모 스크립트

## 1️⃣ 프로젝트 개요 (2분)
"안녕하세요! 오늘은 AI 기반 프로젝트 일정 관리 플랫폼 '포코톤'을 소개해드리겠습니다."

### 주요 특징
- 🚀 **스프린트 중심** 업무 관리
- 🎯 **Round Robin 알고리즘** 기반 자동 분배
- 📊 **실시간 시각화** 및 분석
- 📤 **다양한 형식** Export 지원

## 2️⃣ 데모 시나리오 (8분)

### A. 프로젝트 설정 (2분)
1. **"샘플 데이터 생성"** 버튼 클릭
2. **포코톤 데모 프로젝트** 자동 선택
3. **프로젝트 정보** 확인

### B. 데이터 탐색 (3분)
1. **👥 팀원 관리** 탭
   - 5명의 다양한 역할 팀원 확인
   - 역할별 일일 가용시간 소개

2. **🚀 스프린트 관리** 탭
   - Sprint 1.0: 기초설계
   - Sprint 1.1: 핵심개발  
   - v1.0.0: 정식릴리즈

3. **📋 업무 관리** 탭
   - 10개의 실제적인 개발 업무
   - 우선순위, 예상시간, 담당자 할당

### C. 시뮬레이션 실행 (3분)
1. **🎯 시뮬레이션** 탭 이동
2. **"Round Robin 시뮬레이션 실행"** 버튼 클릭
3. **결과 분석**
   - 팀원별 업무 분배 현황
   - 스프린트별 업무 할당
   - 활용률 및 균형도 지표

## 3️⃣ 고급 기능 시연 (3분)

### A. 시각화 기능
1. **📊 팀원별 업무량**
   - Bar Chart로 할당시간 비교
   - 활용률 시각화
   - 할당시간 vs 가용시간

2. **📅 간트 차트**
   - 스프린트별 타임라인
   - 팀원별 색상 구분
   - 전체 프로젝트 일정

3. **⚖️ 불균형 지표**
   - 활용률 분포
   - 균형도 메트릭
   - 자동 분석 및 권장사항

### B. Export 기능
1. **📤 결과 Export**
   - CSV 개별 다운로드
   - Excel 통합 리포트
   - 실시간 파일명 생성

## 4️⃣ 실용성 강조 (2분)

### 실제 업무 적용 사례
- **스타트업**: 제한된 인력으로 효율적 업무 분배
- **IT 기업**: 스프린트 기반 애자일 개발 관리
- **프로젝트 매니저**: 객관적 데이터 기반 의사결정
- **팀 리더**: 팀원 과부하 방지 및 균형 분배

### 핵심 가치 제안
1. **⏰ 시간 절약**: 수동 분배 대비 90% 시간 단축
2. **📈 객관성**: 알고리즘 기반 공정한 분배
3. **🔍 투명성**: 모든 과정과 결과 시각화
4. **📊 데이터 기반**: Export를 통한 지속적 개선

## 5️⃣ 마무리 및 Q&A (3분)

### 포코톤의 차별점
- **완전 자동화**: 클릭 한 번으로 최적 분배
- **실시간 분석**: 즉시 확인 가능한 시각화
- **확장성**: 스프린트, 팀원, 업무 무제한 추가
- **품질 보장**: 유효성 검증 및 에러 처리

### 향후 계획
- 실제 캘린더 연동
- AI 기반 업무 시간 예측 고도화
- 팀 협업 기능 확장
- 모바일 앱 지원

---

**"포코톤으로 여러분의 프로젝트 관리를 혁신해보세요!"**

*데모 문의: 포코톤 팀*
"""