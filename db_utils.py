# -*- coding: utf-8 -*-
"""
SpiderMind - 数据库工具模块
统一管理 SQLite 数据库路径，避免各页面重复拼接
"""
import os
import sqlite3
import sys
from pathlib import Path


def _find_project_root():
    """自动查找项目根目录（SpiderMind 文件夹）"""
    # 方案1：基于当前文件所在位置（最可靠）
    p = Path(__file__).resolve().parent
    if (p / "main.py").exists():
        return p

    # 方案2：基于调用栈回溯找 main.py 所在目录
    import inspect
    for frame_info in inspect.stack():
        f = frame_info.filename
        if 'main.py' in f or 'pages' in f:
            candidate = Path(f).resolve().parent
            if (candidate / "main.py").exists():
                return candidate
            if candidate.parent and (candidate.parent / "main.py").exists():
                return candidate.parent

    # 方案3：基于当前工作目录
    cwd = Path.cwd()
    if (cwd / "main.py").exists():
        return cwd

    # 方案4：sys.path 中查找
    for sp in sys.path:
        sp_path = Path(sp).resolve()
        if (sp_path / "main.py").exists():
            return sp_path

    # 最终回退
    return p


PROJECT_ROOT = _find_project_root()
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "chronic_records_v2.db"


def get_db_path(force_create=True):
    """获取数据库文件绝对路径，自动创建目录"""
    if force_create:
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            pass  # 静默处理，下面连接时会报更有意义的错误
    return str(DB_PATH)


def get_db_connection():
    """获取数据库连接，自动建表"""
    db_path = get_db_path()

    # 确保文件可访问
    if not os.path.exists(db_path):
        # 确保父目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path, timeout=10)
    _init_tables(conn)
    return conn


def _init_tables(conn):
    """创建所有需要的表（与各页面实际使用的 schema 保持一致）"""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS indicator_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_name TEXT NOT NULL,
            value TEXT NOT NULL,
            unit TEXT DEFAULT '',
            reference_range TEXT DEFAULT '',
            report_source TEXT DEFAULT '手动录入',
            record_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS drug_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_name TEXT NOT NULL,
            dosage TEXT DEFAULT '',
            frequency TEXT DEFAULT '',
            reminder_time TEXT DEFAULT '08:00',
            start_date DATE NOT NULL,
            end_date DATE,
            is_active INTEGER DEFAULT 1,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS medication_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_record_id INTEGER,
            planned_time TEXT,
            actual_time TIMESTAMP,
            status TEXT DEFAULT 'pending',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (drug_record_id) REFERENCES drug_records(id)
        );

        CREATE TABLE IF NOT EXISTS health_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            task_type TEXT DEFAULT 'daily',
            target TEXT DEFAULT '',
            unit TEXT DEFAULT '',
            reminder_time TEXT DEFAULT '08:00',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS task_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            planned_date DATE NOT NULL,
            completed_at TIMESTAMP,
            value TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            actual_value TEXT DEFAULT '',
            FOREIGN KEY (task_id) REFERENCES health_tasks(id)
        );
    """)

    # 兼容旧数据库：补充可能缺失的列
    _ensure_columns(conn)


def _ensure_columns(conn):
    """检测并补充旧数据库中可能缺失的列"""
    alterations = {
        'health_tasks': ['notes'],
        'task_logs': ['actual_value'],
    }
    col_defaults = {
        'notes': "TEXT DEFAULT ''",
        'actual_value': "TEXT DEFAULT ''",
    }
    for table, cols in alterations.items():
        try:
            existing = {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
            for col in cols:
                if col not in existing:
                    conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_defaults[col]}")
        except Exception:
            pass  # 表不存在等情况由 _init_tables 处理
