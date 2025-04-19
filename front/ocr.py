
"""
  印刷文字识别WebAPI接口调用示例接口文档(必看)：https://doc.xfyun.cn/rest_api/%E5%8D%B0%E5%88%B7%E6%96%87%E5%AD%97%E8%AF%86%E5%88%AB.html
  上传图片base64编码后进行urlencode要求base64编码和urlencode后大小不超过4M最短边至少15px，最长边最大4096px支持jpg/png/bmp格式
  (Very Important)创建完webapi应用添加合成服务之后一定要设置ip白名单，找到控制台--我的应用--设置ip白名单，如何设置参考：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=41891
  错误码链接：https://www.xfyun.cn/document/error-code (code返回错误码时必看)
  @author iflytek
"""
import base64
import hashlib
import json
import os
import time

# -*- coding: utf-8 -*-
import requests
from dotenv import load_dotenv

#from urllib import parse
# 印刷文字识别 webapi 接口地址
URL = "http://webapi.xfyun.cn/v1/service/v1/ocr/general"
# 加载环境变量
load_dotenv()

# 获取环境变量中的配置
APPID = os.getenv('XFYUN_APPID')
API_KEY = os.getenv('XFYUN_API_KEY')
if not APPID or not API_KEY:
    raise ValueError("请在.env文件中配置XFYUN_APPID和XFYUN_API_KEY")
def getHeader():
#  当前时间戳
    curTime = str(int(time.time()))
#  支持语言类型和是否开启位置定位(默认否)
    param = {"language": "cn|en", "location": "false"}
    param = json.dumps(param)
    paramBase64 = base64.b64encode(param.encode('utf-8'))

    m2 = hashlib.md5()
    str1 = API_KEY + curTime + str(paramBase64,'utf-8')
    m2.update(str1.encode('utf-8'))
    checkSum = m2.hexdigest()
# 组装http请求头
    header = {
        'X-CurTime': curTime,
        'X-Param': paramBase64,
        'X-Appid': APPID,
        'X-CheckSum': checkSum,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }
    return header


# front/ocr.py
def process_image(image_path):
    """处理图片并返回OCR结果文本列表"""
    with open(image_path, 'rb') as f:
        image_data = f.read()

    image_base64 = str(base64.b64encode(image_data), 'utf-8')
    data = {'image': image_base64}

    response = requests.post(URL, data=data, headers=getHeader())
    result = str(response.content, 'utf-8')
    result_dict = json.loads(result)

    if result_dict['code'] == '0':
        text_list = []
        blocks = result_dict.get('data', {}).get('block', [])
        for block in blocks:
            for line in block.get('line', []):
                for word in line.get('word', []):
                    if 'content' in word:
                        text_list.append(word['content'])
        return text_list
    else:
        raise Exception(f"OCR识别失败：{result_dict.get('desc', '未知错误')}")