"""
SpiderMind - Coze API 对接模块
支持：检查报告分析 / 临床指南分析 / 药物相互作用查询 / 智能爬虫
设计原则：AI只呈现客观数据，禁止"不严重/还好/不用担心"等侥幸性判断语言
"""
import requests
import json
import time
import re
import os
from typing import Dict, Any, Optional, List
from token_manager import get_config

# ===== Coze API 配置（从 .env 文件动态读取，修改 .env 后重启即生效）=====
def _load_config():
    cfg = get_config()
    return cfg["token"], cfg["bot_id"]

COZE_API_TOKEN, COZE_BOT_ID = _load_config()

COZE_API_BASE = "https://api.coze.cn/v1"

# ===== 系统提示词（客观化、安全边界） =====
SYSTEM_PROMPT_REPORT = """你是一位专业的基层慢病健康管理AI助手。
【核心原则】你只能客观呈现检测数据和参考范围，**绝对禁止**出现以下类型的语言：
- 任何表示"不严重""还好""不用担心""问题不大""不用担心"的表述
- 任何安慰性语言，如"没什么大问题""基本正常""问题不大"
- 任何诊断性判断，如"你患有XX病""这是XX的表现"

【你的职责】
1. 从报告单中提取关键医学指标及其数值
2. 将每个指标与其参考范围对照，用客观数据呈现
3. 用通俗易懂的语言解释医学术语（不代替医生做判断）
4. 如指标超出参考范围，只能说"该指标超出参考范围，建议咨询医生"，绝对不能加安慰语

【输出格式要求】
请严格按以下JSON格式输出，不要输出JSON以外的内容：
{
  "indicators": {
    "指标名": "数值",
    ...
  },
  "items": [
    {
      "indicator": "指标名",
      "value": "数值",
      "unit": "单位",
      "reference": "参考范围",
      "note": "客观描述，不做任何判断性语言"
    }
  ],
  "analysis": "综合解读（仅客观描述数据，不做判断）"
}"""

SYSTEM_PROMPT_GUIDELINE = """你是一位专业的临床指南分析AI助手，专门帮助基层医疗工作者快速理解临床指南要点。
【你的职责】
1. 总结指南的核心推荐意见
2. 评估指南在基层医疗机构实施的可执行性
3. 识别关键用药建议、随访要求和禁忌事项
4. 标注基层落地的难点和解决建议

【输出格式】请严格按以下JSON格式输出：
{
  "summary": "指南核心要点总结（3-5条）",
  "key_recommendations": ["推荐1", "推荐2", ...],
  "feasibility": {
    "tech_level": "高/中/低",
    "cost_level": "高/中/低",
    "value": "高/中/低",
    "detail": "详细评估说明"
  },
  "medication_notes": "用药注意事项",
  "followup_notes": "随访要求",
  "contraindications": ["禁忌1", "禁忌2", ...],
  "grassroots_barriers": ["难点1", "难点2", ...],
  "suggestions": "基层落地建议"
}"""

SYSTEM_PROMPT_DRUG_INTERACTION = """你是一位专业的临床药学AI助手。
【你的职责】
1. 客观分析两种药物之间可能存在的相互作用
2. 提示可能的副作用叠加风险
3. 给出用药安全建议

【绝对禁止】
- 绝对禁止给出"可以一起吃"或"不能一起吃"的确定结论
- 只能表述"存在XX相互作用的可能性，请咨询医生"
- 绝对禁止推荐、调整或替代药物

【输出格式】请严格按以下JSON格式输出：
{
  "interaction_level": "高/中/低/未知",
  "mechanism": "相互作用机制说明",
  "risks": ["风险1", "风险2", ...],
  "safety_advice": "用药安全建议（必须包含"请咨询医生"）",
  "note": "补充说明"
}"""

SYSTEM_PROMPT_CRAWLER = """你是一位专业的医学文献爬取策略分析AI。
【你的职责】
根据用户提供的关键词，分析最优的爬取策略，输出推荐的数据源URL和分析思路。
【输出格式】请严格按以下JSON格式输出：
{
  "recommended_sources": ["URL1", "URL2", ...],
  "keywords": ["关键词1", "关键词2", ...],
  "strategy": "爬取策略说明",
  "notes": "注意事项"
}"""


