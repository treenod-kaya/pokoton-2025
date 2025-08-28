# components/team_components.py - 팀원 관련 UI 컴포넌트

import streamlit as st
import pandas as pd
from database import add_team_member, get_team_members, delete_team_member

class TeamMemberForm:
    """팀원 입력 폼 컴포넌트 클래스"""
    
    @staticmethod
    def render():
        """팀원 입력 폼 렌더링"""
        st.header("👥 팀원 관리")
        
        with st.container():
            st.subheader("새 팀원 추가")
            
            # 2행 레이아웃으로 개선
            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                member_name = st.text_input(
                    "팀원명 *", 
                    placeholder="예: 김개발", 
                    key="member_name",
                    help="팀원의 실명 또는 닉네임을 입력하세요"
                )
            with row1_col2:
                member_role = st.selectbox(
                    "역할 *",
                    options=["기획", "클라이언트", "애니메이터", "프로젝트 매니저", "크리에이티브", "기타"],
                    index=None,
                    placeholder="역할을 선택하세요",
                    key="member_role"
                )
            
            # 일일 가용시간 입력 제거 - 기본값 8.0시간으로 고정
            member_hours = 8.0
            
            # 추가 버튼
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                if st.button("👨‍💻 팀원 추가", key="add_member", type="primary", use_container_width=True):
                    if member_name and member_name.strip() and member_role:
                        try:
                            add_team_member(
                                st.session_state.current_project_id, 
                                member_name.strip(), 
                                member_role, 
                                member_hours
                            )
                            st.success(f"✅ 팀원 '{member_name}'({member_role})가 추가되었습니다!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 팀원 추가 중 오류가 발생했습니다: {str(e)}")
                    else:
                        st.error("⚠️ 팀원명과 역할을 입력해주세요.")

class TeamMemberList:
    """팀원 목록 표시 컴포넌트 클래스"""
    
    @staticmethod
    def render():
        """팀원 목록 표시"""
        members = get_team_members(st.session_state.current_project_id)
        
        if members:
            st.subheader(f"📋 현재 팀원 현황 ({len(members)}명)")
            
            # 카드 형태로 팀원 표시
            cols = st.columns(min(len(members), 3))  # 최대 3개 컬럼
            
            for i, member in enumerate(members):
                with cols[i % 3]:
                    # 간단한 팀원 카드 (다크 모드 호환)
                    st.markdown(f"""
                    <div style="
                        border: 1px solid rgba(128, 128, 128, 0.5);
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                        background: rgba(0, 0, 0, 0.05);
                        backdrop-filter: blur(5px);
                    ">
                        <h4 style="margin: 0 0 10px 0; color: inherit;">👤 {member['name']}</h4>
                        <p style="margin: 5px 0; color: inherit;"><strong>역할:</strong> {member['role']}</p>
                        <p style="margin: 5px 0; color: inherit;"><strong>가용시간:</strong> {member['available_hours_per_day']:.1f}시간/일</p>
                        <p style="margin: 5px 0; color: inherit; opacity: 0.7;"><small>등록일: {member['created_at'][:10] if member['created_at'] else ''}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 개별 삭제 버튼
                    if st.button(f"🗑️ 삭제", key=f"delete_{member['id']}", help=f"{member['name']} 삭제"):
                        if delete_team_member(member['id']):
                            st.success(f"✅ {member['name']}이(가) 삭제되었습니다.")
                            st.rerun()
                        else:
                            st.error("❌ 팀원 삭제에 실패했습니다.")
            
            st.markdown("---")
            
            # 팀 요약 정보
            total_hours = sum(m['available_hours_per_day'] for m in members)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("총 팀원 수", f"{len(members)}명")
            with col2:
                st.metric("일일 총 가용시간", f"{total_hours:.1f}시간")
                
            # 테이블 형태도 제공 (토글)
            with st.expander("📊 상세 테이블 보기"):
                members_df = pd.DataFrame([
                    {
                        "ID": m["id"],
                        "팀원명": m["name"],
                        "역할": m["role"],
                        "일일 가용시간": f"{m['available_hours_per_day']:.1f}h",
                        "등록일": m["created_at"][:10] if m["created_at"] else ""
                    } for m in members
                ])
                
                st.dataframe(members_df, use_container_width=True, hide_index=True)
                
        else:
            st.info("👥 아직 추가된 팀원이 없습니다. 위에서 팀원을 추가해주세요.")