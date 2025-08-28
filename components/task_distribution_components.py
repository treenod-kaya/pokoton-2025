# components/task_distribution_components.py - 업무 분배 시뮬레이션 전용 컴포넌트

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from simulation import run_simulation
from database import get_project_summary, get_sprints
from utils.validation import DataValidator, ErrorHandler
from utils.calendar_utils import KoreanHolidayCalendar

class TaskDistributionSimulator:
    """업무 분배 시뮬레이션 전용 컴포넌트"""
    
    @staticmethod
    def render():
        """업무 분배 시뮬레이션 메인 UI"""
        st.header("🎯 자동 업무 분배 시뮬레이션")
        st.markdown("### 스프린트 일정에 맞춘 지능적 업무 분배")
        
        # 프로젝트 기본 정보
        project_summary = get_project_summary(st.session_state.current_project_id)
        
        # 기본 정보 표시
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 팀원", f"{project_summary['team_count']}명")
        with col2:
            st.metric("📋 업무", f"{project_summary['task_count']}개")
        with col3:
            st.metric("🚀 스프린트", f"{len(get_sprints(st.session_state.current_project_id))}개")
        with col4:
            st.metric("⏱️ 총 시간", f"{project_summary['total_estimated_hours']:.1f}h")
        
        # 시뮬레이션 실행 조건 확인
        can_simulate = project_summary['team_count'] > 0 and project_summary['task_count'] > 0
        
        if not can_simulate:
            st.error("⚠️ 시뮬레이션을 실행하려면 팀원과 업무가 필요합니다.")
            if project_summary['team_count'] == 0:
                st.info("👥 **팀원 관리** 탭에서 팀원을 추가해주세요.")
            if project_summary['task_count'] == 0:
                st.info("📝 **업무 관리** 탭에서 업무를 추가해주세요.")
            return
        
        # 시뮬레이션 실행 버튼
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 자동 업무 분배 실행", type="primary", use_container_width=True):
                # 시뮬레이션 실행 전 유효성 검증
                validation_result = DataValidator.validate_simulation_requirements(st.session_state.current_project_id)
                
                if not validation_result["valid"]:
                    for error in validation_result["errors"]:
                        st.error(f"❌ {error}")
                    return
                
                # 경고사항 표시
                for warning in validation_result["warnings"]:
                    st.warning(f"⚠️ {warning}")
                
                try:
                    with st.spinner("🔄 자동 업무 분배 중..."):
                        result = run_simulation(st.session_state.current_project_id)
                        st.session_state.distribution_result = result
                        st.success("✅ 자동 업무 분배가 완료되었습니다!")
                        st.rerun()
                except Exception as e:
                    ErrorHandler.handle_simulation_error(e)
        
        # 결과 표시
        if 'distribution_result' in st.session_state:
            TaskDistributionViewer.render(st.session_state.distribution_result)

