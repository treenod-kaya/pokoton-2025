# components/task_components.py - 업무 관련 UI 컴포넌트

import streamlit as st
import pandas as pd
from database import add_task, get_tasks, delete_task, get_team_members, update_task, get_task_by_id

class TaskForm:
    """업무 입력/수정 폼 컴포넌트 클래스"""
    
    @staticmethod
    def render(task_data=None, is_edit_mode=False):
        """업무 입력/수정 폼 렌더링
        
        Args:
            task_data: 수정 모드일 때 기존 업무 데이터
            is_edit_mode: True면 수정 모드, False면 입력 모드
        """
        if is_edit_mode and task_data:
            st.header(f"✏️ 업무 수정: {task_data['item_name']}")
            form_key_prefix = "edit_"
        else:
            st.header("📋 업무 관리")
            form_key_prefix = ""
        
        # 현재 프로젝트의 팀원 목록 가져오기 (담당자 선택용)
        team_members = get_team_members(st.session_state.current_project_id)
        member_options = ["미지정"] + [m["name"] for m in team_members]
        
        with st.container():
            if not is_edit_mode:
                st.subheader("새 업무 추가")
            
            # 첫 번째 행: 기본 정보
            col1, col2, col3 = st.columns(3)
            with col1:
                default_item_name = task_data['item_name'] if is_edit_mode and task_data else ""
                item_name = st.text_input("업무명 *", value=default_item_name, placeholder="예: 로그인 API 개발", key=f"{form_key_prefix}task_item_name")
            with col2:
                default_priority_index = (task_data['priority'] - 1) if is_edit_mode and task_data else 2
                priority = st.selectbox("우선순위", options=[1, 2, 3, 4, 5], index=default_priority_index, key=f"{form_key_prefix}task_priority")
            with col3:
                if is_edit_mode and task_data:
                    current_assignee = task_data['assignee'] if task_data['assignee'] else "미지정"
                    default_assignee_index = member_options.index(current_assignee) if current_assignee in member_options else 0
                else:
                    default_assignee_index = 0
                assignee = st.selectbox("담당자", options=member_options, index=default_assignee_index, key=f"{form_key_prefix}task_assignee")
            
            # 두 번째 행: 분류 정보
            col1, col2, col3 = st.columns(3)
            with col1:
                attribute_options = ["기능 개발", "버그 수정", "리팩토링", "테스트", "문서화", "기타"]
                if is_edit_mode and task_data:
                    default_attribute_index = attribute_options.index(task_data['attribute']) if task_data['attribute'] in attribute_options else 0
                else:
                    default_attribute_index = 0
                attribute = st.selectbox("속성", options=attribute_options, index=default_attribute_index, key=f"{form_key_prefix}task_attribute")
            with col2:
                # 기존 빌드 목록 (세션 상태로 관리)
                if 'build_types' not in st.session_state:
                    st.session_state.build_types = [
                        "Sprint 1.0", "Sprint 1.1", "Sprint 1.2", 
                        "v1.0.0", "v1.1.0", "v2.0.0",
                        "2024-Q4", "2025-Q1", "Hot Fix"
                    ]
                
                # 수정 모드일 때 현재 빌드가 목록에 없으면 추가
                if is_edit_mode and task_data and task_data['build_type'] and task_data['build_type'] not in st.session_state.build_types:
                    st.session_state.build_types.append(task_data['build_type'])
                
                if is_edit_mode:
                    # 수정 모드: 드롭다운만 표시
                    default_build_index = st.session_state.build_types.index(task_data['build_type']) if task_data and task_data['build_type'] in st.session_state.build_types else 0
                    build_type = st.selectbox("적용 빌드", options=st.session_state.build_types, index=default_build_index, key=f"{form_key_prefix}task_build_type")
                else:
                    # 입력 모드: 새 빌드 추가 옵션 포함
                    build_options = st.session_state.build_types + ["+ 새 빌드 추가"]
                    selected_build = st.selectbox("적용 빌드", options=build_options, index=0, key=f"{form_key_prefix}task_build_select")
                    
                    # 새 빌드 추가 선택 시
                    if selected_build == "+ 새 빌드 추가":
                        new_build = st.text_input("새 빌드명", placeholder="예: Sprint 2.0, v3.0.0", key=f"{form_key_prefix}new_build_input")
                        if new_build and new_build.strip():
                            if st.button("빌드 추가", key=f"{form_key_prefix}add_build_btn"):
                                if new_build.strip() not in st.session_state.build_types:
                                    st.session_state.build_types.append(new_build.strip())
                                    st.success(f"'{new_build}' 빌드가 추가되었습니다!")
                                    st.rerun()
                                else:
                                    st.warning("이미 존재하는 빌드명입니다.")
                        build_type = new_build if new_build and new_build.strip() else ""
                    else:
                        build_type = selected_build
            with col3:
                part_options = ["프론트엔드", "백엔드", "데이터베이스", "인프라", "기획", "디자인", "QA"]
                if is_edit_mode and task_data:
                    default_part_index = part_options.index(task_data['part_division']) if task_data['part_division'] in part_options else 0
                else:
                    default_part_index = 0
                part_division = st.selectbox("파트 구분", options=part_options, index=default_part_index, key=f"{form_key_prefix}task_part_division")
            
            # 세 번째 행: 상세 내용
            default_content = task_data['content'] if is_edit_mode and task_data else ""
            content = st.text_area("업무 내용", value=default_content, placeholder="업무에 대한 자세한 설명을 입력하세요...", key=f"{form_key_prefix}task_content")
            
            # 네 번째 행: 시간 추정
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                fibonacci_options = [1, 2, 3, 5, 8, 13, 21]
                if is_edit_mode and task_data:
                    default_story_points = task_data['story_points_leader'] if task_data['story_points_leader'] in fibonacci_options else 1
                else:
                    default_story_points = 1
                
                story_points_leader = st.number_input(
                    "스토리 포인트", 
                    min_value=min(fibonacci_options), 
                    max_value=max(fibonacci_options), 
                    value=default_story_points, 
                    step=1, 
                    key=f"{form_key_prefix}task_story_points",
                    help="피보나치 수열: 1, 2, 3, 5, 8, 13, 21"
                )
            with col2:
                default_duration_leader = float(task_data['duration_leader']) if is_edit_mode and task_data else 0.0
                duration_leader = st.number_input("예상 기간(리더)", min_value=0.0, max_value=100.0, value=default_duration_leader, step=0.5, key=f"{form_key_prefix}task_duration_leader")
            with col3:
                default_duration_assignee = float(task_data['duration_assignee']) if is_edit_mode and task_data else 0.0
                duration_assignee = st.number_input("예상 기간(담당자)", min_value=0.0, max_value=100.0, value=default_duration_assignee, step=0.5, key=f"{form_key_prefix}task_duration_assignee")
            with col4:
                # 자동 계산된 최종 예상시간
                calculated_hours = (duration_leader + duration_assignee) / 2 if (duration_leader + duration_assignee) > 0 else 0.0
                final_hours = st.text_input("최종 예상시간", value=f"{calculated_hours:.1f}", key=f"{form_key_prefix}task_final_hours", disabled=True, help="리더와 담당자 예상 기간의 평균으로 자동 계산됩니다")
                final_hours = calculated_hours
            
            # 다섯 번째 행: AI 판단 및 연결성  
            col1, col2 = st.columns(2)
            with col1:
                default_ai_judgment = task_data['ai_judgment'] if is_edit_mode and task_data else ""
                ai_judgment = st.text_input("AI 판단", value=default_ai_judgment, placeholder="AI 분석 결과...", key=f"{form_key_prefix}task_ai_judgment")
            with col2:
                # 연결성 - 기존 업무 목록에서 선택
                if is_edit_mode and task_data:
                    # 수정 모드: 현재 수정 중인 업무는 제외
                    existing_tasks = [t for t in get_tasks(st.session_state.current_project_id) if t['id'] != task_data['id']]
                else:
                    existing_tasks = get_tasks(st.session_state.current_project_id)
                
                task_options = ["연결 없음"] + [f"#{task['id']} - {task['item_name']}" for task in existing_tasks]
                
                # 현재 연결성 값 찾기
                default_connectivity_index = 0
                if is_edit_mode and task_data and task_data['connectivity']:
                    for i, option in enumerate(task_options[1:], 1):
                        if option.startswith(f"#{task_data['connectivity']} -"):
                            default_connectivity_index = i
                            break
                
                selected_connectivity = st.selectbox(
                    "업무 연결성", 
                    options=task_options, 
                    index=default_connectivity_index, 
                    key=f"{form_key_prefix}task_connectivity",
                    help="이 업무와 연관된 다른 업무를 선택하세요"
                )
                
                # 실제 저장할 connectivity 값 (ID만 추출)
                if selected_connectivity == "연결 없음":
                    connectivity = ""
                else:
                    connectivity = selected_connectivity.split(" - ")[0].replace("#", "")
            
            # 버튼 행
            if is_edit_mode:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("💾 수정 완료", key=f"{form_key_prefix}update_task", type="primary"):
                        try:
                            update_task(
                                task_id=task_data['id'],
                                attribute=attribute,
                                build_type=build_type,
                                part_division=part_division,
                                priority=priority,
                                item_name=item_name.strip(),
                                content=content,
                                assignee=assignee if assignee != "미지정" else "",
                                story_points_leader=story_points_leader,
                                duration_leader=duration_leader,
                                duration_assignee=duration_assignee,
                                final_hours=final_hours,
                                ai_judgment=ai_judgment,
                                connectivity=connectivity
                            )
                            st.success(f"✅ 업무 '{item_name}'가 수정되었습니다!")
                            del st.session_state.editing_task_id
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 업무 수정 중 오류가 발생했습니다: {str(e)}")
                with col3:
                    if st.button("❌ 취소", key=f"{form_key_prefix}cancel_edit_task"):
                        del st.session_state.editing_task_id
                        st.rerun()
            else:
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                with col_btn2:
                    if st.button("📝 업무 추가", key=f"{form_key_prefix}add_task", type="primary", width="stretch"):
                        if item_name and item_name.strip():
                            try:
                                add_task(
                                    project_id=st.session_state.current_project_id,
                                    attribute=attribute,
                                    build_type=build_type,
                                    part_division=part_division,
                                    priority=priority,
                                    item_name=item_name.strip(),
                                    content=content,
                                    assignee=assignee if assignee != "미지정" else "",
                                    story_points_leader=story_points_leader,
                                    duration_leader=duration_leader,
                                    duration_assignee=duration_assignee,
                                    final_hours=final_hours,
                                    ai_judgment=ai_judgment,
                                    connectivity=connectivity
                                )
                                st.success(f"✅ 업무 '{item_name}'가 추가되었습니다!")
                            except Exception as e:
                                st.error(f"❌ 업무 추가 중 오류가 발생했습니다: {str(e)}")
                        else:
                            st.error("⚠️ 업무명을 입력해주세요.")

