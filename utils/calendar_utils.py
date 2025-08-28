# utils/calendar_utils.py - 달력 및 공휴일 관리 유틸리티

from datetime import datetime, date, timedelta
from typing import List, Set
import calendar

class KoreanHolidayCalendar:
    """한국 공휴일 및 주말 관리 클래스"""
    
    # 2025년 한국 공휴일 (고정)
    FIXED_HOLIDAYS_2025 = {
        "2025-01-01": "신정",
        "2025-01-28": "설날 연휴",
        "2025-01-29": "설날",
        "2025-01-30": "설날 연휴",
        "2025-03-01": "삼일절",
        "2025-05-05": "어린이날",
        "2025-05-06": "어린이날 대체공휴일",
        "2025-05-13": "부처님 오신 날",
        "2025-06-06": "현충일",
        "2025-08-15": "광복절",
        "2025-09-28": "추석 연휴",
        "2025-09-29": "추석",
        "2025-09-30": "추석 연휴",
        "2025-10-03": "개천절",
        "2025-10-09": "한글날",
        "2025-12-25": "크리스마스"
    }
    
    # 2024년 공휴일 (참고용)
    FIXED_HOLIDAYS_2024 = {
        "2024-01-01": "신정",
        "2024-02-09": "설날 연휴",
        "2024-02-10": "설날",
        "2024-02-11": "설날 연휴",
        "2024-02-12": "설날 대체공휴일",
        "2024-03-01": "삼일절",
        "2024-05-05": "어린이날",
        "2024-05-06": "어린이날 대체공휴일",
        "2024-05-15": "부처님 오신 날",
        "2024-06-06": "현충일",
        "2024-08-15": "광복절",
        "2024-09-16": "추석 연휴",
        "2024-09-17": "추석",
        "2024-09-18": "추석 연휴",
        "2024-10-03": "개천절",
        "2024-10-09": "한글날",
        "2024-12-25": "크리스마스"
    }
    
    @classmethod
    def get_holidays_for_year(cls, year: int) -> dict:
        """연도별 공휴일 반환"""
        if year == 2025:
            return cls.FIXED_HOLIDAYS_2025
        elif year == 2024:
            return cls.FIXED_HOLIDAYS_2024
        else:
            # 다른 연도는 기본 공휴일만 (확장 가능)
            return {
                f"{year}-01-01": "신정",
                f"{year}-03-01": "삼일절", 
                f"{year}-05-05": "어린이날",
                f"{year}-06-06": "현충일",
                f"{year}-08-15": "광복절",
                f"{year}-10-03": "개천절",
                f"{year}-10-09": "한글날",
                f"{year}-12-25": "크리스마스"
            }
    
    @classmethod
    def is_holiday(cls, target_date: date) -> bool:
        """특정 날짜가 공휴일인지 확인"""
        holidays = cls.get_holidays_for_year(target_date.year)
        date_str = target_date.strftime('%Y-%m-%d')
        return date_str in holidays
    
    @classmethod
    def is_weekend(cls, target_date: date) -> bool:
        """주말(토, 일) 확인"""
        return target_date.weekday() >= 5  # 5=토요일, 6=일요일
    
    @classmethod 
    def is_workday(cls, target_date: date) -> bool:
        """업무일인지 확인 (공휴일, 주말 제외)"""
        return not (cls.is_holiday(target_date) or cls.is_weekend(target_date))
    
    @classmethod
    def get_next_workday(cls, start_date: date) -> date:
        """다음 업무일 찾기"""
        current_date = start_date
        while not cls.is_workday(current_date):
            current_date += timedelta(days=1)
        return current_date
    
    @classmethod
    def add_workdays(cls, start_date: date, workdays: int) -> date:
        """업무일 기준으로 날짜 추가"""
        current_date = start_date
        days_added = 0
        
        while days_added < workdays:
            if cls.is_workday(current_date):
                days_added += 1
            if days_added < workdays:  # 마지막 날이 아니면 다음날로
                current_date += timedelta(days=1)
        
        return current_date
    
    @classmethod
    def calculate_workdays_between(cls, start_date: date, end_date: date) -> int:
        """두 날짜 사이의 업무일 수 계산"""
        if start_date > end_date:
            return 0
            
        workdays = 0
        current_date = start_date
        
        while current_date <= end_date:
            if cls.is_workday(current_date):
                workdays += 1
            current_date += timedelta(days=1)
        
        return workdays
    
    @classmethod
    def get_holiday_name(cls, target_date: date) -> str:
        """공휴일명 반환"""
        holidays = cls.get_holidays_for_year(target_date.year)
        date_str = target_date.strftime('%Y-%m-%d')
        return holidays.get(date_str, "")

class WorkdayCalculator:
    """업무일 기반 일정 계산 클래스"""
    
    @staticmethod
    def calculate_task_schedule(start_date: date, estimated_hours: float, 
                              daily_hours: float = 8.0, exclude_weekends: bool = True,
                              exclude_holidays: bool = True) -> tuple:
        """
        업무 스케줄 계산
        
        Args:
            start_date: 시작일
            estimated_hours: 예상 작업시간
            daily_hours: 일일 작업시간
            exclude_weekends: 주말 제외 여부
            exclude_holidays: 공휴일 제외 여부
            
        Returns:
            (actual_start_date, actual_end_date, total_calendar_days)
        """
        # 1. 실제 시작일 찾기 (첫 업무일)
        actual_start = start_date
        if exclude_weekends or exclude_holidays:
            while True:
                if exclude_weekends and KoreanHolidayCalendar.is_weekend(actual_start):
                    actual_start += timedelta(days=1)
                    continue
                if exclude_holidays and KoreanHolidayCalendar.is_holiday(actual_start):
                    actual_start += timedelta(days=1)
                    continue
                break
        
        # 2. 필요한 업무일 수 계산
        required_workdays = max(1, int(estimated_hours / daily_hours))
        if estimated_hours % daily_hours > 0:
            required_workdays += 1
        
        # 3. 종료일 계산
        if exclude_weekends or exclude_holidays:
            actual_end = KoreanHolidayCalendar.add_workdays(actual_start, required_workdays - 1)
        else:
            actual_end = actual_start + timedelta(days=required_workdays - 1)
        
        # 4. 총 달력 일수
        total_days = (actual_end - actual_start).days + 1
        
        return actual_start, actual_end, total_days

# 편의 함수들
def is_korean_workday(target_date: date) -> bool:
    """한국 기준 업무일 확인"""
    return KoreanHolidayCalendar.is_workday(target_date)

def get_korean_workday_count(start_date: date, end_date: date) -> int:
    """한국 기준 업무일 수 계산"""
    return KoreanHolidayCalendar.calculate_workdays_between(start_date, end_date)

def add_korean_workdays(start_date: date, workdays: int) -> date:
    """한국 기준 업무일 추가"""
    return KoreanHolidayCalendar.add_workdays(start_date, workdays)