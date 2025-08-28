# test_simulation_data.py - 시뮬레이션 테스트용 풍부한 더미 데이터

from database import create_project, add_team_member, add_task, add_sprint
from datetime import date, timedelta

def create_comprehensive_test_project():
    """자동 업무 분배 기능 검증용 종합 테스트 프로젝트 생성"""
    
    try:
        # 1. 테스트 프로젝트 생성
        import time
        project_name = f"Auto-Distribution Test Project {int(time.time())}"
        project_id = create_project(project_name)
        print(f"Test project created successfully (ID: {project_id})")
        
        # 2. 다양한 역할의 팀원 생성 (5명)
        team_members = [
            {"name": "김백엔드", "role": "백엔드 개발자", "hours": 8.0},
            {"name": "이프론트", "role": "프론트엔드 개발자", "hours": 7.5},
            {"name": "박풀스택", "role": "풀스택 개발자", "hours": 8.0},
            {"name": "정디자인", "role": "UI/UX 디자이너", "hours": 6.0},
            {"name": "최QA", "role": "QA 엔지니어", "hours": 7.0}
        ]
        
        for member in team_members:
            add_team_member(
                project_id=project_id,
                name=member["name"],
                role=member["role"],
                available_hours_per_day=member["hours"]
            )
        print(f"Team members created: {len(team_members)}")
        
        # 3. 스프린트 생성 (3개 스프린트, 실제 날짜)
        today = date.today()
        sprints = [
            {
                "name": "Sprint 1.0 - 기초 설계",
                "description": "프로젝트 기초 구조 및 설계",
                "start_date": today.strftime('%Y-%m-%d'),
                "end_date": (today + timedelta(days=14)).strftime('%Y-%m-%d')
            },
            {
                "name": "Sprint 2.0 - 핵심 기능",
                "description": "핵심 기능 개발 및 구현",
                "start_date": (today + timedelta(days=14)).strftime('%Y-%m-%d'),
                "end_date": (today + timedelta(days=28)).strftime('%Y-%m-%d')
            },
            {
                "name": "Sprint 3.0 - 완성 및 테스트",
                "description": "기능 완성 및 통합 테스트",
                "start_date": (today + timedelta(days=28)).strftime('%Y-%m-%d'),
                "end_date": (today + timedelta(days=42)).strftime('%Y-%m-%d')
            }
        ]
        
        for sprint in sprints:
            add_sprint(
                project_id=project_id,
                name=sprint["name"],
                description=sprint["description"],
                start_date=sprint["start_date"],
                end_date=sprint["end_date"]
            )
        print(f"Sprints created: {len(sprints)}")
        
        # 4. 다양한 우선순위와 시간의 업무 생성 (15개)
        tasks = [
            # Sprint 1.0 업무들 (우선순위 높음)
            {
                "attribute": "설계", "build_type": "Sprint 1.0 - 기초 설계",
                "part_division": "백엔드", "priority": 1, "item_name": "데이터베이스 설계",
                "content": "전체 시스템의 데이터베이스 구조 설계", "assignee": "", 
                "story_points_leader": 13, "duration_leader": 16.0, "final_hours": 16.0
            },
            {
                "attribute": "설계", "build_type": "Sprint 1.0 - 기초 설계",
                "part_division": "프론트엔드", "priority": 1, "item_name": "UI/UX 와이어프레임",
                "content": "사용자 인터페이스 설계 및 와이어프레임 작성", "assignee": "",
                "story_points_leader": 8, "duration_leader": 12.0, "final_hours": 12.0
            },
            {
                "attribute": "설계", "build_type": "Sprint 1.0 - 기초 설계", 
                "part_division": "전체", "priority": 2, "item_name": "시스템 아키텍처 정의",
                "content": "전체 시스템 아키텍처 및 기술 스택 결정", "assignee": "",
                "story_points_leader": 5, "duration_leader": 8.0, "final_hours": 8.0
            },
            {
                "attribute": "개발환경", "build_type": "Sprint 1.0 - 기초 설계",
                "part_division": "백엔드", "priority": 2, "item_name": "개발환경 셋업",
                "content": "백엔드 개발환경 구축 및 CI/CD 파이프라인", "assignee": "",
                "story_points_leader": 8, "duration_leader": 10.0, "final_hours": 10.0
            },
            {
                "attribute": "개발환경", "build_type": "Sprint 1.0 - 기초 설계",
                "part_division": "프론트엔드", "priority": 3, "item_name": "프론트엔드 셋업",
                "content": "React 프로젝트 초기 설정 및 패키지 구성", "assignee": "",
                "story_points_leader": 5, "duration_leader": 6.0, "final_hours": 6.0
            },
            
            # Sprint 2.0 업무들 (핵심 기능)
            {
                "attribute": "기능 개발", "build_type": "Sprint 2.0 - 핵심 기능",
                "part_division": "백엔드", "priority": 1, "item_name": "사용자 인증 API",
                "content": "로그인, 회원가입, JWT 토큰 관리 API 개발", "assignee": "",
                "story_points_leader": 13, "duration_leader": 20.0, "final_hours": 20.0
            },
            {
                "attribute": "기능 개발", "build_type": "Sprint 2.0 - 핵심 기능",
                "part_division": "프론트엔드", "priority": 1, "item_name": "로그인 화면",
                "content": "사용자 로그인 및 회원가입 UI 구현", "assignee": "",
                "story_points_leader": 8, "duration_leader": 14.0, "final_hours": 14.0
            },
            {
                "attribute": "기능 개발", "build_type": "Sprint 2.0 - 핵심 기능",
                "part_division": "백엔드", "priority": 2, "item_name": "데이터 CRUD API",
                "content": "핵심 데이터 생성, 읽기, 수정, 삭제 API", "assignee": "",
                "story_points_leader": 21, "duration_leader": 24.0, "final_hours": 24.0
            },
            {
                "attribute": "기능 개발", "build_type": "Sprint 2.0 - 핵심 기능",
                "part_division": "프론트엔드", "priority": 2, "item_name": "메인 대시보드",
                "content": "사용자 대시보드 UI 및 데이터 시각화", "assignee": "",
                "story_points_leader": 13, "duration_leader": 18.0, "final_hours": 18.0
            },
            {
                "attribute": "디자인", "build_type": "Sprint 2.0 - 핵심 기능",
                "part_division": "디자인", "priority": 3, "item_name": "브랜딩 및 아이콘",
                "content": "브랜드 컬러, 로고, 아이콘 세트 디자인", "assignee": "",
                "story_points_leader": 8, "duration_leader": 12.0, "final_hours": 12.0
            },
            
            # Sprint 3.0 업무들 (완성 및 테스트)
            {
                "attribute": "테스트", "build_type": "Sprint 3.0 - 완성 및 테스트",
                "part_division": "QA", "priority": 1, "item_name": "통합 테스트",
                "content": "전체 시스템 통합 테스트 및 시나리오 검증", "assignee": "",
                "story_points_leader": 13, "duration_leader": 16.0, "final_hours": 16.0
            },
            {
                "attribute": "테스트", "build_type": "Sprint 3.0 - 완성 및 테스트",
                "part_division": "QA", "priority": 2, "item_name": "성능 테스트",
                "content": "시스템 성능 및 부하 테스트", "assignee": "",
                "story_points_leader": 8, "duration_leader": 12.0, "final_hours": 12.0
            },
            {
                "attribute": "버그수정", "build_type": "Sprint 3.0 - 완성 및 테스트", 
                "part_division": "전체", "priority": 1, "item_name": "크리티컬 버그 수정",
                "content": "테스트 중 발견된 중요 버그들 수정", "assignee": "",
                "story_points_leader": 8, "duration_leader": 10.0, "final_hours": 10.0
            },
            {
                "attribute": "배포", "build_type": "Sprint 3.0 - 완성 및 테스트",
                "part_division": "백엔드", "priority": 3, "item_name": "운영 배포",
                "content": "운영 서버 배포 및 모니터링 설정", "assignee": "",
                "story_points_leader": 5, "duration_leader": 8.0, "final_hours": 8.0
            },
            {
                "attribute": "문서화", "build_type": "Sprint 3.0 - 완성 및 테스트",
                "part_division": "전체", "priority": 4, "item_name": "사용자 매뉴얼",
                "content": "최종 사용자 매뉴얼 및 개발 문서 작성", "assignee": "",
                "story_points_leader": 3, "duration_leader": 6.0, "final_hours": 6.0
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
                duration_assignee=0.0,
                final_hours=task["final_hours"],
                ai_judgment="자동생성",
                connectivity=""
            )
        
        print(f"Tasks created: {len(tasks)}")
        
        print(f"\nComprehensive test project created successfully!")
        print(f"   - Project ID: {project_id}")
        print(f"   - Team members: {len(team_members)} (various roles)")
        print(f"   - Sprints: {len(sprints)} (42 days)")
        print(f"   - Tasks: {len(tasks)} (priority 1-4, total 212 hours)")
        print(f"\nAutomatic distribution test points:")
        print(f"   * Round Robin algorithm for fair distribution")
        print(f"   * Priority-based sorting (1->4)")
        print(f"   * Story points consideration")
        print(f"   * Weekend/holiday exclusion")
        print(f"   * Sprint-based scheduling")
        
        return project_id, "종합 테스트 프로젝트 생성 완료"
        
    except Exception as e:
        print(f"Test project creation failed: {str(e)}")
        return None, f"오류: {str(e)}"

if __name__ == "__main__":
    create_comprehensive_test_project()