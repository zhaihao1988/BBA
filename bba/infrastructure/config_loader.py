import os
from typing import Dict
import yaml


def load_chart_of_accounts(path: str) -> Dict[str, str]:
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    # 统一 key 为字符串
    return {str(k): str(v) for k, v in data.items()}


