# components/simulation_components.py - H5 시뮬레이션 관련 UI 컴포넌트

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
from simulation import run_simulation, get_simulation_summary
from database import get_project_summary
from utils import DataValidator, ErrorHandler

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
                # 시뮬레이션 실행 전 유효성 검증
                validation_result = DataValidator.validate_simulation_requirements(st.session_state.current_project_id)
                
                # 오류가 있으면 실행 중단
                if not validation_result["valid"]:
                    for error in validation_result["errors"]:
                        st.error(f"❌ {error}")
                    return
                
                # 경고사항 표시
                for warning in validation_result["warnings"]:
                    st.warning(f"⚠️ {warning}")
                
                try:
                    with st.spinner("시뮬레이션을 실행 중입니다..."):
                        result = run_simulation(st.session_state.current_project_id)
                        st.session_state.simulation_result = result
                        st.success("✅ 시뮬레이션이 완료되었습니다!")
                        
                        # 결과 요약 표시
                        st.info(f"📊 {validation_result['team_count']}명의 팀원에게 {validation_result['task_count']}개의 업무를 분배했습니다.")
                        st.rerun()
                except Exception as e:
                    ErrorHandler.handle_simulation_error(e)

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

class SimulationVisualization:
    """H6. 결과 시각화 컴포넌트"""
    
    @staticmethod
    def render():
        """시뮬레이션 결과 시각화"""
        if 'simulation_result' not in st.session_state:
            st.info("📊 시뮬레이션을 먼저 실행해주세요.")
            return
        
        result = st.session_state.simulation_result
        
        st.header("📊 H6. 결과 시각화")
        
        # 탭으로 구분
        viz_tab1, viz_tab2, viz_tab3 = st.tabs(["📊 팀원별 업무량", "📅 간트 차트", "⚖️ 불균형 지표"])
        
        with viz_tab1:
            SimulationVisualization._render_workload_charts(result)
        
        with viz_tab2:
            SimulationVisualization._render_gantt_chart(result)
        
        with viz_tab3:
            SimulationVisualization._render_imbalance_indicators(result)
    
    @staticmethod
    def _render_workload_charts(result):
        """팀원별 업무량 Bar Chart"""
        st.subheader("👥 팀원별 업무량 분석")
        
        # 데이터 준비
        workload_data = []
        for workload in result.team_workloads:
            workload_data.append({
                "팀원": workload.member_name,
                "역할": workload.role,
                "총할당시간": workload.total_assigned_hours,
                "활용률": workload.utilization_rate,
                "예상소요일": workload.estimated_days,
                "일일가용시간": workload.daily_capacity
            })
        
        if not workload_data:
            st.warning("표시할 데이터가 없습니다.")
            return
        
        df = pd.DataFrame(workload_data)
        
        # 1. 총 할당시간 Bar Chart
        st.markdown("#### 📋 총 할당시간 비교")
        fig1 = px.bar(
            df, 
            x="팀원", 
            y="총할당시간",
            color="역할",
            title="팀원별 총 할당시간 (시간)",
            labels={"총할당시간": "할당시간 (h)"},
            text="총할당시간"
        )
        fig1.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
        
        # 2. 활용률 Bar Chart
        st.markdown("#### 📈 팀원별 활용률")
        fig2 = px.bar(
            df,
            x="팀원",
            y="활용률", 
            color="활용률",
            color_continuous_scale=["green", "yellow", "red"],
            title="팀원별 활용률 (%)",
            labels={"활용률": "활용률 (%)"},
            text="활용률"
        )
        fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig2.add_hline(y=100, line_dash="dash", line_color="red", 
                      annotation_text="100% 기준선")
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
        
        # 3. 할당시간 vs 가용시간 비교
        st.markdown("#### ⚖️ 할당시간 vs 가용시간")
        
        # 전체 가용시간 계산 (일일가용시간 × 예상소요일)
        df['전체가용시간'] = df['일일가용시간'] * df['예상소요일']
        
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name='할당시간',
            x=df['팀원'],
            y=df['총할당시간'],
            marker_color='lightblue'
        ))
        fig3.add_trace(go.Bar(
            name='가용시간',
            x=df['팀원'],
            y=df['전체가용시간'],
            marker_color='lightgreen'
        ))
        
        fig3.update_layout(
            title="할당시간 vs 전체 가용시간 비교",
            xaxis_title="팀원",
            yaxis_title="시간 (h)",
            barmode='group',
            height=400
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    @staticmethod
    def _render_gantt_chart(result):
        """간트 차트 시각화"""
        st.subheader("📅 프로젝트 간트 차트")
        
        if not result.round_robin_assignments:
            st.warning("표시할 업무 할당 정보가 없습니다.")
            return
        
        # 간트 차트 데이터 준비 (실제 날짜 기반)
        gantt_data = []
        
        for assignment in result.round_robin_assignments:
            # 실제 날짜가 있으면 사용, 없으면 일차 기반
            if assignment.start_date and assignment.end_date:
                start_val = assignment.start_date
                finish_val = assignment.end_date
                duration_calc = (datetime.strptime(assignment.end_date, '%Y-%m-%d') - 
                               datetime.strptime(assignment.start_date, '%Y-%m-%d')).days + 1
            else:
                start_val = assignment.start_day
                finish_val = assignment.end_day
                duration_calc = assignment.end_day - assignment.start_day + 1
                
            gantt_data.append({
                'Task': f"{assignment.task_name}",
                'Start': start_val,
                'Finish': finish_val,
                'Resource': assignment.assignee_name,
                'Duration': duration_calc,
                'Hours': assignment.estimated_hours,
                'Sprint': assignment.sprint_name if assignment.sprint_name else "미분류",
                'Priority': assignment.priority
            })
        
        df_gantt = pd.DataFrame(gantt_data)
        
        # 스프린트별 간트 차트
        if result.sprint_workloads:
            st.markdown("#### 🚀 스프린트별 간트 차트")
            
            for sprint_workload in result.sprint_workloads:
                if not sprint_workload.assignments:
                    continue
                    
                sprint_df = df_gantt[df_gantt['Sprint'] == sprint_workload.sprint_name]
                
                if len(sprint_df) == 0:
                    continue
                
                # 날짜 타입 확인해서 라벨 설정
                is_date_based = any('-' in str(val) for val in sprint_df['Start'].values if val is not None)
                
                fig = px.timeline(
                    sprint_df,
                    x_start='Start',
                    x_end='Finish', 
                    y='Task',
                    color='Resource',
                    title=f"📋 {sprint_workload.sprint_name} - 스프린트 간트 차트",
                    labels={
                        'Start': '시작일' if is_date_based else '시작일차', 
                        'Finish': '종료일' if is_date_based else '종료일차'
                    },
                    hover_data=['Hours', 'Duration', 'Priority']
                )
                
                fig.update_layout(
                    height=max(400, len(sprint_df) * 30 + 200),
                    xaxis_title="날짜" if is_date_based else "일차",
                    yaxis_title="업무"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # 전체 프로젝트 간트 차트
        st.markdown("#### 📊 전체 프로젝트 타임라인")
        
        # 전체 데이터에서도 날짜 타입 확인
        is_all_date_based = any('-' in str(val) for val in df_gantt['Start'].values if val is not None)
        
        fig_all = px.timeline(
            df_gantt,
            x_start='Start',
            x_end='Finish',
            y='Task', 
            color='Resource',
            title="전체 프로젝트 간트 차트 (실제 날짜 기반)" if is_all_date_based else "전체 프로젝트 간트 차트",
            labels={
                'Start': '시작일' if is_all_date_based else '시작일차', 
                'Finish': '종료일' if is_all_date_based else '종료일차'
            },
            hover_data=['Hours', 'Duration', 'Sprint', 'Priority']
        )
        
        fig_all.update_layout(
            height=max(500, len(df_gantt) * 25 + 200),
            xaxis_title="날짜" if is_all_date_based else "일차",
            yaxis_title="업무"
        )
        
        st.plotly_chart(fig_all, use_container_width=True)
        
        # 캘린더 뷰 (실제 날짜 기반인 경우에만)
        if is_all_date_based:
            st.markdown("#### 📅 캘린더 뷰")
            
            # 날짜별 업무 그룹화
            calendar_data = []
            for _, row in df_gantt.iterrows():
                start_date = datetime.strptime(row['Start'], '%Y-%m-%d')
                end_date = datetime.strptime(row['Finish'], '%Y-%m-%d')
                
                # 업무 기간 동안 각 날짜별로 데이터 생성
                current_date = start_date
                while current_date <= end_date:
                    calendar_data.append({
                        'Date': current_date.strftime('%Y-%m-%d'),
                        'Task': row['Task'],
                        'Resource': row['Resource'],
                        'Sprint': row['Sprint'],
                        'Hours': row['Hours'] / row['Duration'],  # 일일 시간으로 분할
                        'WeekDay': current_date.strftime('%A'),
                        'Month': current_date.strftime('%B %Y')
                    })
                    current_date += timedelta(days=1)
            
            if calendar_data:
                cal_df = pd.DataFrame(calendar_data)
                
                # 날짜별 팀원 업무량 히트맵
                pivot_data = cal_df.groupby(['Date', 'Resource'])['Hours'].sum().reset_index()
                pivot_table = pivot_data.pivot(index='Resource', columns='Date', values='Hours').fillna(0)
                
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=pivot_table.values,
                    x=pivot_table.columns,
                    y=pivot_table.index,
                    colorscale='RdYlBu_r',
                    hovertemplate='<b>%{y}</b><br>날짜: %{x}<br>업무량: %{z:.1f}시간<extra></extra>'
                ))
                
                fig_heatmap.update_layout(
                    title="📅 팀원별 일일 업무량 캘린더",
                    xaxis_title="날짜",
                    yaxis_title="팀원",
                    height=max(300, len(pivot_table.index) * 50)
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
    
    @staticmethod
    def _render_imbalance_indicators(result):
        """불균형 지표 시각화"""
        st.subheader("⚖️ 업무 분배 불균형 지표")
        
        if not result.team_workloads:
            st.warning("표시할 데이터가 없습니다.")
            return
        
        # 데이터 준비
        workload_data = []
        for workload in result.team_workloads:
            workload_data.append({
                "팀원": workload.member_name,
                "총할당시간": workload.total_assigned_hours,
                "활용률": workload.utilization_rate,
                "예상소요일": workload.estimated_days
            })
        
        df = pd.DataFrame(workload_data)
        
        # 1. 활용률 분포 히스토그램
        st.markdown("#### 📊 활용률 분포")
        fig1 = px.histogram(
            df,
            x="활용률",
            nbins=10,
            title="팀원별 활용률 분포",
            labels={"활용률": "활용률 (%)", "count": "팀원 수"}
        )
        fig1.add_vline(x=100, line_dash="dash", line_color="red", 
                      annotation_text="이상적 활용률 (100%)")
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
        
        # 2. 균형도 지표 계산 및 시각화
        total_hours = df['총할당시간'].tolist()
        if total_hours:
            max_hours = max(total_hours)
            min_hours = min(total_hours)
            avg_hours = sum(total_hours) / len(total_hours)
            std_hours = df['총할당시간'].std()
            
            # 균형도 메트릭
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                balance_ratio = (min_hours / max_hours * 100) if max_hours > 0 else 0
                st.metric("균형도", f"{balance_ratio:.1f}%", 
                         help="최소 할당시간 / 최대 할당시간 × 100 (100%에 가까울수록 균형적)")
            
            with col2:
                st.metric("최대 할당시간", f"{max_hours:.1f}h")
            
            with col3:
                st.metric("최소 할당시간", f"{min_hours:.1f}h")
            
            with col4:
                st.metric("표준편차", f"{std_hours:.1f}h", 
                         help="값이 낮을수록 균등하게 분배됨")
        
        # 3. 팀원별 편차 시각화
        st.markdown("#### 📈 평균 대비 편차")
        df['평균대비편차'] = df['총할당시간'] - df['총할당시간'].mean()
        
        fig3 = px.bar(
            df,
            x="팀원",
            y="평균대비편차",
            color="평균대비편차",
            color_continuous_scale=["red", "white", "blue"],
            title="평균 할당시간 대비 편차",
            labels={"평균대비편차": "편차 (h)"}
        )
        fig3.add_hline(y=0, line_dash="dash", line_color="black", 
                      annotation_text="평균선")
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)
        
        # 4. 종합 분석 및 권장사항
        st.markdown("#### 💡 불균형 분석 결과")
        
        analysis_results = []
        
        # 과부하 팀원
        overloaded = df[df['활용률'] > 100]
        if len(overloaded) > 0:
            analysis_results.append(f"🔴 **과부하 팀원**: {len(overloaded)}명")
            for _, member in overloaded.iterrows():
                analysis_results.append(f"   - {member['팀원']}: {member['활용률']:.1f}% 활용률")
        
        # 저활용 팀원
        underutilized = df[df['활용률'] < 50]
        if len(underutilized) > 0:
            analysis_results.append(f"🟡 **저활용 팀원**: {len(underutilized)}명")
            for _, member in underutilized.iterrows():
                analysis_results.append(f"   - {member['팀원']}: {member['활용률']:.1f}% 활용률")
        
        # 균형도 평가
        balance_ratio = (min(total_hours) / max(total_hours) * 100) if max(total_hours) > 0 else 0
        if balance_ratio >= 80:
            analysis_results.append("✅ **균형도 양호**: 팀원 간 업무 분배가 균등합니다.")
        elif balance_ratio >= 60:
            analysis_results.append("🟡 **균형도 보통**: 일부 개선이 필요합니다.")
        else:
            analysis_results.append("🔴 **균형도 불량**: 업무 재분배를 고려해주세요.")
        
        if not analysis_results:
            analysis_results.append("✅ **이상적인 분배**: 현재 업무 분배가 적절합니다!")
        
        for result_text in analysis_results:
            st.markdown(result_text)

