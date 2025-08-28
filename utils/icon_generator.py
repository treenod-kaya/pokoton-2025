# utils/icon_generator.py - 프로필 아이콘 생성 유틸리티

import base64
from typing import Dict

class ProfileIconGenerator:
    """프로필 아이콘 생성기"""
    
    # 10가지 다양한 컬러 조합
    ICON_COLORS = [
        {"bg": "#FF6B6B", "text": "#FFFFFF"},  # 빨강
        {"bg": "#4ECDC4", "text": "#FFFFFF"},  # 청록
        {"bg": "#45B7D1", "text": "#FFFFFF"},  # 파랑  
        {"bg": "#96CEB4", "text": "#FFFFFF"},  # 연두
        {"bg": "#FECA57", "text": "#FFFFFF"},  # 노랑
        {"bg": "#FF9FF3", "text": "#FFFFFF"},  # 분홍
        {"bg": "#54A0FF", "text": "#FFFFFF"},  # 하늘색
        {"bg": "#5F27CD", "text": "#FFFFFF"},  # 보라
        {"bg": "#00D2D3", "text": "#FFFFFF"},  # 민트
        {"bg": "#FF6348", "text": "#FFFFFF"},  # 주황
    ]
    
    @classmethod
    def get_icon_svg(cls, index: int, name: str = "U") -> str:
        """SVG 형태의 프로필 아이콘 생성"""
        # 인덱스 범위 체크
        color_index = index % len(cls.ICON_COLORS)
        colors = cls.ICON_COLORS[color_index]
        
        # 이름의 첫 글자 추출 (한글/영문 지원)
        initial = name[0].upper() if name else "U"
        
        svg = f'''
        <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{colors['bg']}" stroke="#E0E0E0" stroke-width="1"/>
            <text x="16" y="20" text-anchor="middle" fill="{colors['text']}" 
                  font-family="Arial, sans-serif" font-size="14" font-weight="bold">{initial}</text>
        </svg>
        '''
        return svg.strip()
    
    @classmethod  
    def get_icon_base64(cls, index: int, name: str = "U") -> str:
        """Base64 인코딩된 SVG 아이콘 반환"""
        svg = cls.get_icon_svg(index, name)
        encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{encoded}"
    
    @classmethod
    def get_icon_html(cls, index: int, name: str = "U", size: int = 32) -> str:
        """HTML img 태그 형태로 아이콘 반환"""
        base64_data = cls.get_icon_base64(index, name)
        return f'<img src="{base64_data}" width="{size}" height="{size}" style="border-radius: 50%; margin-right: 8px;">'

def get_random_icon_index() -> int:
    """랜덤 아이콘 인덱스 반환 (0-9)"""
    import random
    return random.randint(0, 9)