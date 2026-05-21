import logging
import sys

# ANSI 색상 코드
_COLORS = {
    "DEBUG":    "\033[90m",   # 회색
    "INFO":     "\033[36m",   # 청록
    "WARNING":  "\033[33m",   # 노랑
    "ERROR":    "\033[31m",   # 빨강
    "CRITICAL": "\033[35m",   # 보라
    "RESET":    "\033[0m",
    "DIM":      "\033[2m",
}

_ICONS = {
    "DEBUG":    "·",
    "INFO":     "✓",
    "WARNING":  "⚠",
    "ERROR":    "✗",
    "CRITICAL": "‼",
}


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        color = _COLORS.get(level, "")
        reset = _COLORS["RESET"]
        dim   = _COLORS["DIM"]
        icon  = _ICONS.get(level, "·")

        # 모듈 이름 마지막 파트만 표시
        short_name = record.name.split(".")[-1]
        time_str = self.formatTime(record, "%H:%M:%S")

        # uvicorn 액세스 로그는 간결하게
        if record.name.startswith("uvicorn.access"):
            return f"{dim}{time_str}{reset}  {record.getMessage()}"

        return (
            f"{dim}{time_str}{reset}  "
            f"{color}{icon} {level:<7}{reset}  "
            f"{dim}{short_name:<22}{reset}  "
            f"{record.getMessage()}"
        )


def _configure_root_logger() -> None:
    """루트 로거 단 한 번만 설정 (중복 방지)"""
    root = logging.getLogger()
    if root.handlers:
        return

    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(ColorFormatter())
    root.addHandler(handler)

    # 외부 라이브러리 노이즈 억제
    for noisy in (
        "httpx", "httpcore", "openai", "chromadb", "watchfiles", "urllib3",
        "pymongo", "mongodb", "topology", "connection", "serverSelection",
        "commandMonitoring", "connectionPoolMonitoring",
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)


_configure_root_logger()


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = True
    return logger


def setup_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    return get_logger(name)


LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