class SimulationExport:
    """H7. 결과 Export 컴포넌트"""
    
    @staticmethod
    def render():
        """시뮬레이션 결과 Export 기능"""
        if 'simulation_result' not in st.session_state:
            st.info("📊 시뮬레이션을 먼저 실행해주세요.")
            return
        
        result = st.session_state.simulation_result
        summary = get_simulation_summary(result)
        
        st.header("📤 H7. 결과 Export")
        
        # Export 옵션
        export_tab1, export_tab2, export_tab3 = st.tabs(["📊 요약 리포트", "📋 상세 데이터", "📈 분석 결과"])
        
        with export_tab1:
            SimulationExport._render_summary_export(result, summary)
        
        with export_tab2:
            SimulationExport._render_detailed_export(result)
        
        with export_tab3:
            SimulationExport._render_analysis_export(result)
    
    @staticmethod
    def _render_summary_export(result, summary):
        """요약 리포트 Export"""
        st.subheader("📊 프로젝트 요약 리포트")
        
        # 요약 정보 표시
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 업무 수", f"{result.total_tasks}개")
        with col2:
            st.metric("총 예상시간", f"{result.total_estimated_hours:.1f}h")
        with col3:
            st.metric("예상 완료일", f"{result.estimated_completion_days}일")
        
        # 요약 리포트 데이터 생성
        summary_data = {
            "항목": [
                "프로젝트 ID",
                "총 업무 수", 
                "총 예상시간",
                "팀원 수",
                "예상 완료일",
                "평균 활용률",
                "시뮬레이션 실행일시"
            ],
            "값": [
                result.project_id,
                f"{result.total_tasks}개",
                f"{result.total_estimated_hours:.1f}h",
                f"{summary['team_count']}명",
                f"{result.estimated_completion_days}일",
                f"{summary['average_utilization']}%",
                summary['created_at']
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Export 버튼
        csv_summary = summary_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 요약 리포트 다운로드 (CSV)",
            data=csv_summary,
            file_name=f"project_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_summary"
        )
    
    @staticmethod
    def _render_detailed_export(result):
        """상세 데이터 Export"""
        st.subheader("📋 상세 업무 할당 데이터")
        
        # 팀원별 워크로드 데이터
        st.markdown("#### 👥 팀원별 워크로드")
        workload_data = []
        for workload in result.team_workloads:
            workload_data.append({
                "팀원명": workload.member_name,
                "역할": workload.role,
                "일일가용시간": workload.daily_capacity,
                "총할당시간": workload.total_assigned_hours,
                "할당업무수": len(workload.assigned_tasks),
                "예상소요일": workload.estimated_days,
                "활용률": f"{workload.utilization_rate:.1f}%"
            })
        
        workload_df = pd.DataFrame(workload_data)
        st.dataframe(workload_df, use_container_width=True, hide_index=True)
        
        # 업무 할당 상세 데이터
        st.markdown("#### 📝 업무 할당 상세")
        assignment_data = []
        for assignment in result.round_robin_assignments:
            assignment_data.append({
                "업무ID": assignment.task_id,
                "업무명": assignment.task_name,
                "담당자": assignment.assignee_name,
                "스프린트": assignment.sprint_name,
                "우선순위": assignment.priority,
                "예상시간": assignment.estimated_hours,
                "시작일차": assignment.start_day,
                "종료일차": assignment.end_day,
                "소요일수": assignment.end_day - assignment.start_day + 1
            })
        
        assignment_df = pd.DataFrame(assignment_data)
        st.dataframe(assignment_df, use_container_width=True, hide_index=True)
        
        # Export 버튼들
        col1, col2 = st.columns(2)
        
        with col1:
            csv_workload = workload_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 팀원별 워크로드 다운로드 (CSV)",
                data=csv_workload,
                file_name=f"team_workload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_workload"
            )
        
        with col2:
            csv_assignment = assignment_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 업무 할당 상세 다운로드 (CSV)",
                data=csv_assignment,
                file_name=f"task_assignments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_assignments"
            )
    
    @staticmethod
    def _render_analysis_export(result):
        """분석 결과 Export"""
        st.subheader("📈 시뮬레이션 분석 결과")
        
        # 스프린트별 분석 데이터
        if result.sprint_workloads:
            st.markdown("#### 🚀 스프린트별 분석")
            sprint_data = []
            for sprint in result.sprint_workloads:
                sprint_data.append({
                    "스프린트명": sprint.sprint_name,
                    "시작일": sprint.sprint_start_date,
                    "종료일": sprint.sprint_end_date,
                    "총업무수": sprint.total_tasks,
                    "총예상시간": f"{sprint.total_hours:.1f}h",
                    "할당된업무": len(sprint.assignments)
                })
            
            sprint_df = pd.DataFrame(sprint_data)
            st.dataframe(sprint_df, use_container_width=True, hide_index=True)
            
            csv_sprint = sprint_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 스프린트별 분석 다운로드 (CSV)",
                data=csv_sprint,
                file_name=f"sprint_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_sprint"
            )
        
        # 불균형 지표 데이터
        st.markdown("#### ⚖️ 불균형 지표")
        balance_data = []
        
        # 팀원별 활용률 및 편차 계산
        workload_hours = [w.total_assigned_hours for w in result.team_workloads]
        if workload_hours:
            avg_hours = sum(workload_hours) / len(workload_hours)
            max_hours = max(workload_hours)
            min_hours = min(workload_hours)
            balance_ratio = (min_hours / max_hours * 100) if max_hours > 0 else 0
            
            for workload in result.team_workloads:
                deviation = workload.total_assigned_hours - avg_hours
                balance_data.append({
                    "팀원명": workload.member_name,
                    "활용률": f"{workload.utilization_rate:.1f}%",
                    "할당시간": f"{workload.total_assigned_hours:.1f}h",
                    "평균대비편차": f"{deviation:.1f}h",
                    "상태": "과부하" if workload.utilization_rate > 100 else "저활용" if workload.utilization_rate < 50 else "적정"
                })
            
            # 전체 균형도 정보 추가
            balance_data.append({
                "팀원명": "=== 전체 지표 ===",
                "활용률": f"{sum(w.utilization_rate for w in result.team_workloads) / len(result.team_workloads):.1f}%",
                "할당시간": f"{sum(workload_hours):.1f}h",
                "평균대비편차": f"{balance_ratio:.1f}%",
                "상태": "균형도"
            })
        
        balance_df = pd.DataFrame(balance_data)
        st.dataframe(balance_df, use_container_width=True, hide_index=True)
        
        csv_balance = balance_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 불균형 지표 다운로드 (CSV)",
            data=csv_balance,
            file_name=f"balance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_balance"
        )
        
        # 전체 데이터 통합 Export
        st.markdown("---")
        st.markdown("#### 📦 통합 데이터 Export")
        
        if st.button("📋 전체 데이터 통합 생성", type="primary"):
            # 모든 데이터를 하나의 Excel 파일로 생성
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # 각 시트별로 데이터 저장
                pd.DataFrame([{
                    "프로젝트ID": result.project_id,
                    "총업무수": result.total_tasks,
                    "총예상시간": result.total_estimated_hours,
                    "예상완료일": result.estimated_completion_days,
                    "시뮬레이션일시": result.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }]).to_excel(writer, sheet_name='프로젝트요약', index=False)
                
                pd.DataFrame(workload_data).to_excel(writer, sheet_name='팀원워크로드', index=False)
                pd.DataFrame(assignment_data).to_excel(writer, sheet_name='업무할당', index=False)
                
                if result.sprint_workloads:
                    pd.DataFrame(sprint_data).to_excel(writer, sheet_name='스프린트분석', index=False)
                
                pd.DataFrame(balance_data).to_excel(writer, sheet_name='불균형지표', index=False)
            
            output.seek(0)
            
            st.download_button(
                label="📥 통합 분석 리포트 다운로드 (Excel)",
                data=output.getvalue(),
                file_name=f"simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel"
            )