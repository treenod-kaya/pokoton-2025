# models/validators.py - 유효성 검증 함수들

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