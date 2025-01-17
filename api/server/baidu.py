import hashlib
import os
import random
import base64
import requests
import urllib
import time
from api import config, tools


config_server = "baidu"
default_translate_app_id = "20211109000995303"
default_translate_secret_key = "qLFDFx7fLRrioaa6CTnk"
default_ocr_app_key = "S1NHCzzzBhL2TUMx5iGpOSUu"
default_ocr_secret_key = "709INHX6GCLsAXXZPLhKGVMmra7bEwGl"


def translate_text(s, fromLang="auto", toLangZh=""):
    config_baidu = config.get_config_section(config_server)

    appId = config_baidu["translate_app_id"]
    secretKey = config_baidu["translate_secret_key"]

    if(len(appId) == 0 or len(secretKey) == 0):
        appId = default_translate_app_id
        secretKey = default_translate_secret_key

    translate_to_languages = config_baidu["translate_to_languages"]

    # fromLang = 'auto'   # 原文语种
    # toLang = 'zh'   # 译文语种
    toLang = translate_to_languages[tools.zh2LangPar(toLangZh)]

    text, ok = translate(s, appId, secretKey, fromLang, toLang)
    return text


def translate(s, appId, secretKey, fromLang="auto", toLang="zh"):
    ok = False

    salt = random.randint(32768, 65536)
    sign = appId + s + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    url = "https://api.fanyi.baidu.com/api/trans/vip/translate?appid=%s&q=%s&from=%s&to=%s&salt=%s&sign=%s"
    url = url % (appId, urllib.parse.quote(s), fromLang, toLang, salt, sign)
    try:
        request = requests.get(url)
        if(request.status_code == 200):
            result = request.json()
            if ("error_code" in result):
                s1 = "百度翻译请求错误：" + result["error_code"] + " " + result["error_msg"]
            else:
                ok = True
                s1 = result["trans_result"][0]["dst"]
        else:
            s1 = "请求错误：" + request.content

    except Exception as e:
        s1 = "网络错误：" + str(e)

    return s1, ok


def get_token_by_url(ocr_api_key, ocr_secret_key):
    ok = False
    access_token = ""
    expires_in_date = -1

    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s' % (
        ocr_api_key, ocr_secret_key)
    try:
        request = requests.get(host)

        jsons = request.json()
        if ("access_token" not in jsons):
            access_token = "错误：" + jsons["error_description"]
        else:
            access_token = jsons["access_token"]
            expires_in_date = time.time() + jsons["expires_in"]
            ok = True

    except Exception as e:
        access_token = "请求错误：" + str(e)

    return ok, str(access_token), expires_in_date


def get_token():
    ok = False
    access_token = ""

    config_baidu = config.get_config_section(config_server)
    expires_in_date = config_baidu["expires_in_date"]

    if (expires_in_date - time.time() > 0):
        access_token = config_baidu["access_token"]
        if(len(access_token) != 0):
            return ok, access_token

    ocr_api_key = config_baidu["ocr_api_key"]
    ocr_secret_key = config_baidu["ocr_secret_key"]

    if (len(ocr_api_key) == 0 or len(ocr_secret_key) == 0):
        ocr_api_key = default_ocr_app_key
        ocr_secret_key = default_ocr_secret_key

    ok, access_token, expires_in_date = get_token_by_url(ocr_api_key, ocr_secret_key)
    if(ok):
        config.set_config(config_server, "access_token", access_token)
        config.set_config(config_server, "expires_in_date", expires_in_date)
    return ok, access_token


def ocr(img_data, latex=False):
    # open('./images/lt.png', 'rb').read()
    '''
    通用文字识别
    '''
    s = ""
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/"
    if(latex):
        request_url += "formula"
    else:
        request_url += "general_basic"
    print(request_url)
    img = base64.b64encode(img_data)
    ok, token = get_token()
    params = {"image": img}
    request_url = request_url + "?access_token=" + token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)

    if response:
        jsons = (response.json())
        print(jsons)
        if ("error_code" in jsons):
            return str(jsons["error_code"]) + jsons["error_msg"]
        else:
            for word in jsons["words_result"]:
                s += word["words"]
                if(latex):
                    s += "\n"

    else:
        print(response.text)

    if(latex):
        s = s.replace(" _ ", "_")
    return s


def check_translate(appId, secretKey):
    text, ok = translate(
        "test",
        appId,
        secretKey,
        "auto",
        "zh",
    )
    return ok


def check_ocr(apiKey, secretKey):
    ok, access_token, expires_in_date = get_token_by_url(apiKey, secretKey)
    return ok
