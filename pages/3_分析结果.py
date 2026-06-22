# -*- coding: utf-8 -*-
"""
SpiderMind - AI智能解读页
"""
import streamlit as st
import sys
import os
from datetime import datetime
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from coze_api import CozeAPI

st.set_page_config(
    page_title="AI智能解读 - SpiderMind",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.hospital_theme import inject_theme, render_nav, render_breadcrumb, render_page_header

inject_theme()
render_nav("3_分析结果")
render_breadcrumb("AI 智能解读")
render_page_header("🧠", "AI 智能解读",
    "基于Coze大模型，客观呈现检查数据与参考范围，提供趋势分析——不出现侥幸性判断语言")

st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# ===== 模式选择（卡片风格）=====
st.markdown("""
<style>
.analysis-mode-card {
    background: white;
    border-radius: 12px;
    border: 2px solid #E8D8C0;
    box-shadow: 0 2px 8px rgba(139,90,30,0.10);
    padding: 20px 18px;
    cursor: pointer;
    transition: all 0.25s;
    text-align: center;
    min-height: 110px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
}
.analysis-mode-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(139,90,30,0.16);
    border-color: #E8722A;
}
.analysis-mode-card.active {
    border-color: #C85A1E;
    background: linear-gradient(135deg, #FFF8F0, #FFFDF8);
    box-shadow: 0 4px 16px rgba(200,90,30,0.20);
}
.amc-icon { font-size: 30px; }
.amc-title { font-size: 14px; font-weight: 700; color: #2D1F0A; font-family: 'Noto Serif SC', serif; }
.amc-sub { font-size: 11px; color: #9A8060; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="principle-box">'
    '<strong>🔒 系统设计原则：</strong>'
    'AI 仅呈现客观医学数据，不提供任何诊断性判断。所有报告解读仅供参考，'
    '不替代专业医生的临床诊断。如有疑问，请咨询您的家庭医生或前往医院就诊。'
    '</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title" style="margin-bottom: 16px;">'
    '<div class="section-title-bar"></div>'
    '<h2>选择分析模式</h2>'
    '</div>', unsafe_allow_html=True)

# 四种分析模式
mode_pages = [
    ("report", "📋", "报告单解读", "REPORT ANALYSIS", "输入报告单，AI提取指标并客观解读"),
    ("guideline", "📖", "临床指南解读", "GUIDELINE ANALYSIS", "解读临床指南，评估基层可执行性"),
    ("trend", "📈", "多指标趋势分析", "TREND ANALYSIS", "追踪历史指标，绘制趋势变化图"),
    ("drug", "💊", "药物相互作用查询", "DRUG INTERACTION", "查询药物组合安全性与相互作用"),
]

mode = st.session_state.get("analysis_mode", "report")

mode_cols = st.columns(4)
for i, (mode_id, icon, title, sub, desc) in enumerate(mode_pages):
    active = "active" if mode == mode_id else ""
    css_class = f"analysis-mode-card {active}".strip()
    with mode_cols[i]:
        if st.button(f"{icon}\n{title}\n{sub}", key=f"mode_btn_{mode_id}", use_container_width=True):
            st.session_state["analysis_mode"] = mode_id
            st.rerun()
        st.markdown(f'<div class="{css_class}" style="margin-top:-8px; padding: 10px 14px; font-size:11px; color:#9A8060; text-align:center; line-height:1.5">{desc}</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# ===== Coze API 初始化 =====
# 去掉缓存确保每次使用最新配置
coze = CozeAPI()

# ====================== 报告单解读 ======================
if mode == "report":
    st.markdown("""
    <style>
    .result-section { background: white; border-radius: 12px; border: 1px solid #E8D8C0;
        box-shadow: 0 2px 8px rgba(139,90,30,0.10); padding: 20px 24px; margin-bottom: 20px; }
    .result-section h3 { font-size: 16px; font-weight: 700; color: #2D1F0A;
        margin: 0 0 14px 0; font-family: 'Noto Serif SC', serif; border-left: 3px solid #C85A1E;
        padding-left: 12px; }
    .safety-box { background: #FEF3E8; border: 1px solid #F0C898; border-left: 4px solid #C85A1E;
        border-radius: 8px; padding: 14px 18px; font-size: 12px; color: #5C4A2A;
        line-height: 1.7; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

    # 左侧：输入区；右侧：示例模板
    col_left, col_right = st.columns([3, 1])

    with col_left:
        # 优先检查：手动录入 / Excel导入传来的数据
        if st.session_state.get('analysis_content'):
            source = st.session_state.get('analysis_source', '')
            if source == 'excel':
                st.success("✅ 检测到Excel导入数据，正在自动分析...")
            elif source == 'manual':
                st.success("✅ 检测到手动输入内容，正在自动分析...")
            else:
                st.success("✅ 检测到已上传的报告数据，正在加载...")
            report_data = st.session_state['analysis_content']
            st.text_area("📄 报告内容", report_data, height=200, disabled=True, key="report_view")
        else:
            report_data = st.text_area(
                "📄 粘贴或输入报告内容",
                placeholder="请粘贴报告单内容，系统将自动识别关键指标...",
                height=220,
                key="report_input"
            )

    with col_right:
        st.markdown("""
        <div style="background:#FDF6EC; border:1px solid #E8D8C0; border-radius:10px; padding:16px; font-size:12px; color:#5C4A2A;">
          <div style="font-weight:700; color:#C85A1E; margin-bottom:8px;">📋 示例报告格式</div>
          <pre style="font-size:11px; line-height:1.6; white-space:pre-wrap; color:#5C4A2A;">
血红蛋白(Hb)  142  g/L  [120-160]
红细胞(RBC)   4.8  ×10¹²/L  [4.0-5.5]
白细胞(WBC)   6.5  ×10⁹/L  [4.0-10.0]
血小板(PLT)    210  ×10⁹/L  [100-300]
谷丙转氨酶(ALT) 28  U/L  [9-50]
谷草转氨酶(AST) 25  U/L  [15-40]</pre>
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 拍照上传后AI会提取文字，也可手动粘贴报告内容")

    if report_data:
        st.markdown('<div class="result-section" style="margin-top:16px;">', unsafe_allow_html=True)
        st.markdown('<h3>🔬 提交AI解读</h3>', unsafe_allow_html=True)

        # 自动触发：从Excel/手动录入跳转过来时，直接开始分析
        auto_trigger = st.session_state.get('analysis_content') and not st.session_state.get('pending_analysis')

        if auto_trigger or st.button("🧠 开始解读报告单", use_container_width=True, type="primary", key="btn_analyze_report"):
            st.session_state['pending_analysis'] = {
                'type': 'report',
                'content': report_data,
                'timestamp': datetime.now().isoformat()
            }
            st.rerun()

        # 解读结果显示
        if st.session_state.get('pending_analysis') and st.session_state['pending_analysis']['type'] == 'report':
            with st.spinner("🔬 AI正在分析报告单，请稍候..."):
                result = coze.analyze_report(
                    st.session_state['pending_analysis']['content'],
                    analysis_type='report'
                )

            if result.get('success'):
                st.success("✅ 解读完成")
                result_data = result.get('data', {})
                items = result_data.get('items', [])

                # ===== 可视化图表 =====
                if items:
                    try:
                        import plotly.graph_objects as go

                        def parse_ref(ref_str):
                            if not ref_str or ref_str in ['详见报告单', 'N/A', '']:
                                return None, None
                            match = re.search(r'([\d.]+)\s*[-~至]\s*([\d.]+)', str(ref_str))
                            if match:
                                return float(match.group(1)), float(match.group(2))
                            lt = re.search(r'<\s*([\d.]+)', str(ref_str))
                            if lt:
                                return None, float(lt.group(1))
                            gt = re.search(r'>\s*([\d.]+)', str(ref_str))
                            if gt:
                                return float(gt.group(1)), None
                            return None, None

                        indicators_data = []
                        for item in items:
                            try:
                                val = float(re.search(r'[\d.]+', str(item.get('value', ''))).group())
                                ref_min, ref_max = parse_ref(item.get('reference', ''))
                                indicators_data.append({
                                    'name': item.get('indicator', '指标'),
                                    'value': val,
                                    'ref_min': ref_min,
                                    'ref_max': ref_max,
                                })
                            except:
                                pass

                        if indicators_data:
                            # 柱状图
                            colors = []
                            for d in indicators_data:
                                if d['ref_min'] is not None and d['ref_max'] is not None:
                                    if d['value'] < d['ref_min'] or d['value'] > d['ref_max']:
                                        colors.append('#E74C3C')
                                    else:
                                        colors.append('#27AE60')
                                elif d['ref_max'] is not None and d['value'] > d['ref_max']:
                                    colors.append('#E74C3C')
                                else:
                                    colors.append('#3498DB')

                            fig1 = go.Figure()
                            fig1.add_trace(go.Bar(
                                x=[d['name'] for d in indicators_data],
                                y=[d['value'] for d in indicators_data],
                                marker_color=colors,
                                text=[f"{d['value']}" for d in indicators_data],
                                textposition='outside',
                            ))

                            for d in indicators_data:
                                if d['ref_max'] is not None:
                                    fig1.add_hline(y=d['ref_max'], line_dash="dash",
                                        line_color="rgba(231,76,60,0.5)", annotation_text=f"上限 {d['ref_max']}")
                                if d['ref_min'] is not None:
                                    fig1.add_hline(y=d['ref_min'], line_dash="dash",
                                        line_color="rgba(39,174,96,0.5)", annotation_text=f"下限 {d['ref_min']}")

                            fig1.update_layout(
                                title="📊 指标检测值 vs 参考范围",
                                yaxis_title="检测值",
                                template="plotly_white",
                                font=dict(family="Microsoft YaHei"),
                                height=350,
                                showlegend=False
                            )
                            st.plotly_chart(fig1, use_container_width=True)

                            leg1, leg2, leg3 = st.columns(3)
                            with leg1: st.markdown("🟢 **绿色**：在参考范围内")
                            with leg2: st.markdown("🔴 **红色**：超出参考范围")
                            with leg3: st.markdown("🔵 **蓝色**：无法判断")

                            # 雷达图
                            if len(indicators_data) >= 3:
                                fig2 = go.Figure()
                                normalized = []
                                for d in indicators_data:
                                    if d['ref_min'] is not None and d['ref_max'] is not None:
                                        ref_mid = (d['ref_min'] + d['ref_max']) / 2
                                        ref_range = d['ref_max'] - d['ref_min']
                                        if ref_range > 0:
                                            score = 50 + (d['value'] - ref_mid) / ref_range * 50
                                            score = max(0, min(100, score))
                                            normalized.append(score)
                                        else:
                                            normalized.append(50)
                                    else:
                                        normalized.append(50)

                                fig2.add_trace(go.Scatterpolar(
                                    r=normalized + [normalized[0]],
                                    theta=[d['name'] for d in indicators_data] + [indicators_data[0]['name']],
                                    fill='toself',
                                    fillcolor='rgba(52,152,219,0.2)',
                                    line=dict(color='#3498DB', width=2),
                                    name='当前值',
                                    marker=dict(size=6)
                                ))
                                fig2.add_trace(go.Scatterpolar(
                                    r=[50] * (len(indicators_data) + 1),
                                    theta=[d['name'] for d in indicators_data] + [indicators_data[0]['name']],
                                    mode='lines',
                                    line=dict(color='rgba(39,174,96,0.5)', width=2, dash='dash'),
                                    name='参考中值',
                                    hoverinfo='skip'
                                ))
                                fig2.update_layout(
                                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                    title="🎯 多指标健康度雷达图",
                                    font=dict(family="Microsoft YaHei"),
                                    height=350,
                                    showlegend=True
                                )
                                st.plotly_chart(fig2, use_container_width=True)

                    except ImportError:
                        st.warning("需要安装 plotly：pip install plotly")

                # ===== 逐项解读 =====
                st.markdown('<h3>📋 逐项解读（仅呈现数据，不做判断）</h3>', unsafe_allow_html=True)
                for item in result_data.get('items', []):
                    ref_str = item.get('reference', '详见报告单')
                    val_str = item.get('value', 'N/A')

                    # 判断是否超出范围
                    try:
                        val_num = float(re.search(r'[\d.]+', str(val_str)).group())
                        ref_match = re.search(r'([\d.]+)\s*[-~至]\s*([\d.]+)', str(ref_str))
                        out_of_range = False
                        if ref_match:
                            r_min, r_max = float(ref_match.group(1)), float(ref_match.group(2))
                            if val_num < r_min or val_num > r_max:
                                out_of_range = True
                    except:
                        out_of_range = False

                    indicator_color = "#E74C3C" if out_of_range else "#27AE60"

                    st.markdown(f"""
                    <div style="background:#FAFAFA; border:1px solid #E8D8C0; border-radius:10px;
                        padding:14px 18px; margin-bottom:12px;">
                        <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                            <div style="font-size:16px;">🔬</div>
                            <div style="font-size:15px; font-weight:700; color:#2D1F0A;">{item.get('indicator', '指标项')}</div>
                            <div style="flex:1"></div>
                            <div style="background:{indicator_color}; color:white; padding:3px 10px;
                                border-radius:12px; font-size:11px; font-weight:600;">
                                {'⚠️ 超出范围' if out_of_range else '✓ 在范围内'}
                            </div>
                        </div>
                        <div style="display:grid; grid-template-columns: 1fr 1fr 2fr; gap:12px; font-size:13px;">
                            <div><div style="font-size:11px; color:#9A8060; margin-bottom:2px;">检测值</div>
                                <div style="font-weight:700; color:#2D1F0A;">{val_str} {item.get('unit','')}</div></div>
                            <div><div style="font-size:11px; color:#9A8060; margin-bottom:2px;">参考范围</div>
                                <div style="font-weight:600; color:#5C4A2A;">{ref_str}</div></div>
                            <div><div style="font-size:11px; color:#9A8060; margin-bottom:2px;">客观呈现</div>
                                <div style="color:#1a5276;">{item.get('note', '数据已呈现，请参考参考范围自行判断')}</div></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # ===== AI综合解读 =====
                st.markdown('<h3>💬 AI综合解读</h3>', unsafe_allow_html=True)
                ai_text = result_data.get('analysis', '')
                st.markdown(f"""
                <div style="background:#FDFAF5; border:1px solid #E8D8C0; border-radius:10px;
                    padding:16px 20px; font-size:15px; color:#2D1F0A; line-height:1.8; margin-bottom:16px;">
                    {ai_text}
                </div>
                """, unsafe_allow_html=True)

                # ===== 安全提示 =====
                st.markdown("""
                <div class="safety-box">
                    ⚠️ <strong>重要提醒：</strong>以上内容仅展示报告数据，不构成任何医疗建议。
                    指标是否异常、是否需要就医，请以主治医生的判断为准。平台不会提示"不严重""还好"
                    "不用担心"等具有侥幸暗示的语言——您的健康，您和医生共同决策。
                </div>
                """, unsafe_allow_html=True)

                # ===== 保存按钮 =====
                if st.button("📥 保存到慢病履历台账", use_container_width=True, key="save_to_records"):
                    try:
                        from datetime import date as _date
                        from db_utils import get_db_connection
                        conn = get_db_connection()
                        c = conn.cursor()
                        today = _date.today().isoformat()
                        for item in result_data.get('items', []):
                            c.execute("INSERT INTO indicator_records (indicator_name,value,unit,reference_range,report_source,record_date) VALUES (?,?,?,?,?,?)",
                                      (item.get('indicator','未知指标'), str(item.get('value','')),
                                       item.get('unit',''), item.get('reference',''), 'AI报告解读', today))
                        conn.commit()
                        conn.close()
                        st.success("✅ 已保存到慢病履历台账")
                    except Exception as e:
                        st.error(f"保存失败：{str(e)}")

                # ===== PDF 导出按钮 =====
                st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
                if st.button("📄 导出分析报告 (HTML)", use_container_width=True, key="btn_export_pdf", type="secondary"):
                    try:
                        import tempfile, os

                        # 生成 HTML 报告
                        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>SpiderMind 健康分析报告</title>
    <style>
        body {{ font-family: "Microsoft YaHei", "SimHei", sans-serif; margin: 40px; color: #2D1F0A; }}
        h1 {{ color: #C85A1E; border-bottom: 2px solid #C85A1E; padding-bottom: 10px; }}
        h2 {{ color: #5C4A2A; margin-top: 30px; }}
        .meta {{ color: #9A8060; font-size: 14px; margin-bottom: 30px; }}
        .indicator {{ background: #FDFAF5; border: 1px solid #E8D8C0; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; }}
        .indicator-name {{ font-weight: 700; font-size: 15px; }}
        .indicator-value {{ color: #C85A1E; font-weight: 700; }}
        .indicator-ref {{ color: #9A8060; font-size: 13px; }}
        .analysis {{ background: #FDFAF5; border: 1px solid #E8D8C0; border-radius: 8px; padding: 16px 20px; line-height: 1.8; margin-top: 20px; }}
        .warning {{ background: #FEF3E8; border: 1px solid #F0C898; border-left: 4px solid #C85A1E; border-radius: 8px; padding: 14px 18px; margin-top: 30px; font-size: 13px; color: #5C4A2A; }}
        @media print {{
            body {{ margin: 20px; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <h1>🧠 SpiderMind 健康分析报告</h1>
    <div class="meta">
        生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}<br>
        报告类型：AI 智能解读
    </div>

    <h2>📋 指标详情</h2>
"""

                        # 添加指标
                        for item in result_data.get('items', []):
                            ind = item.get('indicator', 'N/A')
                            val = item.get('value', 'N/A')
                            unit = item.get('unit', '')
                            ref = item.get('reference', 'N/A')
                            html_content += f"""
    <div class="indicator">
        <span class="indicator-name">{ind}</span>：
        <span class="indicator-value">{val} {unit}</span>
        <span class="indicator-ref">（参考范围：{ref}）</span>
    </div>
"""

                        # 添加 AI 分析
                        html_content += f"""
    <h2>💬 AI 综合解读</h2>
    <div class="analysis">
        {result_data.get('analysis', '暂无解读')}
    </div>

    <div class="warning">
        <strong>⚠️ 重要提醒：</strong>以上内容仅展示报告数据，不构成任何医疗建议。
        指标是否异常、是否需要就医，请以主治医生的判断为准。
    </div>

    <div class="no-print" style="margin-top: 30px;">
        <button onclick="window.print()" style="padding: 10px 20px; font-size: 14px; cursor: pointer;">
            🖨️ 打印 / 保存为 PDF
        </button>
    </div>
</body>
</html>
"""

                        # 保存为临时文件
                        temp_dir = tempfile.gettempdir()
                        html_path = os.path.join(temp_dir, f"SpiderMind_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
                        with open(html_path, "w", encoding="utf-8") as f:
                            f.write(html_content)

                        # 提供下载
                        with open(html_path, "r", encoding="utf-8") as f:
                            st.download_button(
                                label="⬇️ 下载 HTML 报告",
                                data=f.read().encode('utf-8'),
                                file_name=os.path.basename(html_path),
                                mime="text/html",
                                use_container_width=True
                            )
                        st.success("✅ HTML 报告已生成！下载后用浏览器打开，按 Ctrl+P 即可保存为 PDF")
                        os.remove(html_path)
                    except Exception as e:
                        st.error(f"报告生成失败：{str(e)}")

            else:
                st.error(f"❌ 解读失败：{result.get('error')}")

        st.markdown('</div>', unsafe_allow_html=True)

# ====================== 临床指南解读 ======================
elif mode == "guideline":
    col_left, col_right = st.columns([3, 1])

    with col_left:
        guideline_content = st.text_area(
            "📄 粘贴指南正文",
            placeholder="从「临床指南爬取」页获取指南内容，或手动粘贴...",
            height=220,
            key="guideline_input"
        )
        analysis_focus = st.multiselect(
            "重点分析方向",
            ["适用范围", "核心推荐", "用药指导", "随访建议", "禁忌与注意事项", "基层可执行性评估"],
            default=["核心推荐", "基层可执行性评估"],
            key="focus_select"
        )

    with col_right:
        st.markdown("""
        <div style="background:#FDF6EC; border:1px solid #E8D8C0; border-radius:10px; padding:16px; font-size:12px; color:#5C4A2A;">
          <div style="font-weight:700; color:#C85A1E; margin-bottom:8px;">📋 输入格式示例</div>
          <pre style="font-size:11px; line-height:1.6; white-space:pre-wrap; color:#5C4A2A;">
《中国2型糖尿病防治指南（2020版）》

【推荐意见】
1. 生活方式干预是基础治疗
2. 二甲双胍是一线用药
3. HbA1c控制目标：<7%

【用药指导】
- 二甲双胍：起始500mg bid
- 注意胃肠道反应

【随访建议】
- 每3个月检测HbA1c
- 每年筛查并发症</pre>
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 支持从网页直接复制粘贴，AI会自动提取关键信息")

    if st.button("🧠 解读指南", use_container_width=True, type="primary", key="btn_analyze_guideline"):
        if guideline_content:
            with st.spinner("AI正在分析指南内容..."):
                result = coze.analyze_report(guideline_content, analysis_type='guideline')

            if result.get('success'):
                st.success("✅ 指南解读完成")
                st.markdown(f"""
                <div style="background:#FDFAF5; border:1px solid #E8D8C0; border-radius:10px;
                    padding:16px 20px; font-size:13px; color:#2D1F0A; line-height:1.8; margin:16px 0;">
                    {result.get('analysis', '')}
                </div>
                """, unsafe_allow_html=True)

                if "基层可执行性评估" in analysis_focus:
                    feasibility = result.get('feasibility', {})
                    if feasibility:
                        st.markdown('<h3 style="font-size:16px; font-weight:700; color:#2D1F0A; border-left:3px solid #C85A1E; padding-left:12px; margin-top:20px;">🏥 基层可执行性评估</h3>', unsafe_allow_html=True)
                        fc1, fc2, fc3 = st.columns(3)
                        with fc1:
                            st.metric("技术门槛", feasibility.get('tech_level', '中'))
                        with fc2:
                            st.metric("成本评估", feasibility.get('cost_level', '中'))
                        with fc3:
                            st.metric("推广价值", feasibility.get('value', '高'))
                        st.markdown(f"**评估详情：** {feasibility.get('detail', '')}")
            else:
                st.error(f"❌ 解读失败：{result.get('error')}")
        else:
            st.warning("请先输入指南内容")

# ====================== 多指标趋势分析 ======================
elif mode == "trend":
    try:
        from db_utils import get_db_path
        db_path = get_db_path()
        import sqlite3, pandas as _pd
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            all_names = _pd.read_sql_query("SELECT DISTINCT indicator_name FROM indicator_records ORDER BY indicator_name", conn)
            available_indicators = all_names['indicator_name'].tolist()
            conn.close()
        else:
            available_indicators = []
    except:
        available_indicators = []

    if available_indicators:
        selected = st.multiselect("选择要分析的指标（多选）", available_indicators,
                                  default=available_indicators[:3], key="trend_indicators")

        if selected:
            try:
                import pandas as pd, plotly.express as px
                import sqlite3

                conn = sqlite3.connect(db_path)
                placeholders = ",".join("?" * len(selected))
                df = pd.read_sql_query(
                    f"SELECT indicator_name AS 指标, record_date AS 日期, value AS 检测值_原始 FROM indicator_records WHERE indicator_name IN ({placeholders}) ORDER BY record_date",
                    conn, params=selected
                )
                conn.close()

                df['检测值'] = pd.to_numeric(df['检测值_原始'], errors='coerce')
                df = df.dropna(subset=['检测值'])
                df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
                df = df.sort_values('日期')

                if not df.empty:
                    fig = px.line(df, x='日期', y='检测值', color='指标',
                                  markers=True, title='指标趋势变化图')
                    fig.update_layout(template='plotly_white',
                                      font=dict(family="Microsoft YaHei"), height=380)
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown('<h3 style="font-size:16px; font-weight:700; color:#2D1F0A; border-left:3px solid #C85A1E; padding-left:12px; margin-top:16px;">📊 统计摘要</h3>', unsafe_allow_html=True)
                    summary = df.groupby('指标')['检测值'].agg(['mean', 'min', 'max', 'count'])
                    summary.columns = ['平均值', '最小值', '最大值', '记录次数']
                    st.dataframe(summary.round(2), use_container_width=True, hide_index=True)
                else:
                    st.warning("所选指标暂无有效数值数据")
            except ImportError:
                st.warning("需要安装 plotly 和 pandas")
    else:
        st.info("📋 暂无历史数据。请先在「数据上传」页面录入指标，或等待报告解读后自动保存。")

# ====================== 药物相互作用查询 ======================
elif mode == "drug":
    dc1, dc2 = st.columns(2)
    with dc1:
        drug1 = st.text_input("药物①", placeholder="例如：二甲双胍", key="drug1_input")
    with dc2:
        drug2 = st.text_input("药物②", placeholder="例如：阿司匹林", key="drug2_input")

    preset = st.selectbox("常用慢病药物组合快速查询", [
        "— 自定义查询 —",
        "二甲双胍 + 格列美脲",
        "二甲双胍 + 阿卡波糖",
        "氨氯地平 + 贝那普利",
        "阿司匹林 + 华法林",
        "辛伐他汀 + 氨氯地平",
        "奥美拉唑 + 氯吡格雷",
    ], key="drug_preset")

    if preset != "— 自定义查询 —":
        parts = preset.split(' + ')
        drug1 = parts[0]
        drug2 = parts[1] if len(parts) > 1 else ""
        st.info(f"🔍 查询组合：{drug1} + {drug2}")

    if st.button("🔍 查询相互作用", use_container_width=True, type="primary", key="btn_drug_query"):
        if drug1:
            with st.spinner("正在查询药物相互作用信息..."):
                result = coze.query_drug_interaction(drug1, drug2)

            if result.get('success'):
                st.success("✅ 查询完成")
                st.markdown(f"""
                <div style="background:#FDFAF5; border:1px solid #E8D8C0; border-radius:10px;
                    padding:16px 20px; font-size:13px; color:#2D1F0A; line-height:1.8; margin:16px 0;">
                    {result.get('analysis', '')}
                </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                <div class="safety-box">
                    ⚠️ <strong>用药安全提醒：</strong>以上信息仅供参考，不构成用药建议。
                    实际用药请严格遵医嘱。如有疑问，请咨询您的临床药师或主治医生。
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"❌ 查询失败：{result.get('error')}")
        else:
            st.warning("请输入至少一种药物名称")

# ===== 底部导航 =====
st.markdown("""
<div class="sub-footer">
    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
        <span style="color: #C85A1E; font-size: 13px; cursor: pointer;"
              onclick="window.location.href='pages/1_数据上传.py'">← 返回数据上传</span>
        <span style="color: #C85A1E; font-size: 13px; cursor: pointer;"
              onclick="window.location.href='pages/5_慢病履历.py'">慢病履历台账 →</span>
    </div>
    SpiderMind · 基层慢病轻量化智能管理平台 · 仅供辅助参考，不替代专业医疗建议
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
