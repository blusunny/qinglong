#!/usr/bin/env python3
import time
import os
import random
import json
import base64
import hashlib
import rsa
import requests
import re
from urllib.parse import urlparse  # 修复：导入语句完整且格式规范

# 常量定义
BI_RM = list("0123456789abcdefghijklmnopqrstuvwxyz")
B64MAP = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def mask_phone(phone):
    """
    隐藏手机号中间四位
    :param phone: 手机号字符串
    :return: 隐藏后的手机号，如138****1234
    """
    return phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone

def int2char(a):
    """
    将数字转换为对应的字符
    :param a: 0-35的数字
    :return: 对应的字符
    """
    return BI_RM[a]

def b64tohex(a):
    """
    Base64字符串转换为十六进制字符串
    :param a: Base64编码的字符串
    :return: 十六进制字符串
    """
    d = ""
    e = 0
    c = 0
    for i in range(len(a)):
        if list(a)[i] != "=":
            # 修复：变量v赋值语句完整且格式规范
            v = B64MAP.index(list(a)[i])
            if 0 == e:
                e = 1
                d += int2char(v >> 2)
                c = 3 & v
            elif 1 == e:
                e = 2
                d += int2char(c << 2 | v >> 4)
                c = 15 & v
            elif 2 == e:
                e = 3
                d += int2char(c)
                d += int2char(v >> 2)
                c = 3 & v
            else:
                e = 0
                d += int2char(c << 2 | v >> 4)
                d += int2char(15 & v)
    if e == 1:
        d += int2char(c << 2)
    return d

def rsa_encode(j_rsakey, string):
    """
    使用RSA公钥加密字符串
    :param j_rsakey: RSA公钥
    :param string: 需要加密的字符串
    :return: 加密后的字符串
    """
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
    # 修复：pubkey赋值语句完整且格式规范
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    result = b64tohex((base64.b64encode(rsa.encrypt(f'{string}'.encode(), pubkey))).decode())
    return result

def login(username, password):
    """
    登录天翼云盘
    :param username: 用户名
    :param password: 密码
    :return: 登录成功的session对象，失败返回None
    """
    print(" 正在执行登录流程...")
    session = requests.Session()  # 统一格式：赋值语句不换行
    
    try:
        # 获取登录令牌
        url_token = "https://m.cloud.189.cn/udb/udb_login.jsp?pageId=1&pageKey=default&clientType=wap&redirectURL=https://m.cloud.189.cn/zhuanti/2021/shakeLottery/index.html"
        response = session.get(url_token)  # 统一格式：不换行
        
        match = re.search(r"https?://[^\s'\"]+", response.text)  # 统一格式：不换行
        if not match:
            print(" 错误：未找到动态登录页")
            return None

        # 获取登录页面
        url = match.group()
        response = session.get(url)
        match = re.search(r"<a id=\"j-tab-login-link\"[^>]*href=\"([^\"]+)\"", response.text)
        if not match:
            print(" 错误：登录入口获取失败")
            return None

        # 解析登录参数
        href = match.group(1)
        response = session.get(href)

        captcha_token = re.findall(r"captchaToken' value='(.+?)'", response.text)[0]
        lt = re.findall(r'lt = "(.+?)"', response.text)[0]
        return_url = re.findall(r"returnUrl= '(.+?)'", response.text)[0]
        param_id = re.findall(r'paramId = "(.+?)"', response.text)[0]
        j_rsakey = re.findall(r'j_rsaKey" value="(\S+)"', response.text, re.M)[0]
        
        session.headers.update({"lt": lt})

        # RSA加密用户名和密码
        username_encrypted = rsa_encode(j_rsakey, username)
        password_encrypted = rsa_encode(j_rsakey, password)

        # 准备登录数据
        data = {
            "appKey": "cloud",
            "accountType": '01',
            "userName": f"{{RSA}}{username_encrypted}",
            "password": f"{{RSA}}{password_encrypted}",
            "validateCode": "",
            "captchaToken": captcha_token,
            "returnUrl": return_url,
            "mailSuffix": "@189.cn",  # 修复：邮箱后缀不换行
            "paramId": param_id
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0',
            'Referer': 'https://open.e.189.cn/',  # 修复：链接不换行
        }

        # 提交登录请求
        response = session.post(
            "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do",
            data=data,
            headers=headers,
            timeout=10
        )

        # 检查登录结果
        if response.json().get('result', 1) != 0:
            print(f" 登录错误：{response.json().get('msg')}")
            return None

        # 跳转到返回URL完成登录
        session.get(response.json()['toUrl'])
        print(" 登录成功")
        return session

    except Exception as e:
        print(f" 登录异常：{str(e)}")
        return None

