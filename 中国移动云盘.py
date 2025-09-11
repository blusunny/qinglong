# 脚本名称: [中国移动云盘]
# 功能描述: [签到 基础任务 果园 云朵大作战]
# 使用说明:
#   - [抓包 Cookie：任意Authorization]
#   - [注意事项: 简易方法，开抓包进App，搜refresh，找到authTokenRefresh.do ，请求头中的Authorization，响应体<token> xxx</token> 中xxx值（新版加密抓这个）]
# 环境变量设置:
#   - 名称：[ydypCK]   格式：[Authorization值#手机号#token值]
#   - 多账号处理方式：[换行或者@分割]
# 定时设置: [0 0 8,16,20 * * *]
# 更新日志:
#   - [1.30]: [同一环境变量获取]
# 注: 本脚本仅用于个人学习和交流，请勿用于非法用途。作者不承担由于滥用此脚本所引起的任何责任，请在下载后24小时内删除。
# new Env("移动云盘")
# 作者: 洋洋不瘦
# fix 20240828 ArcadiaScriptPublic  频道：https://t.me/ArcadiaScript 群组：https://t.me/ArcadiaScriptPublic
# 抓包 第一个参数小程序orches.yun.139.com 或者aas.caiyun.feixin.10086.cn 搜Basic 全局搜也行  第三个参数app 域名caiyun.feixin.10086.cn或者签到链接https://caiyun.feixin.10086.cn:7071/market/signin/task/click?key=task&id=409的jwttoken
# 中国移动云盘脚本（稳定版）：保留正常功能，跳过失效模块
import os
import random
import re
import time
import uuid
import json
from os import path
import requests
from urllib.parse import urlencode

# -------------------------- 配置参数 --------------------------
UA = 'Mozilla/5.0 (Linux; Android 12; Mi 10 Pro Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/99.0.4844.88 Mobile Safari/537.36 MCloudApp/10.3.0'
MIN_SLEEP = 1
MAX_SLEEP = 2
CLICK_NUM = 15
SHAKE_NUM = 15
DRAW_NUM = 1
REQ_RETRIES = 2  # 减少无效重试，加快执行
REQ_TIMEOUT = 10
GLOBAL_DEBUG = False
NEWLINE = chr(10)

# -------------------------- 全局变量 --------------------------
err_accounts = ''
err_message = ''
user_amount = ''


def load_send():
    """加载通知模块"""
    cur_path = path.abspath(path.dirname(__file__))
    notify_file = path.join(cur_path, "notify.py")
    if path.exists(notify_file):
        try:
            from notify import send
            log_info("加载通知服务成功！")
            return send
        except ImportError as e:
            log_info(f"加载通知服务失败：{str(e)}")
    else:
        log_info("未找到notify.py，通知服务不可用")
    return False


