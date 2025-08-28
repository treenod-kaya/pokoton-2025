# simulation.py - H5 시뮬레이션 로직

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import math
from database import get_team_members, get_tasks

@dataclass
class TaskAssignment:
    """업무 할당 결과"""
    task_id: int
    task_name: str
    assignee_name: str
    estimated_hours: float
    priority: int
    start_day: int
    end_day: int
    
@dataclass
class TeamMemberWorkload:
    """팀원별 업무량"""
    member_id: int
    member_name: str
    role: str
    daily_capacity: float
    total_assigned_hours: float
    assigned_tasks: List[TaskAssignment]
    utilization_rate: float  # 활용률 (%)
    estimated_days: int

@dataclass
class SimulationResult:
    """시뮬레이션 결과"""
    project_id: int
    total_tasks: int
    total_estimated_hours: float
    team_workloads: List[TeamMemberWorkload]
    estimated_completion_days: int
    round_robin_assignments: List[TaskAssignment]
    created_at: datetime

class RoundRobinSimulator:
    """Round Robin 알고리즘 기반 업무 분배 시뮬레이터"""
    
    def __init__(self, project_id: int):
        self.project_id = project_id
        self.team_members = get_team_members(project_id)
        self.tasks = get_tasks(project_id)
    
    def simulate(self) -> SimulationResult:
        """메인 시뮬레이션 실행"""
        if not self.team_members:
            raise ValueError("팀원이 없습니다. 팀원을 먼저 추가해주세요.")
        
        if not self.tasks:
            raise ValueError("업무가 없습니다. 업무를 먼저 추가해주세요.")
        
        # 1. 업무를 우선순위별로 정렬
        sorted_tasks = sorted(self.tasks, key=lambda x: (x['priority'], x['id']))
        
        # 2. Round Robin 방식으로 업무 분배
        assignments = self._distribute_tasks_round_robin(sorted_tasks)
        
        # 3. 팀원별 업무량 계산
        team_workloads = self._calculate_team_workloads(assignments)
        
        # 4. 전체 프로젝트 완료 예상일 계산
        estimated_days = self._calculate_project_timeline(team_workloads)
        
        # 5. 총 업무 시간 계산
        total_hours = sum(task['final_hours'] for task in self.tasks)
        
        return SimulationResult(
            project_id=self.project_id,
            total_tasks=len(self.tasks),
            total_estimated_hours=total_hours,
            team_workloads=team_workloads,
            estimated_completion_days=estimated_days,
            round_robin_assignments=assignments,
            created_at=datetime.now()
        )
    
    def _distribute_tasks_round_robin(self, sorted_tasks: List[Dict]) -> List[TaskAssignment]:
        """Round Robin 방식으로 업무 분배"""
        assignments = []
        member_index = 0
        member_daily_hours = {member['id']: 0.0 for member in self.team_members}
        member_current_day = {member['id']: 1 for member in self.team_members}
        
        for task in sorted_tasks:
            # 현재 순서의 팀원 선택
            current_member = self.team_members[member_index % len(self.team_members)]
            task_hours = task['final_hours']
            
            # 업무 시작일 계산
            start_day = member_current_day[current_member['id']]
            
            # 업무 완료에 필요한 일수 계산
            daily_capacity = current_member['available_hours_per_day']
            required_days = math.ceil(task_hours / daily_capacity)
            end_day = start_day + required_days - 1
            
            # 할당 생성
            assignment = TaskAssignment(
                task_id=task['id'],
                task_name=task['item_name'],
                assignee_name=current_member['name'],
                estimated_hours=task_hours,
                priority=task['priority'],
                start_day=start_day,
                end_day=end_day
            )
            
            assignments.append(assignment)
            
            # 팀원의 다음 업무 시작일 업데이트
            member_current_day[current_member['id']] = end_day + 1
            member_daily_hours[current_member['id']] += task_hours
            
            # 다음 팀원으로 순환
            member_index += 1
        
        return assignments
    
    def _calculate_team_workloads(self, assignments: List[TaskAssignment]) -> List[TeamMemberWorkload]:
        """팀원별 업무량 계산"""
        workloads = []
        
        for member in self.team_members:
            # 해당 팀원에게 할당된 업무들
            member_assignments = [a for a in assignments if a.assignee_name == member['name']]
            
            # 총 할당 시간
            total_hours = sum(a.estimated_hours for a in member_assignments)
            
            # 예상 소요 일수 (연속적이지 않을 수 있으므로 마지막 업무의 종료일로 계산)
            estimated_days = max([a.end_day for a in member_assignments]) if member_assignments else 0
            
            # 활용률 계산 (할당된 총 시간 / (일일 가용시간 × 예상일수))
            if estimated_days > 0:
                max_possible_hours = member['available_hours_per_day'] * estimated_days
                utilization_rate = (total_hours / max_possible_hours) * 100
            else:
                utilization_rate = 0.0
            
            workload = TeamMemberWorkload(
                member_id=member['id'],
                member_name=member['name'],
                role=member['role'],
                daily_capacity=member['available_hours_per_day'],
                total_assigned_hours=total_hours,
                assigned_tasks=member_assignments,
                utilization_rate=round(utilization_rate, 1),
                estimated_days=estimated_days
            )
            
            workloads.append(workload)
        
        return workloads
    
    def _calculate_project_timeline(self, team_workloads: List[TeamMemberWorkload]) -> int:
        """전체 프로젝트 완료 예상일 계산"""
        if not team_workloads:
            return 0
        
        # 모든 팀원 중 가장 늦게 끝나는 날짜
        max_days = max(workload.estimated_days for workload in team_workloads)
        return max_days

def run_simulation(project_id: int) -> SimulationResult:
    """시뮬레이션 실행 (외부 인터페이스)"""
    simulator = RoundRobinSimulator(project_id)
    return simulator.simulate()

def get_simulation_summary(result: SimulationResult) -> Dict:
    """시뮬레이션 결과 요약"""
    return {
        "project_id": result.project_id,
        "total_tasks": result.total_tasks,
        "total_estimated_hours": result.total_estimated_hours,
        "team_count": len(result.team_workloads),
        "estimated_completion_days": result.estimated_completion_days,
        "average_utilization": round(
            sum(w.utilization_rate for w in result.team_workloads) / len(result.team_workloads), 1
        ) if result.team_workloads else 0,
        "created_at": result.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }