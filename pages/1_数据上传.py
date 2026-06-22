# -*- coding: utf-8 -*-
"""
SpiderMind - 数据上传页
报告上传 / 临床指南 / AI解读 / 慢病履历 / 用药提醒 / 健康任务
"""
import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from coze_api import CozeAPI

st.set_page_config(
    page_title="报告上传 - SpiderMind",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== 注入主题 + 渲染导航 =====
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.hospital_theme import inject_theme, render_nav, render_breadcrumb, render_page_header

inject_theme()
render_nav("1_数据上传")
render_breadcrumb("报告上传")
render_page_header("📋", "检查报告上传",
    "支持电子报告导入（Excel/CSV）及手动指标录入，全程本地处理")

st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# ===== 设计原则提示 =====
st.markdown("""
<div class="principle-box">
    <strong>数据安全说明：</strong>所有报告数据仅在本地处理，不上传任何云端服务器。
    AI 仅客观呈现检查数据与参考范围，不出现"不严重""还好"等侥幸性判断语言。
</div>
""", unsafe_allow_html=True)

# ===== 四种录入方式（卡片风格）=====
st.markdown("""
<style>
/* 录入方式卡片 */
.upload-card {
    background: white;
    border-radius: 12px;
    border: 1px solid #E8D8C0;
    box-shadow: 0 2px 8px rgba(139,90,30,0.10);
    overflow: hidden;
    margin-bottom: 0;
    transition: all 0.25s;
}
.upload-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(139,90,30,0.14);
    border-color: #E8722A;
}
.upload-card-header {
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid #E8D8C0;
}
.upload-card-icon {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
}
.uci-orange  { background: #FEE8D6; }
.uci-teal    { background: #D6EEE8; }
.uci-blue    { background: #D6E4F7; }
.uci-green   { background: #D6F0D6; }
.upload-card-title {
    font-size: 15px;
    font-weight: 700;
    color: #2D1F0A;
    margin: 0 0 2px 0;
    font-family: 'Noto Serif SC', serif;
}
.upload-card-sub {
    font-size: 11px;
    color: #9A8060;
    margin: 0;
}
.upload-card-body {
    padding: 16px 20px;
}
.upload-card-desc {
    font-size: 12px;
    color: #5C4A2A;
    line-height: 1.7;
    margin: 0 0 14px 0;
}
.upload-card-tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 14px;
}
.upload-tag {
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 10px;
    background: #FDF6EC;
    color: #5C4A2A;
    border: 1px solid #E8D8C0;
}
.upload-card-divider {
    border-top: 1px dashed #E8D8C0;
    margin: 14px 0;
}
</style>
""", unsafe_allow_html=True)

# 初始化 - 去掉缓存确保每次使用最新配置
coze = CozeAPI()

# 三个录入入口
# ---------- 三个录入入口 ----------
col1, col2, col3 = st.columns(3)

# ---------- 卡片1：Excel上传 ----------
with col1:
    st.markdown("""
    <div class="upload-card">
      <div class="upload-card-header">
        <div class="upload-card-icon uci-blue">📊</div>
        <div>
          <div class="upload-card-title">Excel/CSV 文件导入</div>
          <div class="upload-card-sub">EXCEL IMPORT · CSV</div>
        </div>
      </div>
      <div class="upload-card-body">
        <div class="upload-card-desc">
          直接导入电子体检报告文件（Excel/CSV），系统自动识别指标列和数值列，
          预览数据后批量导入慢病履历。
        </div>
        <div class="upload-card-tags">
          <span class="upload-tag">Excel导入</span>
          <span class="upload-tag">CSV导入</span>
          <span class="upload-tag">字段映射</span>
          <span class="upload-tag">批量导入</span>
        </div>
        <div class="upload-card-divider"></div>
    """, unsafe_allow_html=True)

    excel_file = st.file_uploader(
        "上传Excel/CSV文件",
        type=['xlsx', 'xls', 'csv'],
        key="upload_excel",
        help="支持 .xlsx / .xls / .csv 格式"
    )

    if excel_file:
        import pandas as pd
        try:
            if excel_file.name.endswith('.csv'):
                df = pd.read_csv(excel_file)
            else:
                # 尝试跳过第一行标题行，从第二行读取表头
                df = pd.read_excel(excel_file, header=1)
            st.success(f"✅ 成功读取，共 {len(df)} 行 {len(df.columns)} 列")

            st.markdown("**📊 数据预览（前8行）**")
            st.dataframe(df.head(8), use_container_width=True, hide_index=True)

            name_col = st.selectbox("选择指标名称列", df.columns.tolist(), key="excel_name_col")
            val_col  = st.selectbox("选择检测值列", df.columns.tolist(), key="excel_val_col")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("📥 导入到慢病履历", use_container_width=True, key="excel_save"):
                    try:
                        from datetime import date as _date
                        from db_utils import get_db_connection
                        conn = get_db_connection()
                        c = conn.cursor()
                        today = _date.today().isoformat()
                        saved = 0
                        for _, row in df.iterrows():
                            try:
                                c.execute("INSERT INTO indicator_records (indicator_name,value,report_source,record_date) VALUES (?,?,?,?)",
                                          (str(row[name_col]), str(row[val_col]), 'Excel导入', today))
                                saved += 1
                            except Exception:
                                pass
                        conn.commit()
                        conn.close()
                        st.success(f"✅ 成功导入 {saved} 条记录")
                    except Exception as e:
                        st.error(f"导入失败：{str(e)}")
            with c2:
                if st.button("🚀 送往AI分析", use_container_width=True, key="excel_to_ai"):
                    # 把Excel数据转换为文本格式传给分析页面
                    mapping = {'name': name_col, 'value': val_col}
                    name_field = mapping['name']
                    val_field = mapping['value']
                    # 也支持单位列和参考范围列（如果有的话）
                    unit_field = '单位' if '单位' in df.columns else None
                    ref_field = '参考范围' if '参考范围' in df.columns else None
                    date_field = '检测日期' if '检测日期' in df.columns else '日期' if '日期' in df.columns else None

                    lines = []
                    for _, row in df.iterrows():
                        import pandas as pd
                        name_val = str(row[name_field])
                        num_val = str(row[val_field])
                        unit_val = ""
                        if unit_field and unit_field in df.columns:
                            v = row[unit_field]
                            if pd.notna(v) and str(v).strip():
                                unit_val = f" {v}"
                        ref_val = ""
                        if ref_field and ref_field in df.columns:
                            v = row[ref_field]
                            if pd.notna(v) and str(v).strip():
                                ref_val = f"（参考值：{v}）"
                        date_val = ""
                        if date_field and date_field in df.columns:
                            v = row[date_field]
                            if pd.notna(v) and str(v).strip():
                                date_val = f" 日期：{v}"
                        lines.append(f"{name_val}  {num_val}{unit_val}{ref_val}{date_val}")

                    analysis_text = "\n".join(lines)
                    st.session_state['analysis_content'] = analysis_text
                    st.session_state['analysis_source'] = 'excel'
                    st.switch_page("pages/3_分析结果.py")
        except Exception as e:
            st.error(f"读取文件失败：{str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- 卡片2：手动录入 ----------
with col2:
    st.markdown("""
    <div class="upload-card">
      <div class="upload-card-header">
        <div class="upload-card-icon uci-teal">📝</div>
        <div>
          <div class="upload-card-title">手动录入报告内容</div>
          <div class="upload-card-sub">MANUAL ENTRY · TEXT</div>
        </div>
      </div>
      <div class="upload-card-body">
        <div class="upload-card-desc">
          直接粘贴报告单文字内容，或手动输入关键指标数据。
          适合无法获取电子文件时的快速录入。
        </div>
        <div class="upload-card-tags">
          <span class="upload-tag">粘贴文字</span>
          <span class="upload-tag">手动输入</span>
          <span class="upload-tag">快速录入</span>
        </div>
        <div class="upload-card-divider"></div>
    """, unsafe_allow_html=True)

    manual_input = st.text_area(
        "粘贴或输入报告内容",
        placeholder="请粘贴报告单文字内容，例如：\n空腹血糖：6.5 mmol/L（参考值：3.9-6.1）\n糖化血红蛋白：6.8%（参考值：4.0-6.0）",
        height=180,
        key="manual_input_area"
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 提交AI解读", use_container_width=True, key="manual_ai"):
            if manual_input:
                st.session_state['manual_input'] = manual_input
                st.session_state['analysis_content'] = manual_input
                st.switch_page("pages/3_分析结果.py")
            else:
                st.warning("请先输入报告内容")
    with c2:
        if st.button("📥 保存到慢病履历", use_container_width=True, key="manual_save"):
            if manual_input:
                try:
                    from datetime import date as _date
                    from db_utils import get_db_connection
                    conn = get_db_connection()
                    c = conn.cursor()
                    today = _date.today().isoformat()
                    # 简单解析手动输入内容
                    import re
                    for line in manual_input.strip().split('\n'):
                        m = re.match(r'(.+?)[:：]\s*(.+)', line)
                        if m:
                            c.execute("INSERT INTO indicator_records (indicator_name,value,report_source,record_date,notes) VALUES (?,?,?,?,?)",
                                      (m.group(1).strip(), m.group(2).strip(), '手动录入', today, line))
                    conn.commit()
                    conn.close()
                    st.success("✅ 已保存到慢病履历台账")
                except Exception as e:
                    st.error(f"保存失败：{str(e)}")
            else:
                st.warning("请先输入报告内容")

    st.markdown("</div></div>")

# ---------- 卡片3：批量指标录入 ----------
with col3:
    st.markdown("""
    <div class="upload-card">
      <div class="upload-card-header">
        <div class="upload-card-icon uci-green">⚡</div>
        <div>
          <div class="upload-card-title">批量指标快速录入</div>
          <div class="upload-card-sub">BATCH ENTRY · QUICK LOG</div>
        </div>
      </div>
      <div class="upload-card-body">
        <div class="upload-card-desc">
          定期检测后快速录入多个常见慢病指标（血糖、血压、血脂等），
          打卡式操作，适合日常记录。
        </div>
        <div class="upload-card-tags">
          <span class="upload-tag">快速打卡</span>
          <span class="upload-tag">血糖</span>
          <span class="upload-tag">血压</span>
          <span class="upload-tag">血脂</span>
        </div>
        <div class="upload-card-divider"></div>
    """, unsafe_allow_html=True)

    template = [
        ("空腹血糖", "mmol/L", "3.9~6.1"),
        ("餐后2h血糖", "mmol/L", "<7.8"),
        ("糖化血红蛋白", "%", "4.0~6.0"),
        ("收缩压", "mmHg", "<140"),
        ("舒张压", "mmHg", "<90"),
        ("总胆固醇", "mmol/L", "<5.2"),
        ("甘油三酯", "mmol/L", "<1.7"),
    ]

    batch_vals = {}
    batch_cols = st.columns(2)
    for i, (name, unit, ref) in enumerate(template):
        with batch_cols[i % 2]:
            val = st.text_input(
                f"{name}",
                placeholder=f"参考：{ref} {unit}",
                key=f"batch_{name.replace(' ', '_')}"
            )
            if val:
                batch_vals[name] = {"value": val, "unit": unit, "ref": ref}

    if batch_vals:
        st.markdown(f"**已填写 {len(batch_vals)} 项指标**")
        for name, data in batch_vals.items():
            st.markdown(f"- **{name}**：{data['value']} {data['unit']}（参考：{data['ref']}）")

        if st.button("💾 批量保存到慢病履历", use_container_width=True, key="batch_save"):
            try:
                from datetime import date as _date
                from db_utils import get_db_connection
                conn = get_db_connection()
                c = conn.cursor()
                today = _date.today().isoformat()
                saved = 0
                for name, data in batch_vals.items():
                    c.execute("INSERT INTO indicator_records (indicator_name,value,unit,reference_range,report_source,record_date) VALUES (?,?,?,?,?,?)",
                              (name, data['value'], data['unit'], data['ref'], '批量录入', today))
                    saved += 1
                conn.commit()
                conn.close()
                st.success(f"✅ 成功保存 {saved} 条指标记录")
                st.rerun()
            except Exception as e:
                st.error(f"保存失败：{str(e)}")
    else:
        st.info("在上方输入框中填写指标值后，即可批量保存")

    st.markdown("</div></div>")

# ===== 底部导航 =====
st.markdown("""
<div class="sub-footer" style="margin-top: 32px;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
        <span style="color: #C85A1E; font-size: 13px; cursor: pointer;"
              onclick="window.location.href='main.py'">← 返回首页</span>
        <span style="color: #C85A1E; font-size: 13px; cursor: pointer;"
              onclick="window.location.href='pages/2_网页爬虫.py'">临床指南爬取 →</span>
    </div>
    SpiderMind · 基层慢病轻量化智能管理平台 · 仅供辅助参考，不替代专业医疗建议
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
