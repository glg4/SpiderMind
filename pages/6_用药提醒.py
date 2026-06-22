"""
SpiderMind - 用药提醒页（医院官网风格 + 本地任务打卡）
"""
import streamlit as st
import sys
import os
from datetime import datetime, date, time
import sqlite3
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="用药提醒 - SpiderMind",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

try:
    from components.hospital_theme import inject_theme, render_nav, render_breadcrumb, render_page_header
    inject_theme()
    render_nav("6_用药提醒")
    render_breadcrumb("用药提醒打卡")
    render_page_header("💊", "用药提醒 & 打卡管理",
                       "设置每日服药计划，打卡记录用药依从性，自动统计连续打卡天数，培养规律用药习惯")
except Exception:
    pass

st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# ===== 数据库（统一由 db_utils 管理） =====
from db_utils import get_db_path, get_db_connection


def add_drug(name, dosage, frequency, reminder_time, start_date, end_date=None, notes=''):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO drug_records (drug_name, dosage, frequency, reminder_time, start_date, end_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, dosage, frequency, reminder_time, start_date, end_date, notes))
    conn.commit()
    drug_id = c.lastrowid
    conn.close()
    return drug_id


def get_active_drugs():
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM drug_records WHERE is_active=1 ORDER BY reminder_time",
        conn
    )
    conn.close()
    return df


def log_medication(drug_id, status, notes=''):
    conn = get_db_connection()
    c = conn.cursor()
    planned = c.execute(
        "SELECT reminder_time FROM drug_records WHERE id=?", (drug_id,)
    ).fetchone()
    c.execute("""
        INSERT INTO medication_logs (drug_record_id, planned_time, actual_time, status, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (drug_id, planned[0] if planned else '', datetime.now().strftime('%H:%M:%S'), status, notes))
    conn.commit()
    conn.close()


def get_today_logs():
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT ml.*, dr.drug_name, dr.dosage, dr.frequency, dr.reminder_time
        FROM medication_logs ml
        JOIN drug_records dr ON ml.drug_record_id = dr.id
        WHERE date(ml.actual_time) = date('now')
        ORDER BY ml.actual_time DESC
    """, conn)
    conn.close()
    return df


