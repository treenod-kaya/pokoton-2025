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
            
            # 입사일 입력 추가
            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                from datetime import date
                hire_date = st.date_input(
                    "입사일",
                    value=date.today(),
                    key="member_hire_date",
                    help="팀원의 입사일을 선택하세요"
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
                                member_hours,
                                hire_date.strftime('%Y-%m-%d')
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
                    # 커스텀 아이콘 생성 (안전한 방식)
                    try:
                        from utils.icon_generator import ProfileIconGenerator
                        icon_html = ProfileIconGenerator.get_icon_html(
                            member.get('profile_icon_index', 0), 
                            member['name'], 
                            size=40
                        )
                    except Exception as e:
                        # 아이콘 생성 실패시 기본 이모지 사용
                        icon_html = '<span style="margin-right: 8px;">👤</span>'
                    
                    # D-DAY 계산 (강화된 예외 처리)
                    d_day_text = ""
                    hire_date_value = member.get('hire_date')
                    
                    if (hire_date_value and 
                        hire_date_value != 'None' and
                        str(hire_date_value).strip() and
                        str(hire_date_value).strip().lower() != 'none'):
                        from datetime import date, datetime
                        try:
                            hire_date_str = str(hire_date_value).strip()
                            hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
                            today = date.today()
                            days_diff = (today - hire_date).days
                            
                            if days_diff == 0:
                                d_day_text = "D-DAY"
                            else:
                                d_day_text = f"D+{days_diff}"
                        except (ValueError, AttributeError, TypeError) as e:
                            # 날짜 파싱 실패시 빈 문자열
                            d_day_text = ""
                        except Exception as e:
                            # 기타 모든 오류 처리
                            d_day_text = ""
                    
                    # HTML 이스케이프 처리 (안전한 방식)
                    import html
                    
                    # 각 값에 대한 안전한 처리
                    safe_name = html.escape(str(member.get('name', '이름없음')))
                    safe_role = html.escape(str(member.get('role', '역할없음')))
                    
                    # 입사일 안전한 처리 - None, 'None', 빈 문자열 모두 처리
                    hire_date_display = member.get('hire_date')
                    if (not hire_date_display or 
                        hire_date_display == 'None' or 
                        str(hire_date_display).strip() == '' or
                        str(hire_date_display).strip().lower() == 'none'):
                        hire_date_display = '미입력'
                    safe_hire_date = html.escape(str(hire_date_display))
                    
                    # 등록일 안전한 처리 - 더 강화된 예외 처리
                    created_at_display = member.get('created_at', '')
                    if created_at_display and str(created_at_display).strip():
                        try:
                            created_at_str = str(created_at_display)
                            if len(created_at_str) >= 10:
                                created_at_display = created_at_str[:10]
                            else:
                                created_at_display = created_at_str
                        except Exception as e:
                            created_at_display = '미상'
                    else:
                        created_at_display = '미상'
                    safe_created_at = html.escape(str(created_at_display))
                    
                    # D-DAY 안전한 처리
                    safe_d_day = html.escape(str(d_day_text)) if d_day_text else ''
                    
                    # 간단한 팀원 카드 - HTML을 한 줄로 처리하여 렌더링 문제 해결
                    d_day_span = f'<span style="margin-left: auto; font-size: 12px; background: rgba(0,123,255,0.1); padding: 2px 6px; border-radius: 12px; border: 1px solid rgba(0,123,255,0.3);">{safe_d_day}</span>' if safe_d_day else ''
                    
                    card_html = f'<div style="border: 1px solid rgba(128, 128, 128, 0.5); border-radius: 8px; padding: 15px; margin: 10px 0; background: rgba(0, 0, 0, 0.05); backdrop-filter: blur(5px);"><h4 style="margin: 0 0 10px 0; color: inherit; display: flex; align-items: center;">{icon_html}{safe_name}{d_day_span}</h4><p style="margin: 5px 0; color: inherit;"><b>역할:</b> {safe_role}</p><p style="margin: 5px 0; color: inherit;"><b>입사일:</b> {safe_hire_date}</p><p style="margin: 5px 0; color: inherit; opacity: 0.7;"><small>등록일: {safe_created_at}</small></p></div>'
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    # 개별 삭제 버튼
                    if st.button(f"🗑️ 삭제", key=f"delete_{member['id']}", help=f"{member['name']} 삭제"):
                        if delete_team_member(member['id']):
                            st.success(f"✅ {member['name']}이(가) 삭제되었습니다.")
                            st.rerun()
                        else:
                            st.error("❌ 팀원 삭제에 실패했습니다.")
            
            st.markdown("---")
            
            # 팀 요약 정보
            st.metric("총 팀원 수", f"{len(members)}명")
                
            # 테이블 형태도 제공 (토글)
            with st.expander("📊 상세 테이블 보기"):
                # D-DAY 계산 함수 (강화된 예외 처리)
                def calculate_d_day(hire_date_str):
                    if (not hire_date_str or 
                        hire_date_str == 'None' or 
                        not str(hire_date_str).strip() or
                        str(hire_date_str).strip().lower() == 'none'):
                        return ""
                    try:
                        from datetime import date, datetime
                        hire_date_clean = str(hire_date_str).strip()
                        hire_date = datetime.strptime(hire_date_clean, '%Y-%m-%d').date()
                        today = date.today()
                        days_diff = (today - hire_date).days
                        
                        if days_diff == 0:
                            return "D-DAY"
                        else:
                            return f"D+{days_diff}"
                    except (ValueError, AttributeError, TypeError):
                        return ""
                    except Exception:
                        return ""
                
                members_df = pd.DataFrame([
                    {
                        "ID": m.get("id", ""),
                        "팀원명": m.get("name", "이름없음"),
                        "역할": m.get("role", "역할없음"),
                        "입사일": m.get("hire_date") or "미입력",
                        "D-DAY": calculate_d_day(m.get("hire_date")),
                        "등록일": (m.get("created_at", "")[:10] if m.get("created_at") else "미상")
                    } for m in members
                ])
                
                st.dataframe(members_df, use_container_width=True, hide_index=True)
                
        else:
            st.info("👥 아직 추가된 팀원이 없습니다. 위에서 팀원을 추가해주세요.")