class CozeAPI:
    """Coze API 封装（兼容 coze.cn v3 接口）"""

    SYSTEM_PROMPT_REPORT = SYSTEM_PROMPT_REPORT
    SYSTEM_PROMPT_GUIDELINE = SYSTEM_PROMPT_GUIDELINE
    SYSTEM_PROMPT_DRUG_INTERACTION = SYSTEM_PROMPT_DRUG_INTERACTION

    def __init__(self, api_token: str = None, bot_id: str = None):
        # 每次实例化时重新读取配置，确保 .env 修改后无需重启即可生效
        cfg = get_config()
        self.api_token = api_token or cfg["token"]
        self.bot_id = bot_id or cfg["bot_id"]
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _call_coze(self, message: str, system_prompt: str = "", timeout: int = 120) -> Dict[str, Any]:
        """调用 Coze API（v3 流式接口，非流式模式）"""
        # coze.cn 用 v3 接口
        url = "https://api.coze.cn/v3/chat"
        full_message = f"{system_prompt}\n\n{message}" if system_prompt else message
        payload = {
            "bot_id": self.bot_id,
            "user_id": "spidermind_user",
            "stream": False,
            "additional_messages": [
                {"role": "user", "content": full_message, "content_type": "text", "type": "question"}
            ]
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 0:
                return {"success": False, "error": f"API错误：code={data.get('code')}，{data.get('msg', '')}"}

            chat_id = data["data"]["id"]
            conversation_id = data["data"]["conversation_id"]

            # 轮询获取结果（最多等 timeout 秒）
            for attempt in range(timeout // 3):
                time.sleep(3)
                retrieve_url = f"https://api.coze.cn/v3/chat/retrieve"
                retrieve_resp = requests.get(
                    retrieve_url,
                    headers=self.headers,
                    params={"chat_id": chat_id, "conversation_id": conversation_id},
                    timeout=15
                )
                retrieve_data = retrieve_resp.json()
                status = retrieve_data.get("data", {}).get("status", "")

                if status == "completed":
                    messages_resp = requests.get(
                        "https://api.coze.cn/v3/chat/message/list",
                        headers=self.headers,
                        params={"chat_id": chat_id, "conversation_id": conversation_id},
                        timeout=15
                    )
                    messages_data = messages_resp.json()
                    for msg in messages_data.get("data", []):
                        if msg.get("role") == "assistant" and msg.get("type") == "answer":
                            content = msg.get("content", "")
                            # 清理 markdown 代码块包裹
                            content_clean = content.strip()
                            if content_clean.startswith("```"):
                                content_clean = re.sub(r'^```[a-z]*\n?', '', content_clean)
                                content_clean = re.sub(r'\n?```$', '', content_clean)
                            try:
                                result = json.loads(content_clean)
                                return {"success": True, "data": result, "raw": content}
                            except json.JSONDecodeError:
                                return {"success": True, "data": {"analysis": content}, "raw": content}
                    return {"success": True, "data": {"analysis": "未获取到有效回复"}, "raw": ""}

                elif status in ("failed", "canceled"):
                    last_error = retrieve_data.get("data", {}).get("last_error", {})
                    err_code = last_error.get("code", 0)
                    err_msg = last_error.get("msg", "")
                    if err_code == 4028:
                        return {"success": False, "error": "Coze 免费额度已用完（错误码 4028）。请登录 coze.cn 查看积分余额，或升级付费版。\n每月1号自动重置免费额度。"}
                    elif err_code == 4101:
                        return {"success": False, "error": "Token 已过期（错误码 4101），请重新生成 Token"}
                    elif err_code:
                        return {"success": False, "error": f"Coze错误 [{err_code}]：{err_msg}"}
                    else:
                        return {"success": False, "error": f"对话状态：{status}"}

            return {"success": False, "error": "轮询超时，请稍后重试"}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "请求超时，请检查网络连接"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"网络请求错误：{str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"未知错误：{str(e)}"}

    def analyze_report(self, content: str, analysis_type: str = "report") -> Dict[str, Any]:
        """分析报告单"""
        system_prompt = SYSTEM_PROMPT_REPORT if analysis_type == "report" else SYSTEM_PROMPT_GUIDELINE
        return self._call_coze(content, system_prompt)

    def analyze_guideline(self, content: str) -> Dict[str, Any]:
        """分析临床指南"""
        return self._call_coze(content, SYSTEM_PROMPT_GUIDELINE)

    def query_drug_interaction(self, drug1: str, drug2: str) -> Dict[str, Any]:
        """查询药物相互作用"""
        message = f"请分析以下两种药物之间的相互作用：\n药物1：{drug1}\n药物2：{drug2}"
        return self._call_coze(message, SYSTEM_PROMPT_DRUG_INTERACTION, timeout=60)

    def analyze_crawl_strategy(self, keyword: str) -> Dict[str, Any]:
        """分析爬取策略"""
        return self._call_coze(keyword, SYSTEM_PROMPT_CRAWLER, timeout=60)


class CozeCrawler:
    """基于搜索引擎的临床指南爬取引擎"""

    # 权威医学域名白名单（优先展示）
    TRUSTED_DOMAINS = [
        "nhc.gov.cn", "cmacp.org.cn", "cma.org.cn",
        "dxy.cn", "medsci.cn", "cnki.net",
        "pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov",
        "who.int", "guideline.gov",
        "bmj.com", "nejm.org", "thelancet.com",
        "chkd.cnki.net", "wanfangdata.com.cn",
        "yiigle.com", "medlive.cn",
    ]

    def __init__(self):
        self.api = CozeAPI()
        self.session_storage = []

    def _is_trusted(self, url: str) -> bool:
        """检查URL是否来自权威医学网站"""
        return any(domain in url.lower() for domain in self.TRUSTED_DOMAINS)

    def _search_bing(self, keyword: str, max_results: int = 15) -> List[Dict[str, Any]]:
        """
        使用 Bing 搜索获取真实搜索结果（国内网络友好）
        返回包含 title, url, snippet 的列表
        """
        results = []
        try:
            # 搜索查询：只追加"指南"（避免"专家共识"导致分词错误）
            search_query = keyword
            if "指南" not in keyword:
                search_query = f"{keyword} 指南"
            from urllib.parse import quote
            encoded_query = quote(search_query)
            bing_url = f"https://www.bing.com/search?q={encoded_query}&count={max_results * 2}"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": "https://www.bing.com/",
            }

            resp = requests.get(bing_url, headers=headers, timeout=20)
            resp.encoding = 'utf-8'
            html = resp.text

            import re

            # 方法1: 找到所有 b_algo 的位置，手动切片（避免嵌套 li 问题）
            indices = [m.start() for m in re.finditer(r'<li class="b_algo"', html)]

            for i, idx in enumerate(indices[:max_results * 2]):
                end_idx = indices[i+1] if i+1 < len(indices) else idx + 8000
                block = html[idx:end_idx]

                # 提取标题和URL
                url_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*h="[^"]*"[^>]*>(.*?)</a>', block, re.DOTALL)
                if not url_match:
                    url_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.DOTALL)

                if url_match:
                    url = url_match.group(1)
                    title = re.sub(r'<[^>]+>', '', url_match.group(2)).strip()

                    # 提取摘要
                    snippet = ""
                    snippet_match = re.search(r'<p[^>]*>(.*?)</p>', block, re.DOTALL)
                    if snippet_match:
                        snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()

                    if title and len(title) > 3 and url.startswith('http'):
                        # 过滤 Bing 自身和重复
                        if 'bing.com' not in url and 'microsoft.com' not in url:
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet,
                                "source": self._extract_domain(url),
                                "trusted": self._is_trusted(url)
                            })

                if len(results) >= max_results:
                    break

            # 方法2: 备用 - 如果没解析到，直接搜所有链接
            if not results:
                links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
                seen = set()
                for url, title_html in links:
                    if url in seen or 'bing.com' in url or 'microsoft.com' in url:
                        continue
                    seen.add(url)
                    title = re.sub(r'<[^>]+>', '', title_html).strip()
                    if title and len(title) > 5:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": "",
                            "source": self._extract_domain(url),
                            "trusted": self._is_trusted(url)
                        })
                    if len(results) >= max_results:
                        break

        except Exception as e:
            print(f"Bing搜索失败: {e}")
            return self._fallback_search(keyword)

        return results

    def _fallback_search(self, keyword: str) -> List[Dict[str, Any]]:
        """降级方案：用 Coze AI 生成搜索 URL"""
        strategy = self.api.analyze_crawl_strategy(keyword)
        urls = []
        if strategy.get("success"):
            for url in strategy.get("data", {}).get("recommended_sources", [])[:10]:
                urls.append({
                    "title": f"相关资源",
                    "url": url,
                    "snippet": "",
                    "source": self._extract_domain(url),
                    "trusted": self._is_trusted(url)
                })
        return urls

    def _extract_domain(self, url: str) -> str:
        """从URL提取域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url

    def crawl_url(self, url: str) -> Dict[str, Any]:
        """爬取指定URL，提取正文内容"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc

            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                }
                resp = requests.get(url, headers=headers, timeout=20, allow_redirects=True)

                # 检测是否为 PDF / 二进制文件
                content_type = resp.headers.get('Content-Type', '')
                raw_head = resp.content[:8] if resp.content else b''

                if 'application/pdf' in content_type or raw_head.startswith(b'%PDF'):
                    return {
                        "success": False,
                        "error": "该链接指向PDF文件，无法直接提取正文。请使用「报告上传」页面的拍照上传或手动录入功能导入PDF内容。",
                        "url": url,
                        "content_type": content_type,
                    }

                # 检测其他非文本类型
                if any(ct in content_type for ct in ['image/', 'video/', 'audio/', 'application/octet-stream']):
                    return {
                        "success": False,
                        "error": f"该链接为{content_type}类型文件（非网页），无法提取正文。请上传文件到对应功能页面。",
                        "url": url,
                    }

                resp.encoding = resp.apparent_encoding or 'utf-8'
                html = resp.text

                # 使用更智能的正文提取
                content = self._extract_content(html, url)
                title = self._extract_title(html)

                # 生成摘要（前200字）
                summary = content[:300] + "..." if len(content) > 300 else content

                return {
                    "success": True,
                    "url": url,
                    "domain": domain,
                    "title": title,
                    "source": domain,
                    "content": content[:8000],  # 限制长度
                    "summary": summary,
                    "length": len(content),
                    "trusted": self._is_trusted(url)
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"网页爬取失败：{str(e)}",
                    "url": url
                }

        except Exception as e:
            return {"success": False, "error": str(e), "url": url}

    def _extract_title(self, html: str) -> str:
        """提取页面标题"""
        # 尝试多种标题提取方式
        patterns = [
            r'<h1[^>]*>(.*?)</h1>',
            r'<title[^>]*>(.*?)</title>',
            r'<meta[^>]*name=["\']title["\'][^>]*content=["\']([^"\']+)["\']',
            r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                if title and len(title) > 3:
                    return title
        return "未获取标题"

    def _extract_content(self, html: str, url: str) -> str:
        """智能提取正文内容"""
        # 0. 检测 JS 动态加载页面（正文通过 AJAX 加载）
        loading_markers = ['全文加载中', '内容加载中', '加载中...', '正在加载', 'Loading...']
        is_dynamic = any(marker in html for marker in loading_markers)

        # 1. 去除 script/style/nav/footer/header/aside 等标签及其内容
        html_clean = html
        for tag in ['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']:
            html_clean = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', ' ', html_clean, flags=re.DOTALL | re.IGNORECASE)

        # 2. 去除常见广告和无关区域
        ad_patterns = [
            r'<div[^>]*class=["\'][^"\']*(?:ad|banner|popup|sidebar|comment|related|recommend|share|toolbar|breadcrumb)[^"\']*["\'][^>]*>.*?</div>',
            r'<section[^>]*class=["\'][^"\']*(?:ad|banner|comment)[^"\']*["\'][^>]*>.*?</section>',
        ]
        for pattern in ad_patterns:
            html_clean = re.sub(pattern, ' ', html_clean, flags=re.DOTALL | re.IGNORECASE)

        # 3. 尝试提取 article/main/div.content 等正文区域
        content = ""
        article_patterns = [
            r'<article[^>]*>(.*?)</article>',
            r'<main[^>]*>(.*?)</main>',
            r'<div[^>]*class=["\'][^"\']*(?:content|article|post|entry|main-text|detail)[^"\']*["\'][^>]*>(.*?)</div>',
            r'<div[^>]*id=["\'][^"\']*(?:content|article|post|main)[^"\']*["\'][^>]*>(.*?)</div>',
            r'<section[^>]*class=["\'][^"\']*(?:content|article)[^"\']*["\'][^>]*>(.*?)</section>',
        ]
        for pattern in article_patterns:
            match = re.search(pattern, html_clean, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1)
                break

        # 4. 如果没找到正文区域，用整个 body
        if not content:
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html_clean, re.DOTALL | re.IGNORECASE)
            if body_match:
                content = body_match.group(1)
            else:
                content = html_clean

        # 5. 去除所有 HTML 标签
        content = re.sub(r'<[^>]+>', ' ', content)

        # 6. 清理空白和特殊字符
        content = re.sub(r'\s+', ' ', content).strip()
        content = re.sub(r'[\n\r\t]+', '\n', content)

        # 7. 去除常见垃圾文本
        junk_patterns = [
            r'版权所有.*?保留所有权利',
            r'ICP备\d+号',
            r'京公网安备\d+号',
            r'联系我们.*?|关于我们.*?|免责声明.*?',
            r'分享到.*?|收藏.*?|打印.*?',
            r'上一篇.*?下一篇.*?',
            r'相关阅读.*?|推荐阅读.*?',
            r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+来源：',
        ]
        for pattern in junk_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)

        content = content.strip()

        # 8. 如果是动态加载页面且正文为空/极短，尝试提取页面元数据
        if is_dynamic and len(content) < 100:
            meta_parts = []

            # 提取标题
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
            if title_match:
                meta_parts.append(f"【标题】{re.sub(r'<[^>]+>', '', title_match.group(1)).strip()}")

            # 提取 meta description
            desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if desc_match:
                meta_parts.append(f"【摘要】{desc_match.group(1).strip()}")

            # 提取 meta keywords
            kw_match = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if kw_match:
                meta_parts.append(f"【关键词】{kw_match.group(1).strip()}")

            # 提取作者信息
            author_match = re.search(r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if author_match:
                meta_parts.append(f"【作者】{author_match.group(1).strip()}")

            # 提取 Open Graph 描述
            og_desc = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if og_desc and (not desc_match or og_desc.group(1) != desc_match.group(1)):
                meta_parts.append(f"【描述】{og_desc.group(1).strip()}")

            # 提取 JSON-LD 结构化数据中的摘要
            jsonld_match = re.search(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
            if jsonld_match:
                try:
                    import json
                    ld_data = json.loads(jsonld_match.group(1))
                    if isinstance(ld_data, dict):
                        if 'description' in ld_data and ld_data['description']:
                            meta_parts.append(f"【结构化摘要】{ld_data['description']}")
                        if 'abstract' in ld_data and ld_data['abstract']:
                            meta_parts.append(f"【结构化摘要】{ld_data['abstract']}")
                except:
                    pass

            # 提取 eprints 格式的学术元数据（中华医学期刊等）
            eprints_title = re.search(r'<meta[^>]*name=["\']eprints\.title["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if eprints_title:
                meta_parts.append(f"【标题】{eprints_title.group(1).strip()}")

            eprints_authors = re.findall(r'<meta[^>]*name=["\']eprints\.creators_name["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if eprints_authors:
                meta_parts.append(f"【作者】{'、'.join(eprints_authors)}")

            eprints_date = re.search(r'<meta[^>]*name=["\']eprints\.date["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if eprints_date:
                meta_parts.append(f"【发表日期】{eprints_date.group(1).strip()}")

            eprints_abstract = re.search(r'<meta[^>]*name=["\']eprints\.abstract["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if eprints_abstract:
                # 清理 HTML 实体
                abstract_text = eprints_abstract.group(1).strip()
                abstract_text = abstract_text.replace('&#x27;', "'")
                meta_parts.append(f"【摘要】{abstract_text}")

            eprints_keywords = re.search(r'<meta[^>]*name=["\']eprints\.keywords["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if eprints_keywords:
                meta_parts.append(f"【关键词】{eprints_keywords.group(1).strip()}")

            if meta_parts:
                meta_parts.insert(0, "【提示】该页面正文需浏览器渲染加载，以下为页面元数据：")
                return '\n\n'.join(meta_parts)
            else:
                return "【提示】该页面正文通过 JavaScript 动态加载，无法直接提取。请尝试在浏览器中打开原文查看。"

        return content

    def save_content(self, result: Dict[str, Any]) -> str:
        """保存爬取内容到本地"""
        save_dir = os.path.join(os.path.dirname(__file__), "data", "guidelines")
        os.makedirs(save_dir, exist_ok=True)

        from datetime import datetime
        filename = f"guideline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(save_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        self.session_storage.append(result)
        return filepath

    def search_guidelines(self, keyword: str, max_results: int = 15) -> List[Dict[str, Any]]:
        """
        搜索指南：使用 DuckDuckGo 搜索引擎获取真实结果
        返回包含 title, url, snippet, content 的完整列表
        """
        # 1. 搜索获取结果列表
        search_results = self._search_bing(keyword, max_results=max_results * 2)

        if not search_results:
            return []

        # 2. 优先爬取权威来源
        trusted = [r for r in search_results if r.get("trusted")]
        others = [r for r in search_results if not r.get("trusted")]
        ordered = trusted + others

        # 3. 爬取前 max_results 个页面的正文
        results = []
        for item in ordered[:max_results]:
            url = item.get("url", "")
            if not url or not url.startswith("http"):
                continue

            # 爬取页面内容
            crawled = self.crawl_url(url)
            if crawled.get("success"):
                results.append({
                    "title": crawled.get("title", item.get("title", "未知标题")),
                    "url": url,
                    "source": crawled.get("source", item.get("source", "未知来源")),
                    "summary": crawled.get("summary", item.get("snippet", "")),
                    "content": crawled.get("content", ""),
                    "trusted": item.get("trusted", False),
                    "length": crawled.get("length", 0)
                })

        return results


def get_clinical_guidelines(keyword: str, max_results: int = 15) -> List[Dict[str, Any]]:
    """快捷函数：获取临床指南数据（搜索引擎驱动）"""
    crawler = CozeCrawler()
    return crawler.search_guidelines(keyword, max_results=max_results)


def check_token_status() -> dict:
    """检测 Token 和 Bot 是否可用（动态读取最新配置）"""
    cfg = get_config()
    token = cfg["token"]
    bot_id = cfg["bot_id"]

    if not token:
        return {"valid": False, "error": "Token 未配置"}

    try:
        r = requests.post(
            "https://api.coze.cn/v3/chat",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "bot_id": bot_id,
                "user_id": "status_check",
                "stream": False,
                "additional_messages": [{"role": "user", "content": "hi", "content_type": "text", "type": "question"}]
            },
            timeout=10
        )
        data = r.json()
        if data.get("code") == 0:
            return {"valid": True, "status": "connected"}
        return {"valid": False, "error": data.get("msg", "未知错误")}
    except Exception as e:
        return {"valid": False, "error": str(e)}


if __name__ == "__main__":
    # 快速测试
    api = CozeAPI()
    print("✅ CozeAPI 初始化成功")
    print(f"Bot ID: {COZE_BOT_ID}")
