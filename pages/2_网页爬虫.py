"""
SpiderMind - 临床指南爬虫页（医院官网风格）
"""
import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coze_api import CozeCrawler, get_clinical_guidelines

st.set_page_config(
    page_title="临床指南 - SpiderMind",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

try:
    from components.hospital_theme import inject_theme, render_nav, render_breadcrumb, render_page_header
    inject_theme()
    render_nav("2_网页爬虫")
    render_breadcrumb("临床指南爬取")
    render_page_header("🧬", "临床指南 & 专家共识",
                       "输入疾病关键词或指定URL，自动从权威医学网站采集最新临床指南与专家共识")
except Exception:
    pass

st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# 初始化爬虫 - 去掉缓存确保每次使用最新配置
crawler = CozeCrawler()

# 两个入口：URL指定 + 关键词智能爬取
tab1, tab2 = st.tabs(["🔗 URL指定爬取", "🔍 关键词智能爬取"])

with tab1:
    st.subheader("指定URL爬取")
    url_input = st.text_input(
        "输入医学文献URL",
        placeholder="例如：https://www.nhc.gov.cn/...",
        help="支持国家卫健委、中华医学会、丁香园等权威医学网站"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        crawl_btn = st.button("🚀 开始爬取", use_container_width=True)
    with col2:
        st.info("💡 支持网页正文提取，自动过滤广告和无关内容")

    if crawl_btn and url_input:
        if not url_input.startswith(('http://', 'https://')):
            url_input = 'https://' + url_input

        with st.spinner("正在爬取..."):
            result = crawler.crawl_url(url_input)

        if result.get('success'):
            content = result.get('content', '')
            is_dynamic = '【提示】' in content and ('JavaScript' in content or '元数据' in content)

            if is_dynamic:
                st.warning("⚠️ 该页面正文通过 JavaScript 动态加载，已提取页面元数据")
            else:
                st.success("✅ 爬取成功！")

            col_meta, col_content = st.columns([1, 3])
            with col_meta:
                st.markdown("**📄 基本信息**")
                st.write(f"标题：{result.get('title', 'N/A')}")
                st.write(f"来源：{result.get('source', 'N/A')}")
                st.write(f"字数：{len(content)} 字")

            with col_content:
                if is_dynamic:
                    st.markdown("**📝 页面元数据（原文需浏览器查看）**")
                else:
                    st.markdown("**📝 正文内容**")
                st.text_area("内容预览", content, height=400, disabled=True)

            # 保存到本地
            save_path = crawler.save_content(result)
            st.session_state['last_crawled'] = result
            st.session_state['last_save_path'] = save_path
            st.session_state['last_content_type'] = 'guideline'
        else:
            st.error(f"❌ 爬取失败：{result.get('error', '未知错误')}")

with tab2:
    st.subheader("关键词智能爬取")
    keyword = st.text_input(
        "输入疾病/指南关键词",
        placeholder="例如：慢性病管理指南、糖尿病、基层高血压...",
        help="输入关键词后，系统调用Coze AI智能分析最优爬取策略"
    )

    disease_presets = st.multiselect(
        "常用慢病指南快速选择",
        [
            "中国2型糖尿病防治指南",
            "中国高血压防治指南",
            "慢性阻塞性肺疾病防治指南",
            "中国血脂异常防治指南",
            "基层糖尿病防治指南",
            "慢性心力衰竭防治指南",
            "慢性肾脏病防治指南",
            "痛风及高尿酸血症防治指南"
        ],
        default=[]
    )

    crawl_strategy = st.selectbox(
        "爬取策略",
        ["自动最优（Coze AI推荐）", "广泛覆盖（多源爬取）", "精准聚焦（权威优先）"]
    )

    max_results = st.slider("爬取数量", min_value=5, max_value=20, value=10, step=5,
        help="选择要爬取的搜索结果数量（越多越全面，但耗时更长）")

    if st.button("🔍 智能爬取", use_container_width=True):
        if not keyword and not disease_presets:
            st.warning("请输入关键词或选择预设疾病")
        else:
            query = keyword or "、".join(disease_presets)
            st.info(f"🎯 搜索关键词：{query} ｜ 目标数量：{max_results} 条")

            progress_bar = st.progress(0)
            status_text = st.empty()

            with st.spinner("正在通过搜索引擎获取真实医学资料..."):
                guidelines = get_clinical_guidelines(query, max_results=max_results)

            progress_bar.empty()
            status_text.empty()

            if guidelines:
                # 统计
                trusted_count = sum(1 for g in guidelines if g.get('trusted'))
                st.success(f"✅ 成功获取 {len(guidelines)} 条资料（权威来源 {trusted_count} 条）")

                for i, g in enumerate(guidelines):
                    trusted_badge = "🏥 " if g.get('trusted') else "🌐 "
                    title = g.get('title', f'资料{i+1}')
                    # 截断过长标题
                    display_title = title[:60] + "..." if len(title) > 60 else title

                    with st.expander(f"{trusted_badge}{display_title}", expanded=i == 0):
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.markdown(f"**来源：** `{g.get('source', '未知')}`")
                            st.markdown(f"**字数：** {g.get('length', 0)} 字")
                            if g.get('trusted'):
                                st.markdown("🛡️ **权威来源**")
                        with col2:
                            st.markdown(f"**摘要：**\n> {g.get('summary', '暂无摘要')}")

                        if g.get('url'):
                            st.markdown(f"[🔗 查看原文]({g['url']})")

                        if g.get('content'):
                            with st.expander("📄 完整内容", expanded=False):
                                st.text_area("内容", g['content'], height=300, disabled=True, key=f"gcontent_{i}")
            else:
                st.warning("未找到相关指南，请尝试更换关键词或检查网络连接")

# 底部统计
st.divider()
col_stat1, col_stat2, col_stat3 = st.columns(3)
with col_stat1:
    st.metric("🗂️ 已爬取文档", len(st.session_state.get('crawled_docs', [])), help="本次会话累计爬取数量")
with col_stat2:
    st.metric("⏱️ 最后爬取时间", st.session_state.get('last_crawl_time', '—'))
with col_stat3:
    st.metric("📊 Coze API状态", "✅ 已连接")

if st.session_state.get('last_crawled'):
    st.divider()
    if st.button("📤 将此内容送往AI分析", use_container_width=False):
        st.session_state['analysis_source'] = 'guideline'
        st.success("已切换到「分析结果」页面进行处理")
        st.switch_page("pages/3_分析结果.py")
