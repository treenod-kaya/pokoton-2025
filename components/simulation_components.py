# components/simulation_components.py - H5 시뮬레이션 관련 UI 컴포넌트

import streamlit as st
import pandas as pd
from simulation import run_simulation, get_simulation_summary
from database import get_project_summary

class SimulationRunner:
    """시뮬레이션 실행 컴포넌트"""
    
    @staticmethod
    def render():
        """시뮬레이션 실행 UI"""
        st.header("🎯 H5. 업무 분배 시뮬레이션")
        
        # 프로젝트 기본 정보 표시
        project_summary = get_project_summary(st.session_state.current_project_id)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("팀원 수", f"{project_summary['team_count']}명")
        with col2:
            st.metric("업무 수", f"{project_summary['task_count']}개")
        with col3:
            st.metric("총 예상시간", f"{project_summary['total_estimated_hours']:.1f}h")
        with col4:
            st.metric("일일 총 가용시간", f"{project_summary['total_daily_capacity']:.1f}h/day")
        
        # 시뮬레이션 실행 조건 확인
        can_simulate = project_summary['team_count'] > 0 and project_summary['task_count'] > 0
        
        if not can_simulate:
            if project_summary['team_count'] == 0:
                st.warning("⚠️ 팀원을 먼저 추가해주세요.")
            if project_summary['task_count'] == 0:
                st.warning("⚠️ 업무를 먼저 추가해주세요.")
            return
        
        # 시뮬레이션 실행 버튼
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Round Robin 시뮬레이션 실행", type="primary"):
                try:
                    with st.spinner("시뮬레이션을 실행 중입니다..."):
                        result = run_simulation(st.session_state.current_project_id)
                        st.session_state.simulation_result = result
                        st.success("✅ 시뮬레이션이 완료되었습니다!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ 시뮬레이션 실행 중 오류가 발생했습니다: {str(e)}")

class SimulationResults:
    """시뮬레이션 결과 표시 컴포넌트"""
    
    @staticmethod
    def render():
        """시뮬레이션 결과 UI"""
        if 'simulation_result' not in st.session_state:
            st.info("📊 시뮬레이션을 먼저 실행해주세요.")
            return
        
        result = st.session_state.simulation_result
        summary = get_simulation_summary(result)
        
        st.header("📊 시뮬레이션 결과")
        
        # 결과 요약
        st.subheader("📈 프로젝트 요약")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("예상 완료일", f"{result.estimated_completion_days}일")
        with col2:
            st.metric("전체 업무", f"{result.total_tasks}개")
        with col3:
            st.metric("총 예상시간", f"{result.total_estimated_hours:.1f}h")
        with col4:
            st.metric("평균 활용률", f"{summary['average_utilization']}%")
        
        # 팀원별 업무 분배 결과
        st.subheader("👥 팀원별 업무 분배")
        
        # 팀원별 워크로드 테이블
        workload_data = []
        for workload in result.team_workloads:
            workload_data.append({
                "팀원": workload.member_name,
                "역할": workload.role,
                "일일가용시간": f"{workload.daily_capacity:.1f}h",
                "할당된업무수": len(workload.assigned_tasks),
                "총할당시간": f"{workload.total_assigned_hours:.1f}h",
                "예상소요일": f"{workload.estimated_days}일",
                "활용률": f"{workload.utilization_rate:.1f}%"
            })
        
        if workload_data:
            workload_df = pd.DataFrame(workload_data)
            st.dataframe(workload_df, hide_index=True, use_container_width=True)
        
        # 업무 할당 상세 결과
        st.subheader("📋 업무 할당 상세")
        
        # 할당 결과 테이블
        assignment_data = []
        for assignment in result.round_robin_assignments:
            assignment_data.append({
                "업무ID": assignment.task_id,
                "업무명": assignment.task_name,
                "담당자": assignment.assignee_name,
                "우선순위": assignment.priority,
                "예상시간": f"{assignment.estimated_hours:.1f}h",
                "시작일": f"{assignment.start_day}일차",
                "완료일": f"{assignment.end_day}일차",
                "소요일수": f"{assignment.end_day - assignment.start_day + 1}일"
            })
        
        if assignment_data:
            assignment_df = pd.DataFrame(assignment_data)
            st.dataframe(assignment_df, hide_index=True, use_container_width=True)
        
        # 팀원별 상세 업무 목록
        st.subheader("🔍 팀원별 상세 업무")
        
        for workload in result.team_workloads:
            with st.expander(f"👤 {workload.member_name} ({workload.role}) - {len(workload.assigned_tasks)}개 업무"):
                if workload.assigned_tasks:
                    member_tasks = []
                    for task in workload.assigned_tasks:
                        member_tasks.append({
                            "업무명": task.task_name,
                            "우선순위": task.priority,
                            "예상시간": f"{task.estimated_hours:.1f}h",
                            "일정": f"{task.start_day}일차 ~ {task.end_day}일차"
                        })
                    
                    member_df = pd.DataFrame(member_tasks)
                    st.dataframe(member_df, hide_index=True, use_container_width=True)
                    
                    # 팀원별 통계
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("총 할당시간", f"{workload.total_assigned_hours:.1f}h")
                    with col2:
                        st.metric("예상 소요일", f"{workload.estimated_days}일")
                    with col3:
                        st.metric("활용률", f"{workload.utilization_rate:.1f}%")
                else:
                    st.info("할당된 업무가 없습니다.")
        
        # 시뮬레이션 초기화 버튼
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 새로운 시뮬레이션", type="secondary"):
                if 'simulation_result' in st.session_state:
                    del st.session_state.simulation_result
                st.rerun()