def send_wxpusher(msg):
    """
    发送消息到WxPusher
    :param msg: 要发送的消息内容
    """
    # 从环境变量获取WxPusher配置
    app_token = os.getenv("WXPUSHER_APP_TOKEN")
    uids = os.getenv("WXPUSHER_UID", "").split('&')

    if not app_token or not uids:
        print(" 未配置WxPusher，跳过消息推送")
        return

    url = "https://wxpusher.zjiecode.com/api/send/message"  # 修复：链接不换行
    headers = {"Content-Type": "application/json"}

    for uid in uids:
        data = {
            "appToken": app_token,
            "content": msg,
            "contentType": 3,  # 3表示HTML格式
            "topicIds": [],
            "uids": [uid],
        }
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            if response.json().get('code') == 1000:
                print(f" 消息推送成功 -> UID: {uid}")
            else:
                print(f" 消息推送失败：{response.text}")
        except Exception as e:
            print(f" 推送异常：{str(e)}")

def main():
    """
    主函数：处理所有账号的签到和抽奖
    """
    print("\n=============== 天翼云盘签到开始 ===============")

    # 从环境变量获取账号信息
    usernames = os.getenv("ty_username", "").split('&')
    passwords = os.getenv("ty_password", "").split('&')

    # 检查环境变量
    if not usernames or not passwords or not usernames[0] or not passwords[0]:
        print(" 请设置环境变量 ty_username 和 ty_password")
        return

    # 确保账号密码数量匹配
    if len(usernames) != len(passwords):
        print(" 账号和密码数量不匹配")
        return

    # 组合账号信息
    accounts = [{"username": u, "password": p} for u, p in zip(usernames, passwords)]
    all_results = []

    for acc in accounts:
        username = acc["username"]
        password = acc["password"]
        masked_phone = mask_phone(username)
        account_result = {"username": masked_phone, "sign": "", "lottery": ""}

        print(f"\n 处理账号：{masked_phone}")

        # 登录流程
        session = login(username, password)
        if not session:
            account_result["sign"] = " 登录失败"
            all_results.append(account_result)
            continue

        # 签到流程
        try:
            # 每日签到
            rand = str(round(time.time() * 1000))  # 修复：不换行
            sign_url = f'https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
                "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
                "Host": "m.cloud.189.cn",
            }
            response = session.get(sign_url, headers=headers).json()

            if 'isSign' in response:
                if response.get('isSign') == "false":
                    account_result["sign"] = f" +{response.get('netdiskBonus', '0')}M"
                else:
                    account_result["sign"] = f" 已签到+{response.get('netdiskBonus', '0')}M"
            else:
                account_result["sign"] = f" 签到失败: {response.get('errorMsg', '未知错误')}"

            # 单次抽奖
            time.sleep(random.randint(2, 5))  # 修复：不换行
            lottery_url = 'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN'
            response = session.get(lottery_url, headers=headers).json()

            if "errorCode" in response:
                account_result["lottery"] = f" {response.get('errorCode')}"
            else:
                prize = response.get('prizeName') or response.get('description', '未知奖品')
                account_result["lottery"] = f" {prize}"

        except Exception as e:
            account_result["sign"] = " 操作异常"
            account_result["lottery"] = f" {str(e)}"

        all_results.append(account_result)
        print(f"  {account_result['sign']} | {account_result['lottery']}")

    # 生成汇总表格
    table = "###  天翼云盘签到汇总\n\n"
    table += "| 账号 | 签到结果 | 每日抽奖 |\n"
    table += "|:-:|:-:|:-:|\n"
    for res in all_results:
        table += f"| {res['username']} | {res['sign']} | {res['lottery']} |\n"

    # 发送汇总推送
    send_wxpusher(table)
    print("\n 所有账号处理完成！")

if __name__ == "__main__":
    main()
