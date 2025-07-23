"""
공통 로깅 설정
모든 모듈에서 사용할 수 있는 표준화된 로깅 설정
"""
import logging
import sys
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    표준화된 로거 설정
    
    Args:
        name: 로거 이름 (보통 __name__ 사용)
        level: 로깅 레벨
        
    Returns:
        설정된 로거 인스턴스
    """
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 설정되어 있으면 중복 설정 방지
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    로거 인스턴스 반환 (간단한 버전)
    
    Args:
        name: 로거 이름
        
    Returns:
        로거 인스턴스
    """
    return setup_logger(name)


# 로깅 레벨 상수
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
} 