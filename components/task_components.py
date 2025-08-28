# components/task_components.py - 업무 관련 UI 컴포넌트

import streamlit as st
import pandas as pd
from database import add_task, get_tasks, delete_task, get_team_members, update_task, get_task_by_id

class TaskForm:
    """업무 입력 폼 컴포넌트 클래스"""
    
    @staticmethod
    def render():
        """업무 입력 폼 렌더링"""
        st.header("📋 업무 관리")
        
        # 현재 프로젝트의 팀원 목록 가져오기 (담당자 선택용)
        team_members = get_team_members(st.session_state.current_project_id)
        member_options = ["미지정"] + [m["name"] for m in team_members]
        
        with st.container():
            st.subheader("새 업무 추가")
            
            # 첫 번째 행: 기본 정보
            col1, col2, col3 = st.columns(3)
            with col1:
                item_name = st.text_input("업무명 *", placeholder="예: 로그인 API 개발", key="task_item_name")
            with col2:
                priority = st.selectbox("우선순위", options=[1, 2, 3, 4, 5], index=2, key="task_priority")
            with col3:
                assignee = st.selectbox("담당자", options=member_options, index=0, key="task_assignee")
            
            # 두 번째 행: 분류 정보
            col1, col2, col3 = st.columns(3)
            with col1:
                attribute = st.selectbox(
                    "속성", 
                    options=["기능 개발", "버그 수정", "리팩토링", "테스트", "문서화", "기타"],
                    index=0, key="task_attribute"
                )
            with col2:
                # 기존 빌드 목록 (세션 상태로 관리)
                if 'build_types' not in st.session_state:
                    st.session_state.build_types = [
                        "Sprint 1.0", "Sprint 1.1", "Sprint 1.2", 
                        "v1.0.0", "v1.1.0", "v2.0.0",
                        "2024-Q4", "2025-Q1", "Hot Fix"
                    ]
                
                build_options = st.session_state.build_types + ["+ 새 빌드 추가"]
                selected_build = st.selectbox(
                    "적용 빌드",
                    options=build_options,
                    index=0,
                    key="task_build_select"
                )
                
                # 새 빌드 추가 선택 시
                if selected_build == "+ 새 빌드 추가":
                    new_build = st.text_input(
                        "새 빌드명",
                        placeholder="예: Sprint 2.0, v3.0.0",
                        key="new_build_input"
                    )
                    if new_build and new_build.strip():
                        if st.button("빌드 추가", key="add_build_btn"):
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
                part_division = st.selectbox(
                    "파트 구분",
                    options=["프론트엔드", "백엔드", "데이터베이스", "인프라", "기획", "디자인", "QA"],
                    index=0, key="task_part_division"
                )
            
            # 세 번째 행: 상세 내용
            content = st.text_area("업무 내용", placeholder="업무에 대한 자세한 설명을 입력하세요...", key="task_content")
            
            # 네 번째 행: 시간 추정
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                # 피보나치 수열 스토리 포인트 (1, 2, 3, 5, 8, 13, 21)
                fibonacci_options = [1, 2, 3, 5, 8, 13, 21]
                
                # 현재 스토리 포인트 값 관리
                if 'current_story_points' not in st.session_state:
                    st.session_state.current_story_points = 1
                
                # 현재 값이 피보나치 수열에 없으면 기본값으로 설정
                if st.session_state.current_story_points not in fibonacci_options:
                    st.session_state.current_story_points = 1
                
                story_points_leader = st.number_input(
                    "스토리 포인트", 
                    min_value=min(fibonacci_options), 
                    max_value=max(fibonacci_options), 
                    value=st.session_state.current_story_points, 
                    step=1, 
                    key="task_story_points",
                    help="피보나치 수열: 1, 2, 3, 5, 8, 13, 21"
                )
                
                # 입력값을 가장 가까운 피보나치 수로 조정
                if story_points_leader != st.session_state.current_story_points:
                    closest_fib = min(fibonacci_options, key=lambda x: abs(x - story_points_leader))
                    st.session_state.current_story_points = closest_fib
                    story_points_leader = closest_fib
            with col2:
                duration_leader = st.number_input("예상 기간(리더)", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="task_duration_leader")
            with col3:
                duration_assignee = st.number_input("예상 기간(담당자)", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key="task_duration_assignee")
            with col4:
                # 자동 계산된 최종 예상시간 (리더와 담당자 예상의 평균)
                calculated_hours = (duration_leader + duration_assignee) / 2 if (duration_leader + duration_assignee) > 0 else 0.0
                
                final_hours = st.text_input("최종 예상시간", value=f"{calculated_hours:.1f}", key="task_final_hours", disabled=True, help="리더와 담당자 예상 기간의 평균으로 자동 계산됩니다")
                final_hours = calculated_hours  # 실제 계산값 사용
            
            # 다섯 번째 행: AI 판단 및 연결성
            col1, col2 = st.columns(2)
            with col1:
                ai_judgment = st.text_input("AI 판단", placeholder="AI 분석 결과...", key="task_ai_judgment")
            with col2:
                # 현재 프로젝트의 기존 업무 목록 가져오기 (연결성 선택용)
                existing_tasks = get_tasks(st.session_state.current_project_id)
                task_options = ["연결 없음"] + [f"#{task['id']} - {task['item_name']}" for task in existing_tasks]
                
                selected_connectivity = st.selectbox(
                    "업무 연결성", 
                    options=task_options, 
                    index=0, 
                    key="task_connectivity",
                    help="이 업무와 연관된 다른 업무를 선택하세요"
                )
                
                # 실제 저장할 connectivity 값 (ID만 추출)
                if selected_connectivity == "연결 없음":
                    connectivity = ""
                else:
                    # "#123 - 업무명" 형태에서 ID만 추출
                    connectivity = selected_connectivity.split(" - ")[0].replace("#", "")
            
            # 추가 버튼
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                if st.button("📝 업무 추가", key="add_task", type="primary", width="stretch"):
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