class SimulationAnalysis:
    """시뮬레이션 분석 컴포넌트"""
    
    @staticmethod
    def render():
        """시뮬레이션 분석 UI"""
        if 'simulation_result' not in st.session_state:
            return
        
        result = st.session_state.simulation_result
        
        st.header("📈 시뮬레이션 분석")
        
        # 업무 분배 균형도 분석
        st.subheader("⚖️ 업무 분배 균형도")
        
        total_hours = [w.total_assigned_hours for w in result.team_workloads]
        if total_hours:
            max_hours = max(total_hours)
            min_hours = min(total_hours)
            avg_hours = sum(total_hours) / len(total_hours)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("최대 할당시간", f"{max_hours:.1f}h")
            with col2:
                st.metric("최소 할당시간", f"{min_hours:.1f}h")
            with col3:
                balance_ratio = (min_hours / max_hours * 100) if max_hours > 0 else 0
                st.metric("균형도", f"{balance_ratio:.1f}%", help="최소/최대 비율 (100%에 가까울수록 균형적)")
        
        # 활용률 분석
        st.subheader("📊 팀원 활용률 분석")
        
        utilization_rates = [w.utilization_rate for w in result.team_workloads]
        if utilization_rates:
            avg_utilization = sum(utilization_rates) / len(utilization_rates)
            
            for workload in result.team_workloads:
                col1, col2 = st.columns([3, 1])
                with col1:
                    progress_value = min(workload.utilization_rate / 100, 1.0)
                    st.progress(progress_value, text=f"{workload.member_name} ({workload.role})")
                with col2:
                    color = "🟢" if workload.utilization_rate <= 100 else "🔴"
                    st.write(f"{color} {workload.utilization_rate:.1f}%")
        
        # 권장사항
        st.subheader("💡 권장사항")
        
        recommendations = []
        
        # 과부하 팀원 체크
        overloaded_members = [w for w in result.team_workloads if w.utilization_rate > 100]
        if overloaded_members:
            recommendations.append("🔴 **과부하 팀원이 있습니다:**")
            for member in overloaded_members:
                recommendations.append(f"   - {member.member_name}: {member.utilization_rate:.1f}% 활용률")
            recommendations.append("   💡 업무 재분배 또는 팀원 추가를 고려해보세요.")
        
        # 저활용 팀원 체크
        underutilized_members = [w for w in result.team_workloads if w.utilization_rate < 50]
        if underutilized_members:
            recommendations.append("🟡 **저활용 팀원이 있습니다:**")
            for member in underutilized_members:
                recommendations.append(f"   - {member.member_name}: {member.utilization_rate:.1f}% 활용률")
            recommendations.append("   💡 추가 업무 할당을 고려해보세요.")
        
        # 균형도 체크
        if total_hours and len(total_hours) > 1:
            balance_ratio = (min(total_hours) / max(total_hours) * 100) if max(total_hours) > 0 else 0
            if balance_ratio < 70:
                recommendations.append("⚖️ **업무 분배가 불균형적입니다.**")
                recommendations.append("   💡 우선순위나 업무 크기를 조정해보세요.")
        
        if not recommendations:
            recommendations.append("✅ **현재 업무 분배가 적절합니다!**")
        
        for rec in recommendations:
            st.markdown(rec)