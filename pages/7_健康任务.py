"""
SpiderMind - 健康任务页（医院官网风格 + 本地任务打卡）
"""
import streamlit as st
import sys
import os
from datetime import datetime, date, timedelta
import sqlite3
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="健康任务 - SpiderMind",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

try:
    from components.hospital_theme import inject_theme, render_nav, render_breadcrumb, render_page_header
    inject_theme()
    render_nav("7_健康任务")
    render_breadcrumb("健康任务管理")
    render_page_header("🎯", "健康任务管理",
                       "设定每日健康打卡目标，追踪执行进度，培养规律自我管理习惯，支持自定义任务模板")
except Exception:
    pass

st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# ===== 数据库（统一由 db_utils 管理） =====
from db_utils import get_db_path, get_db_connection


def add_task(name, task_type, target, unit, reminder_time):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO health_tasks (task_name, task_type, target, unit, reminder_time)
        VALUES (?, ?, ?, ?, ?)
    """, (name, task_type, target, unit, reminder_time))
    task_id = c.lastrowid

    # 自动生成今天和未来7天的任务记录
    for i in range(7):
        d = (date.today() + timedelta(days=i)).isoformat()
        c.execute("""
            INSERT INTO task_logs (task_id, planned_date, status)
            VALUES (?, ?, 'pending')
        """, (task_id, d))

    conn.commit()
    conn.close()
    return task_id


def get_active_tasks():
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM health_tasks WHERE is_active=1 ORDER BY reminder_time",
        conn
    )
    conn.close()
    return df


def get_today_tasks():
    conn = get_db_connection()
    today = date.today().isoformat()
    df = pd.read_sql_query("""
        SELECT tl.*, ht.task_name, ht.task_type, ht.target, ht.unit, ht.reminder_time
        FROM task_logs tl
        JOIN health_tasks ht ON tl.task_id = ht.id
        WHERE tl.planned_date = ? AND ht.is_active = 1
        ORDER BY ht.reminder_time
    """, conn, params=(today,))
    conn.close()
    return df


def complete_task(log_id, value=''):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE task_logs SET status='done', completed_at=datetime('now'), value=?
        WHERE id=?
    """, (value, log_id))
    conn.commit()
    conn.close()


