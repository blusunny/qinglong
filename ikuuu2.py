import os
import requests
import json

# 配置信息 - 从环境变量获取，避免硬编码敏感信息
WXPUSHER_TOKEN = os.getenv("WXPUSHER_TOKEN", "")
WXPUSHER_UID = os.getenv("WXPUSHER_UID", "")
IKUUU_ACCOUNTS = os.getenv("IKUUU_ACCOUNTS", "").split("#")  # 格式: 账号1&密码1#账号2&密码2

# 全局变量用于收集日志
log_messages = []

def log(message):
    """记录日志并打印"""
    print(message)
    log_messages.append(message)

def send_wxpusher(msg):
    """发送消息到WXPusher"""
    if not WXPUSHER_TOKEN or not WXPUSHER_UID:
        log("WXPusher配置不完整，跳过推送")
        return
    
    url = "https://wxpusher.zjiecode.com/api/send/message"
    headers = {"Content-Type": "application/json"}
    data = {
        "appToken": WXPUSHER_TOKEN,
        "content": msg,
        "contentType": 1,  # 文本类型
        "uids": [WXPUSHER_UID]
    }
    
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=10)
        resp.raise_for_status()  # 触发HTTP错误状态码的异常
        result = resp.json()
        
        if result.get("code") == 1000:
            log("WXPusher推送成功")
        else:
            log(f"WXPusher推送失败: {result.get('msg', '未知错误')}")
            
    except requests.exceptions.RequestException as e:
        log(f"WXPusher请求异常: {str(e)}")
    except json.JSONDecodeError:
        log("WXPusher返回数据格式错误")

def login_and_checkin(account_info):
    """处理单个账号的登录和签到"""
    try:
        email, password = account_info.split("&", 1)
    except ValueError:
        return "账号格式错误，应为'邮箱&密码'\n"
    
    # 这里是示例域名，实际使用时可能需要动态检测可用域名
    base_url = "https://ikuuu.de"
    login_url = f"{base_url}/auth/login"
    checkin_url = f"{base_url}/user/checkin"
    
    # 登录
    try:
        session = requests.Session()
        login_data = {
            "email": email,
            "passwd": password,
            "code": ""
        }
        
        login_resp = session.post(
            login_url,
            data=login_data,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"},
            timeout=10
        )
        
        login_result = login_resp.json()
        if login_result.get("ret") != 1:
            return f"账号 {email} 登录失败: {login_result.get('msg', '未知错误')}\n"
        
        # 签到
        checkin_resp = session.post(
            checkin_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"},
            timeout=10
        )
        
        checkin_result = checkin_resp.json()
        return f"账号 {email} 签到结果: {checkin_result.get('msg', '未知结果')}\n"
        
    except Exception as e:
        return f"账号 {email} 处理出错: {str(e)}\n"

def notify(title, message):
    """模拟原有通知函数，实际使用时替换为真实实现"""
    # 这里可以是其他通知方式的实现，如PushPlus等
    log(f"发送通知: {title}\n{message}")

def main():
    log("===== IKUUU机场签到开始 =====")
    
    # 检查账号配置
    if not IKUUU_ACCOUNTS or IKUUU_ACCOUNTS == [""]:
        log("未配置任何账号，退出程序")
        return
    
    log(f"检测到 {len(IKUUU_ACCOUNTS)} 个账号，开始签到...")
    
    # 处理所有账号
    sendmsg = ""
    for account in IKUUU_ACCOUNTS:
        if account.strip():  # 跳过空账号
            sendmsg += login_and_checkin(account)
    
    # 准备推送内容
    table = f"IKUUU机场签到汇总\n{sendmsg}"
    
    # 发送推送
    notify("IKUUU机场签到结果", sendmsg)
    send_wxpusher(table)
    
    log("\n===== 所有账号处理完成 =====")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"程序运行出错: {str(e)}")
        # 出错时也尝试推送错误信息
        if WXPUSHER_TOKEN and WXPUSHER_UID:
            send_wxpusher(f"IKUUU签到脚本出错: {str(e)}")
