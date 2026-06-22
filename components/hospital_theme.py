# -*- coding: utf-8 -*-
"""
components.hospital_theme
医院风格主题组件 - 为 SpiderMind 子页面提供统一的页面框架
"""

import streamlit as st
import datetime
import os


def inject_theme():
    """注入统一的医院风格主题 CSS"""
    st.markdown("""
<style>
/* ===== 字体引入 ===== */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&display=swap');

/* ===== 全局变量 - 广医一院风格 ===== */
:root {
    --brand:       #C85A1E;
    --brand-dark:  #9C3F10;
    --brand-light: #E8722A;
    --gold:        #D4A94A;
    --cream:       #F9F3EA;
    --cream2:      #FDF6EC;
    --warm-white:  #FFFDF8;
    --ink:         #2D1F0A;
    --ink-mid:     #5C4A2A;
    --ink-muted:   #9A8060;
    --border:      #E8D8C0;
    --border-warm: #D4B896;
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

/* ===== 面包屑导航 ===== */
.breadcrumb-bar {
    background: white;
    border-bottom: 1px solid var(--border);
    padding: 0;
}
.breadcrumb-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 32px;
    display: flex;
    align-items: center;
    gap: 8px;
    height: 42px;
}
.breadcrumb-item {
    font-size: 12px;
    color: var(--ink-muted);
    cursor: pointer;
    transition: color 0.2s;
}
.breadcrumb-item:hover { color: var(--brand); }
.breadcrumb-sep {
    color: var(--border-warm);
    font-size: 12px;
}
.breadcrumb-item.current {
    color: var(--ink);
    font-weight: 600;
}

/* ===== 页面头部 ===== */
.page-header {
    background: linear-gradient(135deg, #1A0A00 0%, #2D1500 40%, #4A2000 100%);
    padding: 0;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 600px 400px at 70% 50%, rgba(200,90,30,0.2) 0%, transparent 60%);
}
.page-header-inner {
    position: relative;
    z-index: 2;
    max-width: 1280px;
    margin: 0 auto;
    padding: 36px 32px;
    display: flex;
    align-items: center;
    gap: 24px;
}
.page-header-icon {
    font-size: 56px;
    flex-shrink: 0;
    filter: drop-shadow(0 4px 16px rgba(0,0,0,0.4));
}
.page-header-info { flex: 1; }
.page-header-title {
    font-size: 28px;
    font-weight: 700;
    color: white;
    font-family: 'Noto Serif SC', serif;
    line-height: 1.2;
    margin-bottom: 8px;
    text-shadow: 0 2px 12px rgba(0,0,0,0.4);
}
.page-header-subtitle {
    font-size: 13px;
    color: rgba(255,255,255,0.6);
    line-height: 1.6;
}
.page-header-badge {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(200,90,30,0.4);
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
    backdrop-filter: blur(8px);
}
.page-header-badge-icon { font-size: 32px; line-height: 1; margin-bottom: 4px; }
.page-header-badge-text { color: rgba(255,255,255,0.6); font-size: 11px; }

/* ===== 主内容区 ===== */
.page-content {
    max-width: 1280px;
    margin: 0 auto;
    padding: 28px 32px;
}

/* ===== 通用卡片 ===== */
.card {
    background: white;
    border-radius: 12px;
    border: 1px solid var(--border);
    box-shadow: 0 2px 12px var(--shadow);
    overflow: hidden;
}
.card-header {
    background: linear-gradient(90deg, #2D1500, #4A2800);
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.card-header h3 {
    color: white;
    font-size: 14px;
    margin: 0;
    font-weight: 600;
    letter-spacing: 1px;
}
.card-body { padding: 20px; }

/* ===== 按钮样式 ===== */
.btn-primary {
    background: linear-gradient(135deg, var(--brand), var(--brand-dark));
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 1px;
}
.btn-primary:hover {
    background: linear-gradient(135deg, var(--brand-light), var(--brand));
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(200,90,30,0.3);
}

/* ===== 表单样式 ===== */
.stTextInput > label, .stTextArea > label, .stSelectbox > label {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--ink-mid) !important;
    letter-spacing: 0.5px !important;
}

/* ===== 分隔线 ===== */
.divider {
    border: none;
    border-top: 1px dashed var(--border);
    margin: 16px 0;
}

/* ===== 底栏 ===== */
.site-footer {
    background: #1A0A00;
    padding: 28px 0 18px;
    margin-top: 40px;
    border-top: 3px solid var(--brand);
}
.footer-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 32px;
}
.footer-inner .copyright {
    color: rgba(255,255,255,0.25);
    font-size: 11px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


def render_nav(current_page: str = ""):
    """渲染顶部导航栏

    Args:
        current_page: 当前页面标识，用于高亮当前项
    """
    today = datetime.date.today()
    date_str = today.strftime("%Y年%m月%d日")
    weekdays = ["周一","周二","周三","周四","周五","周六","周日"]
    week_str = weekdays[today.weekday()]

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

    nav_links_html = ""
    for label, path in nav_pages:
        is_active = "active" if path == current_page or (
            current_page == "main.py" and path == "main.py"
        ) or (
            current_page in path
        ) else ""
        nav_links_html += f'<a href="?nav_goto={path}" class="nav-link {is_active}">{label}</a>'

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

    # 处理导航跳转
    if "nav_goto" in st.query_params:
        target = st.query_params["nav_goto"]
        del st.query_params["nav_goto"]
        st.session_state["_nav_target"] = target

    if "_nav_target" in st.session_state and st.session_state["_nav_target"]:
        target = st.session_state.pop("_nav_target")
        st.switch_page(target)


def render_breadcrumb(current: str = ""):
    """渲染面包屑导航

    Args:
        current: 当前页面名称（字符串），会自动生成：首页 > 当前页面
               也支持传入 items 列表: [("首页", "main.py"), ("报告上传", None)]
    """
    # 如果是字符串，自动构建标准面包屑
    if isinstance(current, str):
        items = [("首页", "main.py"), (current, None)]
    else:
        items = current

    html = '<div class="breadcrumb-bar"><div class="breadcrumb-inner">'
    for i, item in enumerate(items):
        if isinstance(item, tuple):
            label, href = item
        else:
            label, href = item, None
        if i > 0:
            html += '<span class="breadcrumb-sep">›</span>'
        if href:
            html += f'<span class="breadcrumb-item" onclick="window.location.href=\'?nav_goto={href}\'">{label}</span>'
        else:
            html += f'<span class="breadcrumb-item current">{label}</span>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_page_header(icon: str, title: str, subtitle: str, badge_text: str = ""):
    """渲染页面头部（Banner）

    Args:
        icon: 大 emoji 图标
        title: 页面标题
        subtitle: 副标题描述
        badge_text: 右侧徽章文字（可选）
    """
    badge_html = ""
    if badge_text:
        badge_html = f"""
    <div class="page-header-badge">
      <div class="page-header-badge-icon">🏥</div>
      <div class="page-header-badge-text">{badge_text}</div>
    </div>
"""

    st.markdown(f"""
<div class="page-header">
  <div class="page-header-inner">
    <div class="page-header-icon">{icon}</div>
    <div class="page-header-info">
      <div class="page-header-title">{title}</div>
      <div class="page-header-subtitle">{subtitle}</div>
    </div>
    {badge_html}
  </div>
</div>
""", unsafe_allow_html=True)


def render_footer():
    """渲染底栏"""
    st.markdown("""
<div class="site-footer">
  <div class="footer-inner">
    <div class="copyright">
      © 2026 SpiderMind · 基层慢病轻量化智能管理平台 · 仅供辅助参考，不替代专业医疗建议
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
