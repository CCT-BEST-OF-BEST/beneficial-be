import json
from pathlib import Path

def load_rag_config():
    # 현재 파일에서 ../../rag/rag_config.json로 이동!
    config_path = Path(__file__).parent.parent / "schema" / "rag_schema.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

