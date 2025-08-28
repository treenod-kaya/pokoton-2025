# models.py - 데이터 모델 정의

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Project:
    """프로젝트 데이터 모델"""
    id: Optional[int] = None
    name: str = ""
    created_at: Optional[datetime] = None

@dataclass  
class TeamMember:
    """팀원 데이터 모델"""
    id: Optional[int] = None
    project_id: int = 0
    name: str = ""
    role: str = ""
    available_hours_per_day: float = 8.0
    created_at: Optional[datetime] = None

@dataclass
class Task:
    """업무 데이터 모델 (H4: 13개 필드)"""
    id: Optional[int] = None
    project_id: int = 0
    attribute: str = ""                    # 속성
    build_type: str = ""                   # 적용 빌드
    part_division: str = ""                # 파트 구분  
    priority: int = 3                      # 우선순위 (1-5)
    item_name: str = ""                    # 항목 (업무명)
    content: str = ""                      # 내용
    assignee: str = ""                     # 담당자
    story_points_leader: int = 0           # 스토리 포인트(리더 입력)
    duration_leader: float = 0.0           # 업무 예상 기간 (리더 입력)
    duration_assignee: float = 0.0         # 업무 예상 기간(담당자 입력)
    final_hours: float = 0.0               # 업무 예상 시간(최종)
    ai_judgment: str = ""                  # AI 판단
    connectivity: str = ""                 # 업무 연결성
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """유효성 검증"""
        if not (1 <= self.priority <= 5):
            raise ValueError("우선순위는 1~5 사이의 값이어야 합니다.")
        if not self.item_name.strip():
            raise ValueError("업무명(항목)은 필수입니다.")

def validate_project_name(name: str) -> bool:
    """프로젝트명 유효성 검증"""
    return bool(name and name.strip())

def validate_team_member(name: str, role: str, hours: float) -> bool:
    """팀원 정보 유효성 검증"""
    return (
        bool(name and name.strip()) and
        bool(role and role.strip()) and
        0 < hours <= 24
    )

def validate_task(name: str, difficulty: int, hours: float) -> bool:
    """업무 정보 유효성 검증"""
    return (
        bool(name and name.strip()) and
        1 <= difficulty <= 5 and
        hours > 0
    )