def get_drug_stats(drug_id, days=30):
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT date(actual_time) as day, status, COUNT(*) as count
        FROM medication_logs
        WHERE drug_record_id=? AND actual_time >= date('now', ?)
        GROUP BY day, status
        ORDER BY day
    """, conn, params=(drug_id, f'-{days} days'))
    conn.close()
    return df

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

# 三大功能入口
func_tabs = ["💊 用药打卡", "⚙️ 计划管理", "📊 服药统计"]
tab_labels = ["打卡", "管理", "统计"]

col_func1, col_func2, col_func3 = st.columns(3)
func_items = [
    (col_func1, "💊", "用药打卡", "Medication Check-in",
     "记录每日服药情况<br>追踪用药依从性", "#FFF3EE"),
    (col_func2, "⚙️", "计划管理", "Plan Management",
     "添加/编辑用药计划<br>设置提醒时间", "#F0FFF4"),
    (col_func3, "📊", "服药统计", "Statistics",
     "查看依从率趋势<br>分析打卡记录", "#F0F4FF"),
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
tab1, tab2, tab3 = st.tabs(["💊 用药打卡", "⚙️ 用药计划管理", "📊 服药统计"])

# ===== 用药打卡 =====
with tab1:
    today_str = date.today().strftime('%Y年%m月%d日')
    st.markdown(f"📅 **{today_str}**")

    active_drugs = get_active_drugs()

    if active_drugs.empty:
        st.info("📝 暂无用药计划，请在「用药计划管理」中添加")
    else:
        # 按时段分组
        morning = active_drugs[active_drugs['reminder_time'] <= '12:00']
        afternoon = active_drugs[(active_drugs['reminder_time'] > '12:00') & (active_drugs['reminder_time'] <= '18:00')]
        evening = active_drugs[active_drugs['reminder_time'] > '18:00']

        for label, group in [("🌅 早间用药", morning), ("☀️ 午间用药", afternoon), ("🌙 晚间用药", evening)]:
            if not group.empty:
                # 时段标题卡片
                st.markdown(f"""
                <div style="
                    background: linear-gradient(90deg, #FFF8F4 0%, #FFF3EE 100%);
                    border-left: 3px solid #C85A1E;
                    border-radius: 8px;
                    padding: 10px 16px;
                    margin: 16px 0 8px 0;
                    font-size: 13px;
                    font-weight: 700;
                    color: #8B4513;
                    letter-spacing: 0.5px;
                ">{label}</div>
                """, unsafe_allow_html=True)

                for _, drug in group.iterrows():
                    drug_id = drug['id']
                    drug_name = drug['drug_name']
                    dosage = drug['dosage']
                    freq = drug['frequency']

                    today_logs = get_today_logs()
                    drug_today = today_logs[today_logs['drug_record_id'] == drug_id]
                    done = not drug_today.empty

                    # 药品卡片
                    status_color = "#27ae60" if done else "#f39c12"
                    status_bg = "#F0FFF8" if done else "#FFFEF5"
                    status_icon = "✅" if done else "⏳"
                    status_label = f"已打卡：{drug_today.iloc[0]['actual_time'][:8]}" if done else f"计划时间：{drug['reminder_time']}"

                    st.markdown(f"""
                    <div style="
                        background: {status_bg};
                        border: 1px solid #E8D8C0;
                        border-left: 4px solid {status_color};
                        border-radius: 10px;
                        padding: 16px 20px;
                        margin-bottom: 8px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    ">
                        <div>
                            <div style="font-size:15px;font-weight:700;color:#2D1F0A;">{status_icon} {drug_name} <span style="font-size:12px;color:#7A6A50;">{dosage}</span></div>
                            <div style="font-size:11px;color:#9A8060;margin-top:4px;">{freq} | {status_label}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    col_card, col_action = st.columns([4, 1])
                    with col_action:
                        if not done:
                            if st.button("✅ 已服药", key=f"btn_{drug_id}", use_container_width=True):
                                log_medication(drug_id, 'taken')
                                st.rerun()
                        else:
                            st.markdown("<div style='color:#27ae60;font-size:13px;padding-top:8px;text-align:center;'>已完成 ✓</div>", unsafe_allow_html=True)

        # 今日打卡总览
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #F0FFF8 0%, #E8F5EC 100%);
            border: 1px solid #C8E6C9;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
        ">
            <div style="font-size:13px;font-weight:700;color:#2D7A4F;margin-bottom:12px;">📋 今日打卡总览</div>
        """, unsafe_allow_html=True)

        today_logs = get_today_logs()
        if not today_logs.empty:
            taken = today_logs[today_logs['status'] == 'taken']
            total = len(active_drugs)
            done_count = len(taken)
            remaining = total - done_count

            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("已打卡", f"{done_count}/{total}")
            with col_stat2:
                st.metric("待打卡", f"{remaining}项")
            with col_stat3:
                rate = (done_count / total * 100) if total > 0 else 0
                st.metric("完成率", f"{rate:.0f}%",
                         delta="全部完成 ✓" if remaining == 0 else f"还剩{remaining}项")

        st.markdown("</div>", unsafe_allow_html=True)

# ===== 用药计划管理 =====
with tab2:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #F0FFF4 0%, #E8F5EC 100%);
        border: 1px solid #C8E6C9;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    ">
        <div style="font-size:13px;font-weight:700;color:#2D7A4F;margin-bottom:12px;">➕ 新增用药计划</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        drug_name = st.text_input("药物名称", placeholder="例如：二甲双胍")
    with col2:
        dosage = st.text_input("剂量", placeholder="例如：500mg / 1片")

    frequency = st.selectbox(
        "用药频率",
        ["每日1次", "每日2次", "每日3次", "每周1次", "每周2次", "每周3次", "隔日1次", "必要时"]
    )

    reminder_time = st.time_input("提醒时间", value=time(8, 0))

    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("开始日期", value=date.today())
    with col_date2:
        has_end = st.checkbox("设置结束日期")
        end_date = st.date_input("结束日期（可选）", value=date.today()) if has_end else None

    notes = st.text_area("备注（可选）", placeholder="如：餐后服用、避免与XX同服等...")

    if st.button("💾 保存用药计划", use_container_width=True):
        if drug_name:
            add_drug(
                drug_name, dosage, frequency,
                reminder_time.strftime('%H:%M'),
                start_date.isoformat(),
                end_date.isoformat() if end_date else None,
                notes
            )
            st.success(f"✅ 已添加：{drug_name} {dosage} | 提醒时间：{reminder_time.strftime('%H:%M')}")
            st.rerun()
        else:
            st.error("请填写药物名称")

    st.markdown("</div>", unsafe_allow_html=True)

    # 当前计划列表
    st.markdown("""
    <div style="
        background: white;
        border: 1px solid #E8D8C0;
        border-radius: 12px;
        padding: 20px;
    ">
        <div style="font-size:13px;font-weight:700;color:#2D1F0A;margin-bottom:16px;">📋 当前用药计划</div>
    """, unsafe_allow_html=True)

    active_drugs = get_active_drugs()

    if active_drugs.empty:
        st.info("暂无用药计划")
    else:
        for _, drug in active_drugs.iterrows():
            with st.expander(f"💊 {drug['drug_name']} {drug['dosage']} | {drug['frequency']} | ⏰ {drug['reminder_time']}"):
                col_info, col_del = st.columns([3, 1])
                with col_info:
                    st.markdown(f"""
                    **药物：** {drug['drug_name']}<br>
                    **剂量：** {drug['dosage']}<br>
                    **频率：** {drug['frequency']}<br>
                    **提醒时间：** {drug['reminder_time']}<br>
                    **开始日期：** {drug['start_date']}<br>
                    {"**结束日期：** " + str(drug['end_date']) if drug['end_date'] else ""}<br>
                    {"**备注：** " + drug['notes'] if drug['notes'] else ""}
                    """)
                with col_del:
                    if st.button("🗑️ 删除", key=f"del_{drug['id']}"):
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("UPDATE drug_records SET is_active=0 WHERE id=?", (drug['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ===== 服药统计 =====
with tab3:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #F0F4FF 0%, #E8ECF5 100%);
        border: 1px solid #C5D4F0;
        border-radius: 12px;
        padding: 20px;
    ">
        <div style="font-size:13px;font-weight:700;color:#1A3A8F;margin-bottom:16px;">📊 服药依从性统计</div>
    """, unsafe_allow_html=True)

    active_drugs = get_active_drugs()
    if active_drugs.empty:
        st.info("暂无用药计划")
    else:
        selected_drug = st.selectbox("选择药物查看依从性", active_drugs['drug_name'].tolist())
        drug_row = active_drugs[active_drugs['drug_name'] == selected_drug].iloc[0]
        drug_id = drug_row['id']

        days_range = st.slider("统计周期（天）", 7, 90, 30)

        stats = get_drug_stats(drug_id, days_range)
        if not stats.empty:
            import plotly.express as px
            fig = px.bar(
                stats, x='day', y='count', color='status',
                color_discrete_map={'taken': '#27ae60', 'missed': '#e74c3c', 'pending': '#f39c12'},
                title=f"{selected_drug} 服药依从性（近{days_range}天）"
            )
            fig.update_layout(template='plotly_white', font=dict(family="Microsoft YaHei"), height=350)
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='transparent',
                xaxis=dict(showgrid=False, gridcolor='#F0F0F0'),
                yaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
            )
            st.plotly_chart(fig, use_container_width=True)

            taken = stats[stats['status'] == 'taken']['count'].sum()
            total = stats['count'].sum()
            compliance = (taken / total * 100) if total > 0 else 0

            col_c, col_t = st.columns(2)
            with col_c:
                st.metric("依从率", f"{compliance:.1f}%")
            with col_t:
                st.metric("统计周期", f"{total}次服药 | {taken}次完成")
        else:
            st.info(f"暂无{selected_drug}的服药记录（近{days_range}天）")

    st.markdown("</div>", unsafe_allow_html=True)

# 底部导航
st.divider()
col_prev, col_next = st.columns(2)
with col_prev:
    st.page_link("pages/5_慢病履历.py", label="← 慢病履历", icon="📋")
with col_next:
    st.page_link("pages/2_网页爬虫.py", label="临床指南爬取 →", icon="🧬")
