# -*- coding: utf-8 -*-
"""
SpiderMind - 慢病履历台账页
"""
import streamlit as st
import sys
import os
from datetime import datetime, date
import sqlite3
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="慢病履历 - SpiderMind",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from components.hospital_theme import inject_theme, render_nav, render_breadcrumb, render_page_header

inject_theme()
render_nav("慢病履历")
render_breadcrumb("慢病履历台账")
render_page_header("📝", "慢病履历台账",
    "本地SQLite数据库存储历次检查记录，可视化趋势图，支持CSV/Excel导出，方便就诊时向医生展示")

st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# ===== 数据库（统一由 db_utils 管理） =====
from db_utils import get_db_path, get_db_connection

def save_indicator_record(indicator_name, value, unit='', reference='', report_source='手动录入', notes=''):
    conn = get_db_connection()
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("INSERT INTO indicator_records (indicator_name,value,unit,reference_range,report_source,record_date,notes) VALUES (?,?,?,?,?,?,?)",
              (indicator_name, value, unit, reference, report_source, today, notes))
    conn.commit()
    conn.close()
    return True

def get_indicator_history(indicator_name=None, days=365):
    conn = get_db_connection()
    query = "SELECT * FROM indicator_records WHERE record_date >= date('now', ?)"
    params = [f'-{days} days']
    if indicator_name:
        query += " AND indicator_name = ?"
        params.append(indicator_name)
    query += " ORDER BY record_date DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_all_indicators():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT DISTINCT indicator_name FROM indicator_records ORDER BY indicator_name", conn)
    conn.close()
    return df['indicator_name'].tolist()

def _parse_ref(ref_str, which):
    if not ref_str:
        return None
    import re
    nums = re.findall(r'[\d.]+', ref_str)
    if len(nums) >= 2:
        return float(nums[1]) if which == 'max' else float(nums[0])
    elif len(nums) == 1:
        return float(nums[0])
    return None