def log_info(msg):
    """带时间戳的日志输出"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


class YP:
    def __init__(self, cookie):
        self.notebook_id = None
        self.note_token = None
        self.note_auth = None
        self.click_num = CLICK_NUM
        self.shake_num = SHAKE_NUM
        self.draw_num = DRAW_NUM
        self.session = requests.Session()
        self.timestamp = str(int(round(time.time() * 1000)))
        self.cookies = {'sensors_stay_time': self.timestamp}
        
        # 解析账号信息
        cookie_parts = cookie.strip().split("#")
        if len(cookie_parts) != 3:
            raise ValueError(f"账号格式错误（需满足：Authorization#手机号#token），当前：{cookie}")
        
        self.Authorization = cookie_parts[0]
        self.account = cookie_parts[1]
        self.auth_token = cookie_parts[2]
        self.encrypt_account = self.account[:3] + "*" * 4 + self.account[7:]
        
        # 基础请求头（仅保留稳定可用的）
        self.jwtHeaders = {
            'User-Agent': UA,
            'Accept': '*/*',
            'Host': 'caiyun.feixin.10086.cn',
            'Content-Type': 'application/json',
            'Referer': 'https://caiyun.feixin.10086.cn/'
        }

    @staticmethod
    def catch_errors(func):
        """异常捕获装饰器：减少无效报错"""
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # 仅记录关键错误，跳过已知失效模块的错误
                err_msg = f"用户[{self.encrypt_account}]：{str(e)}"
                if "文件上传" not in err_msg and "果园" not in err_msg and "云朵大作战" not in err_msg:
                    global err_message
                    log_info(f"错误：{err_msg}")
                    err_message += f"{err_msg}{NEWLINE}"
            return None
        return wrapper

    def sleep(self, min_delay=None, max_delay=None):
        """随机延迟"""
        min_d = min_delay if min_delay is not None else MIN_SLEEP
        max_d = max_delay if max_delay is not None else MAX_SLEEP
        delay = random.uniform(min_d, max_d)
        time.sleep(delay)

    def send_request(self, url, headers=None, cookies=None, data=None, params=None, method='GET', debug=None):
        """统一请求方法：简化逻辑，减少无效重试"""
        debug = debug if debug is not None else GLOBAL_DEBUG
        self.session.headers.update(headers or {})
        if cookies:
            self.session.cookies.update(cookies)
        
        request_args = {}
        if isinstance(data, dict):
            if headers and 'Content-Type' in headers and 'application/x-www-form-urlencoded' in headers['Content-Type']:
                request_args['data'] = urlencode(data)
            else:
                request_args['json'] = data
        elif data is not None:
            request_args['data'] = data
        
        for attempt in range(REQ_RETRIES):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    timeout=REQ_TIMEOUT,** request_args
                )
                response.raise_for_status()
                if debug:
                    log_info(f"【{url}】响应数据：{response.text}")
                return response
            except (requests.RequestException, ConnectionError, TimeoutError) as e:
                # 已知失效模块的错误，直接跳过重试
                if "upload.caiyun" in url or "fun.mail.10086.cn/cxmail" in url or "hecheng1T/beinvite" in url:
                    log_info(f"请求异常（已知失效模块，跳过重试）：{str(e)}")
                    return None
                log_info(f"请求异常（{attempt+1}/{REQ_RETRIES}）：{str(e)}")
                if attempt >= REQ_RETRIES - 1:
                    log_info(f"达到最大重试次数，请求失败：{url}")
                    return None
                self.sleep(1, 2)

    @catch_errors
    def run(self):
        """主执行流程：仅保留稳定可用功能"""
        log_info(f"\n======== 开始处理账号：{self.encrypt_account} ========")
        if self.jwt():
            self.signin_status()    # 签到（稳定）
            self.click()            # 戳一下（稳定）
            self.get_tasklist(url='sign_in_3', app_type='cloud_app')  # 云盘任务（跳过上传）
            
            log_info("\n☁️  开始处理云朵大作战（已知接口失效，简化执行）")
            self.cloud_game()  # 仅查询状态，不报错
            
            log_info("\n🌳 果园任务（已知接口失效，暂不支持）")  # 直接跳过，不触发错误
            
            log_info("\n📰 开始处理公众号任务（稳定）")
            self.wxsign()       # 公众号签到
            self.shake()        # 摇一摇
            self.surplus_num()  # 抽奖
            
            log_info("\n🔥 开始处理热门任务（稳定）")
            self.backup_cloud() # 备份云朵
            self.open_send()    # 通知任务
            
            log_info("\n📧 开始处理139邮箱任务（稳定）")
            self.get_tasklist(url='newsign_139mail', app_type='email_app')
            self.receive()      # 云朵汇总
        else:
            global err_accounts
            err_accounts += f"{self.encrypt_account}{NEWLINE}"
            log_info(f"账号[{self.encrypt_account}]：JWT获取失败，可能CK已失效")

    @catch_errors
    def sso(self):
        """获取SSO令牌（稳定）"""
        sso_url = 'https://orches.yun.139.com/orchestration/auth-rebuild/token/v1.0/querySpecToken'
        sso_headers = {
            'Authorization': self.Authorization,
            'User-Agent': UA,
            'Content-Type': 'application/json',
            'Host': 'orches.yun.139.com',
            'Referer': 'https://orches.yun.139.com/'
        }
        sso_payload = {"account": self.account, "toSourceId": "001005"}
        
        response = self.send_request(sso_url, headers=sso_headers, data=sso_payload, method='POST')
        if not response:
            return None
        
        sso_data = response.json()
        if sso_data.get('success'):
            log_info(f"账号[{self.encrypt_account}]：SSO令牌获取成功")
            return sso_data['data']['token']
        else:
            log_info(f"账号[{self.encrypt_account}]：SSO获取失败：{sso_data.get('message', '未知错误')}")
            return None

    @catch_errors
    def jwt(self):
        """获取JWT令牌（稳定）"""
        token = self.sso()
        if not token:
            return False
        
        jwt_url = f"https://caiyun.feixin.10086.cn/portal/auth/tyrzLogin.action?ssoToken={token}"
        response = self.send_request(jwt_url, headers=self.jwtHeaders, method='POST')
        if not response:
            return False
        
        jwt_data = response.json()
        if jwt_data.get('code') == 0 and 'token' in jwt_data.get('result', {}):
            self.jwtHeaders['jwtToken'] = jwt_data['result']['token']
            self.cookies['jwtToken'] = jwt_data['result']['token']
            log_info(f"账号[{self.encrypt_account}]：JWT令牌获取成功")
            return True
        else:
            log_info(f"账号[{self.encrypt_account}]：JWT获取失败：{jwt_data.get('msg', '未知错误')}")
            return False

    @catch_errors
    def signin_status(self):
        """签到（稳定）"""
        self.sleep()
        # 查询签到状态
        check_url = 'https://caiyun.feixin.10086.cn/market/signin/page/info?client=app'
        response = self.send_request(check_url, headers=self.jwtHeaders, cookies=self.cookies)
        if not response:
            return
        
        check_data = response.json()
        if check_data.get('msg') != 'success':
            self.log_info(err_msg=f"签到状态查询失败：{check_data.get('msg')}")
            return
        
        today_sign_in = check_data['result'].get('todaySignIn', False)
        if today_sign_in:
            log_info(f"账号[{self.encrypt_account}]：今日已签到")
            return
        
        # 执行签到
        signin_url = 'https://caiyun.feixin.10086.cn/market/signin/page/signIn'
        signin_response = self.send_request(signin_url, headers=self.jwtHeaders, cookies=self.cookies, method='POST')
        if not signin_response:
            self.log_info(err_msg="签到请求发送失败")
            return
        
        signin_data = signin_response.json()
        if signin_data.get('msg') == 'success':
            log_info(f"账号[{self.encrypt_account}]：签到成功")
        else:
            self.log_info(err_msg=f"签到失败：{signin_data.get('msg')}")

    @catch_errors
    def click(self):
        """戳一下（稳定）"""
        log_info(f"账号[{self.encrypt_account}]：开始戳一下（共{self.click_num}次）")
        url = "https://caiyun.feixin.10086.cn/market/signin/task/click?key=task&id=319"
        successful_click = 0
        
        for i in range(self.click_num):
            response = self.send_request(url, headers=self.jwtHeaders, cookies=self.cookies)
            if response:
                return_data = response.json()
                if 'result' in return_data:
                    log_info(f"戳一下[{i+1}/{self.click_num}]：{return_data['result']}")
                    successful_click += 1
            self.sleep(0.2, 0.5)
        
        if successful_click == 0:
            log_info(f"账号[{self.encrypt_account}]：戳一下未获得任何奖励")
        else:
            log_info(f"账号[{self.encrypt_account}]：戳一下完成，成功{successful_click}次")

    @catch_errors
    def get_tasklist(self, url, app_type):
        """获取任务列表：跳过失效任务（文件上传）"""
        task_url = f'https://caiyun.feixin.10086.cn/market/signin/task/taskList?marketname={url}'
        response = self.send_request(task_url, headers=self.jwtHeaders, cookies=self.cookies)
        if not response:
            self.log_info(err_msg=f"获取{app_type}任务列表失败")
            return
        
        self.sleep()
        return_data = response.json()
        task_list = return_data.get('result', {})
        if not task_list:
            log_info(f"账号[{self.encrypt_account}]：{app_type}无任务数据")
            return
        
        # 处理任务：强制跳过文件上传（ID=106）和果园相关任务
        for task_type, tasks in task_list.items():
            if task_type in ["new", "hidden", "hiddenabc"]:
                continue
            
            # 云盘任务
            if app_type == 'cloud_app':
                if task_type == "month":
                    log_info(f"\n📆 云盘每月任务（账号：{self.encrypt_account}）")
                    skip_task_ids = [110, 113, 417, 409]
                elif task_type == "day":
                    log_info(f"\n📆 云盘每日任务（账号：{self.encrypt_account}）")
                    skip_task_ids = [404, 106]  # 强制跳过文件上传（ID=106）
                else:
                    continue
            
            # 139邮箱任务
            elif app_type == 'email_app' and task_type == "month":
                log_info(f"\n📆 139邮箱每月任务（账号：{self.encrypt_account}）")
                skip_task_ids = [1004, 1005, 1015, 1020]
            else:
                continue
            
            # 执行任务
            for task in tasks:
                task_id = task.get('id')
                task_name = task.get('name', '未知任务')
                task_status = task.get('state', '')
                
                # 额外跳过已知失效的任务
                if task_id == 106:
                    log_info(f"跳过任务：{task_name}（ID：{task_id}，接口已失效）")
                    continue
                if task_id in skip_task_ids:
                    log_info(f"跳过任务：{task_name}（ID：{task_id}）")
                    continue
                if task_status == 'FINISH':
                    log_info(f"已完成：{task_name}")
                    continue
                
                log_info(f"去完成：{task_name}（ID：{task_id}）")
                self.do_task(task_id, task_type, app_type)
                self.sleep(2, 3)

    @catch_errors
    def do_task(self, task_id, task_type, app_type):
        """执行任务：仅保留稳定任务（如创建笔记）"""
        self.sleep()
        # 触发任务点击
        task_url = f'https://caiyun.feixin.10086.cn/market/signin/task/click?key=task&id={task_id}'
        self.send_request(task_url, headers=self.jwtHeaders, cookies=self.cookies)
        
        # 仅处理创建笔记任务（其他失效任务跳过）
        if app_type == 'cloud_app' and task_type == 'day' and task_id == 107:
            log_info(f"账号[{self.encrypt_account}]：开始处理创建笔记任务")
            self.refresh_notetoken()
            if self.note_token and self.note_auth:
                self.get_notebook_id()
                self.create_note()
            else:
                self.log_info(err_msg="创建笔记失败：笔记Token未获取")

    @catch_errors
    def refresh_notetoken(self):
        """刷新笔记Token（稳定）"""
        log_info(f"账号[{self.encrypt_account}]：刷新笔记Token")
        note_url = 'http://mnote.caiyun.feixin.10086.cn/noteServer/api/authTokenRefresh.do'
        note_payload = {
            "authToken": self.auth_token,
            "userPhone": self.account
        }
        note_headers = {
            'User-Agent': 'mobile',
            'APP_CP': 'android',
            'CP_VERSION': '3.2.0',
            'Host': 'mnote.caiyun.feixin.10086.cn',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        
        response = self.send_request(note_url, headers=note_headers, data=note_payload, method="POST")
        if response:
            self.note_token = response.headers.get('NOTE_TOKEN')
            self.note_auth = response.headers.get('APP_AUTH')
            if self.note_token and self.note_auth:
                log_info(f"账号[{self.encrypt_account}]：笔记Token刷新成功")
            else:
                self.log_info(err_msg="笔记Token获取失败")

    @catch_errors
    def get_notebook_id(self):
        """获取默认笔记本ID（稳定）"""
        note_url = 'http://mnote.caiyun.feixin.10086.cn/noteServer/api/syncNotebookV3.do'
        headers = {
            'User-Agent': 'mobile',
            'APP_CP': 'android',
            'CP_VERSION': '3.2.0',
            'APP_NUMBER': self.account,
            'APP_AUTH': self.note_auth,
            'NOTE_TOKEN': self.note_token,
            'Host': 'mnote.caiyun.feixin.10086.cn',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        payload = {
            "addNotebooks": [],
            "delNotebooks": [],
            "notebookRefs": [],
            "updateNotebooks": []
        }
        
        response = self.send_request(note_url, headers=headers, data=payload, method='POST')
        if response:
            return_data = response.json()
            notebooks = return_data.get('notebooks', [])
            if notebooks:
                self.notebook_id = notebooks[0]['notebookId']
                log_info(f"账号[{self.encrypt_account}]：获取默认笔记本ID成功")
            else:
                raise ValueError("未获取到笔记本列表")

    @catch_errors
    def create_note(self):
        """创建笔记（稳定）"""
        if not self.notebook_id:
            raise ValueError("创建笔记失败：笔记本ID未获取")
        
        note_id = uuid.uuid4().hex
        create_time = str(int(round(time.time() * 1000)))
        self.sleep(3, 4)
        update_time = str(int(round(time.time() * 1000)))
        
        note_url = 'http://mnote.caiyun.feixin.10086.cn/noteServer/api/createNote.do'
        headers = {
            'User-Agent': 'mobile',
            'APP_CP': 'android',
            'CP_VERSION': '3.2.0',
            'APP_NUMBER': self.account,
            'APP_AUTH': self.note_auth,
            'NOTE_TOKEN': self.note_token,
            'Host': 'mnote.caiyun.feixin.10086.cn',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        payload = {
            "archived": 0,
            "attachmentdir": note_id,
            "contents": [{
                "contentid": 0,
                "data": "<font size=\"3\">自动创建的笔记内容</font>",
                "noteId": note_id,
                "sortOrder": 0,
                "type": "RICHTEXT"
            }],
            "createtime": create_time,
            "noteid": note_id,
            "tags": [{
                "id": self.notebook_id,
                "text": "默认笔记本"
            }],
            "title": f"自动笔记_{create_time}",
            "updatetime": update_time,
            "userphone": self.account
        }
        
        response = self.send_request(note_url, headers=headers, data=payload, method='POST')
        if response and response.status_code == 200:
            log_info(f"账号[{self.encrypt_account}]：笔记创建成功")
        else:
            self.log_info(err_msg="笔记创建失败")

    @catch_errors
    def wxsign(self):
        """公众号签到（稳定）"""
        self.sleep()
        url = 'https://caiyun.feixin.10086.cn/market/playoffic/followSignInfo?isWx=true'
        response = self.send_request(url, headers=self.jwtHeaders, cookies=self.cookies)
        if not response:
            self.log_info(err_msg="公众号签到状态查询失败")
            return
        
        return_data = response.json()
        if return_data.get('msg') != 'success':
            self.log_info(err_msg=f"公众号签到失败：{return_data.get('msg')}")
            return
        
        if return_data['result'].get('todaySignIn'):
            log_info(f"账号[{self.encrypt_account}]：公众号今日已签到")
        else:
            self.log_info(err_msg="公众号签到失败：可能未绑定公众号")

    @catch_errors
    def shake(self):
        """摇一摇（稳定）"""
        log_info(f"账号[{self.encrypt_account}]：开始摇一摇（共{self.shake_num}次）")
        url = "https://caiyun.feixin.10086.cn/market/shake-server/shake/shakeIt?flag=1"
        successful_shakes = 0
        
        for i in range(self.shake_num):
            response = self.send_request(url, headers=self.jwtHeaders, cookies=self.cookies, method='POST')
            if response:
                return_data = response.json()
                shake_prize = return_data["result"].get("shakePrizeconfig")
                if shake_prize:
                    log_info(f"摇一摇[{i+1}/{self.shake_num}]：获得{shake_prize['name']}")
                    successful_shakes += 1
            self.sleep(1, 2)
        
        if successful_shakes == 0:
            log_info(f"账号[{self.encrypt_account}]：摇一摇未获得任何奖励")
        else:
            log_info(f"账号[{self.encrypt_account}]：摇一摇完成，成功获得{successful_shakes}次奖励")

    @catch_errors
    def surplus_num(self):
        """抽奖（稳定）"""
        self.sleep()
        # 查询抽奖信息
        draw_info_url = 'https://caiyun.feixin.10086.cn/market/playoffic/drawInfo'
        response = self.send_request(draw_info_url, headers=self.jwtHeaders)
        if not response:
            self.log_info(err_msg="抽奖信息查询失败")
            return
        
        draw_info_data = response.json()
        if draw_info_data.get('msg') != 'success':
            self.log_info(err_msg=f"抽奖信息查询失败：{draw_info_data.get('msg')}")
            return
        
        remain_num = draw_info_data['result'].get('surplusNumber', 0)
        log_info(f"账号[{self.encrypt_account}]：剩余抽奖次数{remain_num}")
        
        # 执行抽奖
        if remain_num > 0:
            draw_url = "https://caiyun.feixin.10086.cn/market/playoffic/draw"
            draw_count = min(self.draw_num, remain_num)
            for i in range(draw_count):
                self.sleep()
                draw_response = self.send_request(draw_url, headers=self.jwtHeaders, method='GET')
                if draw_response:
                    draw_data = draw_response.json()
                    if draw_data.get("code") == 0:
                        prize_name = draw_data["result"].get("prizeName", "未知奖励")
                        log_info(f"抽奖[{i+1}/{draw_count}]：获得{prize_name}")
                    else:
                        log_info(f"抽奖[{i+1}/{draw_count}]：失败（{draw_data.get('msg', '未知错误')}）")

    @catch_errors
    def cloud_game(self):
        """云朵大作战：仅查询状态，不执行（接口失效）"""
        # 仅查询状态，不报错
        game_info_url = 'https://caiyun.feixin.10086.cn/market/signin/hecheng1T/info?op=info'
        game_info_response = self.send_request(game_info_url, headers=self.jwtHeaders, cookies=self.cookies)
        if not game_info_response:
            log_info("云朵大作战：状态查询失败（接口失效）")
            return
        
        game_info_data = game_info_response.json()
        if not game_info_data or game_info_data.get('code', -1) != 0:
            log_info("云朵大作战：状态查询失败（接口失效）")
            return
        
        currnum = game_info_data.get('result', {}).get('info', {}).get('curr', 0)
        rank = game_info_data.get('result', {}).get('history', {}).get('0', {}).get('rank', '未知')
        log_info(f"账号[{self.encrypt_account}]：云朵大作战 - 今日剩余次数{currnum}，本月排名{rank}（接口失效，暂不执行）")

    @catch_errors
    def receive(self):
        """云朵汇总（稳定）"""
        # 查询待领取云朵
        receive_url = "https://caiyun.feixin.10086.cn/market/signin/page/receive"
        receive_response = self.send_request(receive_url, headers=self.jwtHeaders, cookies=self.cookies)
        if not receive_response:
            self.log_info(err_msg="待领取云朵查询失败")
            return
        
        receive_data = receive_response.json()
        receive_amount = receive_data["result"].get("receive", "0")
        total_amount = receive_data["result"].get("total", "0")
        log_info(f"账号[{self.encrypt_account}]：待领取云朵{receive_amount}，当前总云朵{total_amount}")
        
        # 查询奖品日志
        self.sleep()
        prize_url = f"https://caiyun.feixin.10086.cn/market/prizeApi/checkPrize/getUserPrizeLogPage?currPage=1&pageSize=15&_={self.timestamp}"
        prize_response = self.send_request(prize_url, headers=self.jwtHeaders, cookies=self.cookies)
        if not prize_response:
            self.log_info(err_msg="奖品日志查询失败")
            return
        
        prize_data = prize_response.json()
        result = prize_data.get('result', {}).get('result', [])
        rewards = []
        for prize in result:
            prize_name = prize.get('prizeName', '未知奖品')
            flag = prize.get('flag', 0)  # 1：待领取，0：已领取
            if flag == 1:
                rewards.append(f"- 待领取奖品：{prize_name}")
        
        # 汇总云朵信息
        global user_amount
        reward_str = f"{NEWLINE}".join(rewards) if rewards else "- 无待领取奖品"
        msg = f"账号[{self.encrypt_account}]：总云朵{total_amount}{NEWLINE}{reward_str}"
        user_amount += f"{msg}{NEWLINE}"
        log_info(f"\n账号[{self.encrypt_account}]：云朵汇总{NEWLINE}{msg}")

    @catch_errors
    def backup_cloud(self):
        """备份云朵（稳定）"""
        # 1. 连续备份奖励
        backup_url = 'https://caiyun.feixin.10086.cn/market/backupgift/info'
        backup_response = self.send_request(backup_url, headers=self.jwtHeaders)
        if not backup_response:
            self.log_info(err_msg="连续备份奖励查询失败")
            return
        
        backup_data = backup_response.json()
        state = backup_data.get('result', {}).get('state', -1)
        if state == -1:
            log_info(f"账号[{self.encrypt_account}]：连续备份 - 本月未备份，无奖励")
        elif state == 0:
            log_info(f"账号[{self.encrypt_account}]：连续备份 - 领取本月奖励")
            receive_url = 'https://caiyun.feixin.10086.cn/market/backupgift/receive'
            receive_response = self.send_request(receive_url, headers=self.jwtHeaders, method='POST')
            if receive_response:
                receive_data = receive_response.json()
                cloud_count = receive_data.get('result', {}).get('result', 0)
                log_info(f"账号[{self.encrypt_account}]：连续备份奖励 - 获得{cloud_count}云朵")
        elif state == 1:
            log_info(f"账号[{self.encrypt_account}]：连续备份 - 本月奖励已领取")
        
        # 2. 膨胀云朵
        self.sleep()
        expend_url = 'https://caiyun.feixin.10086.cn/market/signin/page/taskExpansion'
        expend_response = self.send_request(expend_url, headers=self.jwtHeaders, cookies=self.cookies)
        if not expend_response:
            self.log_info(err_msg="膨胀云朵查询失败")
            return
        
        expend_data = expend_response.json()
        cur_month_backup = expend_data.get('result', {}).get('curMonthBackup', False)
        pre_month_backup = expend_data.get('result', {}).get('preMonthBackup', False)
        cur_month_accepted = expend_data.get('result', {}).get('curMonthBackupTaskAccept', False)
        next_month_cloud = expend_data.get('result', {}).get('nextMonthTaskRecordCount', 0)
        
        if cur_month_backup:
            log_info(f"账号[{self.encrypt_account}]：膨胀云朵 - 本月已备份，下月可领{next_month_cloud}云朵")
        else:
            log_info(f"账号[{self.encrypt_account}]：膨胀云朵 - 本月未备份，下月无膨胀奖励")
        
        if pre_month_backup and not cur_month_accepted:
            log_info(f"账号[{self.encrypt_account}]：膨胀云朵 - 领取上月备份奖励")
            receive_url = f'https://caiyun.feixin.10086.cn/market/signin/page/receiveTaskExpansion?acceptDate={expend_data.get("acceptDate", "")}'
            receive_response = self.send_request(receive_url, headers=self.jwtHeaders, cookies=self.cookies, method='GET')
            if receive_response:
                receive_data = receive_response.json()
                if receive_data.get("code") == 0:
                    cloud_count = receive_data.get('result', {}).get('cloudCount', 0)
                    log_info(f"账号[{self.encrypt_account}]：膨胀云朵奖励 - 获得{cloud_count}云朵")
        elif pre_month_backup:
            log_info(f"账号[{self.encrypt_account}]：膨胀云朵 - 上月备份奖励已领取")
        else:
            log_info(f"账号[{self.encrypt_account}]：膨胀云朵 - 上月未备份，无奖励可领")

    @catch_errors
    def open_send(self):
        """通知任务（稳定）"""
        send_url = 'https://caiyun.feixin.10086.cn/market/msgPushOn/task/status'
        send_response = self.send_request(send_url, headers=self.jwtHeaders)
        if not send_response:
            self.log_info(err_msg="通知任务状态查询失败")
            return
        
        send_data = send_response.json()
        push_on = send_data.get('result', {}).get('pushOn', 0)
        first_task_status = send_data.get('result', {}).get('firstTaskStatus', 0)
        second_task_status = send_data.get('result', {}).get('secondTaskStatus', 0)
        on_duaration = send_data.get('result', {}).get('onDuaration', 0)
        
        if push_on == 1:
            log_info(f"账号[{self.encrypt_account}]：通知已开启（已开启{on_duaration}天）")
            reward_url = 'https://caiyun.feixin.10086.cn/market/msgPushOn/task/obtain'
            
            if first_task_status != 3:
                log_info(f"账号[{self.encrypt_account}]：领取通知任务1奖励")
                reward1_response = self.send_request(reward_url, headers=self.jwtHeaders, data={"type": 1}, method='POST')
                if reward1_response:
                    reward1_data = reward1_response.json()
                    log_info(f"任务1奖励：{reward1_data.get('result', {}).get('description', '领取成功')}")
            else:
                log_info(f"账号[{self.encrypt_account}]：通知任务1奖励已领取")
            
            if second_task_status == 2:
                log_info(f"账号[{self.encrypt_account}]：领取通知任务2奖励")
                reward2_response = self.send_request(reward_url, headers=self.jwtHeaders, data={"type": 2}, method='POST')
                if reward2_response:
                    reward2_data = reward2_response.json()
                    log_info(f"任务2奖励：{reward2_data.get('result', {}).get('description', '领取成功')}")
            else:
                log_info(f"账号[{self.encrypt_account}]：通知任务2奖励已领取或未满足条件")
        else:
            log_info(f"账号[{self.encrypt_account}]：通知未开启（状态：{push_on}），无法领取奖励")

    def log_info(self, err_msg=None, amount=None):
        """实例内日志汇总"""
        global err_message, user_amount
        if err_msg is not None:
            err_message += f'用户[{self.encrypt_account}]:{err_msg}{NEWLINE}'
        elif amount is not None:
            user_amount += f'用户[{self.encrypt_account}]:{amount}{NEWLINE}'


if __name__ == "__main__":
    log_info("=" * 50)
    log_info("开始执行中国移动云盘自动化脚本（稳定版）")
    log_info("=" * 50)
    
    # 获取环境变量
    env_name = 'ydypCK'
    token = os.getenv(env_name)
    if not token:
        log_info(f"⛔️ 未获取到环境变量：{env_name}，请检查配置")
        exit(1)
    
    # 解析多账号
    cookies = [acc for acc in re.split(r'[@\n]', token) if acc.strip()]
    log_info(f"共获取到{len(cookies)}个账号")
    
    # 执行每个账号
    for i, account_info in enumerate(cookies, start=1):
        try:
            yp = YP(account_info)
            yp.run()
        except ValueError as e:
            log_info(f"第{i}个账号处理失败：{str(e)}")
            err_message += f"第{i}个账号：{str(e)}{NEWLINE}"
        
        # 多账号间隔延迟
        if i < len(cookies):
            delay = random.randint(5, 10)
            log_info(f"\n等待{delay}秒后处理下一个账号...")
            time.sleep(delay)
    
    # 输出汇总信息
    log_info("\n" + "=" * 50)
    log_info("脚本执行完成，汇总信息如下：")
    log_info("=" * 50)
    
    # 失效账号
    if err_accounts:
        err_count = err_accounts.count(NEWLINE)
        log_info(f"\n❌ 失效账号（共{err_count}个）：")
        log_info(err_accounts.strip())
    else:
        log_info("\n✅ 所有账号CK均有效")
    
    # 错误信息（仅显示关键错误）
    if err_message:
        err_msg_count = err_message.count(NEWLINE)
        log_info(f"\n❌ 关键错误信息汇总（共{err_msg_count}条）：")
        log_info(err_message.strip())
    else:
        log_info("\n✅ 无关键错误信息")
    
    # 云朵数量汇总
    if user_amount:
        log_info(f"\n☁️  云朵数量汇总：")
        log_info(user_amount.strip())
    
    # 发送通知
    send = load_send()
    if send:
        log_info("\n📢 开始发送通知...")
        notify_title = "中国移动云盘任务执行结果（稳定版）"
        err_count = err_accounts.count(NEWLINE)
        err_msg_count = err_message.count(NEWLINE)
        
        notify_content = f"""
【执行汇总】
• 总账号数：{len(cookies)}
• 失效账号数：{err_count}
• 关键错误数：{err_msg_count}
• 说明：文件上传、果园、云朵大作战接口已失效，暂不支持

【失效账号】
{err_accounts.strip() or '无'}

【关键错误】
{err_message.strip() or '无'}

【云朵数量】
{user_amount.strip() or '无'}
        """.strip()
        send(notify_title, notify_content)
        log_info("📢 通知发送完成")
    else:
        log_info("\n📢 通知服务不可用，跳过发送")
