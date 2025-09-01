"""
인증 및 보안 관련 유틸리티
비밀번호 해싱 등
"""

from werkzeug.security import generate_password_hash, check_password_hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시된 비밀번호를 비교하여 검증
    
    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호
    
    Returns:
        bool: 비밀번호 일치 여부
    """
    return check_password_hash(hashed_password, plain_password)

def get_password_hash(password: str) -> str:
    """
    평문 비밀번호를 해시화
    
    Args:
        password: 평문 비밀번호
    
    Returns:
        str: 해시된 비밀번호
    """
    return generate_password_hash(password)