# ===== 页面风格CSS =====
st.markdown("""
<style>
.record-card {
    background: white;
    border-radius: 10px;
    border: 1px solid #E8D8C0;
    box-shadow: 0 2px 6px rgba(139,90,30,0.10);
    padding: 12px 16px;
    margin-bottom: 10px;
}
.record-card strong { color: #2D1F0A; font-size: 13px; }
.record-card small { color: #9A8060; font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# ===== 三大功能卡片（可点击切换）=====
st.markdown('<div class="section-title" style="margin-bottom: 16px;">'
    '<div class="section-title-bar"></div>'
    '<h2>选择功能模块</h2>'
    '</div>', unsafe_allow_html=True)

mode_pages = [
    ("entry", "📝", "手动录入指标", "RECORD ENTRY", "新增慢病指标记录，支持预设模板快速填充"),
    ("trend", "📈", "指标趋势图", "TREND CHART", "追踪历史指标变化，可视化趋势与参考范围对比"),
    ("history", "📁", "历史记录", "HISTORY LOG", "查看完整记录，支持筛选和CSV导出"),
]

current = st.session_state.get("record_mode", "entry")
mode_cols = st.columns(3)
for i, (mode_id, icon, title, sub, desc) in enumerate(mode_pages):
    active = "active" if current == mode_id else ""
    with mode_cols[i]:
        if st.button(f"{icon}\n{title}\n{sub}", key=f"rec_mode_{mode_id}", use_container_width=True):
            st.session_state["record_mode"] = mode_id
            st.rerun()
        st.markdown(f"""
        <div style="margin-top:-6px; padding: 8px 14px; font-size:11px; color:#9A8060; text-align:center; line-height:1.5">{desc}</div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

all_inds = get_all_indicators()

# ====================== 手动录入 ======================
if current == "entry":
    preset_indicators = {
        "空腹血糖 (FPG)": {"unit": "mmol/L", "ref": "3.9~6.1"},
        "餐后2h血糖 (2hPBG)": {"unit": "mmol/L", "ref": "<7.8"},
        "糖化血红蛋白 (HbA1c)": {"unit": "%", "ref": "4.0~6.0"},
        "收缩压 (SBP)": {"unit": "mmHg", "ref": "<140"},
        "舒张压 (DBP)": {"unit": "mmHg", "ref": "<90"},
        "总胆固醇 (TC)": {"unit": "mmol/L", "ref": "<5.2"},
        "甘油三酯 (TG)": {"unit": "mmol/L", "ref": "<1.7"},
        "低密度脂蛋白 (LDL-C)": {"unit": "mmol/L", "ref": "<3.4"},
        "高密度脂蛋白 (HDL-C)": {"unit": "mmol/L", "ref": ">1.0"},
        "血肌酐 (SCr)": {"unit": "μmol/L", "ref": "44~133"},
        "血尿酸 (UA)": {"unit": "μmol/L", "ref": "150~440"},
        "谷丙转氨酶 (ALT)": {"unit": "U/L", "ref": "9~50"},
        "谷草转氨酶 (AST)": {"unit": "U/L", "ref": "15~40"},
        "白细胞 (WBC)": {"unit": "×10⁹/L", "ref": "3.5~9.5"},
        "血红蛋白 (Hb)": {"unit": "g/L", "ref": "115~175"},
        "血小板 (PLT)": {"unit": "×10⁹/L", "ref": "125~350"},
    }

    col_main, col_side = st.columns([3, 1])

    with col_main:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #2D1500, #4A2800);
            border-radius: 10px; padding: 16px 20px; margin-bottom: 16px;">
            <div style="font-size: 14px; font-weight: 700; color: white; margin-bottom: 4px; font-family: 'Noto Serif SC', serif;">新增指标记录</div>
            <div style="font-size: 11px; color: rgba(255,255,255,0.5);">选择预设指标可自动填充参考范围</div>
        </div>
        """, unsafe_allow_html=True)

        selected_preset = st.selectbox("选择指标（可快速填充参考范围）",
            ["— 自定义 —"] + list(preset_indicators.keys()), key="preset_select")

        row1 = st.columns([2, 1, 1])
        with row1[0]:
            indicator_name = st.text_input("指标名称",
                value=selected_preset if selected_preset != "— 自定义 —" else "",
                placeholder="例如：空腹血糖")
        with row1[1]:
            value = st.text_input("检测值", placeholder="例如：5.6")
        with row1[2]:
            unit = st.text_input("单位",
                value=preset_indicators.get(selected_preset, {}).get("unit", ""),
                placeholder="mmol/L")

        row2 = st.columns([2, 2])
        with row2[0]:
            reference = st.text_input("参考范围（自动填充，可修改）",
                value=preset_indicators.get(selected_preset, {}).get("ref", ""),
                placeholder="3.9~6.1")
        with row2[1]:
            report_source = st.selectbox("数据来源",
                ["手动录入", "AI报告解读", "临床指南", "爬取数据"], key="source_select")

        notes = st.text_area("备注（可选）",
            placeholder="如：空腹采血、近期用药情况等...", height=80, key="notes_input")

        if st.button("💾 保存记录", use_container_width=True, type="primary", key="btn_save_record"):
            if indicator_name and value:
                save_indicator_record(indicator_name, value, unit, reference, report_source, notes)
                st.success(f"✅ 已保存：{indicator_name} = {value} {unit}")
                st.rerun()
            else:
                st.error("请填写指标名称和检测值")

    with col_side:
        st.markdown("""
        <div style="background: white; border: 1px solid #E8D8C0; border-radius: 10px;
            padding: 16px; box-shadow: 0 2px 6px rgba(139,90,30,0.10);">
          <div style="font-weight: 700; color: #C85A1E; font-size: 13px; margin-bottom: 10px; font-family: 'Noto Serif SC', serif;">📊 常用指标参考值</div>
          <div style="font-size: 11px; color: #5C4A2A; line-height: 1.9;">
            <div style="display:flex; justify-content:space-between; border-bottom: 1px dashed #E8D8C0; padding-bottom: 4px; margin-bottom: 4px;">
                <span>空腹血糖</span><span style="color:#C85A1E; font-weight:600;">3.9~6.1 mmol/L</span>
            </div>
            <div style="display:flex; justify-content:space-between; border-bottom: 1px dashed #E8D8C0; padding-bottom: 4px; margin-bottom: 4px;">
                <span>糖化血红蛋白</span><span style="color:#C85A1E; font-weight:600;">4.0~6.0 %</span>
            </div>
            <div style="display:flex; justify-content:space-between; border-bottom: 1px dashed #E8D8C0; padding-bottom: 4px; margin-bottom: 4px;">
                <span>收缩压</span><span style="color:#C85A1E; font-weight:600;">&lt;140 mmHg</span>
            </div>
            <div style="display:flex; justify-content:space-between; border-bottom: 1px dashed #E8D8C0; padding-bottom: 4px; margin-bottom: 4px;">
                <span>舒张压</span><span style="color:#C85A1E; font-weight:600;">&lt;90 mmHg</span>
            </div>
            <div style="display:flex; justify-content:space-between; border-bottom: 1px dashed #E8D8C0; padding-bottom: 4px; margin-bottom: 4px;">
                <span>总胆固醇</span><span style="color:#C85A1E; font-weight:600;">&lt;5.2 mmol/L</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>甘油三酯</span><span style="color:#C85A1E; font-weight:600;">&lt;1.7 mmol/L</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # 最近录入
    st.markdown("""
    <div style="margin-top: 24px;">
        <div style="font-weight: 700; color: #2D1F0A; font-size: 15px; margin-bottom: 12px;
            font-family: 'Noto Serif SC', serif; border-left: 3px solid #C85A1E; padding-left: 12px;">🕐 最近录入</div>
    </div>
    """, unsafe_allow_html=True)

    recent = get_indicator_history(days=7)
    if not recent.empty:
        rc = st.columns(min(len(recent.head(5)), 5))
        for i, (_, row) in enumerate(recent.head(5).iterrows()):
            with rc[i]:
                st.markdown(f"""
                <div class="record-card" style="text-align:center;">
                    <div style="font-size: 11px; color: #9A8060; margin-bottom: 4px;">{row['record_date']}</div>
                    <div style="font-size: 13px; font-weight: 700; color: #2D1F0A; margin-bottom: 2px;">{row['indicator_name']}</div>
                    <div style="font-size: 18px; font-weight: 700; color: #C85A1E;">{row['value']}</div>
                    <div style="font-size: 11px; color: #9A8060;">{row['unit']}</div>
                    <div style="font-size: 10px; color: #9A8060; margin-top: 4px;">{row['report_source']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("暂无记录，请先录入指标数据")

# ====================== 趋势图 ======================
elif current == "trend":
    if not all_inds:
        st.info("📋 暂无数据，请先在「手动录入」中添加指标记录")
    else:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #2D1500, #4A2800);
            border-radius: 10px; padding: 16px 20px; margin-bottom: 16px;">
            <div style="font-size: 14px; font-weight: 700; color: white; margin-bottom: 4px; font-family: 'Noto Serif SC', serif;">📈 指标趋势追踪</div>
            <div style="font-size: 11px; color: rgba(255,255,255,0.5);">选择指标，查看历史变化趋势与参考范围对比</div>
        </div>
        """, unsafe_allow_html=True)

        selected = st.multiselect("选择要查看趋势的指标（可多选）",
            all_inds, default=all_inds[:3], key="trend_select")

        if selected:
            days_range = st.slider("时间范围（天）", 30, 730, 180, key="days_slider")

            trend_data = []
            for ind in selected:
                df = get_indicator_history(ind, days_range)
                if not df.empty:
                    for _, row in df.iterrows():
                        try:
                            val = float(row['value'])
                        except:
                            continue
                        trend_data.append({
                            '指标': ind,
                            '日期': row['record_date'],
                            '检测值': val,
                            '参考上限': _parse_ref(row['reference_range'], 'max'),
                            '参考下限': _parse_ref(row['reference_range'], 'min'),
                            '来源': row['report_source']
                        })

            if trend_data:
                trend_df = pd.DataFrame(trend_data)
                trend_df['日期'] = pd.to_datetime(trend_df['日期'])
                trend_df = trend_df.sort_values('日期')

                import plotly.express as px
                import plotly.graph_objects as go

                total_points = len(trend_df)
                num_indicators = len(selected)

                # 智能选择图表类型
                if total_points <= 2:
                    # 数据点极少 → 柱状图（折线无法呈现趋势）
                    chart_type = "bar"
                    chart_title = "📊 指标对比（柱状图）"
                elif total_points <= 15 and num_indicators == 1:
                    # 数据点较少 + 单指标 → 柱状图（看各次测量更直观）
                    chart_type = "bar"
                    chart_title = "📊 指标趋势（柱状图）"
                elif num_indicators == 1:
                    # 多数据点 + 单指标 → 折线图（趋势一目了然）
                    chart_type = "line"
                    chart_title = "📈 指标趋势（折线图）"
                else:
                    # 多指标 → 折线图（柱状图多指标会太乱）
                    chart_type = "line"
                    chart_title = "📈 多指标趋势（折线图）"

                # 根据类型生成图表
                if chart_type == "bar":
                    trend_df['日期_str'] = trend_df['日期'].dt.strftime('%m-%d')
                    fig = px.bar(
                        trend_df, x='日期_str', y='检测值', color='指标',
                        title=chart_title, text='检测值',
                        color_discrete_sequence=['#E8722A', '#1A8A5A', '#1A5296', '#7A1A96', '#1A8A38']
                    )
                    fig.update_traces(textposition='outside', textfont_size=10)
                else:
                    fig = px.line(
                        trend_df, x='日期', y='检测值', color='指标',
                        markers=True, title=chart_title,
                        color_discrete_sequence=['#E8722A', '#1A8A5A', '#1A5296', '#7A1A96', '#1A8A38']
                    )

                # 添加参考范围区间
                for ind in selected:
                    ind_data = trend_df[trend_df['指标'] == ind]
                    if not ind_data.empty:
                        upper = ind_data['参考上限'].dropna().iloc[0] if ind_data['参考上限'].dropna().any() else None
                        lower = ind_data['参考下限'].dropna().iloc[0] if ind_data['参考下限'].dropna().any() else None
                        if upper:
                            fig.add_hrect(y0=lower or (upper * 0.7), y1=upper,
                                line_width=0, fillcolor="green", opacity=0.08,
                                annotation_text=f"{ind}参考范围", row="all", col=1)

                fig.update_layout(
                    font=dict(family="Microsoft YaHei"), height=400,
                    paper_bgcolor='white', plot_bgcolor='white',
                    showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)

                # 统计卡片
                max_cols = 4
                sc = st.columns(min(len(selected), max_cols))
                for i, ind in enumerate(selected):
                    ind_stats = trend_df[trend_df['指标'] == ind]['检测值']
                    with sc[i % max_cols]:
                        delta_str = ""
                        if len(ind_stats) > 1:
                            change = ind_stats.iloc[-1] - ind_stats.iloc[0]
                            delta_str = f"{'↑' if change > 0 else '↓'} {abs(change):.2f}"
                        st.metric(
                            label=ind,
                            value=f"{ind_stats.mean():.2f}" if len(ind_stats) > 0 else "—",
                            delta=delta_str if delta_str else None
                        )

                # 数据表格
                st.markdown("""
                <div style="font-weight: 700; color: #2D1F0A; font-size: 15px; margin-top: 20px;
                    margin-bottom: 12px; font-family: 'Noto Serif SC', serif;
                    border-left: 3px solid #C85A1E; padding-left: 12px;">📊 数据明细</div>
                """, unsafe_allow_html=True)
                display = trend_df[['日期', '指标', '检测值', '来源']].copy()
                display['日期'] = display['日期'].dt.strftime('%Y-%m-%d')
                st.dataframe(display, use_container_width=True, hide_index=True)
            else:
                st.warning("所选指标暂无有效数值数据")

# ====================== 历史记录 ======================
elif current == "history":
    st.markdown("""
    <div style="background: linear-gradient(90deg, #2D1500, #4A2800);
        border-radius: 10px; padding: 16px 20px; margin-bottom: 16px;">
        <div style="font-size: 14px; font-weight: 700; color: white; margin-bottom: 4px; font-family: 'Noto Serif SC', serif;">📁 完整历史记录</div>
        <div style="font-size: 11px; color: rgba(255,255,255,0.5);">支持按指标和来源筛选，支持CSV导出</div>
    </div>
    """, unsafe_allow_html=True)

    filter_indicator = st.selectbox("筛选指标", ["全部"] + all_inds, key="filter_indicator")
    filter_source = st.selectbox("筛选来源", ["全部", "手动录入", "AI报告解读", "临床指南"], key="filter_source")

    query = "SELECT * FROM indicator_records WHERE 1=1"
    params = []
    if filter_indicator != "全部":
        query += " AND indicator_name = ?"
        params.append(filter_indicator)
    if filter_source != "全部":
        query += " AND report_source = ?"
        params.append(filter_source)
    query += " ORDER BY record_date DESC, created_at DESC"

    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if not df.empty:
        display_df = df[['record_date', 'indicator_name', 'value', 'unit', 'reference_range', 'report_source']].copy()
        display_df.columns = ['日期', '指标', '检测值', '单位', '参考范围', '来源']

        # 统计摘要
        stat_cols = st.columns(3)
        with stat_cols[0]:
            st.metric("记录总数", f"{len(df)} 条")
        with stat_cols[1]:
            st.metric("涉及指标", f"{df['indicator_name'].nunique()} 个")
        with stat_cols[2]:
            st.metric("最早记录", df['record_date'].min() if not df.empty else "—")

        st.markdown("""
        <div style="font-weight: 700; color: #2D1F0A; font-size: 15px; margin-top: 16px;
            margin-bottom: 12px; font-family: 'Noto Serif SC', serif;
            border-left: 3px solid #C85A1E; padding-left: 12px;">📋 记录列表</div>
        """, unsafe_allow_html=True)
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

        csv = display_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 导出CSV", csv, "慢病履历记录.csv", "text/csv",
                           use_container_width=True)
    else:
        st.info("暂无记录")

# ===== 底部导航 =====
st.markdown("""
<div class="sub-footer">
    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
        <span style="color: #C85A1E; font-size: 13px; cursor: pointer;"
              onclick="window.location.href='pages/3_分析结果.py'">← 返回AI分析</span>
        <span style="color: #C85A1E; font-size: 13px; cursor: pointer;"
              onclick="window.location.href='pages/6_用药提醒.py'">用药提醒 →</span>
    </div>
    SpiderMind · 基层慢病轻量化智能管理平台 · 仅供辅助参考，不替代专业医疗建议
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
