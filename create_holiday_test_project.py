# -*- coding: utf-8 -*-
# create_holiday_test_project.py - 한국 공휴일 검증용 샘플 프로젝트 생성

from database import create_project, add_team_member, add_task, add_sprint
from datetime import date, timedelta
import time

def create_holiday_verification_project():
    """한국 공휴일 제외 일정 분배 검증용 프로젝트 생성"""
    
    try:
        # 1. 테스트 프로젝트 생성
        project_name = f"Holiday Test Project {int(time.time())}"
        project_id = create_project(project_name)
        print(f"[OK] Test project created (ID: {project_id})")
        
        # 2. 팀원 생성 (3명, 다양한 가용시간)
        team_members = [
            {"name": "김개발", "role": "백엔드 개발자", "hours": 8.0},
            {"name": "이디자인", "role": "UI/UX 디자이너", "hours": 6.0},
            {"name": "박테스트", "role": "QA 엔지니어", "hours": 7.0}
        ]
        
        for member in team_members:
            add_team_member(
                project_id=project_id,
                name=member["name"],
                role=member["role"],
                available_hours_per_day=member["hours"]
            )
        print(f"[OK] Team members created: {len(team_members)}")
        
        # 3. 한국 공휴일이 포함된 스프린트 생성
        # 2025년 설날 연휴 포함 (1월 28일~30일)
        # 2025년 어린이날 포함 (5월 5일~6일)
        
        today = date.today()
        
        sprints = [
            {
                "name": "Sprint 1 - 설날 연휴 포함",
                "description": "설날 연휴가 포함된 스프린트 (1/28~1/30 연휴)",
                "start_date": "2025-01-20",  # 월요일 시작
                "end_date": "2025-02-07"     # 금요일 종료 (18일간, 설날 연휴 3일 포함)
            },
            {
                "name": "Sprint 2 - 어린이날 연휴 포함", 
                "description": "어린이날 연휴가 포함된 스프린트 (5/5~5/6 연휴)",
                "start_date": "2025-04-28",  # 월요일 시작
                "end_date": "2025-05-16"     # 금요일 종료 (18일간, 어린이날 연휴 2일 포함)
            },
            {
                "name": "Sprint 3 - 추석 연휴 포함",
                "description": "추석 연휴가 포함된 스프린트 (9/28~9/30 연휴)",
                "start_date": "2025-09-22",  # 월요일 시작
                "end_date": "2025-10-10"     # 금요일 종료 (18일간, 추석 연휴 3일 포함)
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
        print(f"[OK] Sprints created: {len(sprints)} (with Korean holidays)")
        
        # 4. 다양한 시간의 업무 생성 (공휴일 제외 검증용)
        tasks = [
            # Sprint 1 업무들 (설날 연휴 고려)
            {
                "attribute": "개발", "build_type": "Sprint 1 - 설날 연휴 포함",
                "part_division": "백엔드", "priority": 1, "item_name": "사용자 인증 API",
                "content": "로그인/회원가입 API 개발", "assignee": "",
                "story_points_leader": 8, "duration_leader": 24.0, "final_hours": 24.0
            },
            {
                "attribute": "설계", "build_type": "Sprint 1 - 설날 연휴 포함",
                "part_division": "전체", "priority": 2, "item_name": "데이터베이스 설계",
                "content": "전체 시스템 DB 구조 설계", "assignee": "",
                "story_points_leader": 5, "duration_leader": 16.0, "final_hours": 16.0
            },
            {
                "attribute": "디자인", "build_type": "Sprint 1 - 설날 연휴 포함",
                "part_division": "UI/UX", "priority": 3, "item_name": "메인 화면 디자인",
                "content": "메인 화면 UI/UX 디자인 작업", "assignee": "",
                "story_points_leader": 3, "duration_leader": 12.0, "final_hours": 12.0
            },
            
            # Sprint 2 업무들 (어린이날 연휴 고려)
            {
                "attribute": "개발", "build_type": "Sprint 2 - 어린이날 연휴 포함",
                "part_division": "백엔드", "priority": 1, "item_name": "데이터 처리 엔진",
                "content": "핵심 데이터 처리 로직 개발", "assignee": "",
                "story_points_leader": 13, "duration_leader": 32.0, "final_hours": 32.0
            },
            {
                "attribute": "개발", "build_type": "Sprint 2 - 어린이날 연휴 포함",
                "part_division": "프론트엔드", "priority": 2, "item_name": "대시보드 구현",
                "content": "사용자 대시보드 개발", "assignee": "",
                "story_points_leader": 8, "duration_leader": 20.0, "final_hours": 20.0
            },
            {
                "attribute": "테스트", "build_type": "Sprint 2 - 어린이날 연휴 포함",
                "part_division": "QA", "priority": 3, "item_name": "기능 테스트",
                "content": "개발된 기능들 테스트", "assignee": "",
                "story_points_leader": 5, "duration_leader": 14.0, "final_hours": 14.0
            },
            
            # Sprint 3 업무들 (추석 연휴 고려)
            {
                "attribute": "개발", "build_type": "Sprint 3 - 추석 연휴 포함",
                "part_division": "백엔드", "priority": 1, "item_name": "성능 최적화",
                "content": "시스템 성능 최적화 작업", "assignee": "",
                "story_points_leader": 8, "duration_leader": 28.0, "final_hours": 28.0
            },
            {
                "attribute": "배포", "build_type": "Sprint 3 - 추석 연휴 포함",
                "part_division": "전체", "priority": 2, "item_name": "운영 배포",
                "content": "운영 환경 배포 및 설정", "assignee": "",
                "story_points_leader": 5, "duration_leader": 16.0, "final_hours": 16.0
            },
            {
                "attribute": "테스트", "build_type": "Sprint 3 - 추석 연휴 포함",
                "part_division": "QA", "priority": 3, "item_name": "통합 테스트",
                "content": "전체 시스템 통합 테스트", "assignee": "",
                "story_points_leader": 8, "duration_leader": 21.0, "final_hours": 21.0
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
        
        print(f"[OK] Tasks created: {len(tasks)}")
        
        print(f"\nSUCCESS: Holiday verification project created successfully!")
        print(f"   - Project ID: {project_id}")
        print(f"   - Team members: {len(team_members)} (다양한 가용시간)")
        print(f"   - Sprints: {len(sprints)} (한국 공휴일 포함)")
        print(f"   - Tasks: {len(tasks)} (총 {sum(t['final_hours'] for t in tasks)}시간)")
        
        print(f"\n[HOLIDAY CHECK] 한국 공휴일 검증 포인트:")
        print(f"   * Sprint 1: 설날 연휴 (1/28~1/30) - 3일간 공휴일")
        print(f"   * Sprint 2: 어린이날 연휴 (5/5~5/6) - 2일간 공휴일") 
        print(f"   * Sprint 3: 추석 연휴 (9/28~9/30) - 3일간 공휴일")
        print(f"   * 각 스프린트마다 주말도 자동 제외됨")
        
        print(f"\n[VERIFY] 확인할 사항:")
        print(f"   - 공휴일이 업무일에서 제외되었는가?")
        print(f"   - 주말이 업무일에서 제외되었는가?")
        print(f"   - 일일 작업시간이 8시간을 초과하지 않는가?")
        print(f"   - 업무 분배가 Round Robin으로 공정하게 되었는가?")
        
        return project_id, "한국 공휴일 검증용 프로젝트 생성 완료"
        
    except Exception as e:
        print(f"ERROR: Test project creation failed: {str(e)}")
        return None, f"오류: {str(e)}"

if __name__ == "__main__":
    create_holiday_verification_project()