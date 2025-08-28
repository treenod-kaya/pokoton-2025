# components/system_components.py - 시스템 관련 UI 컴포넌트

import streamlit as st
from database import get_all_projects

class SystemStatus:
    """시스템 상태 확인 컴포넌트 클래스"""
    
    @staticmethod
    def render():
        """시스템 상태 확인 렌더링"""
        st.subheader("🔍 시스템 상태 확인")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 데이터베이스 연결 테스트
            try:
                from database import db
                conn_test = db.get_connection()
                conn_test.close()
                st.success("✅ 데이터베이스 연결 성공")
            except Exception as e:
                st.error(f"❌ 데이터베이스 연결 실패: {e}")
        
        with col2:
            # 설정 파일 로딩 테스트
            try:
                from config import STREAMLIT_CONFIG
                st.success(f"✅ 설정 로딩 완료")
                st.caption(f"앱 제목: {STREAMLIT_CONFIG['page_title'][:20]}...")
            except Exception as e:
                st.error(f"❌ 설정 로딩 실패: {e}")
        
        with col3:
            # 프로젝트 목록 테스트
            try:
                projects = get_all_projects()
                st.success(f"✅ 프로젝트 조회 완료")
                st.caption(f"총 {len(projects)}개 프로젝트")
            except Exception as e:
                st.error(f"❌ 프로젝트 조회 실패: {e}")

class DevelopmentTools:
    """개발 도구 컴포넌트 클래스"""
    
    @staticmethod
    def render():
        """개발 도구 렌더링"""
        with st.expander("🔧 개발 도구", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📝 샘플 데이터 생성"):
                    try:
                        from init_db import insert_sample_data
                        insert_sample_data()
                        st.success("샘플 데이터가 생성되었습니다!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"샘플 데이터 생성 실패: {e}")
            
            with col2:
                if st.button("🔄 데이터베이스 상태 확인"):
                    try:
                        from init_db import check_database_status
                        check_database_status()
                        st.success("콘솔에서 데이터베이스 상태를 확인하세요.")
                    except Exception as e:
                        st.error(f"상태 확인 실패: {e}")

class ProgressIndicator:
    """진행 단계 표시 컴포넌트 클래스"""
    
    @staticmethod
    def render(current_step: str):
        """진행 단계 표시 렌더링"""
        steps = {
            "H1": "환경 세팅",
            "H2": "팀원 입력", 
            "H3": "업무 입력",
            "H4": "시뮬레이션",
            "H5": "결과 표시"
        }
        
        st.markdown("### 📊 개발 진행 상황")
        
        cols = st.columns(len(steps))
        for i, (step_key, step_name) in enumerate(steps.items()):
            with cols[i]:
                if step_key == current_step:
                    st.success(f"🟢 {step_key}\\n{step_name}")
                elif step_key < current_step:
                    st.info(f"✅ {step_key}\\n{step_name}")
                else:
                    st.markdown(f'<p style="color:#808080;">⚪ {step_key}<br/>{step_name}</p>', unsafe_allow_html=True)