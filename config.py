# config.py - 프로젝트 설정 파일

# 데이터베이스 설정
DATABASE_CONFIG = {
    "db_path": "pokoton.db",
    "tables": {
        "projects": "projects",
        "team_members": "team_members", 
        "tasks": "tasks"
    }
}

# Streamlit 설정
STREAMLIT_CONFIG = {
    "page_title": "포코톤 - 일정 관리 시뮬레이션",
    "page_icon": "📋",
    "layout": "wide"
}

# 업무 관련 상수
TASK_ATTRIBUTES = ["기능개발", "버그수정", "리팩토링", "테스트", "문서화"]

PART_DIVISIONS = ["프론트엔드", "백엔드", "QA", "기획", "디자인"]

PRIORITY_LEVELS = [
    (1, "1-긴급"),
    (2, "2-높음"), 
    (3, "3-보통"),
    (4, "4-낮음"),
    (5, "5-매우낮음")
]

# 기본값
DEFAULT_VALUES = {
    "team_member_hours": 8.0,
    "task_difficulty": 3,
    "task_estimated_hours": 8.0
}

# 파일 경로
FILE_PATHS = {
    "database": "database.py",
    "models": "models.py",
    "utils": "utils.py"
}