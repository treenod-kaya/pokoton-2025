# database.py - 데이터베이스 연결 및 CRUD 함수

import sqlite3
from typing import List, Dict, Optional
from config import DATABASE_CONFIG
# Sprint 모델은 임시로 여기서 정의
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date

@dataclass
class Sprint:
    """스프린트/빌드 데이터 모델"""
    id: Optional[int] = None
    project_id: int = 0
    name: str = ""
    description: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "planned"
    created_at: Optional[datetime] = None

def validate_sprint(name: str, start_date: Optional[date], end_date: Optional[date]) -> bool:
    """스프린트 정보 유효성 검증"""
    if not (name and name.strip()):
        return False
    
    if start_date and end_date:
        return start_date <= end_date
    
    return True

# 기존 모델들은 models 모듈에서 import
from models import Project, TeamMember, Task, validate_project_name, validate_team_member, validate_task

class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self):
        self.db_path = DATABASE_CONFIG["db_path"]
    
    def get_connection(self):
        """데이터베이스 연결 반환"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = (), fetch: str = None):
        """쿼리 실행 헬퍼 함수"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            
            if fetch == "one":
                result = cursor.fetchone()
            elif fetch == "all":
                result = cursor.fetchall()
            elif fetch == "lastrowid":
                result = cursor.lastrowid
            else:
                result = None
            
            conn.commit()
            return result
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

# 전역 데이터베이스 매니저 인스턴스
db = DatabaseManager()

# 프로젝트 관련 함수들
def create_project(name: str) -> int:
    """새 프로젝트 생성"""
    if not validate_project_name(name):
        raise ValueError("유효하지 않은 프로젝트명입니다.")
    
    try:
        project_id = db.execute_query(
            "INSERT INTO projects (name) VALUES (?)",
            (name.strip(),),
            fetch="lastrowid"
        )
        return project_id
    except sqlite3.IntegrityError:
        raise ValueError(f"프로젝트 '{name}'은 이미 존재합니다.")

def get_all_projects() -> List[Dict]:
    """모든 프로젝트 조회"""
    rows = db.execute_query(
        "SELECT id, name, created_at FROM projects ORDER BY created_at DESC",
        fetch="all"
    )
    
    return [{"id": row[0], "name": row[1], "created_at": row[2]} for row in rows or []]

def get_project_by_id(project_id: int) -> Optional[Dict]:
    """ID로 프로젝트 조회"""
    row = db.execute_query(
        "SELECT id, name, created_at FROM projects WHERE id = ?",
        (project_id,),
        fetch="one"
    )
    
    if row:
        return {"id": row[0], "name": row[1], "created_at": row[2]}
    return None

def delete_project(project_id: int) -> bool:
    """프로젝트 삭제"""
    result = db.execute_query(
        "DELETE FROM projects WHERE id = ?",
        (project_id,)
    )
    return True  # 삭제 성공

