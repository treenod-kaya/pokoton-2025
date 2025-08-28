# utils/validation.py - 유효성 검증 및 에러 처리 유틸리티

import streamlit as st
import pandas as pd
from typing import Union, List, Dict, Any
import re
from datetime import date, datetime

class ValidationError(Exception):
    """유효성 검증 오류"""
    pass

class FormValidator:
    """폼 입력 유효성 검증 클래스"""
    
    @staticmethod
    def validate_project_name(name: str) -> bool:
        """프로젝트명 유효성 검증"""
        if not name or not name.strip():
            raise ValidationError("프로젝트명을 입력해주세요.")
        
        if len(name.strip()) < 2:
            raise ValidationError("프로젝트명은 최소 2글자 이상이어야 합니다.")
        
        if len(name.strip()) > 50:
            raise ValidationError("프로젝트명은 50글자를 초과할 수 없습니다.")
        
        # 특수문자 제한
        if re.search(r'[<>:"/\\|?*]', name):
            raise ValidationError("프로젝트명에 특수문자 < > : \" / \\ | ? * 는 사용할 수 없습니다.")
        
        return True
    
    @staticmethod
    def validate_team_member(name: str, role: str, hours: float) -> bool:
        """팀원 정보 유효성 검증"""
        # 이름 검증
        if not name or not name.strip():
            raise ValidationError("팀원명을 입력해주세요.")
        
        if len(name.strip()) < 2:
            raise ValidationError("팀원명은 최소 2글자 이상이어야 합니다.")
        
        if len(name.strip()) > 20:
            raise ValidationError("팀원명은 20글자를 초과할 수 없습니다.")
        
        # 역할 검증
        if not role or not role.strip():
            raise ValidationError("역할을 선택해주세요.")
        
        # 가용시간 검증
        if hours <= 0:
            raise ValidationError("일일 가용시간은 0보다 커야 합니다.")
        
        if hours > 24:
            raise ValidationError("일일 가용시간은 24시간을 초과할 수 없습니다.")
        
        return True
    
    @staticmethod
    def validate_task(name: str, priority: int, hours: float) -> bool:
        """업무 정보 유효성 검증"""
        # 업무명 검증
        if not name or not name.strip():
            raise ValidationError("업무명을 입력해주세요.")
        
        if len(name.strip()) < 2:
            raise ValidationError("업무명은 최소 2글자 이상이어야 합니다.")
        
        if len(name.strip()) > 100:
            raise ValidationError("업무명은 100글자를 초과할 수 없습니다.")
        
        # 우선순위 검증
        if not (1 <= priority <= 5):
            raise ValidationError("우선순위는 1~5 사이의 값이어야 합니다.")
        
        # 예상시간 검증
        if hours < 0:
            raise ValidationError("예상시간은 0 이상이어야 합니다.")
        
        if hours > 1000:
            raise ValidationError("예상시간은 1000시간을 초과할 수 없습니다.")
        
        return True
    
    @staticmethod
    def validate_sprint(name: str, start_date: date = None, end_date: date = None) -> bool:
        """스프린트 정보 유효성 검증"""
        # 스프린트명 검증
        if not name or not name.strip():
            raise ValidationError("스프린트명을 입력해주세요.")
        
        if len(name.strip()) < 2:
            raise ValidationError("스프린트명은 최소 2글자 이상이어야 합니다.")
        
        if len(name.strip()) > 30:
            raise ValidationError("스프린트명은 30글자를 초과할 수 없습니다.")
        
        # 날짜 검증
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("시작일이 종료일보다 늦을 수 없습니다.")
            
            # 스프린트 기간이 너무 길면 경고
            duration = (end_date - start_date).days
            if duration > 365:
                raise ValidationError("스프린트 기간은 1년을 초과할 수 없습니다.")
        
        return True