def get_streak(task_id):
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT planned_date, status FROM task_logs
        WHERE task_id=? AND planned_date <= date('now')
        ORDER BY planned_date DESC
        LIMIT 30
    """, conn, params=(task_id,))
    conn.close()

    streak = 0
    today = date.today()
    for _, row in df.iterrows():
        d = date.fromisoformat(row['planned_date'])
        if row['status'] == 'done':
            if d == today or d == today - timedelta(days=1) or (streak > 0 and d == today - timedelta(days=streak)):
                streak += 1
            else:
                break
        else:
            if d < today:
                break
    return streak


import pandas as pd

# ===== 功能卡片区 =====
st.markdown("""
<style>
.feature-card {
    background: white;
    border: 1px solid #E8D8C0;
    border-left: 4px solid #C85A1E;
    border-radius: 12px;
    padding: 24px 20px;
    text-align: center;
    transition: all 0.2s;
    cursor: pointer;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
}
.feature-card:hover {
    border-color: #C85A1E;
    box-shadow: 0 4px 16px rgba(200,90,30,0.1);
}
.feature-card .card-icon { font-size: 32px; margin-bottom: 4px; }
.feature-card .card-title { font-size: 15px; font-weight: 700; color: #2D1F0A; }
.feature-card .card-sub { font-size: 11px; color: #9A8060; letter-spacing: 0.5px; }
.feature-card .card-desc { font-size: 12px; color: #7A6A50; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

col_func1, col_func2, col_func3 = st.columns(3)
func_items = [
    (col_func1, "✅", "今日打卡", "Today's Check-in",
     "查看今日任务<br>完成健康打卡", "#FFF3EE"),
    (col_func2, "⚙️", "任务管理", "Task Management",
     "添加/编辑健康任务<br>设置提醒时间", "#F0FFF4"),
    (col_func3, "📊", "统计总览", "Statistics",
     "查看完成率趋势<br>追踪健康目标", "#F0F4FF"),
]

for col, icon, title, sub, desc, bg in func_items:
    with col:
        st.markdown(f"""
        <div class="feature-card" style="background:{bg}; border-left-color:#27ae60;">
            <div class="card-icon">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-sub">{sub}</div>
            <div class="card-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ===== Tab布局 =====
tab1, tab2, tab3 = st.tabs(["✅ 今日打卡", "⚙️ 任务管理", "📊 统计总览"])

# ===== 今日打卡 =====
with tab1:
    today_str = date.today().strftime('%Y年%m月%d日 %A')
    st.markdown(f"📅 **{today_str}**")

    today_tasks = get_today_tasks()

    if today_tasks.empty:
        st.info("📝 暂无健康任务，请在「任务管理」中添加")
    else:
        # 按时段分组
        morning = today_tasks[today_tasks['reminder_time'] <= '12:00']
        afternoon = today_tasks[(today_tasks['reminder_time'] > '12:00') & (today_tasks['reminder_time'] <= '18:00')]
        evening = today_tasks[today_tasks['reminder_time'] > '18:00']

        for label, group in [("🌅 早间任务", morning), ("☀️ 午间任务", afternoon), ("🌙 晚间任务", evening)]:
            if not group.empty:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(90deg, #F0F4FF 0%, #E8ECF5 100%);
                    border-left: 3px solid #3B5BDB;
                    border-radius: 8px;
                    padding: 10px 16px;
                    margin: 16px 0 8px 0;
                    font-size: 13px;
                    font-weight: 700;
                    color: #1A3A8F;
                    letter-spacing: 0.5px;
                ">{label}</div>
                """, unsafe_allow_html=True)

                for _, task in group.iterrows():
                    status = task['status']
                    is_done = status == 'done'

                    status_color = "#27ae60" if is_done else "#f39c12"
                    status_bg = "#F0FFF8" if is_done else "#FFFEF5"
                    status_icon = "✅" if is_done else "⏳"
                    status_label = f"完成时间：{task['completed_at']}" if is_done else f"计划时间：{task['reminder_time']}"
                    target_text = f" | {task['target']}{task['unit']}" if task['target'] else ""

                    st.markdown(f"""
                    <div style="
                        background: {status_bg};
                        border: 1px solid #E8D8C0;
                        border-left: 4px solid {status_color};
                        border-radius: 10px;
                        padding: 16px 20px;
                        margin-bottom: 8px;
                    ">
                        <div style="font-size:15px;font-weight:700;color:#2D1F0A;">{status_icon} {task['task_name']}
                            <span style="font-size:12px;color:#7A6A50;">{target_text}</span>
                        </div>
                        <div style="font-size:11px;color:#9A8060;margin-top:4px;">{status_label}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    col_card, col_action = st.columns([4, 1])
                    with col_action:
                        if not is_done:
                            if task['target']:
                                val = st.text_input(
                                    f"输入{task['task_name']}值",
                                    placeholder=f"目标：{task['target']}{task['unit']}",
                                    key=f"val_{task['id']}",
                                    label_visibility="collapsed"
                                )
                                if st.button("✅ 完成", key=f"btn_{task['id']}", use_container_width=True):
                                    complete_task(task['id'], val)
                                    st.rerun()
                            else:
                                if st.button("✅ 完成", key=f"btn_{task['id']}", use_container_width=True):
                                    complete_task(task['id'])
                                    st.rerun()
                        else:
                            st.markdown("<div style='color:#27ae60;font-size:13px;padding-top:8px;text-align:center;'>已完成 ✓</div>", unsafe_allow_html=True)

        # 今日总览
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #F0F4FF 0%, #E8ECF5 100%);
            border: 1px solid #C5D4F0;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
        ">
            <div style="font-size:13px;font-weight:700;color:#1A3A8F;margin-bottom:12px;">📋 今日打卡总览</div>
        """, unsafe_allow_html=True)

        total = len(today_tasks)
        done = len(today_tasks[today_tasks['status'] == 'done'])
        remaining = total - done

        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("已完成", f"{done}/{total}")
        with col_stat2:
            st.metric("待完成", f"{remaining}项")
        with col_stat3:
            rate = (done / total * 100) if total > 0 else 0
            st.metric("完成率", f"{rate:.0f}%",
                     delta="全部完成 ✓" if remaining == 0 else f"还剩{remaining}项")

        st.markdown("</div>", unsafe_allow_html=True)

# ===== 任务管理 =====
with tab2:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #F0FFF4 0%, #E8F5EC 100%);
        border: 1px solid #C8E6C9;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    ">
        <div style="font-size:13px;font-weight:700;color:#2D7A4F;margin-bottom:12px;">➕ 添加健康任务</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        task_name = st.text_input("任务名称", placeholder="例如：测量血压、记录血糖、健走30分钟")
    with col2:
        task_type = st.selectbox("任务类型", ["daily", "每周", "每月"],
                                 format_func=lambda x: {"daily": "每日", "每周": "每周", "每月": "每月"}.get(x, x))

    col3, col4 = st.columns(2)
    with col3:
        target = st.text_input("目标值（可选）", placeholder="例如：30、10000")
    with col4:
        unit = st.text_input("单位（可选）", placeholder="例如：分钟、步、mmHg")

    reminder_time = st.time_input("提醒时间", value=datetime.strptime('08:00', '%H:%M').time())

    # 预设任务卡片
    st.markdown("""
    <div style="font-size:12px;font-weight:700;color:#2D7A4F;margin-bottom:10px;">⚡ 快速添加预设任务</div>
    """, unsafe_allow_html=True)

    preset_cards = [
        ("🩸 测量血压", "收缩压/舒张压", "mmHg", "08:00"),
        ("🩸 测量血糖", "空腹/餐后", "mmol/L", "07:30"),
        ("🚶 健走运动", "30", "分钟", "19:00"),
        ("💧 饮水记录", "2000", "ml", "09:00"),
        ("📝 症状记录", "", "", "20:00"),
        ("😴 睡眠记录", "7-8", "小时", "23:00"),
    ]

    for i in range(0, len(preset_cards), 3):
        row = preset_cards[i:i+3]
        preset_cols = st.columns(3)
        for j, (name, tgt, unt, t) in enumerate(row):
            with preset_cols[j]:
                if st.button(name, key=f"preset_{i+j}", use_container_width=True):
                    add_task(name, "daily", tgt, unt, t)
                    st.success(f"✅ 已添加：{name}")
                    st.rerun()

    if st.button("💾 保存自定义任务", use_container_width=True) and task_name:
        add_task(task_name, task_type, target, unit, reminder_time.strftime('%H:%M'))
        st.success(f"✅ 已添加：{task_name}")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # 任务列表
    st.markdown("""
    <div style="
        background: white;
        border: 1px solid #E8D8C0;
        border-radius: 12px;
        padding: 20px;
    ">
        <div style="font-size:13px;font-weight:700;color:#2D1F0A;margin-bottom:16px;">📋 当前任务</div>
    """, unsafe_allow_html=True)

    active_tasks = get_active_tasks()
    if active_tasks.empty:
        st.info("暂无任务")
    else:
        for _, task in active_tasks.iterrows():
            streak = get_streak(task['id'])
            with st.expander(f"🎯 {task['task_name']} {task['target']}{task['unit']} | ⏰ {task['reminder_time']}"):
                col_info, col_del = st.columns([3, 1])
                with col_info:
                    st.markdown(f"""
                    **任务：** {task['task_name']}<br>
                    **类型：** {"每日" if task['task_type'] == 'daily' else task['task_type']}<br>
                    {"**目标：** " + task['target'] + task['unit'] if task['target'] else ""}<br>
                    **提醒时间：** {task['reminder_time']}
                    """)
                    if streak > 0:
                        st.markdown(f"连续坚持：**{streak}** 天 🔥")
                with col_del:
                    if st.button("🗑️ 删除", key=f"del_task_{task['id']}"):
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("UPDATE health_tasks SET is_active=0 WHERE id=?", (task['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ===== 统计总览 =====
with tab3:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #FFF3EE 0%, #FFF8F4 100%);
        border: 1px solid #F0D8C8;
        border-radius: 12px;
        padding: 20px;
    ">
        <div style="font-size:13px;font-weight:700;color:#8B4513;margin-bottom:16px;">📊 健康任务统计总览</div>
    """, unsafe_allow_html=True)

    active_tasks = get_active_tasks()
    if active_tasks.empty:
        st.info("暂无任务数据")
    else:
        days_range = st.slider("统计周期（天）", 7, 90, 30)

        for _, task in active_tasks.iterrows():
            task_id = task['id']
            conn = get_db_connection()
            df = pd.read_sql_query("""
                SELECT planned_date, status FROM task_logs
                WHERE task_id=? AND planned_date >= date('now', ?)
                ORDER BY planned_date
            """, conn, params=(task_id, f'-{days_range} days'))
            conn.close()

            if not df.empty:
                total = len(df)
                done = len(df[df['status'] == 'done'])
                rate = (done / total * 100) if total > 0 else 0

                # 任务统计卡片
                bar_color = "#27ae60" if rate >= 70 else "#f39c12" if rate >= 40 else "#e74c3c"
                st.markdown(f"""
                <div style="
                    background: white;
                    border: 1px solid #E8D8C0;
                    border-radius: 10px;
                    padding: 16px 20px;
                    margin-bottom: 12px;
                ">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                        <div style="font-size:14px;font-weight:700;color:#2D1F0A;">🎯 {task['task_name']}</div>
                        <div style="font-size:13px;font-weight:700;color:{bar_color};">完成率 {rate:.1f}% <span style="font-size:11px;color:#9A8060;">({done}/{total})</span></div>
                    </div>
                    <div style="background:#F5F5F5;border-radius:6px;height:8px;overflow:hidden;">
                        <div style="background:{bar_color};width:{rate}%;height:100%;border-radius:6px;transition:width 0.3s;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                try:
                    import plotly.express as px
                    df_plot = df.copy()
                    df_plot['日期'] = pd.to_datetime(df_plot['planned_date'])
                    df_plot['状态'] = df_plot['status'].map({'done': '已完成', 'pending': '待完成', 'missed': '已错过'})
                    fig = px.bar(
                        df_plot, x='日期', y='planned_date',
                        color='状态',
                        color_discrete_map={'已完成': '#27ae60', '待完成': '#d5e8f7', '已错过': '#e74c3c'},
                        title=f"{task['task_name']} 完成情况",
                        height=200
                    )
                    fig.update_layout(showlegend=False, template='plotly_white',
                                     font=dict(family="Microsoft YaHei"))
                    fig.update_layout(
                        plot_bgcolor='white', paper_bgcolor='transparent',
                        xaxis=dict(showgrid=False, gridcolor='#F0F0F0'),
                        yaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    pass

    st.markdown("</div>", unsafe_allow_html=True)

# 底部导航
st.divider()
col_prev, col_next = st.columns(2)
with col_prev:
    st.page_link("pages/6_用药提醒.py", label="← 用药提醒", icon="💊")
with col_next:
    st.page_link("main.py", label="返回首页 →", icon="🏠")