class TaskEditForm:
    """업무 수정 폼 컴포넌트 클래스"""
    
    @staticmethod
    def render():
        """업무 수정 폼 렌더링"""
        if 'editing_task_id' not in st.session_state:
            return
            
        task_id = st.session_state.editing_task_id
        task = get_task_by_id(task_id)
        
        if not task:
            st.error("선택한 업무를 찾을 수 없습니다.")
            del st.session_state.editing_task_id
            return
        
        st.header(f"✏️ 업무 수정: {task['item_name']}")
        
        # 현재 프로젝트의 팀원 목록 가져오기 (담당자 선택용)
        team_members = get_team_members(st.session_state.current_project_id)
        member_options = ["미지정"] + [m["name"] for m in team_members]
        
        with st.container():
            # 첫 번째 행: 기본 정보
            col1, col2, col3 = st.columns(3)
            with col1:
                item_name = st.text_input("업무명 *", value=task['item_name'], key="edit_task_item_name")
            with col2:
                priority = st.selectbox("우선순위", options=[1, 2, 3, 4, 5], index=task['priority']-1, key="edit_task_priority")
            with col3:
                current_assignee = task['assignee'] if task['assignee'] else "미지정"
                assignee_index = member_options.index(current_assignee) if current_assignee in member_options else 0
                assignee = st.selectbox("담당자", options=member_options, index=assignee_index, key="edit_task_assignee")
            
            # 두 번째 행: 분류 정보
            col1, col2, col3 = st.columns(3)
            with col1:
                attribute_options = ["기능 개발", "버그 수정", "리팩토링", "테스트", "문서화", "기타"]
                attribute_index = attribute_options.index(task['attribute']) if task['attribute'] in attribute_options else 0
                attribute = st.selectbox("속성", options=attribute_options, index=attribute_index, key="edit_task_attribute")
            with col2:
                # 기존 빌드 목록
                if 'build_types' not in st.session_state:
                    st.session_state.build_types = [
                        "Sprint 1.0", "Sprint 1.1", "Sprint 1.2", 
                        "v1.0.0", "v1.1.0", "v2.0.0",
                        "2024-Q4", "2025-Q1", "Hot Fix"  
                    ]
                
                # 현재 빌드가 목록에 없으면 추가
                if task['build_type'] and task['build_type'] not in st.session_state.build_types:
                    st.session_state.build_types.append(task['build_type'])
                
                build_index = st.session_state.build_types.index(task['build_type']) if task['build_type'] in st.session_state.build_types else 0
                build_type = st.selectbox("적용 빌드", options=st.session_state.build_types, index=build_index, key="edit_task_build_type")
            with col3:
                part_options = ["프론트엔드", "백엔드", "데이터베이스", "인프라", "기획", "디자인", "QA"]
                part_index = part_options.index(task['part_division']) if task['part_division'] in part_options else 0
                part_division = st.selectbox("파트 구분", options=part_options, index=part_index, key="edit_task_part_division")
            
            # 세 번째 행: 상세 내용
            content = st.text_area("업무 내용", value=task['content'], key="edit_task_content")
            
            # 네 번째 행: 시간 추정
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                fibonacci_options = [1, 2, 3, 5, 8, 13, 21]
                story_index = fibonacci_options.index(task['story_points_leader']) if task['story_points_leader'] in fibonacci_options else 0
                story_points_leader = st.selectbox("스토리 포인트", options=fibonacci_options, index=story_index, key="edit_task_story_points")
            with col2:
                duration_leader = st.number_input("예상 기간(리더)", value=float(task['duration_leader']), min_value=0.0, max_value=100.0, step=0.5, key="edit_task_duration_leader")
            with col3:
                duration_assignee = st.number_input("예상 기간(담당자)", value=float(task['duration_assignee']), min_value=0.0, max_value=100.0, step=0.5, key="edit_task_duration_assignee")
            with col4:
                # 자동 계산된 최종 예상시간
                calculated_hours = (duration_leader + duration_assignee) / 2 if (duration_leader + duration_assignee) > 0 else 0.0
                final_hours = st.text_input("최종 예상시간", value=f"{calculated_hours:.1f}", key="edit_task_final_hours", disabled=True, help="리더와 담당자 예상 기간의 평균으로 자동 계산됩니다")
                final_hours = calculated_hours
            
            # 다섯 번째 행: AI 판단 및 연결성
            col1, col2 = st.columns(2)
            with col1:
                ai_judgment = st.text_input("AI 판단", value=task['ai_judgment'], key="edit_task_ai_judgment")
            with col2:
                # 연결성 - 기존 업무 목록에서 선택 (현재 수정 중인 업무는 제외)
                existing_tasks = [t for t in get_tasks(st.session_state.current_project_id) if t['id'] != task_id]
                task_options = ["연결 없음"] + [f"#{t['id']} - {t['item_name']}" for t in existing_tasks]
                
                # 현재 연결성 값 찾기
                current_connectivity = "연결 없음"
                if task['connectivity']:
                    for option in task_options[1:]:  # "연결 없음" 제외
                        if option.startswith(f"#{task['connectivity']} -"):
                            current_connectivity = option
                            break
                
                connectivity_index = task_options.index(current_connectivity) if current_connectivity in task_options else 0
                selected_connectivity = st.selectbox("업무 연결성", options=task_options, index=connectivity_index, key="edit_task_connectivity")
                
                # 실제 저장할 connectivity 값 (ID만 추출)
                if selected_connectivity == "연결 없음":
                    connectivity = ""
                else:
                    connectivity = selected_connectivity.split(" - ")[0].replace("#", "")
            
            # 버튼 행
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 수정 완료", key="update_task", type="primary"):
                    try:
                        update_task(
                            task_id=task_id,
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
                if st.button("❌ 취소", key="cancel_edit_task"):
                    del st.session_state.editing_task_id
                    st.rerun()