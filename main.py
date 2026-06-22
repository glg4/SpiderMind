# -*- coding: utf-8 -*-
"""
SpiderMind - 基层慢病轻量化智能管理平台
主页面 - 医院官网风格设计
"""

import streamlit as st
import os
import datetime
from pathlib import Path

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="SpiderMind · 慢病智能管理平台",
    page_icon="❤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 功能卡片跳转处理 ====================
# 从 query params 读取跳转目标并切换页面
if "goto" in st.query_params:
    target = st.query_params["goto"]
    # 避免循环：只有目标是其他页面时才跳转
    if not os.path.basename(__file__).startswith(target.replace("pages/", "").split(".")[0] + "."):
        try:
            st.switch_page(str(Path(target)))
        except Exception:
            pass
    # 清除 query param
    del st.query_params["goto"]

# ==================== 全局 CSS ====================
st.markdown("""
<style>
/* ===== 字体引入 ===== */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&display=swap');

/* ===== 全局变量 - 广医一院风格 ===== */
:root {
    --brand:       #C85A1E;   /* 主橙色 */
    --brand-dark:  #9C3F10;   /* 深橙 */
    --brand-light: #E8722A;   /* 亮橙 */
    --gold:        #D4A94A;   /* 金色点缀 */
    --cream:       #F9F3EA;   /* 米黄底色 */
    --cream2:      #FDF6EC;   /* 浅米黄 */
    --warm-white:  #FFFDF8;   /* 暖白 */
    --ink:         #2D1F0A;   /* 深墨色文字 */
    --ink-mid:     #5C4A2A;   /* 中色文字 */
    --ink-muted:   #9A8060;   /* 弱色文字 */
    --border:      #E8D8C0;   /* 边框 */
    --border-warm: #D4B896;   /* 暖边框 */
    --shadow:      rgba(139, 90, 30, 0.12);
}

/* ===== 隐藏 Streamlit 默认元素 ===== */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="collapsedControl"] { display: none !important; }
.stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ===== 页面背景 ===== */
.stApp {
    background-color: var(--cream);
    background-image:
        radial-gradient(ellipse 800px 600px at 20% 0%, rgba(200, 90, 30, 0.04) 0%, transparent 60%),
        radial-gradient(ellipse 600px 400px at 80% 100%, rgba(212, 169, 74, 0.06) 0%, transparent 60%);
}

/* ===== 顶部导航栏 ===== */
.top-nav {
    background: linear-gradient(180deg, #1A0A00 0%, #2D1500 100%);
    padding: 0;
    position: sticky;
    top: 0;
    z-index: 999;
    border-bottom: 3px solid var(--brand);
}
.nav-inner {
    max-width: 1280px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    height: 70px;
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 14px;
}
.nav-logo .logo-icon {
    width: 42px;
    height: 42px;
    background: linear-gradient(135deg, var(--brand), var(--gold));
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
    box-shadow: 0 0 0 3px rgba(200,90,30,0.3);
}
.nav-logo .logo-text-cn {
    font-size: 20px;
    font-weight: 700;
    color: white;
    letter-spacing: 2px;
    line-height: 1.2;
    font-family: 'Noto Serif SC', serif;
}
.nav-logo .logo-text-en {
    font-size: 10px;
    color: rgba(255,255,255,0.5);
    letter-spacing: 1px;
    text-transform: uppercase;
}
.nav-links {
    display: flex;
    gap: 2px;
    align-items: center;
}
.nav-links a.nav-link {
    color: rgba(255,255,255,0.75);
    text-decoration: none;
    font-size: 13px;
    padding: 8px 16px;
    border-radius: 4px;
    transition: all 0.2s;
    cursor: pointer;
    white-space: nowrap;
    display: inline-block;
}
.nav-links a.nav-link:hover, .nav-links a.nav-link.active {
    color: white;
    background: rgba(200,90,30,0.4);
}
.nav-links a.nav-link.active { color: var(--brand-light); }
.nav-date {
    color: rgba(255,255,255,0.4);
    font-size: 11px;
    padding-left: 16px;
    border-left: 1px solid rgba(255,255,255,0.1);
    margin-left: 8px;
}

/* ===== Hero Banner ===== */
.hero-banner {
    background: linear-gradient(135deg, #1A0A00 0%, #2D1500 40%, #4A2000 70%, #6B3010 100%);
    position: relative;
    overflow: hidden;
    height: 340px;
    display: flex;
    align-items: center;
}
.hero-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 600px 400px at 70% 50%, rgba(200,90,30,0.25) 0%, transparent 60%),
        radial-gradient(ellipse 400px 300px at 20% 80%, rgba(212,169,74,0.15) 0%, transparent 50%);
}
.hero-pattern {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 50%;
    background:
        repeating-linear-gradient(
            45deg,
            transparent,
            transparent 20px,
            rgba(200,90,30,0.04) 20px,
            rgba(200,90,30,0.04) 21px
        );
}
.hero-content {
    position: relative;
    z-index: 2;
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 60px;
    width: 100%;
}
.hero-tag {
    display: inline-block;
    background: rgba(200,90,30,0.3);
    border: 1px solid rgba(200,90,30,0.5);
    color: var(--brand-light);
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.hero-title {
    font-size: 42px;
    font-weight: 700;
    color: white;
    font-family: 'Noto Serif SC', serif;
    line-height: 1.2;
    margin-bottom: 12px;
    text-shadow: 0 2px 20px rgba(0,0,0,0.5);
}
.hero-title span { color: var(--brand-light); }
.hero-subtitle {
    font-size: 15px;
    color: rgba(255,255,255,0.65);
    line-height: 1.8;
    max-width: 520px;
    margin-bottom: 28px;
}
.hero-stats {
    display: flex;
    gap: 40px;
}
.hero-stat-item {
    text-align: center;
}
.hero-stat-num {
    font-size: 28px;
    font-weight: 700;
    color: var(--brand-light);
    font-family: 'Noto Serif SC', serif;
    line-height: 1;
}
.hero-stat-label {
    font-size: 11px;
    color: rgba(255,255,255,0.45);
    margin-top: 4px;
    letter-spacing: 1px;
}
.hero-right {
    position: absolute;
    right: 80px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 2;
}
.hero-badge {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(200,90,30,0.3);
    border-radius: 16px;
    padding: 24px 28px;
    text-align: center;
    backdrop-filter: blur(8px);
}
.hero-badge-icon { font-size: 48px; line-height: 1; margin-bottom: 8px; }
.hero-badge-text { color: rgba(255,255,255,0.7); font-size: 12px; line-height: 1.6; }

/* ===== 公告栏 ===== */
.notice-bar {
    background: linear-gradient(90deg, var(--brand) 0%, var(--brand-dark) 100%);
    padding: 12px 0;
}
.notice-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 32px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.notice-label {
    background: rgba(255,255,255,0.2);
    color: white;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
    letter-spacing: 1px;
}
.notice-text {
    color: rgba(255,255,255,0.9);
    font-size: 12px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ===== 快捷入口区 ===== */
.quick-section {
    background: white;
    border-bottom: 1px solid var(--border);
    padding: 0;
}
.quick-inner {
    max-width: 1280px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(6, 1fr);
}

/* ===== 主内容区容器 ===== */
.main-wrap {
    max-width: 1280px;
    margin: 0 auto;
    padding: 36px 32px;
}

/* ===== 板块标题 ===== */
.section-title {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}
.section-title-bar {
    width: 4px;
    height: 22px;
    background: linear-gradient(180deg, var(--brand), var(--gold));
    border-radius: 2px;
    flex-shrink: 0;
}
.section-title h2 {
    font-size: 20px;
    font-weight: 700;
    color: var(--ink);
    margin: 0;
    font-family: 'Noto Serif SC', serif;
    letter-spacing: 1px;
}
.section-title .sub {
    font-size: 12px;
    color: var(--ink-muted);
    margin-left: auto;
    cursor: pointer;
}
.section-title .sub:hover { color: var(--brand); }

/* ===== 功能卡片（院区卡片风格）===== */
.func-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 36px;
}
.func-card {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: 0 2px 12px var(--shadow);
    transition: all 0.25s;
    cursor: pointer;
    text-decoration: none;
}
.func-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(139,90,30,0.16);
    border-color: var(--brand-light);
}
.func-card-img {
    height: 130px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}
.fc-orange { background: linear-gradient(135deg, #3D1A00 0%, #7A3510 50%, #C85A1E 100%); }
.fc-teal   { background: linear-gradient(135deg, #003D2A 0%, #0A5E3F 50%, #1A8A5A 100%); }
.fc-blue   { background: linear-gradient(135deg, #001A3D 0%, #0A3060 50%, #1A5296 100%); }
.fc-purple { background: linear-gradient(135deg, #2A003D 0%, #4A0A60 50%, #7A1A96 100%); }
.fc-green  { background: linear-gradient(135deg, #003D0A 0%, #0A5E20 50%, #1A8A38 100%); }
.fc-gold   { background: linear-gradient(135deg, #3D2A00 0%, #6B4A00 50%, #A87A0A 100%); }
.func-card-img-icon {
    font-size: 52px;
    opacity: 0.9;
    filter: drop-shadow(0 4px 12px rgba(0,0,0,0.4));
    transition: transform 0.3s;
}
.func-card:hover .func-card-img-icon { transform: scale(1.12) rotate(3deg); }
.func-card-img-pattern {
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
        45deg,
        transparent,
        transparent 12px,
        rgba(255,255,255,0.03) 12px,
        rgba(255,255,255,0.03) 13px
    );
}
.func-card-img-label {
    position: absolute;
    bottom: 10px;
    left: 14px;
    background: rgba(0,0,0,0.45);
    color: rgba(255,255,255,0.9);
    font-size: 10px;
    padding: 3px 8px;
    border-radius: 4px;
    letter-spacing: 1px;
    backdrop-filter: blur(4px);
}
.func-card-body {
    padding: 16px 18px;
}
.func-card-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 6px 0;
    font-family: 'Noto Serif SC', serif;
}
.func-card-desc {
    font-size: 12px;
    color: var(--ink-muted);
    line-height: 1.7;
    margin: 0 0 12px 0;
}
.func-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 12px;
    border-top: 1px solid var(--border);
}
.func-card-tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}
.func-tag {
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 10px;
    background: var(--cream2);
    color: var(--ink-mid);
    border: 1px solid var(--border);
}
.func-arrow {
    color: var(--brand);
    font-size: 16px;
    font-weight: 700;
    transition: transform 0.2s;
}
.func-card:hover .func-arrow { transform: translateX(4px); }

/* ===== 信息看板 ===== */
.info-board {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 36px;
}
.board-panel {
    background: white;
    border-radius: 12px;
    border: 1px solid var(--border);
    overflow: hidden;
    box-shadow: 0 2px 8px var(--shadow);
}
.board-panel-header {
    background: linear-gradient(90deg, #2D1500, #4A2800);
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.board-panel-header h3 {
    color: white;
    font-size: 14px;
    margin: 0;
    font-weight: 600;
    letter-spacing: 1px;
}
.board-panel-body { padding: 20px; }
.news-item {
    display: flex;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px dashed var(--border);
    align-items: flex-start;
}
.news-item:last-child { border-bottom: none; padding-bottom: 0; }
.news-date {
    background: var(--cream2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 11px;
    color: var(--brand);
    font-weight: 600;
    white-space: nowrap;
    line-height: 1.4;
    text-align: center;
    min-width: 44px;
}
.news-content .title {
    font-size: 13px;
    color: var(--ink);
    line-height: 1.5;
    margin-bottom: 2px;
    font-weight: 500;
}
.news-content .title:hover { color: var(--brand); cursor: pointer; }
.news-content .meta { font-size: 11px; color: var(--ink-muted); }

/* ===== 系统状态卡片 ===== */
.status-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 36px;
}
.status-card {
    background: white;
    border-radius: 10px;
    padding: 18px;
    border: 1px solid var(--border);
    box-shadow: 0 2px 6px var(--shadow);
    display: flex;
    align-items: center;
    gap: 14px;
}
.status-icon {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}
.si-ok     { background: #E8F5E9; }
.si-warn   { background: #FFF8E1; }
.si-info   { background: #E3F2FD; }
.si-brand  { background: #FEE8D6; }
.status-info { flex: 1; min-width: 0; }
.status-info .num {
    font-size: 20px;
    font-weight: 700;
    color: var(--ink);
    line-height: 1.2;
}
.status-info .label {
    font-size: 11px;
    color: var(--ink-muted);
    margin-top: 2px;
}

/* ===== 设计原则横幅 ===== */
.principle-banner {
    background: linear-gradient(90deg, #FEF3E8, #FFFDF8);
    border: 1px solid #F0C898;
    border-left: 4px solid var(--brand);
    border-radius: 8px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 28px;
    font-size: 13px;
    color: var(--ink-mid);
    line-height: 1.6;
}
.principle-icon { font-size: 20px; flex-shrink: 0; }
.principle-text strong { color: var(--brand-dark); }

/* ===== 底栏 ===== */
.site-footer {
    background: #1A0A00;
    padding: 32px 0 20px;
    margin-top: 40px;
    border-top: 3px solid var(--brand);
}
.footer-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 32px;
}
.footer-grid {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 32px;
    margin-bottom: 24px;
}
.footer-brand-name {
    color: white;
    font-size: 20px;
    font-weight: 700;
    font-family: 'Noto Serif SC', serif;
    margin-bottom: 8px;
    letter-spacing: 1px;
}
.footer-brand-desc { color: rgba(255,255,255,0.4); font-size: 12px; line-height: 1.8; }
.footer-col-title {
    color: var(--brand-light);
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 12px;
    letter-spacing: 1px;
}
.footer-link {
    color: rgba(255,255,255,0.5);
    font-size: 12px;
    display: block;
    margin-bottom: 6px;
    cursor: pointer;
    transition: color 0.2s;
}
.footer-link:hover { color: rgba(255,255,255,0.85); }
.footer-divider { border-color: rgba(255,255,255,0.08); margin: 0 0 16px 0; }
.footer-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.footer-copyright { color: rgba(255,255,255,0.25); font-size: 11px; }
.footer-badges { display: flex; gap: 12px; }
.footer-badge {
    background: rgba(200,90,30,0.15);
    border: 1px solid rgba(200,90,30,0.3);
    color: rgba(200,90,30,0.7);
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 10px;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ==================== 获取今日日期 ====================
today = datetime.date.today()
date_str = today.strftime("%Y年%m月%d日")
weekdays = ["周一","周二","周三","周四","周五","周六","周日"]
week_str = weekdays[today.weekday()]

# ==================== 顶部导航栏（HTML 导航链接 + session_state 跳转）====================
nav_pages = [
    ("首页", "main.py"),
    ("报告上传", "pages/1_数据上传.py"),
    ("临床指南", "pages/2_网页爬虫.py"),
    ("AI解读", "pages/3_分析结果.py"),
    ("健康问答", "pages/4_健康问答.py"),
    ("慢病履历", "pages/5_慢病履历.py"),
    ("用药提醒", "pages/6_用药提醒.py"),
    ("健康任务", "pages/7_健康任务.py"),
]

# 生成导航链接 HTML（横向排列，白色字体）
nav_links_html = ""
for label, path in nav_pages:
    nav_links_html += f'<a href="?nav_goto={path}" class="nav-link">{label}</a>'

st.markdown(f"""
<div class="top-nav">
  <div class="nav-inner">
    <div class="nav-logo">
      <div class="logo-icon">❤</div>
      <div>
        <div class="logo-text-cn">SpiderMind 慢病管理</div>
        <div class="logo-text-en">Chronic Disease Intelligent Management Platform</div>
      </div>
    </div>
    <nav class="nav-links">
      {nav_links_html}
    </nav>
    <span class="nav-date">{date_str} {week_str}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# 处理导航跳转（用 session_state + query_params 避免闪烁）
if "nav_goto" in st.query_params:
    target = st.query_params["nav_goto"]
    del st.query_params["nav_goto"]
    st.session_state["_nav_target"] = target

if "_nav_target" in st.session_state and st.session_state["_nav_target"]:
    target = st.session_state.pop("_nav_target")
    st.switch_page(target)

# ==================== Hero Banner ====================
st.markdown("""
<div class="hero-banner">
  <div class="hero-pattern"></div>
  <div class="hero-content">
    <div class="hero-tag">INTELLIGENT · LOCAL · SECURE</div>
    <div class="hero-title">基层慢病<span>智能管理</span>平台</div>
    <div class="hero-subtitle">
      面向高血压、糖尿病等慢性病患者，提供本地化健康档案、AI辅助解读、
      临床指南查询等全链路管理服务，数据全程不离开本地。
    </div>
    <div class="hero-stats">
      <div class="hero-stat-item">
        <div class="hero-stat-num">6</div>
        <div class="hero-stat-label">功能模块</div>
      </div>
      <div class="hero-stat-item">
        <div class="hero-stat-num">100%</div>
        <div class="hero-stat-label">本地存储</div>
      </div>
      <div class="hero-stat-item">
        <div class="hero-stat-num">AI</div>
        <div class="hero-stat-label">客观解读</div>
      </div>
      <div class="hero-stat-item">
        <div class="hero-stat-num">0</div>
        <div class="hero-stat-label">云端上传</div>
      </div>
    </div>
  </div>
  <div class="hero-right">
    <div class="hero-badge">
      <div class="hero-badge-icon">🏥</div>
      <div class="hero-badge-text">基层医疗专项<br>慢病智能管理<br>Powered by Coze AI</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ==================== 公告滚动栏 ====================
st.markdown(f"""
<div class="notice-bar">
  <div class="notice-inner">
    <span class="notice-label">最新公告</span>
    <span class="notice-text">
      📢 &nbsp; 系统已更新：新增药物相互作用查询功能 &nbsp;｜&nbsp;
      📋 &nbsp; 支持导入电子检查报告（Excel/CSV）进行AI智能解读 &nbsp;｜&nbsp;
      🔒 &nbsp; 数据全程本地存储，AI只客观呈现数据，不做判断性表述 &nbsp;｜&nbsp;
      {date_str} &nbsp; 系统运行正常
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ==================== 核心指标概览区 ====================
st.markdown('<div class="quick-section"><div class="quick-inner">', unsafe_allow_html=True)

# 三个关键指标卡片
overview_cols = st.columns(3)

overview_items = [
    ("🩺", "本周期已录入", "0 条健康记录", "#FEE8D6"),
    ("📊", "健康趋势评分", "暂无数据", "#D6EEE8"),
    ("💊", "用药依从率", "尚未统计", "#D6F0D6"),
]

for i, (icon, label, value, bg) in enumerate(overview_items):
    with overview_cols[i]:
        st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #E8D8C0;
            border-radius: 12px;
            padding: 20px 16px;
            text-align: center;
            min-height: 100px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 8px;
        ">
            <div style="font-size: 28px;">{icon}</div>
            <div style="font-size: 11px; color: #9A8060; letter-spacing: 1px;">{label}</div>
            <div style="font-size: 14px; font-weight: 700; color: #2D1F0A;">{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# ==================== 主内容区 ====================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

# ----- 设计原则横幅 -----
st.markdown("""
<div class="principle-banner">
  <span class="principle-icon">🛡️</span>
  <div class="principle-text">
    <strong>核心设计原则：</strong>AI 仅客观呈现检查数据（如"血糖 7.2 mmol/L，参考范围 3.9–6.1"），
    不出现"不严重""还好""不用担心"等侥幸性语言，避免患者因错误安慰而错过就诊时机。
    数据全程本地 SQLite 存储，不上传任何云端服务器。
  </div>
</div>
""", unsafe_allow_html=True)

# ----- 系统状态看板 -----
from db_utils import get_db_path, get_db_connection
db_path = get_db_path()
db_exists = os.path.exists(db_path)

# 实时读取数据库统计
record_count = 0
drug_count = 0
task_count = 0
if db_exists:
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # 健康记录数
        try:
            c.execute("SELECT COUNT(*) FROM health_records")
            record_count = c.fetchone()[0]
        except:
            pass

        # 用药计划数
        try:
            c.execute("SELECT COUNT(*) FROM drug_records WHERE is_active=1")
            drug_count = c.fetchone()[0]
        except:
            pass

        # 健康任务数
        try:
            c.execute("SELECT COUNT(*) FROM health_tasks WHERE is_active=1")
            task_count = c.fetchone()[0]
        except:
            pass

        conn.close()
    except:
        pass

from token_manager import get_config, save_token, mask_token, get_token
from coze_api import check_token_status

api_status, api_icon, api_si = "未配置", "⚠️", "si-warn"
api_error_msg = ""
current_token = get_token()
try:
    status = check_token_status()
    if status.get('valid'):
        api_status, api_icon, api_si = "已连接", "✅", "si-ok"
    else:
        api_error_msg = status.get('error', '')
except Exception as e:
    api_error_msg = str(e)

st.markdown(f"""
<div class="status-grid">
  <div class="status-card">
    <div class="status-icon si-ok">✅</div>
    <div class="status-info">
      <div class="num">{record_count}</div>
      <div class="label">健康记录（条）</div>
    </div>
  </div>
  <div class="status-card">
    <div class="status-icon si-info">💊</div>
    <div class="status-info">
      <div class="num">{drug_count}</div>
      <div class="label">用药计划（个）</div>
    </div>
  </div>
  <div class="status-card">
    <div class="status-icon si-brand">🎯</div>
    <div class="status-info">
      <div class="num">{task_count}</div>
      <div class="label">健康任务（个）</div>
    </div>
  </div>
  <div class="status-card">
    <div class="status-icon {api_si}">{api_icon}</div>
    <div class="status-info">
      <div class="num">{api_status}</div>
      <div class="label">Coze AI 接口</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Token 失效时：展示更新入口 ──────────────────────────────────────────
if api_si != "si-ok":
    st.markdown(f"""
    <div style="
        background: #FCEBEB;
        border: 1px solid #F09595;
        border-left: 4px solid #E24B4A;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 13px;
        color: #791F1F;
    ">
        <span style="font-size:18px;">⚠️</span>
        <div>
            <strong>Coze AI 接口未连接</strong>
            {"&nbsp;·&nbsp;" + api_error_msg if api_error_msg else ""}
            &nbsp;·&nbsp; 当前Token：<code style="background:#F7C1C1;padding:2px 6px;border-radius:4px;">{mask_token(current_token)}</code>
            &nbsp;·&nbsp; 展开下方"更新Token"立即修复
        </div>
    </div>
    """, unsafe_allow_html=True)

with st.expander("🔑 更新 Coze API Token（Token过期时点此更新）", expanded=(api_si != "si-ok")):
    cfg = get_config()
    st.markdown(f"""
    <div style="font-size:12px;color:#5F5E5A;margin-bottom:12px;line-height:1.8;">
    <b>当前配置</b><br>
    Token：<code>{mask_token(cfg['token'])}</code>&nbsp;&nbsp;
    Bot ID：<code>{cfg['bot_id']}</code><br>
    <span style="color:#854F0B;">Token保存在项目根目录的 <code>.env</code> 文件中，修改后刷新页面即生效，无需重启。</span>
    </div>
    """, unsafe_allow_html=True)

    with st.form("token_update_form"):
        new_token = st.text_input(
            "粘贴新 Token",
            placeholder="cztei_xxxx 或 pat_xxxx",
            help="在 Coze 控制台 → 个人中心 → 访问令牌 获取，建议选'无过期时间'"
        )
        col1, col2 = st.columns([1, 2])
        with col1:
            submitted = st.form_submit_button("💾 保存并验证", use_container_width=True)
        with col2:
            st.markdown(
                '<span style="font-size:12px;color:#888;line-height:2.5;">保存后自动验证连接，无需手动重启</span>',
                unsafe_allow_html=True
            )

        if submitted:
            if not new_token.strip():
                st.error("Token 不能为空")
            else:
                ok = save_token(new_token.strip())
                if ok:
                    # 热重载：直接改内存中的全局变量让当次校验生效
                    import coze_api as _ca
                    _ca.COZE_API_TOKEN = new_token.strip()
                    test = check_token_status()
                    if test.get('valid'):
                        st.success("✅ Token 已保存，连接验证通过！刷新页面后状态更新。")
                    else:
                        st.warning(f"Token 已保存到 .env，但连接验证失败：{test.get('error', '')}  请确认Token是否正确。")
                else:
                    st.error("保存失败，请检查 .env 文件权限或目录是否有写入权限")

# ----- 核心功能模块（院区卡片风格）-----
st.markdown("""
<div class="section-title">
  <div class="section-title-bar"></div>
  <h2>核心功能模块</h2>
</div>
""", unsafe_allow_html=True)

func_pages = [
    ("pages/1_数据上传.py", "fc-orange", "📋", "REPORT UPLOAD", "检查报告上传",
     "支持导入电子检查报告（Excel/CSV）或手动录入血压、血糖等关键指标。",
     ["Excel导入", "CSV导入", "手动录入"]),
    ("pages/2_网页爬虫.py", "fc-teal", "🧬", "CLINICAL GUIDE", "临床指南爬取",
     "自动爬取最新临床指南与专家共识，支持关键词智能搜索，为用药方案和生活方式提供循证参考。",
     ["最新指南", "关键词搜索", "专家共识"]),
    ("pages/3_分析结果.py", "fc-blue", "🧠", "AI ANALYSIS", "AI 智能解读",
     "基于Coze大模型，客观呈现检查数据与参考范围，结合临床指南提供趋势分析，不出现侥幸性判断语言。",
     ["报告解读", "趋势分析", "药物查询"]),
    ("pages/4_健康问答.py", "fc-purple", "💬", "HEALTH Q&A", "健康问答",
     "直接向 AI 提问健康相关问题，获取客观的健康知识解答，不提供诊断建议。",
     ["健康咨询", "知识问答", "客观解答"]),
    ("pages/5_慢病履历.py", "fc-green", "📝", "HEALTH RECORDS", "慢病履历台账",
     "本地SQLite数据库存储历次检查记录，可视化趋势图，支持CSV/Excel导出，方便就诊时向医生展示。",
     ["本地存储", "趋势图", "导出报表"]),
    ("pages/6_用药提醒.py", "fc-gold", "💊", "MEDICATION ALERT", "用药提醒打卡",
     "设置每日服药计划，打卡记录用药依从性，自动统计连续打卡天数，培养规律用药习惯。",
     ["服药打卡", "依从性统计", "提醒设置"]),
    ("pages/7_健康任务.py", "fc-orange", "🎯", "HEALTH TASKS", "健康任务管理",
     "设定每日健康打卡目标（步数、血压测量、饮水量等），追踪执行进度，支持自定义任务模板。",
     ["每日打卡", "自定义模板", "连续统计"]),
]

# 功能卡片区 CSS：让 page_link 看起来像卡片
st.markdown("""
<style>
/* 功能卡片 form_submit_button：透明覆盖层，让整张卡片可点击 */
#func-card-area {
    background: #F5EFE0;
    border-top: 1px solid #E8D8C0;
    border-bottom: 1px solid #E8D8C0;
    padding: 20px 32px 0 32px;
    margin-bottom: 0;
}
#func-card-area div[data-testid="stForm"] {
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
}
#func-card-area div[data-testid="stFormSubmitButton"] > button {
    all: unset !important;
    display: block !important;
    width: 100% !important;
    height: 100% !important;
    min-height: 200px !important;
    cursor: pointer !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
}
#func-card-area div[data-testid="stFormSubmitButton"]:hover > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
#func-card-area div[data-testid="stFormSubmitButton"]:active > button {
    background: rgba(232,114,42,0.05) !important;
}
/* 功能卡片 HTML 样式 */
.func-card {
    display: flex;
    flex-direction: column;
    background: white;
    border: 1px solid #E8D8C0;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(139,90,30,0.12);
    overflow: hidden;
    padding: 20px;
    min-height: 200px;
    transition: all 0.25s;
    z-index: 1;
}
.func-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(139,90,30,0.16);
    border-color: #E8722A;
}
.func-card-icon {
    font-size: 28px;
    margin-bottom: 8px;
}
.func-card-tag {
    font-size: 9px;
    font-weight: 700;
    color: #E8722A;
    letter-spacing: 1px;
    margin-bottom: 6px;
    font-family: "Courier New", monospace;
}
.func-card-title {
    font-size: 15px;
    font-weight: 700;
    color: #2D1F0A;
    margin-bottom: 8px;
}
.func-card-desc {
    font-size: 12px;
    color: #6B5744;
    line-height: 1.5;
    margin-bottom: 10px;
    flex: 1;
}
.func-card-tags {
    font-size: 11px;
    color: #A08060;
}
.func-card-clickable-bar {
    color: #8B5A1E;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 2px;
    text-align: center;
    padding: 10px 0;
    border-top: 1px dashed #D4C4A0;
}
</style>
""", unsafe_allow_html=True)

# 功能卡片区：用 form_submit_button + CSS 去除按钮样式，实现透明覆盖层
st.markdown('<div id="func-card-area">', unsafe_allow_html=True)

for row in range(0, 6, 3):
    cols = st.columns(3)
    for col_idx in range(3):
        i = row + col_idx
        if i >= len(func_pages):
            break
        page, fc_cls, icon, label_tag, title, desc, tags = func_pages[i]
        with cols[col_idx]:
            with st.form(key=f"func_card_{i}", clear_on_submit=True):
                # HTML 渲染完整卡片外观
                card_html = f"""
                <div class="func-card">
                    <div class="func-card-icon">{icon}</div>
                    <div class="func-card-tag">{label_tag}</div>
                    <div class="func-card-title">{title}</div>
                    <div class="func-card-desc">{desc}</div>
                    <div class="func-card-tags">{" ".join(tags)}</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                # 透明 form_submit_button 覆盖整张卡片，点击设置 query param 跳转
                if st.form_submit_button(label=" ", use_container_width=True):
                    st.query_params["goto"] = page

