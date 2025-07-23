"""
pytest 설정 파일
"""
import pytest
import sys
import os
import asyncio

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pytest-asyncio는 pytest.ini에서 설정

# asyncio 모드 설정
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 