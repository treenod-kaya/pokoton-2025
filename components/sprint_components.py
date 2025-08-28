# components/sprint_components.py - 스프린트 관리 UI 컴포넌트

import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import add_sprint, get_sprints, delete_sprint, update_sprint, get_sprint_by_id

class SprintForm:
    """스프린트 입력/수정 폼 컴포넌트"""
    
    @staticmethod
    def render(sprint_data=None, is_edit_mode=False):
        """스프린트 입력/수정 폼 렌더링"""
        if is_edit_mode and sprint_data:
            st.header(f"✏️ 스프린트 수정: {sprint_data['name']}")
            form_key_prefix = "edit_sprint_"
        else:
            st.header("🚀 스프린트 관리")
            form_key_prefix = ""
        
        with st.container():
            if not is_edit_mode:
                st.subheader("새 스프린트 추가")
            
            # 첫 번째 행: 기본 정보
            col1, col2 = st.columns(2)
            with col1:
                default_name = sprint_data['name'] if is_edit_mode and sprint_data else ""
                name = st.text_input("스프린트명 *", value=default_name, placeholder="예: Sprint 1.0, v1.0.0", key=f"{form_key_prefix}sprint_name")
            with col2:
                status_options = ["planned", "active", "completed"]
                status_labels = {"planned": "계획됨", "active": "진행중", "completed": "완료됨"}
                
                if is_edit_mode and sprint_data:
                    default_status_index = status_options.index(sprint_data['status']) if sprint_data['status'] in status_options else 0
                else:
                    default_status_index = 0
                
                selected_status = st.selectbox("상태", options=status_options, 
                                             format_func=lambda x: status_labels[x],
                                             index=default_status_index, 
                                             key=f"{form_key_prefix}sprint_status")
            
            # 두 번째 행: 설명
            default_description = sprint_data['description'] if is_edit_mode and sprint_data else ""
            description = st.text_area("스프린트 설명", value=default_description, 
                                     placeholder="스프린트에 대한 자세한 설명을 입력하세요...", 
                                     key=f"{form_key_prefix}sprint_description")
            
            # 세 번째 행: 일정
            col1, col2 = st.columns(2)
            with col1:
                if is_edit_mode and sprint_data and sprint_data['start_date']:
                    try:
                        default_start = datetime.strptime(sprint_data['start_date'], "%Y-%m-%d").date()
                    except:
                        default_start = date.today()
                else:
                    default_start = date.today()
                
                start_date = st.date_input("시작일", value=default_start, key=f"{form_key_prefix}sprint_start_date")
            
            with col2:
                if is_edit_mode and sprint_data and sprint_data['end_date']:
                    try:
                        default_end = datetime.strptime(sprint_data['end_date'], "%Y-%m-%d").date()
                    except:
                        default_end = start_date
                else:
                    default_end = start_date
                
                end_date = st.date_input("종료일", value=default_end, key=f"{form_key_prefix}sprint_end_date")
            
            # 버튼 행
            if is_edit_mode:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("💾 수정 완료", key=f"{form_key_prefix}update_sprint", type="primary"):
                        try:
                            if start_date > end_date:
                                st.error("⚠️ 시작일이 종료일보다 늦을 수 없습니다.")
                            else:
                                update_sprint(
                                    sprint_id=sprint_data['id'],
                                    name=name.strip(),
                                    description=description,
                                    start_date=start_date.strftime("%Y-%m-%d"),
                                    end_date=end_date.strftime("%Y-%m-%d"),
                                    status=selected_status
                                )
                                st.success(f"✅ 스프린트 '{name}'가 수정되었습니다!")
                                del st.session_state.editing_sprint_id
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ 스프린트 수정 중 오류가 발생했습니다: {str(e)}")
                with col3:
                    if st.button("❌ 취소", key=f"{form_key_prefix}cancel_edit_sprint"):
                        del st.session_state.editing_sprint_id
                        st.rerun()
            else:
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                with col_btn2:
                    if st.button("🚀 스프린트 추가", key=f"{form_key_prefix}add_sprint", type="primary", use_container_width=True):
                        if name and name.strip():
                            try:
                                if start_date > end_date:
                                    st.error("⚠️ 시작일이 종료일보다 늦을 수 없습니다.")
                                else:
                                    add_sprint(
                                        project_id=st.session_state.current_project_id,
                                        name=name.strip(),
                                        description=description,
                                        start_date=start_date.strftime("%Y-%m-%d"),
                                        end_date=end_date.strftime("%Y-%m-%d"),
                                        status=selected_status
                                    )
                                    st.success(f"✅ 스프린트 '{name}'가 추가되었습니다!")
                            except Exception as e:
                                st.error(f"❌ 스프린트 추가 중 오류가 발생했습니다: {str(e)}")
                        else:
                            st.error("⚠️ 스프린트명을 입력해주세요.")