class TaskList:
    """업무 목록 표시 컴포넌트 클래스"""
    
    @staticmethod
    def render():
        """업무 목록 표시"""
        tasks = get_tasks(st.session_state.current_project_id)
        
        if tasks:
            st.subheader(f"📊 업무 현황 ({len(tasks)}개)")
            
            # 업무 테이블 표시
            tasks_df = pd.DataFrame([
                {
                    "ID": task["id"],
                    "업무명": task["item_name"],
                    "속성": task.get("attribute", ""),
                    "빌드": task.get("build_type", ""),
                    "파트": task.get("part_division", ""),
                    "우선순위": task.get("priority", 3),
                    "담당자": task.get("assignee", "미지정"),
                    "스토리포인트": task.get("story_points_leader", 0),
                    "리더예상": f"{task.get('duration_leader', 0):.1f}h",
                    "담당자예상": f"{task.get('duration_assignee', 0):.1f}h", 
                    "최종시간": f"{task.get('final_hours', 0):.1f}h",
                    "AI판단": task.get("ai_judgment", "")[:20] + "..." if len(task.get("ai_judgment", "")) > 20 else task.get("ai_judgment", ""),
                    "연결성": f"#{task.get('connectivity', '')}" if task.get('connectivity', '') else "없음",
                    "등록일": task["created_at"][:10] if task["created_at"] else ""
                } for task in tasks
            ])
            
            st.dataframe(tasks_df, width="stretch", hide_index=True)
            
            # 업무 수정/삭제 기능
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("✏️ 업무 수정"):
                    task_to_edit = st.selectbox(
                        "수정할 업무 선택",
                        options=[t["id"] for t in tasks],
                        format_func=lambda x: next(t["item_name"] for t in tasks if t["id"] == x),
                        index=None,
                        placeholder="수정할 업무를 선택하세요",
                        key="edit_task_select"
                    )
                    
                    if task_to_edit:
                        if st.button("업무 수정하기", key="edit_task_btn", type="primary"):
                            st.session_state.editing_task_id = task_to_edit
                            st.rerun()
            
            with col2:
                with st.expander("🗑️ 업무 삭제"):
                    task_to_delete = st.selectbox(
                        "삭제할 업무 선택",
                        options=[t["id"] for t in tasks],
                        format_func=lambda x: next(t["item_name"] for t in tasks if t["id"] == x),
                        index=None,
                        placeholder="삭제할 업무를 선택하세요",
                        key="delete_task_select"
                    )
                    
                    if task_to_delete and st.button("업무 삭제", key="delete_task", type="secondary"):
                        if delete_task(task_to_delete):
                            st.success("✅ 업무가 삭제되었습니다.")
                            st.rerun()
                        else:
                            st.error("❌ 업무 삭제에 실패했습니다.")
        else:
            st.info("📝 아직 추가된 업무가 없습니다. 위에서 업무를 추가해주세요.")