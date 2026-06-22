"""
SpiderMind - Coze 额度快速诊断工具
用法：双击运行或 python check_coze_quota.py
"""
import requests, json, sys, os

def check():
    from token_manager import get_config
    cfg = get_config()
    token = cfg["token"]
    bot_id = cfg["bot_id"]
    
    if not token:
        print("❌ Token 未配置")
        return
    
    print(f"🔍 Token: {token[:12]}...{token[-6:]}")
    print(f"🔍 Bot ID: {bot_id}")
    print()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试发送一个最小请求
    print("📤 发送测试请求...")
    r = requests.post(
        "https://api.coze.cn/v3/chat",
        headers=headers,
        json={
            "bot_id": bot_id,
            "user_id": "quota_check",
            "stream": False,
            "additional_messages": [
                {"role": "user", "content": "hi", "content_type": "text", "type": "question"}
            ]
        },
        timeout=30
    )
    
    data = r.json()
    chat_id = data.get("data", {}).get("id", "")
    conv_id = data.get("data", {}).get("conversation_id", "")
    
    import time
    for i in range(15):
        time.sleep(2)
        ret = requests.get(
            "https://api.coze.cn/v3/chat/retrieve",
            headers=headers,
            params={"chat_id": chat_id, "conversation_id": conv_id},
            timeout=10
        )
        rd = ret.json()
        status = rd.get("data", {}).get("status", "")
        last_error = rd.get("data", {}).get("last_error", {})
        
        print(f"  [{i+1:2d}] 状态: {status}", end="")
        if last_error.get("code"):
            print(f"  |  错误码: {last_error.get('code')}  |  信息: {last_error.get('msg')}")
        else:
            print()
        
        if status == "completed":
            print("\n✅ 额度正常，API 可用！")
            return
        elif status in ("failed", "canceled"):
            err_code = last_error.get("code", 0)
            err_msg = last_error.get("msg", "")
            print()
            print("=" * 60)
            print(f"❌ API 调用失败！")
            print(f"   错误码: {err_code}")
            print(f"   错误信息: {err_msg}")
            print()
            
            if err_code == 4028:
                print("🔧 原因：Coze 免费额度已用完")
                print()
                print("解决方案（3选1）：")
                print("  1. 登录 coze.cn → 个人中心 → 查看积分余额")
                print("     等待下月1号自动重置免费额度")
                print()
                print("  2. 登录 coze.cn → 升级付费版（按月订阅）")
                print("     约 ¥49/月 起，可立即恢复使用")
                print()
                print("  3. 注册新的 Coze 账号，重新创建 Bot")
                print("     新账号通常有赠送积分")
                print("=" * 60)
            elif err_code == 4101:
                print("❌ Token 已过期，需要重新生成")
            else:
                print("❌ 请检查 Coze 平台状态")
            return
    
    print("⏱️ 轮询超时")

if __name__ == "__main__":
    check()
    input("\n按回车键退出...")