class SprintList:
    """스프린트 목록 표시 컴포넌트"""
    
    @staticmethod
    def render():
        """스프린트 목록 표시"""
        sprints = get_sprints(st.session_state.current_project_id)
        
        if sprints:
            st.subheader(f"🗓️ 스프린트 현황 ({len(sprints)}개)")
            
            # 스프린트 테이블 표시
            sprints_df = pd.DataFrame([
                {
                    "ID": sprint["id"],
                    "스프린트명": sprint["name"],
                    "상태": {"planned": "📅 계획됨", "active": "🔄 진행중", "completed": "✅ 완료됨"}.get(sprint["status"], sprint["status"]),
                    "시작일": sprint["start_date"] if sprint["start_date"] else "미정",
                    "종료일": sprint["end_date"] if sprint["end_date"] else "미정",
                    "설명": sprint["description"][:30] + "..." if len(sprint.get("description", "")) > 30 else sprint.get("description", ""),
                    "생성일": sprint["created_at"][:10] if sprint["created_at"] else ""
                } for sprint in sprints
            ])
            
            st.dataframe(sprints_df, use_container_width=True, hide_index=True)
            
            # 스프린트 수정/삭제 기능
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("✏️ 스프린트 수정"):
                    sprint_to_edit = st.selectbox(
                        "수정할 스프린트 선택",
                        options=[s["id"] for s in sprints],
                        format_func=lambda x: next(s["name"] for s in sprints if s["id"] == x),
                        index=None,
                        placeholder="수정할 스프린트를 선택하세요",
                        key="edit_sprint_select"
                    )
                    
                    if sprint_to_edit:
                        if st.button("스프린트 수정하기", key="edit_sprint_btn", type="primary"):
                            st.session_state.editing_sprint_id = sprint_to_edit
                            st.rerun()
            
            with col2:
                with st.expander("🗑️ 스프린트 삭제"):
                    sprint_to_delete = st.selectbox(
                        "삭제할 스프린트 선택",
                        options=[s["id"] for s in sprints],
                        format_func=lambda x: next(s["name"] for s in sprints if s["id"] == x),
                        index=None,
                        placeholder="삭제할 스프린트를 선택하세요",
                        key="delete_sprint_select"
                    )
                    
                    if sprint_to_delete and st.button("스프린트 삭제", key="delete_sprint", type="secondary"):
                        if delete_sprint(sprint_to_delete):
                            st.success("✅ 스프린트가 삭제되었습니다.")
                            st.rerun()
                        else:
                            st.error("❌ 스프린트 삭제에 실패했습니다.")
        else:
            st.info("🚀 아직 추가된 스프린트가 없습니다. 위에서 스프린트를 추가해주세요.")

class SprintTaskDistribution:
    """스프린트별 업무 분배 표시 컴포넌트"""
    
    @staticmethod
    def render():
        """스프린트별 업무 분배 현황"""
        if 'simulation_result' not in st.session_state:
            st.info("📊 시뮬레이션을 먼저 실행해주세요.")
            return
        
        result = st.session_state.simulation_result
        
        if not result.sprint_workloads:
            st.info("📅 스프린트별 업무 분배 정보가 없습니다.")
            return
        
        st.header("📅 스프린트별 업무 분배")
        
        # 스프린트별 요약
        for sprint_workload in result.sprint_workloads:
            with st.expander(f"🚀 {sprint_workload.sprint_name} ({sprint_workload.total_tasks}개 업무, {sprint_workload.total_hours:.1f}h)", expanded=True):
                
                # 스프린트 기본 정보
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("업무 수", f"{sprint_workload.total_tasks}개")
                with col2:
                    st.metric("총 예상시간", f"{sprint_workload.total_hours:.1f}h")
                with col3:
                    st.metric("시작일", sprint_workload.sprint_start_date if sprint_workload.sprint_start_date else "미정")
                with col4:
                    st.metric("종료일", sprint_workload.sprint_end_date if sprint_workload.sprint_end_date else "미정")
                
                # 스프린트 내 업무 목록
                if sprint_workload.assignments:
                    st.subheader("📋 업무 목록")
                    assignment_data = []
                    for assignment in sprint_workload.assignments:
                        assignment_data.append({
                            "업무명": assignment.task_name,
                            "담당자": assignment.assignee_name,
                            "우선순위": assignment.priority,
                            "예상시간": f"{assignment.estimated_hours:.1f}h",
                            "일정": f"{assignment.start_day}일차 ~ {assignment.end_day}일차"
                        })
                    
                    assignment_df = pd.DataFrame(assignment_data)
                    st.dataframe(assignment_df, use_container_width=True, hide_index=True)
                else:
                    st.info("이 스프린트에는 할당된 업무가 없습니다.")