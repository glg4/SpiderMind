"""
SpiderMind - Token 管理工具
支持从 .env 文件读取、运行时更新、持久化保存 Token
"""
import os
import re
from pathlib import Path

ENV_FILE = Path(__file__).parent / ".env"


def _read_env_file() -> dict:
    """读取 .env 文件，返回 key-value 字典"""
    result = {}
    if not ENV_FILE.exists():
        return result
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                result[k.strip()] = v.strip()
    return result


def get_token() -> str:
    """获取当前 Token（优先 .env，其次环境变量）"""
    env = _read_env_file()
    return (
        env.get("COZE_API_TOKEN")
        or os.environ.get("COZE_API_TOKEN")
        or ""
    )


def get_config() -> dict:
    """获取完整配置"""
    env = _read_env_file()
    token = env.get("COZE_API_TOKEN") or os.environ.get("COZE_API_TOKEN") or ""
    # 检测是否为空或占位符
    if not token or "在这里填入" in token or "请在这里" in token:
        token = ""
    return {
        "token": token,
        "bot_id": env.get("COZE_BOT_ID") or "7623014360998461482",
    }


def save_token(new_token: str, bot_id: str = None) -> bool:
    """
    将新 Token 写入 .env 文件（原地更新，保留注释）
    返回 True 表示成功
    """
    new_token = new_token.strip()
    if not new_token:
        return False

    # 读取现有内容
    lines = []
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

    def update_or_append(lines, key, value):
        """更新已存在的 key，或在末尾追加"""
        pattern = re.compile(rf"^{re.escape(key)}\s*=")
        updated = False
        new_lines = []
        for line in lines:
            if pattern.match(line):
                new_lines.append(f"{key}={value}\n")
                updated = True
            else:
                new_lines.append(line)
        if not updated:
            new_lines.append(f"{key}={value}\n")
        return new_lines

    lines = update_or_append(lines, "COZE_API_TOKEN", new_token)
    if bot_id:
        lines = update_or_append(lines, "COZE_BOT_ID", bot_id)

    try:
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    except Exception:
        return False


def mask_token(token: str) -> str:
    """脱敏显示 Token"""
    if not token or len(token) < 12:
        return "（未配置）"
    return token[:8] + "..." + token[-6:]
