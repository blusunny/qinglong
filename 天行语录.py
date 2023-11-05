# 原作者@author Sten  
# 原作者仓库:https://github.com/aefa6/QinglongScript.git  
# 原代码运行输出不成功，在“文心一言”的帮助下成功输出了内容，哈哈（20231105）  
# 自行修改11、25、26三行，其中11行的api必填.  
# 需要在天行提前注册获取api(https://www.tianapi.com/console/,数据管理-我的密钥key)并申请相应接口才能使用，https://www.tianapi.com/list/  

import requests  
import json  
import notify  
  
api = "天行API密钥" # 这里填写你在天行API注册的密钥  
  
pyurl = f'https://apis.tianapi.com/pyqwenan/index?key={api}' #朋友圈文案   
caurl = f'https://apis.tianapi.com/caihongpi/index?key={api}' #彩虹屁  
tiurl = f'https://apis.tianapi.com/tiangou/index?key={api}' #舔狗日志  
zaurl = f'https://apis.tianapi.com/zaoan/index?key={api}' #早安心语   
saurl = f'https://apis.tianapi.com/saylove/index?key={api}' #土味情话
mrurl = f'https://apis.tianapi.com/bulletin/index?key={api}' #每日简报
lrurl = f'https://apis.tianapi.com/joke/index?key={api}' #雷人笑话
hsurl = f'https://apis.tianapi.com/hsjz/index?key={api}' #失恋分手句子 
zhurl = f'https://apis.tianapi.com/zhanan/index?key={api}' #渣男语录  
waurl = f'https://apis.tianapi.com/wanan/index?key={api}' #晚安心语 
duurl = f'https://apis.tianapi.com/dujitang/index?key={api}' #毒鸡汤  

urls = [pyurl, caurl, tiurl, mrurl, zaurl, lrurl, saurl] # 按照格式填写你要推送的内容对应的url，默认是朋友圈文案、舔狗日志和毒鸡汤  
count = 2 # 相同类型推文的数量，默认是两条  
  
contents = ""  
for url in urls:  
    for i in range(count):  
        response = requests.get(url)  
        data = json.loads(response.text)  
        contents += data.get('result', {}).get('content', '') + "\n" + "\n"  
notify.send("语录", contents)