st.markdown('</div>', unsafe_allow_html=True)

# 功能区与看板之间的灰色横条，写上"了解详情"
st.markdown('<div class="func-card-clickable-bar">了解详情 →</div>', unsafe_allow_html=True)

# ----- 信息看板：最新动态 + 健康常识 -----
st.markdown("""
<div class="section-title">
  <div class="section-title-bar"></div>
  <h2>平台动态 · 健康资讯</h2>
  <span class="sub">查看更多 →</span>
</div>
<div class="info-board">
  <div class="board-panel">
    <div class="board-panel-header">
      <span>📢</span>
      <h3>平台更新公告</h3>
    </div>
    <div class="board-panel-body">
      <div class="news-item">
        <div class="news-date">04<br>17</div>
        <div class="news-content">
          <div class="title">v2.0 发布：新增慢病履历台账与趋势可视化功能</div>
          <div class="meta">系统更新 · 本次更新增加SQLite本地存储与Plotly趋势图</div>
        </div>
      </div>
      <div class="news-item">
        <div class="news-date">04<br>15</div>
        <div class="news-content">
          <div class="title">药物相互作用查询模块正式上线</div>
          <div class="meta">功能新增 · 联合Coze大模型提供药物风险提示</div>
        </div>
      </div>
      <div class="news-item">
        <div class="news-date">04<br>12</div>
        <div class="news-content">
          <div class="title">AI解读模块更新：严格禁止侥幸性语言输出</div>
          <div class="meta">策略优化 · 系统提示词全面迭代，仅客观呈现数据</div>
        </div>
      </div>
      <div class="news-item">
        <div class="news-date">04<br>07</div>
        <div class="news-content">
          <div class="title">SpiderMind 基础架构完成，临床指南爬取模块就绪</div>
          <div class="meta">里程碑 · 支持关键词搜索与URL指定爬取</div>
        </div>
      </div>
    </div>
  </div>

  <div class="board-panel">
    <div class="board-panel-header">
      <span>🩺</span>
      <h3>慢病管理知识库</h3>
    </div>
    <div class="board-panel-body">
      <div class="news-item">
        <div class="news-date">高血<br>压</div>
        <div class="news-content">
          <div class="title">家庭血压监测：建议每日早晚各测一次，连续7天取平均值</div>
          <div class="meta">《中国高血压防治指南2023》推荐</div>
        </div>
      </div>
      <div class="news-item">
        <div class="news-date">糖<br>尿病</div>
        <div class="news-content">
          <div class="title">HbA1c目标：大多数2型糖尿病患者控制目标为＜7%</div>
          <div class="meta">《中国2型糖尿病防治指南2020》</div>
        </div>
      </div>
      <div class="news-item">
        <div class="news-date">用<br>药</div>
        <div class="news-content">
          <div class="title">切勿自行停药：慢病药物需规律服用，停药前请咨询医生</div>
          <div class="meta">健康提示 · 用药依从性是慢病管理关键</div>
        </div>
      </div>
      <div class="news-item">
        <div class="news-date">就<br>诊</div>
        <div class="news-content">
          <div class="title">携带健康档案：就诊时出示检查趋势图，辅助医生判断病情</div>
          <div class="meta">使用建议 · 慢病履历台账可直接导出给医生</div>
        </div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# 关闭主内容区
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 底栏 ====================
st.markdown("""
<div class="site-footer">
  <div class="footer-inner">
    <div class="footer-grid">
      <div>
        <div class="footer-brand-name">❤ SpiderMind</div>
        <div class="footer-brand-desc">
          基层慢病轻量化智能管理平台<br>
          Chronic Disease Intelligent Management Platform<br><br>
          面向基层医疗机构与慢病患者，提供本地化、<br>
          智能化的健康自管理解决方案。
        </div>
      </div>
      <div>
        <div class="footer-col-title">功能模块</div>
        <span class="footer-link">📋 检查报告上传</span>
        <span class="footer-link">🧬 临床指南爬取</span>
        <span class="footer-link">🧠 AI智能解读</span>
        <span class="footer-link">📝 慢病履历台账</span>
        <span class="footer-link">💊 用药提醒打卡</span>
        <span class="footer-link">🎯 健康任务管理</span>
      </div>
      <div>
        <div class="footer-col-title">设计原则</div>
        <span class="footer-link">🔒 数据本地存储</span>
        <span class="footer-link">🚫 不上传云端</span>
        <span class="footer-link">🎯 客观呈现数据</span>
        <span class="footer-link">✅ 无判断性语言</span>
        <span class="footer-link">🏥 配合就诊使用</span>
      </div>
      <div>
        <div class="footer-col-title">技术支持</div>
        <span class="footer-link">🤖 Coze AI 大模型</span>
        <span class="footer-link">🐍 Python + Streamlit</span>
        <span class="footer-link">🗃️ SQLite 本地数据库</span>
        <span class="footer-link">📊 Plotly 可视化</span>
        <span class="footer-link">🕷️ 智能爬虫引擎</span>
      </div>
    </div>
    <hr class="footer-divider">
    <div class="footer-bottom">
      <div class="footer-copyright">
        © 2026 SpiderMind · 基层慢病轻量化智能管理平台 · 仅供辅助参考，不替代专业医疗建议
      </div>
      <div class="footer-badges">
        <span class="footer-badge">LOCAL STORAGE</span>
        <span class="footer-badge">AI POWERED</span>
        <span class="footer-badge">OPEN SOURCE</span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
