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
    """업무 데이터 모델"""
    id: Optional[int] = None
    project_id: int = 0
    name: str = ""
    difficulty: int = 3  # 1~5
    estimated_hours: float = 8.0
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """유효성 검증"""
        if not (1 <= self.difficulty <= 5):
            raise ValueError("난이도는 1~5 사이의 값이어야 합니다.")
        if self.estimated_hours <= 0:
            raise ValueError("예상 시간은 0보다 큰 값이어야 합니다.")

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