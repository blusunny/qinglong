import requests
import re
import time
import json
import random
import datetime
import base64
import threading
import ssl
import execjs
import os
import sys

from bs4 import BeautifulSoup

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.strxor import strxor
from Crypto.Cipher import AES
from http import cookiejar  # Python 2: import cookielib as cookiejar
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context


class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False
    
def printn(m):  
    print(f'\n{m}')
ORIGIN_CIPHERS = ('DEFAULT@SECLEVEL=1')


class DESAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        """
        A TransportAdapter that re-enables 3DES support in Requests.
        """
        CIPHERS = ORIGIN_CIPHERS.split(':')
        random.shuffle(CIPHERS)
        CIPHERS = ':'.join(CIPHERS)
        self.CIPHERS = CIPHERS + ':!aNULL:!eNULL:!MD5'
        super().__init__(*args, **kwargs)
 
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=self.CIPHERS)
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)
 
    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=self.CIPHERS)
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).proxy_manager_for(*args, **kwargs)
 

requests.packages.urllib3.disable_warnings()
ssl_context = ssl.create_default_context()
ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")  # Set security level to allow smaller DH keys    
ss = requests.session()
ss.headers={"User-Agent":"Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36","Referer":"https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"}    
ss.mount('https://', DESAdapter())       
ss.cookies.set_policy(BlockAll())
yc = 1
wt = 0
kswt = 0.1
yf = datetime.datetime.now().strftime("%Y%m")
ip_list = []
jp = {"9": {}, "13": {}}
try:
    with open('电信金豆换话费.log') as fr:
        dhjl = json.load(fr)
except :
    dhjl = {}
if yf not in dhjl:
    dhjl[yf] = {}
load_token_file = 'chinaTelecom_cache.json'
try:
    with open(load_token_file, 'r') as f:
        load_token = json.load(f)
except:
    load_token = {}
    




errcode = {
    "0":"兑换成功",
    "412":"兑换次数已达上限",
    "413":"商品已兑完",
    "420":"未知错误",
    "410":"该活动已失效~",
    "Y0001":"当前等级不足，去升级兑当前话费",
    "Y0002":"使用翼相连网络600分钟或连接并拓展网络500分钟可兑换此奖品",
    "Y0003":"使用翼相连共享流量400M或共享WIFI：2GB可兑换此奖品",
    "Y0004":"使用翼相连共享流量2GB可兑换此奖品",
    "Y0005":"当前等级不足，去升级兑当前话费",
    "E0001":"您的网龄不足10年，暂不能兑换"
}










#加密参数
key = b'1234567`90koiuyhgtfrdews'
iv = 8 * b'\0'

public_key_b64 = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----'''

public_key_data = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----'''


def t(h):    
    date = datetime.datetime.now()
    date_zero = datetime.datetime.now().replace(year=date.year, month=date.month, day=date.day, hour=h, minute=59, second=59)
    date_zero_time = int(time.mktime(date_zero.timetuple()))
    return date_zero_time
    


def encrypt(text):    
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(text.encode(), DES3.block_size))
    return ciphertext.hex()

def decrypt(text):
    ciphertext = bytes.fromhex(text)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), DES3.block_size)
    return plaintext.decode()
    
    
    
def b64(plaintext):
    public_key = RSA.import_key(public_key_b64)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return base64.b64encode(ciphertext).decode()
    
def encrypt_para(plaintext):
    public_key = RSA.import_key(public_key_data)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return ciphertext.hex()
  
            
def encode_phone(text):
    encoded_chars = []
    for char in text:
        encoded_chars.append(chr(ord(char) + 2))
    return ''.join(encoded_chars)

def ophone(t):
    key = b'34d7cb0bcdf07523'
    utf8_key = key.decode('utf-8')
    utf8_t = t.encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB) 
    ciphertext = cipher.encrypt(pad(utf8_t, AES.block_size)) 
    return ciphertext.hex() 

def send(uid,content):
    
    r = requests.post('https://wxpusher.zjiecode.com/api/send/message',json={"appToken":appToken,"content":content,"contentType":1,"uids":[uid]}).json()
    return r
    
            