class DataValidator:
    """데이터 유효성 검증 클래스"""
    
    @staticmethod
    def validate_simulation_requirements(project_id: int) -> Dict[str, Any]:
        """시뮬레이션 실행 요구사항 검증"""
        from database import get_team_members, get_tasks
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "team_count": 0,
            "task_count": 0
        }
        
        # 팀원 검증
        team_members = get_team_members(project_id)
        validation_result["team_count"] = len(team_members)
        
        if len(team_members) == 0:
            validation_result["valid"] = False
            validation_result["errors"].append("팀원이 없습니다. 최소 1명의 팀원을 추가해주세요.")
        
        # 업무 검증
        tasks = get_tasks(project_id)
        validation_result["task_count"] = len(tasks)
        
        if len(tasks) == 0:
            validation_result["valid"] = False
            validation_result["errors"].append("업무가 없습니다. 최소 1개의 업무를 추가해주세요.")
        
        # 경고사항 체크
        if len(team_members) > len(tasks):
            validation_result["warnings"].append(f"팀원 수({len(team_members)})가 업무 수({len(tasks)})보다 많습니다.")
        
        # 업무 시간 검증
        total_hours = sum(task['final_hours'] for task in tasks)
        total_capacity = sum(member['available_hours_per_day'] for member in team_members)
        
        if total_hours == 0:
            validation_result["warnings"].append("모든 업무의 예상시간이 0시간입니다.")
        
        if total_capacity == 0:
            validation_result["valid"] = False
            validation_result["errors"].append("팀원들의 총 가용시간이 0입니다.")
        
        return validation_result

class ErrorHandler:
    """에러 처리 클래스"""
    
    @staticmethod
    def handle_validation_error(error: ValidationError, context: str = ""):
        """유효성 검증 오류 처리"""
        error_msg = f"❌ {str(error)}"
        if context:
            error_msg = f"❌ [{context}] {str(error)}"
        
        st.error(error_msg)
        return False
    
    @staticmethod
    def handle_database_error(error: Exception, operation: str = "데이터베이스 작업"):
        """데이터베이스 오류 처리"""
        error_msg = f"❌ {operation} 중 오류가 발생했습니다: {str(error)}"
        st.error(error_msg)
        
        # 개발 모드에서는 상세 오류 정보 표시
        if st.session_state.get('debug_mode', False):
            st.exception(error)
        
        return False
    
    @staticmethod
    def handle_simulation_error(error: Exception):
        """시뮬레이션 오류 처리"""
        error_msg = f"❌ 시뮬레이션 실행 중 오류가 발생했습니다: {str(error)}"
        st.error(error_msg)
        
        # 일반적인 해결 방법 제시
        with st.expander("🔧 문제 해결 방법"):
            st.markdown("""
            ### 가능한 해결 방법:
            1. **데이터 확인**: 팀원과 업무 정보가 올바르게 입력되었는지 확인
            2. **시간 정보**: 업무 예상시간과 팀원 가용시간이 적절한지 확인
            3. **페이지 새로고침**: 브라우저를 새로고침한 후 다시 시도
            4. **데이터 초기화**: 개발 도구에서 데이터베이스를 초기화한 후 다시 입력
            """)
        
        return False
    
    @staticmethod
    def safe_execute(func, *args, error_context: str = "", **kwargs):
        """안전한 함수 실행"""
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return ErrorHandler.handle_validation_error(e, error_context)
        except Exception as e:
            return ErrorHandler.handle_database_error(e, error_context)

def validate_form_input(validator_func, *args, context: str = ""):
    """폼 입력 유효성 검증 데코레이터"""
    try:
        return validator_func(*args)
    except ValidationError as e:
        ErrorHandler.handle_validation_error(e, context)
        return False
    except Exception as e:
        ErrorHandler.handle_database_error(e, context)
        return False

# 공통 유효성 검증 함수들
def is_valid_email(email: str) -> bool:
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone: str) -> bool:
    """전화번호 형식 검증"""
    pattern = r'^[0-9\-\+\(\)\s]+$'
    return re.match(pattern, phone) is not None

def sanitize_filename(filename: str) -> str:
    """파일명 정리"""
    # 특수문자 제거
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 공백을 언더스코어로 변경
    filename = re.sub(r'\s+', '_', filename)
    return filename