# 스프린트 관련 함수들
def add_sprint(project_id: int, name: str, description: str = "", start_date: str = "", end_date: str = "", status: str = "planned") -> int:
    """스프린트 추가"""
    from datetime import datetime
    
    if not validate_sprint(name, None, None):
        raise ValueError("유효하지 않은 스프린트 정보입니다.")
    
    # 날짜 변환 (빈 문자열이면 None으로)
    start_date_obj = start_date if start_date else None
    end_date_obj = end_date if end_date else None
    
    try:
        sprint_id = db.execute_query(
            '''INSERT INTO sprints (project_id, name, description, start_date, end_date, status)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (project_id, name.strip(), description, start_date_obj, end_date_obj, status),
            fetch="lastrowid"
        )
        return sprint_id
    except sqlite3.IntegrityError:
        raise ValueError(f"스프린트 '{name}'은 이미 존재합니다.")

def get_sprints(project_id: int) -> List[Dict]:
    """프로젝트의 스프린트 목록 조회"""
    rows = db.execute_query(
        '''SELECT id, name, description, start_date, end_date, status, created_at
           FROM sprints
           WHERE project_id = ?
           ORDER BY start_date, created_at''',
        (project_id,),
        fetch="all"
    )
    
    return [{
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "start_date": row[3],
        "end_date": row[4],
        "status": row[5],
        "created_at": row[6]
    } for row in rows or []]

def get_sprint_by_id(sprint_id: int) -> Optional[Dict]:
    """ID로 스프린트 조회"""
    row = db.execute_query(
        '''SELECT id, project_id, name, description, start_date, end_date, status, created_at
           FROM sprints
           WHERE id = ?''',
        (sprint_id,),
        fetch="one"
    )
    
    if row:
        return {
            "id": row[0],
            "project_id": row[1],
            "name": row[2],
            "description": row[3],
            "start_date": row[4],
            "end_date": row[5],
            "status": row[6],
            "created_at": row[7]
        }
    return None

def get_sprint_by_name(project_id: int, name: str) -> Optional[Dict]:
    """이름으로 스프린트 조회"""
    row = db.execute_query(
        '''SELECT id, project_id, name, description, start_date, end_date, status, created_at
           FROM sprints
           WHERE project_id = ? AND name = ?''',
        (project_id, name),
        fetch="one"
    )
    
    if row:
        return {
            "id": row[0],
            "project_id": row[1],
            "name": row[2],
            "description": row[3],
            "start_date": row[4],
            "end_date": row[5],
            "status": row[6],
            "created_at": row[7]
        }
    return None

def update_sprint(sprint_id: int, name: str, description: str = "", start_date: str = "", end_date: str = "", status: str = "planned") -> bool:
    """스프린트 수정"""
    if not validate_sprint(name, None, None):
        raise ValueError("유효하지 않은 스프린트 정보입니다.")
    
    # 날짜 변환 (빈 문자열이면 None으로)
    start_date_obj = start_date if start_date else None
    end_date_obj = end_date if end_date else None
    
    try:
        db.execute_query(
            '''UPDATE sprints SET
                name = ?, description = ?, start_date = ?, end_date = ?, status = ?
               WHERE id = ?''',
            (name.strip(), description, start_date_obj, end_date_obj, status, sprint_id)
        )
        return True
    except sqlite3.IntegrityError:
        raise ValueError(f"스프린트 '{name}'은 이미 존재합니다.")

def delete_sprint(sprint_id: int) -> bool:
    """스프린트 삭제"""
    db.execute_query(
        "DELETE FROM sprints WHERE id = ?",
        (sprint_id,)
    )
    return True

# 팀원 관련 함수들
def add_team_member(project_id: int, name: str, role: str, available_hours_per_day: float) -> int:
    """팀원 추가"""
    if not validate_team_member(name, role, available_hours_per_day):
        raise ValueError("유효하지 않은 팀원 정보입니다.")
    
    member_id = db.execute_query(
        '''INSERT INTO team_members (project_id, name, role, available_hours_per_day)
           VALUES (?, ?, ?, ?)''',
        (project_id, name.strip(), role.strip(), available_hours_per_day),
        fetch="lastrowid"
    )
    return member_id

def get_team_members(project_id: int) -> List[Dict]:
    """프로젝트의 팀원 목록 조회"""
    rows = db.execute_query(
        '''SELECT id, name, role, available_hours_per_day, created_at
           FROM team_members
           WHERE project_id = ?
           ORDER BY created_at''',
        (project_id,),
        fetch="all"
    )
    
    return [{
        "id": row[0],
        "name": row[1],
        "role": row[2],
        "available_hours_per_day": row[3],
        "created_at": row[4]
    } for row in rows or []]

def delete_team_member(member_id: int) -> bool:
    """팀원 삭제"""
    db.execute_query(
        "DELETE FROM team_members WHERE id = ?",
        (member_id,)
    )
    return True

# 업무 관련 함수들 (H4: 13개 필드 지원)
def add_task(project_id: int, attribute: str = "", build_type: str = "", part_division: str = "",
             priority: int = 3, item_name: str = "", content: str = "", assignee: str = "",
             story_points_leader: int = 0, duration_leader: float = 0.0, duration_assignee: float = 0.0,
             final_hours: float = 0.0, ai_judgment: str = "", connectivity: str = "") -> int:
    """업무 추가 (H4: 13개 필드)"""
    if not item_name.strip():
        raise ValueError("업무명(항목)은 필수입니다.")
    if not (1 <= priority <= 5):
        raise ValueError("우선순위는 1~5 사이의 값이어야 합니다.")
    
    task_id = db.execute_query(
        '''INSERT INTO tasks (
            project_id, attribute, build_type, part_division, priority, item_name, content, 
            assignee, story_points_leader, duration_leader, duration_assignee, final_hours, 
            ai_judgment, connectivity
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (project_id, attribute, build_type, part_division, priority, item_name.strip(), content,
         assignee, story_points_leader, duration_leader, duration_assignee, final_hours,
         ai_judgment, connectivity),
        fetch="lastrowid"
    )
    return task_id

def get_tasks(project_id: int) -> List[Dict]:
    """프로젝트의 업무 목록 조회 (H4: 13개 필드)"""
    rows = db.execute_query(
        '''SELECT id, attribute, build_type, part_division, priority, item_name, content,
                  assignee, story_points_leader, duration_leader, duration_assignee, final_hours,
                  ai_judgment, connectivity, created_at
           FROM tasks
           WHERE project_id = ?
           ORDER BY priority, created_at''',
        (project_id,),
        fetch="all"
    )
    
    return [{
        "id": row[0],
        "attribute": row[1],
        "build_type": row[2],
        "part_division": row[3],
        "priority": row[4], 
        "item_name": row[5],
        "content": row[6],
        "assignee": row[7],
        "story_points_leader": row[8],
        "duration_leader": row[9],
        "duration_assignee": row[10],
        "final_hours": row[11],
        "ai_judgment": row[12],
        "connectivity": row[13],
        "created_at": row[14]
    } for row in rows or []]

def update_task(task_id: int, attribute: str = "", build_type: str = "", part_division: str = "",
                priority: int = 3, item_name: str = "", content: str = "", assignee: str = "",
                story_points_leader: int = 0, duration_leader: float = 0.0, duration_assignee: float = 0.0,
                final_hours: float = 0.0, ai_judgment: str = "", connectivity: str = "") -> bool:
    """업무 수정"""
    if not item_name.strip():
        raise ValueError("업무명(항목)은 필수입니다.")
    if not (1 <= priority <= 5):
        raise ValueError("우선순위는 1~5 사이의 값이어야 합니다.")
    
    db.execute_query(
        '''UPDATE tasks SET
            attribute = ?, build_type = ?, part_division = ?, priority = ?, item_name = ?, content = ?,
            assignee = ?, story_points_leader = ?, duration_leader = ?, duration_assignee = ?, 
            final_hours = ?, ai_judgment = ?, connectivity = ?
           WHERE id = ?''',
        (attribute, build_type, part_division, priority, item_name.strip(), content,
         assignee, story_points_leader, duration_leader, duration_assignee, final_hours,
         ai_judgment, connectivity, task_id)
    )
    return True

def get_task_by_id(task_id: int) -> Optional[Dict]:
    """ID로 업무 조회"""
    row = db.execute_query(
        '''SELECT id, attribute, build_type, part_division, priority, item_name, content,
                  assignee, story_points_leader, duration_leader, duration_assignee, final_hours,
                  ai_judgment, connectivity, created_at
           FROM tasks
           WHERE id = ?''',
        (task_id,),
        fetch="one"
    )
    
    if row:
        return {
            "id": row[0],
            "attribute": row[1],
            "build_type": row[2],
            "part_division": row[3],
            "priority": row[4], 
            "item_name": row[5],
            "content": row[6],
            "assignee": row[7],
            "story_points_leader": row[8],
            "duration_leader": row[9],
            "duration_assignee": row[10],
            "final_hours": row[11],
            "ai_judgment": row[12],
            "connectivity": row[13],
            "created_at": row[14]
        }
    return None

def delete_task(task_id: int) -> bool:
    """업무 삭제"""
    db.execute_query(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )
    return True

# 프로젝트 요약 정보
def get_project_summary(project_id: int) -> Dict:
    """프로젝트 요약 정보 조회"""
    # 팀원 수
    team_count_result = db.execute_query(
        "SELECT COUNT(*) FROM team_members WHERE project_id = ?",
        (project_id,),
        fetch="one"
    )
    team_count = team_count_result[0] if team_count_result else 0
    
    # 업무 수
    task_count_result = db.execute_query(
        "SELECT COUNT(*) FROM tasks WHERE project_id = ?",
        (project_id,),
        fetch="one"
    )
    task_count = task_count_result[0] if task_count_result else 0
    
    # 총 예상 시간 (H4: final_hours 컬럼 사용)
    total_hours_result = db.execute_query(
        "SELECT SUM(final_hours) FROM tasks WHERE project_id = ?",
        (project_id,),
        fetch="one"
    )
    total_hours = total_hours_result[0] if total_hours_result and total_hours_result[0] else 0
    
    # 총 가용 시간 (일일)
    total_capacity_result = db.execute_query(
        "SELECT SUM(available_hours_per_day) FROM team_members WHERE project_id = ?",
        (project_id,),
        fetch="one"
    )
    total_daily_capacity = total_capacity_result[0] if total_capacity_result and total_capacity_result[0] else 0
    
    return {
        "team_count": team_count,
        "task_count": task_count,
        "total_estimated_hours": total_hours,
        "total_daily_capacity": total_daily_capacity
    }