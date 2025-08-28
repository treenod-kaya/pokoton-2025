# init_db.py - SQLite 데이터베이스 초기화 스크립트

import sqlite3
import os
from config import DATABASE_CONFIG

def create_database():
    """데이터베이스 파일 생성"""
    db_path = DATABASE_CONFIG["db_path"]
    
    if os.path.exists(db_path):
        print(f"기존 데이터베이스 파일 발견: {db_path}")
        return
    
    # 빈 데이터베이스 파일 생성
    conn = sqlite3.connect(db_path)
    conn.close()
    print(f"새 데이터베이스 파일 생성: {db_path}")

def create_tables():
    """데이터베이스 테이블 생성"""
    db_path = DATABASE_CONFIG["db_path"]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 프로젝트 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print(">> projects 테이블 생성 완룼")
    
    # 팀원 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            available_hours_per_day REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    ''')
    print(">> team_members 테이블 생성 완룼")
    
    # 업무 테이블 (H4: 13개 필드로 확장)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            attribute TEXT DEFAULT '',                    -- 속성
            build_type TEXT DEFAULT '',                   -- 적용 빌드
            part_division TEXT DEFAULT '',                -- 파트 구분
            priority INTEGER DEFAULT 3,                   -- 우선순위 (1-5)
            item_name TEXT NOT NULL,                      -- 항목 (업무명)
            content TEXT DEFAULT '',                      -- 내용
            assignee TEXT DEFAULT '',                     -- 담당자
            story_points_leader INTEGER DEFAULT 0,        -- 스토리 포인트(리더 입력)
            duration_leader REAL DEFAULT 0.0,            -- 업무 예상 기간 (리더 입력)
            duration_assignee REAL DEFAULT 0.0,          -- 업무 예상 기간(담당자 입력)
            final_hours REAL DEFAULT 0.0,                -- 업무 예상 시간(최종)
            ai_judgment TEXT DEFAULT '',                  -- AI 판단
            connectivity TEXT DEFAULT '',                 -- 업무 연결성
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    ''')
    print(">> tasks 테이블 생성 완룼")
    
    conn.commit()
    conn.close()

def insert_sample_data():
    """샘플 데이터 삽입 (선택사항)"""
    db_path = DATABASE_CONFIG["db_path"]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 샘플 프로젝트
        cursor.execute("INSERT INTO projects (name) VALUES (?)", ("샘플 프로젝트",))
        project_id = cursor.lastrowid
        
        # 샘플 팀원
        sample_members = [
            (project_id, "김개발", "백엔드 개발자", 8.0),
            (project_id, "박디자인", "UI/UX 디자이너", 7.0),
            (project_id, "이기획", "프로덕트 매니저", 6.0)
        ]
        
        cursor.executemany(
            "INSERT INTO team_members (project_id, name, role, available_hours_per_day) VALUES (?, ?, ?, ?)",
            sample_members
        )
        
        # 샘플 업무 (H4: 13개 필드)
        sample_tasks = [
            (project_id, "기능 개발", "Sprint 1.0", "백엔드", 4, "로그인 기능 개발", "사용자 인증 시스템 구축", "김개발", 8, 20.0, 16.0, 16.0, "복잡도 중간", "회원가입과 연관"),
            (project_id, "기능 개발", "Sprint 1.0", "프론트엔드", 3, "메인 페이지 디자인", "랜딩 페이지 UI/UX 작업", "이디자인", 5, 15.0, 12.0, 12.0, "표준적인 작업", "네비게이션과 연관"),
            (project_id, "문서화", "Sprint 1.0", "기획", 2, "사용자 요구사항 분석", "프로젝트 요구사항 정리", "박기획", 3, 10.0, 8.0, 8.0, "간단한 작업", "전체 기획과 연관")
        ]
        
        cursor.executemany(
            '''INSERT INTO tasks (
                project_id, attribute, build_type, part_division, priority, item_name, content,
                assignee, story_points_leader, duration_leader, duration_assignee, final_hours,
                ai_judgment, connectivity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            sample_tasks
        )
        
        conn.commit()
        print(">> 샘플 데이터 삽입 완료")
        
    except sqlite3.IntegrityError as e:
        print(f">> 샘플 데이터가 이미 존재합니다: {e}")
    
    conn.close()

def check_database_status():
    """데이터베이스 상태 확인"""
    db_path = DATABASE_CONFIG["db_path"]
    
    if not os.path.exists(db_path):
        print(">> 데이터베이스 파일이 존재하지 않습니다.")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블 목록 확인
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f">> 데이터베이스 상태: {db_path}")
    print(f">> 테이블 수: {len(tables)}")
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  - {table_name}: {count}개 레코드")
    
    conn.close()
    return True

def initialize_database(with_sample_data=False):
    """전체 데이터베이스 초기화 프로세스"""
    print(">> 데이터베이스 초기화 시작...")
    
    # 1. 데이터베이스 파일 생성
    create_database()
    
    # 2. 테이블 생성
    create_tables()
    
    # 3. 샘플 데이터 삽입 (선택)
    if with_sample_data:
        insert_sample_data()
    
    # 4. 상태 확인
    check_database_status()
    
    print(">> 데이터베이스 초기화 완료!")

if __name__ == "__main__":
    # 스크립트 직접 실행 시
    import sys
    
    with_sample = "--with-sample" in sys.argv
    initialize_database(with_sample_data=with_sample)
    
    print(f"\n>> 사용법:")
    print(f"  기본 초기화: python init_db.py")
    print(f"  샘플 데이터 포함: python init_db.py --with-sample")