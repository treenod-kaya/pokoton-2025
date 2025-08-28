# database.py - 데이터베이스 연결 및 CRUD 함수

import sqlite3
from typing import List, Dict, Optional
from config import DATABASE_CONFIG
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

# 팀원 관련 함수들
def add_team_member(project_id: int, name: str, role: str, available_hours_per_day: float, skill_level: str = "중급", hourly_cost: float = 5.0) -> int:
    """팀원 추가 (H3 개선: 숙련도, 비용 추가)"""
    if not validate_team_member(name, role, available_hours_per_day):
        raise ValueError("유효하지 않은 팀원 정보입니다.")
    
    # 기존 테이블에 새 컬럼이 없으면 기본 필드만 사용
    try:
        member_id = db.execute_query(
            '''INSERT INTO team_members (project_id, name, role, available_hours_per_day, skill_level, hourly_cost)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (project_id, name.strip(), role.strip(), available_hours_per_day, skill_level, hourly_cost),
            fetch="lastrowid"
        )
    except:
        # 기존 테이블 구조 사용 (fallback)
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

# 업무 관련 함수들
def add_task(project_id: int, name: str, difficulty: int, estimated_hours: float) -> int:
    """업무 추가"""
    if not validate_task(name, difficulty, estimated_hours):
        raise ValueError("유효하지 않은 업무 정보입니다.")
    
    task_id = db.execute_query(
        '''INSERT INTO tasks (project_id, name, difficulty, estimated_hours)
           VALUES (?, ?, ?, ?)''',
        (project_id, name.strip(), difficulty, estimated_hours),
        fetch="lastrowid"
    )
    return task_id

def get_tasks(project_id: int) -> List[Dict]:
    """프로젝트의 업무 목록 조회"""
    rows = db.execute_query(
        '''SELECT id, name, difficulty, estimated_hours, created_at
           FROM tasks
           WHERE project_id = ?
           ORDER BY created_at''',
        (project_id,),
        fetch="all"
    )
    
    return [{
        "id": row[0],
        "name": row[1],
        "difficulty": row[2],
        "estimated_hours": row[3],
        "created_at": row[4]
    } for row in rows or []]

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
    
    # 총 예상 시간
    total_hours_result = db.execute_query(
        "SELECT SUM(estimated_hours) FROM tasks WHERE project_id = ?",
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