def userLoginNormal(phone,password):
    alphabet = 'abcdef0123456789'
    uuid = [''.join(random.sample(alphabet, 8)),''.join(random.sample(alphabet, 4)),'4'+''.join(random.sample(alphabet, 3)),''.join(random.sample(alphabet, 4)),''.join(random.sample(alphabet, 12))]
    timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'
    
    r = ss.post('https://appgologin.189.cn:9031/login/client/userLoginNormal',json={"headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "", "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": "", "userLoginName": phone}, "content": {"attach": "test", "fieldData": {"loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": b64(loginAuthCipherAsymmertric), "deviceUid": uuid[0] + uuid[1] + uuid[2], "phoneNum": encode_phone(phone), "isChinatelecom": "0", "systemVersion": "15.4.0", "authentication": password}}}).json()

    l = r['responseData']['data']['loginSuccessResult']
    
    if l:
        load_token[phone] = l
        with open(load_token_file, 'w') as f:
            json.dump(load_token, f)
        ticket = get_ticket(phone,l['userId'],l['token']) 
        return ticket
       
    return False
def get_ticket(phone,userId,token):
    r = ss.post('https://appgologin.189.cn:9031/map/clientXML',data='<Request><HeaderInfos><Code>getSingle</Code><Timestamp>'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>'+token+'</Token><UserLoginName>'+phone+'</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>'+encrypt(userId)+'</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>',headers={'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'})

    
    tk = re.findall('<Ticket>(.*?)</Ticket>',r.text)
    if len(tk) == 0:        
        return False
    
    
    return decrypt(tk[0])


        
        

    

def exchange(phone,s,title,aid, uid):
    global rs
    try:
        if rs:
            khhWNSbEsFUP = js.call('main').split('=')
            
            cookie={"4khhWNSbEsFUO":khhWNSbEsFUO,"4khhWNSbEsFUP":khhWNSbEsFUP[1]}
        else:
            cookie = {} 

        r = s.post('http://wapact.189.cn:9000/gateway/stand/detailNew/exchange',json={"activityId":aid},cookies=cookie)#,proxies={"https":"http://"+random.choice(ip_list)+":443"})
        printn(f"响应码: {r.status_code} {r.text}")
        
        if '$_ts=window' in r.text:
            rs = 1
            first_request(r.text)
            return
        r = r.json()        
        
        if r["code"] == 0:
            if r["biz"] != {} and r["biz"]["resultCode"] in errcode:
                printn(f'{str(datetime.datetime.now())[11:22]} {phone} {title} {errcode[r["biz"]["resultCode"]]}')
                
                if r["biz"]["resultCode"] in ["0","412"]:
                    if r["biz"]["resultCode"] == "0":
                        msg = phone+":"+title+"兑换成功"
                        
                        send(uid, msg)
                    if phone not in dhjl[yf][title]:
                        dhjl[yf][title] += "#"+phone
                        with open('电信金豆换话费.log', 'w') as f:
                            json.dump(dhjl, f, ensure_ascii=False)
                            
            
        else:

            printn(f'{str(datetime.datetime.now())[11:22]} {phone} {r}')
            
    except Exception as e:
        print(e)
    
    
def dh(phone,s,title,aid,wt, uid):

    while wt > time.time():
        time.sleep(1)
        #break
    
    printn(f"{str(datetime.datetime.now())[11:22]} {phone} {title} 开始兑换")
    cs = 0
    while cs < 3:
        threading.Thread(target=exchange,args=(phone,s,title,aid, uid)).start()      
        
        cs += 1 
        #return



    
def check(headers, aid):
    r = requests.get('http://wapact.189.cn:9000/gateway/stand/detail/check' + aid,headers=headers,verify=False).json()
    return r
def ks(phone, ticket, uid):
    global wt
    
    s = requests.session()
    s.headers={"User-Agent":"Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36","Referer":"https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"}
    s.cookies.set_policy(BlockAll())
    s.mount('https://', DESAdapter())  
    s.timeout = 30   
    
    login = s.post('http://wapact.189.cn:9000/unified/user/login',json={"ticket":ticket,"backUrl":"https%3A%2F%2Fwapact.189.cn%3A9001","platformCode":"P201010301","loginType":2}).json()
    if login['code'] == 0:
        #printn(phone, "获取token","成功")
        s.headers["Authorization"] = "Bearer " + login["biz"]["token"]   

        r = s.get('http://wapact.189.cn:9000/gateway/golden/api/queryInfo').json()
    
        
        printn(f'{phone} 金豆余额 {r["biz"]["amountTotal"]}')


        queryBigDataAppGetOrInfo = s.get('http://wapact.189.cn:9000/gateway/golden/api/queryBigDataAppGetOrInfo?floorType=0&userType=1&page&1&order=2&tabOrder=').json()

        for i in queryBigDataAppGetOrInfo["biz"]["ExchangeGoodslist"]:
            if '话费' not in i["title"]:continue
            

            if '0.5元' in i["title"] or '5元' in  i["title"]:
                jp["9"][i["title"]] = i["id"]
            elif '1元' in i["title"] or '10元' in i["title"]:
                jp["13"][i["title"]] = i["id"]
            
                


        h = datetime.datetime.now().hour
        if  11 > h:
            h = 9            
        else:
            h = 13
        
        if len(sys.argv) ==2:
            h = int(sys.argv[1])
        
        d = jp[str(h)]
        
        wt = t(h) + kswt
        
        
        for di in d:
            
            
            
            if di not in dhjl[yf]:
                dhjl[yf][di] = ""
            if phone in dhjl[yf][di] :
                printn(f"{phone} {di} 已兑换")
                
            else:
                
                printn(f"{phone} {di}")
                if wt - time.time() > 20 * 60:
                    printn("等待时间超过20分钟")
                    return

                threading.Thread(target=dh,args=(phone,s,di,d[di],wt, uid)).start()
            
            
    else:
        
        printn(f"{phone} 获取token {login['message']}")
       
       

def first_request(res=''):
    global js, khhWNSbEsFUO
    with open('瑞数通杀.js', 'r') as f:
        js_code_ym = f.read()
    url = 'http://wapact.189.cn:9000/gateway/stand/detailNew/exchange'
    if res == '':
        response = ss.get(url)
        res =  response.text
        if 'Set-Cookie' in response.headers:
            
            khhWNSbEsFUO = re.findall('khhWNSbEsFUO=([^;]+)',response.headers['Set-Cookie'])[0]
    soup = BeautifulSoup(res, 'html.parser')
    scripts = soup.find_all('script')
    for script in scripts:
        if 'src' in str(script):
            rsurl =  re.findall('src="([^"]+)"', str(script))[0]
            
        if '$_ts=window' in script.get_text():
            ts_code = script.get_text()
            
    
    urls  = url.split('/')
    rsurl = urls[0] + '//' + urls[2] + rsurl
    #print(rsurl)    
    ts_code += requests.get(rsurl).text
    content_code = soup.find_all('meta')[1].get('content')
    
    js_code = js_code_ym.replace('content_code', content_code).replace("'ts_code'", ts_code)
    js = execjs.compile(js_code) 
    
    return content_code, ts_code, khhWNSbEsFUO

    
    
def main():
    global wt,rs
    r = ss.get('http://wapact.189.cn:9000/gateway/stand/detailNew/exchange')
    
    if '$_ts=window' in r.text:
        rs = 1
        print("瑞数加密已开启")
        first_request()
    else:
        print("瑞数加密已关闭")
        rs = 0       
         
    for i in chinaTelecomAccount.split('&'):
        i = i.split('@')
        phone = i[0]
        password = i[1]
        uid = i[-1]
        ticket = False 
        #ticket = get_userTicket(phone)  
        
        if phone in load_token:
            printn(f'{phone} 使用缓存登录')
            ticket = get_ticket(phone,load_token[phone]['userId'],load_token[phone]['token'])
        
        if ticket == False:
            printn(f'{phone} 使用密码登录')
            ticket = userLoginNormal(phone,password)
           
        if ticket:
            threading.Thread(target=ks,args=(phone, ticket, uid)).start()
            time.sleep(1)
        else:
            printn(f'{phone} 登录失败')
        

appToken = ""

chinaTelecomAccount = os.environ.get('jdhf')

if chinaTelecomAccount:
    main()