class TaskDistributionViewer:
    """업무 분배 결과 시각화"""
    
    @staticmethod
    def render(result):
        """분배 결과 2가지 타임라인 뷰"""
        st.markdown("---")
        st.header("📊 자동 분배 결과")
        
        # 2가지 타임라인 뷰를 탭으로 구분
        timeline_tab1, timeline_tab2 = st.tabs([
            "🚀 스프린트별 타임라인",
            "🗓️ 전체 프로젝트 타임라인"
        ])
        
        with timeline_tab1:
            TaskDistributionViewer._render_sprint_timeline(result)
        
        with timeline_tab2:
            TaskDistributionViewer._render_project_timeline(result)
    
    @staticmethod
    def _render_project_timeline(result):
        """스프린트 일정에 맞는 전체 프로젝트 타임라인"""
        st.subheader("🗓️ 전체 프로젝트 타임라인")
        st.markdown("스프린트별 업무 분배 및 일정 현황")
        
        if not result.round_robin_assignments:
            st.warning("분배된 업무가 없습니다.")
            return
        
        # 스프린트별 데이터 준비
        sprint_data = []
        task_data = []
        
        # 스프린트 정보 수집
        for sprint_workload in result.sprint_workloads:
            if sprint_workload.sprint_start_date and sprint_workload.sprint_end_date:
                sprint_data.append({
                    'Sprint': sprint_workload.sprint_name,
                    'Start': sprint_workload.sprint_start_date,
                    'Finish': sprint_workload.sprint_end_date,
                    'Type': 'Sprint',
                    'Tasks': sprint_workload.total_tasks,
                    'Hours': sprint_workload.total_hours
                })
        
        # 업무 할당 정보 수집
        for assignment in result.round_robin_assignments:
            if assignment.start_date and assignment.end_date:
                # 1일 업무의 경우 종료일을 하루 뒤로 설정하여 막대로 표시
                start_date = assignment.start_date
                finish_date = assignment.end_date
                
                if start_date == finish_date:
                    # 1일 업무는 다음날까지로 표시하여 막대가 보이도록 함
                    finish_datetime = datetime.strptime(finish_date, '%Y-%m-%d') + timedelta(days=1)
                    finish_date = finish_datetime.strftime('%Y-%m-%d')
                
                task_data.append({
                    'Task': f"{assignment.task_name} ({assignment.assignee_name})",
                    'Start': start_date,
                    'Finish': finish_date,
                    'Type': 'Task',
                    'Sprint': assignment.sprint_name,
                    'Assignee': assignment.assignee_name,
                    'Priority': assignment.priority,
                    'Hours': assignment.estimated_hours,
                    'OriginalFinish': assignment.end_date  # 원래 종료일 보관
                })
        
        # 전체 타임라인 차트
        if sprint_data or task_data:
            # 스프린트 백그라운드 표시
            fig = go.Figure()
            
            # 스프린트 기간을 배경으로 표시
            colors = ['rgba(255,182,193,0.3)', 'rgba(173,216,230,0.3)', 'rgba(144,238,144,0.3)', 
                     'rgba(255,218,185,0.3)', 'rgba(221,160,221,0.3)']
            
            for i, sprint in enumerate(sprint_data):
                fig.add_shape(
                    type="rect",
                    x0=sprint['Start'], x1=sprint['Finish'],
                    y0=-0.5, y1=len(task_data) + 0.5,
                    fillcolor=colors[i % len(colors)],
                    opacity=0.3,
                    layer="below",
                    line_width=0,
                )
                
                # 스프린트 라벨 추가
                fig.add_annotation(
                    x=sprint['Start'],
                    y=len(task_data) + 0.3,
                    text=f"📅 {sprint['Sprint']}",
                    showarrow=False,
                    font=dict(size=12, color="blue"),
                    bgcolor="white",
                    bordercolor="blue",
                    borderwidth=1
                )
            
            # 담당자별 색상 매핑 (전체 프로젝트용)
            distinct_colors = [
                '#FF6B6B',  # 빨간색
                '#4ECDC4',  # 청록색
                '#45B7D1',  # 파란색
                '#96CEB4',  # 연두색
                '#FFEAA7',  # 노란색
                '#DDA0DD',  # 자주색
                '#98D8C8',  # 민트색
                '#F7DC6F',  # 황금색
                '#BB8FCE',  # 라벤더
                '#85C1E9'   # 하늘색
            ]
            
            unique_assignees = list(set(task['Assignee'] for task in task_data))
            color_map = {assignee: distinct_colors[i % len(distinct_colors)] 
                        for i, assignee in enumerate(unique_assignees)}
            
            # 중복 범례 방지를 위한 담당자 추적
            legend_shown = set()
            
            # 업무 타임라인 추가
            for i, task in enumerate(task_data):
                show_legend = task['Assignee'] not in legend_shown
                if show_legend:
                    legend_shown.add(task['Assignee'])
                
                fig.add_trace(go.Scatter(
                    x=[task['Start'], task['Finish']],
                    y=[i, i],
                    mode='lines+markers',
                    name=task['Assignee'],
                    line=dict(
                        width=10,
                        color=color_map[task['Assignee']]
                    ),
                    marker=dict(
                        size=8,
                        color=color_map[task['Assignee']],
                        line=dict(width=2, color='white')
                    ),
                    hovertemplate=(
                        f"<b>{task['Task']}</b><br>"
                        f"👤 담당자: {task['Assignee']}<br>"
                        f"🚀 스프린트: {task['Sprint']}<br>"
                        f"📅 기간: {'1일 업무' if task['Start'] == task['OriginalFinish'] else task['Start'] + ' ~ ' + task['OriginalFinish']}<br>"
                        f"⭐ 우선순위: P{task['Priority']}<br>"
                        f"⏱️ 예상시간: {task['Hours']:.1f}h"
                        "<extra></extra>"
                    ),
                    showlegend=show_legend,
                    legendgroup=task['Assignee']
                ))
            
            fig.update_layout(
                title=dict(
                    text="🗓️ 스프린트 기반 전체 프로젝트 타임라인",
                    font=dict(size=18),
                    x=0.5
                ),
                xaxis_title="📅 날짜",
                yaxis_title="📋 업무",
                height=max(450, len(task_data) * 35 + 250),
                showlegend=True,
                legend=dict(
                    title="👥 담당자",
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02,
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="rgba(0,0,0,0.2)",
                    borderwidth=1
                ),
                yaxis=dict(
                    tickmode='array',
                    tickvals=list(range(len(task_data))),
                    ticktext=[f"{task['Task'][:30]}..." if len(task['Task']) > 30 else task['Task'] for task in task_data],
                    tickfont=dict(size=11)
                ),
                xaxis=dict(
                    tickfont=dict(size=11),
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                plot_bgcolor='rgba(248,249,250,0.8)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 프로젝트 요약 정보
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📋 총 업무", len(task_data))
            with col2:
                total_hours = sum(task['Hours'] for task in task_data)
                st.metric("⏱️ 총 시간", f"{total_hours:.1f}h")
            with col3:
                if task_data:
                    earliest = min(task['Start'] for task in task_data)
                    latest = max(task['Finish'] for task in task_data)
                    total_days = (datetime.strptime(latest, '%Y-%m-%d') - 
                                datetime.strptime(earliest, '%Y-%m-%d')).days + 1
                    st.metric("📅 총 기간", f"{total_days}일")
            with col4:
                # 업무일 계산
                if task_data:
                    earliest_date = datetime.strptime(earliest, '%Y-%m-%d').date()
                    latest_date = datetime.strptime(latest, '%Y-%m-%d').date()
                    workdays = KoreanHolidayCalendar.calculate_workdays_between(earliest_date, latest_date)
                    st.metric("💼 업무일", f"{workdays}일")
    
    @staticmethod
    def _render_sprint_timeline(result):
        """스프린트 각각의 타임라인"""
        st.subheader("🚀 스프린트별 상세 타임라인")
        st.markdown("각 스프린트 내 업무 분배 현황")
        
        if not result.sprint_workloads:
            st.warning("스프린트 데이터가 없습니다.")
            return
        
        for sprint_workload in result.sprint_workloads:
            st.markdown(f"#### 📅 {sprint_workload.sprint_name}")
            
            # 스프린트 정보
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("업무 수", f"{sprint_workload.total_tasks}개")
            with col2:
                st.metric("총 시간", f"{sprint_workload.total_hours:.1f}h")
            with col3:
                if sprint_workload.sprint_start_date:
                    # 날짜 형식을 한국어로 변환
                    start_date = datetime.strptime(sprint_workload.sprint_start_date, '%Y-%m-%d')
                    formatted_start = start_date.strftime('%m/%d')
                    st.metric("시작일", formatted_start)
                else:
                    st.metric("시작일", "미정")
            with col4:
                if sprint_workload.sprint_end_date:
                    # 날짜 형식을 한국어로 변환
                    end_date = datetime.strptime(sprint_workload.sprint_end_date, '%Y-%m-%d')
                    formatted_end = end_date.strftime('%m/%d')
                    st.metric("종료일", formatted_end)
                else:
                    st.metric("종료일", "미정")
            with col5:
                if sprint_workload.sprint_start_date and sprint_workload.sprint_end_date:
                    start_date = datetime.strptime(sprint_workload.sprint_start_date, '%Y-%m-%d').date()
                    end_date = datetime.strptime(sprint_workload.sprint_end_date, '%Y-%m-%d').date()
                    workdays = KoreanHolidayCalendar.calculate_workdays_between(start_date, end_date)
                    st.metric("영업일", f"{workdays}일")
                else:
                    st.metric("영업일", "미정")
            
            # 스프린트별 업무 필터링
            sprint_tasks = [a for a in result.round_robin_assignments 
                          if a.sprint_name == sprint_workload.sprint_name and a.start_date and a.end_date]
            
            if sprint_tasks:
                # 디버깅 정보 표시
                st.markdown("**🔍 일정 분배 분석 (공휴일/주말 제외 검증)**")
                
                # 스프린트 기간 분석
                if sprint_workload.sprint_start_date and sprint_workload.sprint_end_date:
                    sprint_start = datetime.strptime(sprint_workload.sprint_start_date, '%Y-%m-%d').date()
                    sprint_end = datetime.strptime(sprint_workload.sprint_end_date, '%Y-%m-%d').date()
                    
                    total_days = (sprint_end - sprint_start).days + 1
                    workdays = KoreanHolidayCalendar.calculate_workdays_between(sprint_start, sprint_end)
                    holidays = []
                    weekends = []
                    
                    # 공휴일과 주말 목록 생성
                    current_date = sprint_start
                    while current_date <= sprint_end:
                        if KoreanHolidayCalendar.is_holiday(current_date):
                            holiday_name = KoreanHolidayCalendar.get_holiday_name(current_date)
                            holidays.append(f"{current_date.strftime('%m/%d')} ({holiday_name})")
                        elif KoreanHolidayCalendar.is_weekend(current_date):
                            weekday = ['월', '화', '수', '목', '금', '토', '일'][current_date.weekday()]
                            weekends.append(f"{current_date.strftime('%m/%d')} ({weekday})")
                        current_date += timedelta(days=1)
                    
                    # 스프린트 기간 정보
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("전체 기간", f"{total_days}일")
                    with col2:
                        st.metric("업무일", f"{workdays}일", delta=f"-{total_days-workdays}일")
                    with col3:
                        st.metric("공휴일", f"{len(holidays)}일")
                    with col4:
                        st.metric("주말", f"{len(weekends)}일")
                    
                    if holidays:
                        st.info(f"🏮 **공휴일**: {', '.join(holidays)}")
                    if weekends:
                        st.info(f"📅 **주말**: {', '.join(weekends[:5])}{'...' if len(weekends) > 5 else ''}")
                
                # 업무별 상세 분석
                st.markdown("**📋 업무별 일정 분석**")
                
                analysis_data = []
                for assignment in sprint_tasks:
                    start_date = datetime.strptime(assignment.start_date, '%Y-%m-%d').date()
                    end_date = datetime.strptime(assignment.end_date, '%Y-%m-%d').date()
                    
                    # 업무 기간 분석
                    task_total_days = (end_date - start_date).days + 1
                    task_workdays = KoreanHolidayCalendar.calculate_workdays_between(start_date, end_date)
                    daily_hours = assignment.estimated_hours / max(1, task_workdays)  # 0으로 나누기 방지
                    
                    # 업무 기간 중 공휴일/주말 체크
                    task_holidays = []
                    task_weekends = []
                    current_date = start_date
                    while current_date <= end_date:
                        if KoreanHolidayCalendar.is_holiday(current_date):
                            task_holidays.append(current_date.strftime('%m/%d'))
                        elif KoreanHolidayCalendar.is_weekend(current_date):
                            task_weekends.append(current_date.strftime('%m/%d'))
                        current_date += timedelta(days=1)
                    
                    analysis_data.append({
                        '업무명': assignment.task_name,
                        '담당자': assignment.assignee_name,
                        '우선순위': f"P{assignment.priority}",
                        '스토리포인트': assignment.story_points,
                        '시작일': assignment.start_date,
                        '종료일': assignment.end_date,
                        '전체기간': f"{task_workdays}일 (영업일)",
                        '예상시간': f"{assignment.estimated_hours:.1f}h",
                        '일일시간': f"{daily_hours:.1f}h/일",
                        '공휴일': ', '.join(task_holidays) if task_holidays else '-',
                        '주말': ', '.join(task_weekends) if task_weekends else '-',
                        '비고': '⚠️ 시간부족' if daily_hours > 8 else '✅ 적정' if daily_hours > 0 else '❌ 오류'
                    })
                
                # 분석 테이블 표시
                df_analysis = pd.DataFrame(analysis_data)
                st.dataframe(df_analysis, use_container_width=True)
                
                # 문제점 분석
                issues = []
                for data in analysis_data:
                    if '⚠️' in data['비고']:
                        issues.append(f"• {data['업무명']}: 일일 {data['일일시간']} (8시간 초과)")
                    elif '❌' in data['비고']:
                        issues.append(f"• {data['업무명']}: 일정 오류 발생")
                
                if issues:
                    st.error("**🚨 일정 분배 문제점:**")
                    for issue in issues:
                        st.markdown(issue)
                else:
                    st.success("**✅ 일정 분배가 적절합니다!**")
                
                # 간단한 타임라인 (디버깅용)
                st.markdown("**📊 간단 타임라인 (검증용)**")
                
                task_data = []
                for assignment in sprint_tasks:
                    # 1일 업무의 경우 종료일을 하루 뒤로 설정하여 막대로 표시
                    start_date = assignment.start_date
                    finish_date = assignment.end_date
                    
                    # 모든 업무에 대해 종료일에 1일을 추가하여 정확한 기간 표시
                    # (Plotly timeline에서는 종료일이 exclusive이므로)
                    finish_datetime = datetime.strptime(finish_date, '%Y-%m-%d') + timedelta(days=1)
                    finish_date = finish_datetime.strftime('%Y-%m-%d')
                    
                    task_data.append({
                        'Task': assignment.task_name,
                        'Start': start_date,
                        'Finish': finish_date,
                        'Assignee': assignment.assignee_name,
                        'Priority': assignment.priority,
                        'Hours': assignment.estimated_hours,
                        'OriginalFinish': assignment.end_date  # 원래 종료일 보관
                    })
                
                df_sprint = pd.DataFrame(task_data)
                
                # 명시적인 색상 팔레트 정의
                distinct_colors = [
                    '#FF6B6B',  # 빨간색
                    '#4ECDC4',  # 청록색
                    '#45B7D1',  # 파란색
                    '#96CEB4',  # 연두색
                    '#FFEAA7',  # 노란색
                    '#DDA0DD',  # 자주색
                    '#98D8C8',  # 민트색
                    '#F7DC6F',  # 황금색
                    '#BB8FCE',  # 라벤더
                    '#85C1E9'   # 하늘색
                ]
                
                # 담당자별 색상 매핑
                unique_assignees = df_sprint['Assignee'].unique()
                color_map = {assignee: distinct_colors[i % len(distinct_colors)] 
                           for i, assignee in enumerate(unique_assignees)}
                
                fig = px.timeline(
                    df_sprint,
                    x_start='Start',
                    x_end='Finish',
                    y='Task',
                    color='Assignee',
                    title=f"📊 {sprint_workload.sprint_name} 업무 타임라인",
                    color_discrete_map=color_map
                )
                
                # 각 trace(담당자별)에 맞는 호버 정보 설정
                for trace in fig.data:
                    assignee_name = trace.name  # trace.name이 담당자명
                    trace.hovertemplate = (
                        "<b>%{y}</b><br>"
                        f"👤 {assignee_name}"
                        "<extra></extra>"
                    )
                
                # 주말/공휴일 배경 추가 (스프린트 전체 기간)
                if task_data and sprint_workload.sprint_start_date and sprint_workload.sprint_end_date:
                    # 스프린트 전체 기간으로 설정 (업무 범위가 아닌 스프린트 전체 범위)
                    timeline_start = datetime.strptime(sprint_workload.sprint_start_date, '%Y-%m-%d').date()
                    timeline_end = datetime.strptime(sprint_workload.sprint_end_date, '%Y-%m-%d').date()
                    
                    # 주말/공휴일 배경 및 날짜 라벨 추가
                    current_date = timeline_start
                    while current_date <= timeline_end:
                        if KoreanHolidayCalendar.is_weekend(current_date) or KoreanHolidayCalendar.is_holiday(current_date):
                            # 하루 전체를 회색 배경으로 표시
                            next_date = current_date + timedelta(days=1)
                            fig.add_shape(
                                type="rect",
                                x0=current_date.strftime('%Y-%m-%d'),
                                x1=next_date.strftime('%Y-%m-%d'),
                                y0=-1.0,  # 여유를 두어 더 넓게
                                y1=len(task_data),  # 상단도 여유를 두어 더 넓게
                                fillcolor='rgba(100,100,100,0.4)',  # 더 진한 회색, 높은 투명도
                                opacity=0.4,
                                layer="below",
                                line_width=0
                            )
                            
                            # 주말/공휴일 날짜를 빨간색으로 표시 (어노테이션 제거, tick 색상으로 처리)
                        current_date += timedelta(days=1)

                # 모든 날짜에 대한 커스텀 tick 설정 (스프린트 전체 기간)
                if task_data and sprint_workload.sprint_start_date and sprint_workload.sprint_end_date:
                    # 스프린트 전체 기간의 모든 날짜에 대해 tick 설정
                    date_range = []
                    tick_texts = []
                    weekdays = ['월', '화', '수', '목', '금', '토', '일']
                    
                    # 스프린트 전체 기간 사용 (배경 shape와 동일한 범위)
                    tick_timeline_start = datetime.strptime(sprint_workload.sprint_start_date, '%Y-%m-%d').date()
                    tick_timeline_end = datetime.strptime(sprint_workload.sprint_end_date, '%Y-%m-%d').date()
                    
                    current_date = tick_timeline_start
                    while current_date <= tick_timeline_end:
                        date_range.append(current_date.strftime('%Y-%m-%d'))
                        weekday_name = weekdays[current_date.weekday()]
                        
                        # 주말/공휴일이면 빨간색으로 스타일링
                        if KoreanHolidayCalendar.is_weekend(current_date) or KoreanHolidayCalendar.is_holiday(current_date):
                            if KoreanHolidayCalendar.is_holiday(current_date):
                                holiday_name = KoreanHolidayCalendar.get_holiday_name(current_date)
                                # 공휴일: 아이콘과 배경색 추가, bold 스타일
                                tick_text = f"<span style='color:red; font-weight:bold; background-color:rgba(255,200,200,0.7); padding:2px 4px; border-radius:3px;'>🏮 {current_date.strftime('%m/%d')}<br>({holiday_name})</span>"
                            else:
                                # 주말: 빨간색 bold 스타일
                                tick_text = f"<span style='color:red; font-weight:bold;'>{current_date.strftime('%m/%d')}<br>({weekday_name})</span>"
                        else:
                            tick_text = f"{current_date.strftime('%m/%d')}<br>({weekday_name})"
                        
                        tick_texts.append(tick_text)
                        current_date += timedelta(days=1)

                # 레이아웃 개선 (한국식 날짜 포맷)
                fig.update_layout(
                    height=max(350, len(task_data) * 45 + 120),
                    xaxis_title="📅 날짜",
                    yaxis_title="📋 업무",
                    font=dict(size=12),
                    title_font_size=16,
                    legend=dict(
                        title="👥 담당자",
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(
                        tickmode='array',
                        tickvals=date_range if task_data else [],
                        ticktext=tick_texts if task_data else [],
                        tickangle=-45,
                        tickfont=dict(size=10),
                        gridcolor='rgba(0,0,0,0.1)',
                        # X축 범위를 스프린트 전체 기간으로 명시적 설정
                        range=[sprint_workload.sprint_start_date, sprint_workload.sprint_end_date] if (sprint_workload.sprint_start_date and sprint_workload.sprint_end_date) else None
                    )
                )
                
                # 막대 스타일 개선
                fig.update_traces(
                    marker_line_width=1,
                    marker_line_color="white",
                    opacity=0.8
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("이 스프린트에 할당된 업무가 없습니다.")
            
            st.markdown("---")
    
        
        # 분배 재실행 버튼
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 분배 재실행", type="secondary"):
                if 'distribution_result' in st.session_state:
                    del st.session_state.distribution_result
                st.rerun()