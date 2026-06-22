# -*- coding: utf-8 -*-
"""
SpiderMind - 健康问答对话框
新增功能：用户可以直接提问健康相关问题，AI 给出客观回答
"""
import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from coze_api import CozeAPI

st.set_page_config(
    page_title="健康问答 - SpiderMind",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.hospital_theme import inject_theme, render_nav, render_breadcrumb, render_page_header

inject_theme()
render_nav("健康问答")
render_breadcrumb("健康问答")
render_page_header("💬", "健康问答",
    "直接向 AI 提问健康相关问题，AI 仅客观回答问题，不做诊断")

st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# ===== 设计原则提示 =====
st.markdown("""
<div class="principle-box">
    <strong>🔒 系统设计原则：</strong>
    AI 仅回答健康知识性问题，不提供诊断建议。所有回答仅供参考，
    不替代专业医生的临床诊断。如有健康问题，请咨询您的家庭医生或前往医院就诊。
</div>
""", unsafe_allow_html=True)

# ===== 初始化会话状态 =====
if "qa_history" not in st.session_state:
    st.session_state["qa_history"] = []

if "qa_input" not in st.session_state:
    st.session_state["qa_input"] = ""

# ===== Coze API 初始化 =====
coze = CozeAPI()

# ===== 问题输入区 =====
st.markdown("""
<div class="section-title" style="margin-bottom: 16px;">
    <div class="section-title-bar"></div>
    <h2>提问健康相关问题</h2>
</div>
""", unsafe_allow_html=True)

# 快捷问题示例
st.markdown("**💡 提问示例：**")
example_questions = [
    "空腹血糖 7.2 mmol/L 是什么意思？",
    "高血压患者平时需要注意什么？",
    "糖化血红蛋白 HbA1c 正常值是多少？",
    "服用二甲双胍期间可以喝酒吗？",
    "如何正确理解血脂检查报告？",
]

cols = st.columns(len(example_questions))
for i, eq in enumerate(example_questions):
    with cols[i]:
        if st.button(eq, key=f"eq_{i}", use_container_width=True):
            st.session_state["qa_input"] = eq

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# 问题输入框
user_question = st.text_area(
    "请输入您的问题",
    value=st.session_state.get("qa_input", ""),
    placeholder="例如：我今天测血糖 8.5，是不是很严重？",
    height=100,
    key="question_input"
)

# 提交按钮
col_submit, col_clear = st.columns([3, 1])
with col_submit:
    submit = st.button("🧠 向 AI 提问", use_container_width=True, type="primary", key="btn_ask")
with col_clear:
    if st.button("🗑️ 清空对话", use_container_width=True, key="btn_clear"):
        st.session_state["qa_history"] = []
        st.rerun()

# ===== 处理提问 =====
if submit and user_question:
    # 添加用户问题到历史
    st.session_state["qa_history"].append({
        "role": "user",
        "content": user_question,
        "time": datetime.now().strftime("%H:%M")
    })

    # 调用 Coze API
    with st.spinner("🔬 AI 正在思考，请稍候..."):
        try:
            # 构造健康问答的提示词
            health_qa_prompt = """你是一位专业的健康管理知识问答 AI 助手。
【核心原则】你只能客观回答健康知识性问题，绝对禁止出现以下类型的语言：
- 任何表示"不严重""还好""不用担心""问题不大"的表述
- 任何安慰性语言
- 任何诊断性判断，如"你患有XX病"

【你的职责】
1. 客观回答用户关于健康指标、疾病知识、用药常识的问题
2. 引用权威指南或医学共识（如适用）
3. 如问题涉及诊断，必须说明"请咨询医生"
4. 回答要通俗易懂，但保持医学准确性

用户问题：""" + user_question

            result = coze.analyze_report(health_qa_prompt, analysis_type='report')

            if result.get('success'):
                ai_answer = result.get('data', {}).get('analysis', result.get('raw', '暂无回答'))
            else:
                ai_answer = f"抱歉，AI 服务暂时无法回答（{result.get('error', '未知错误')}），请稍后再试或重新描述问题。"

        except Exception as e:
            ai_answer = f"系统错误：{str(e)}，请检查 Coze API 配置。"

    # 添加 AI 回答到历史
    st.session_state["qa_history"].append({
        "role": "assistant",
        "content": ai_answer,
        "time": datetime.now().strftime("%H:%M")
    })

    # 清空输入框
    st.session_state["qa_input"] = ""
    st.rerun()

# ===== 对话历史显示 =====
if st.session_state["qa_history"]:
    st.markdown("""
    <div class="section-title" style="margin-top: 24px; margin-bottom: 16px;">
        <div class="section-title-bar"></div>
        <h2>对话历史</h2>
    </div>
    """, unsafe_allow_html=True)

    for i, msg in enumerate(st.session_state["qa_history"]):
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="background: #E3F2FD; border: 1px solid #90CAF9; border-radius: 10px;
                padding: 12px 16px; margin-bottom: 12px; margin-left: 20%;">
                <div style="font-size: 11px; color: #1565C0; margin-bottom: 6px;">👤 您提问于 {msg["time"]}</div>
                <div style="font-size: 14px; color: #1a1a1a; line-height: 1.6;">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: #FDFAF5; border: 1px solid #E8D8C0; border-radius: 10px;
                padding: 12px 16px; margin-bottom: 12px; margin-right: 20%;">
                <div style="font-size: 11px; color: #C85A1E; margin-bottom: 6px;">🧠 AI 回答于 {msg["time"]}</div>
                <div style="font-size: 14px; color: #2D1F0A; line-height: 1.8;">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

    # 导出对话记录按钮
    st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
    if st.button("📥 导出对话记录 (TXT)", use_container_width=True, key="btn_export_qa"):
        txt_content = f"SpiderMind 健康问答记录\n导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*50}\n\n"
        for msg in st.session_state["qa_history"]:
            role_label = "提问" if msg["role"] == "user" else "AI回答"
            txt_content += f"[{msg['time']}] {role_label}：\n{msg['content']}\n\n{'-'*50}\n\n"

        st.download_button(
            label="⬇️ 下载对话记录",
            data=txt_content.encode('utf-8'),
            file_name=f"SpiderMind_QA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
        st.success("✅ 对话记录已生成，点击上方按钮下载")

else:
    st.info("💡 还没有对话记录。在上方输入问题，开始与 AI 健康助手对话吧！")

# ===== 底部导航 =====
st.markdown("""
<div class="sub-footer">
    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
        <span style="color: #C85A1E; font-size: 13px; cursor: pointer;"
              onclick="window.location.href='pages/3_分析结果.py'">← AI 智能解读</span>
        <span style="color: #C85A1E; font-size: 13px; cursor: pointer;"
              onclick="window.location.href='pages/5_慢病履历.py'">慢病履历台账 →</span>
    </div>
    SpiderMind · 基层慢病轻量化智能管理平台 · 仅供辅助参考，不替代专业医疗建议
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
