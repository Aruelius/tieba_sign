#! /usr/bin/env python
#coding:utf-8
import os
import requests
import time
import json
import pyzbar.pyzbar as pyzbar
from PIL import Image
from lxml import etree
from io import BytesIO
import threading
from fake_useragent import UserAgent

def getTimestamp():
    return str(int(time.time() * 1000))

def saveCookiesForUser(user):
    ck_dict = s.cookies.get_dict()
    with open('.%s' % user, 'w') as f:
        ck_str = json.dumps(ck_dict)
        f.write(ck_str)
        f.close()

def loadCookiesForUser(user):
    with open('.%s' % user,'r') as fp1:
        load_cookies = json.loads(fp1.read())
    return load_cookies

def unicast(channel_id):
    tt = getTimestamp()
    r = s.get(
        url = 'https://passport.baidu.com/channel/unicast',
        params = {
            'channel_id': channel_id,
            'tpl': 'tb',
            'apiver': 'v3',
            'callback': '',
            'tt': tt,
            '_': tt
        }
    )
    rsp = r.text.replace('(','').replace(')','')
    rsp_json = json.loads(rsp)
    try:
        channel_v = json.loads(rsp_json['channel_v'])
        return channel_v
    except:
        print('扫描超时')

def qrbdusslogin(bduss):
    tt = getTimestamp()
    r = s.get(
        url = 'https://passport.baidu.com/v3/login/main/qrbdusslogin',
        params = {
            'v': tt,
            'bduss': bduss,
            'u': 'https://tieba.baidu.com/index.html',
            'loginVersion': 'v4',
            'qrcode': '1',
            'tpl': 'tb',
            'apiver': 'v3',
            'tt': tt,
            'alg': 'v1',
            'time': tt[10:],
        }
    )
    rsp = json.loads(r.text.replace("'",'"'))
    bdu = rsp['data']['hao123Param']
    s.get(f'https://user.hao123.com/static/crossdomain.php?bdu={bdu}&t={tt}')
    s.get('http://tieba.baidu.com/f/like/mylike?pn=')

def readQRcode(imgurl):
    downQRcode(imgurl)
    img = Image.open('qrcode.png')
    barcodes = pyzbar.decode(img)
    for barcode in barcodes:
        barcodeData = barcode.data.decode("utf-8")
        return barcodeData

def downQRcode(imgurl):
    r = s.get(f'https://{imgurl}')
    with open('qrcode.png', 'wb') as f:
        f.write(r.content)
        f.close()

def getQRcode():
    tt = getTimestamp()
    r = s.get(
        url = 'https://passport.baidu.com/v2/api/getqrcode',
        params = {
            'lp': 'pc',
            'qrloginfrom': 'pc',
            'apiver': 'v3',
            'tt': tt,
            'tpl': 'tb',
            '_': tt
        }
    )
    app = input('有百度贴吧APP / 百度APP，请输入 1 ，没有请输入 2：')
    imgurl = r.json()['imgurl']
    while True:
        if app == '1':
            print(f'请使用浏览器打开二维码链接并使用百度贴吧APP / 百度APP扫描：https://{imgurl}')
            print('注意：请使用IE浏览器打开二维码链接！！！')
            break
        elif app == '2':
            qrurl = readQRcode(imgurl)
            print(f'请使用已经登录了百度贴吧网页端的浏览器打开链接并按照提示完成登陆：{qrurl}')
            break
    
    channel_id = r.json()['sign']
    return channel_id

def qrlogin(user):
    channel_id = getQRcode()
    while True:
        rsp = unicast(channel_id)
        if rsp:
            if rsp['status'] == 1:
                print('扫描成功,请在手机端确认登录!')
            if rsp['status'] == 0:
                print('确认登陆成功')
                bduss = rsp['v']
                # print(f'bduss:{bduss}')
                qrbdusslogin(bduss)
                saveCookiesForUser(user)
                break

def login(user):
    qrlogin(user)
    print('Login : True')
    load_cookies = loadCookiesForUser(user)
    cookies = requests.utils.cookiejar_from_dict(load_cookies)
    s.cookies.update(cookies)
    tiebas = getbar()
    list.extend(tiebas)
    start(tiebas)

def checkLogin():
    r = s.get('https://tieba.baidu.com/f/user/json_userinfo')
    try:
        print(r.json()['data']['user_name_weak'])
        return True
    except:
        return False

def getbar():
    url = 'http://tieba.baidu.com/f/like/mylike?pn='
    r_bar = s.get(url + '1')
    webpage = etree.HTML(r_bar.text)

    pages = ['1']
    pns = webpage.xpath('//*[@id="j_pagebar"]/div/a') # 判断页数
    for pn in pns:
        if pn.text.isnumeric():
            pages.append(pn.text)

    tiebas = []
    for pageid in pages:
        r_bar_1 = s.get(url + pageid)
        webpage = etree.HTML(r_bar_1.text)
        tag_a = webpage.xpath('//a[@title]') # 获取贴吧
        for a in tag_a:
            if a.text:
                tiebas.append(a.text)
    return tiebas

def recognize_captcha(remote_url, rec_times):
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/\
                537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
    }

    for _ in range(rec_times):
        # 请求
        while True:
            try:
                response = requests.request("GET", remote_url, headers=headers, timeout=6)
                if response.text:
                    break
                else:
                    print("retry, response.text is empty")
            except Exception as ee:
                print(ee)

        # 识别
        url = "http://222.187.238.211:10086/b"
        files = {'image_file': ('captcha.jpg', BytesIO(response.content), 'application')}
        r = requests.post(url=url, files=files)

        # 识别结果
        try:
            predict_text = json.loads(r.text)["value"]
            return predict_text
        except:
            recognize_captcha(remote_url, rec_times)

def sign_vcode(tieba, tbs, captcha_input_str, captcha_vcode_str):

    data = {
        'ie':'utf-8',
        'kw':tieba,
        'tbs':tbs,
        'captcha_input_str':captcha_input_str,
        'captcha_vcode_str':captcha_vcode_str
    }
    r = s.post('http://tieba.baidu.com/sign/add', data = data)
    try:
        resp = r.json()
        if resp['data']['errmsg'] == 'success':
            print('贴吧:%s\t' % tieba, end = '')
            print('状态:打码签到成功!')

    except:
        print('贴吧:%s\t' % tieba, end = '')
        print('状态:%s' % resp['error'])

def gettbs():
    r = s.get('http://tieba.baidu.com/dc/common/tbs')
    try:
        resp = r.json()
        return resp['tbs']
    except:
        time.sleep(1.2)
        gettbs()
        
def sign(tieba):
    tbs = gettbs()

    data = {
        'ie':'utf-8',
        'kw':tieba,
        'tbs':tbs
    }
    r = s.post('http://tieba.baidu.com/sign/add', data = data)
    try:
        resp = r.json()
        if resp['data']['errmsg'] == 'success':
            print('贴吧:%s\t' % tieba, end = '')
            print('状态:签到成功!')
    except:
        if resp['error'] == 'need vcode': # 需要验证码
            captcha_vcode_str = resp['data']['captcha_vcode_str']
            captcha_url = 'https://tieba.baidu.com/cgi-bin/genimg?%s' % captcha_vcode_str
            captcha_input_str = recognize_captcha(captcha_url, 1)
            sign_vcode(tieba,tbs,captcha_input_str,captcha_vcode_str)
        else:
            print('贴吧:%s\t' % tieba, end = '') # 黑名单或者别的情况
            print('状态:%s' % resp['error'])

def start(tiebas):
    threads=[] 
    for tieba in tiebas:
        t=threading.Thread(target=sign,args=(tieba,))
        threads.append(t)
    
    for tieba in threads:
        tieba.start()
    
    for tieba in threads:
        tieba.join()

def main():
    for user in users:
        ua = UserAgent(verify_ssl=False).random
        s.headers.update({'User-Agent': ua})
        if os.path.exists('.%s' % user):
            load_cookies = loadCookiesForUser(user)
            cookies = requests.utils.cookiejar_from_dict(load_cookies)
            s.cookies.update(cookies)
            if checkLogin():
                print('CookieLogin : True')
                tiebas = getbar()
                list.extend(tiebas)
                start(tiebas)
            else:
                 print('%sCookies失效...正在重新登录...' % user)
                 login(user)
        else:
            login(user)

        s.cookies.clear()
        s.headers.clear()



if __name__ == "__main__":
    list = []
    users = ['', '']
    s = requests.session()
    start_time = time.time()
    main()
    end_time = time.time()
    print('总共签到{}个贴吧,耗时:{}秒'.format(len(list), int(end_time - start_time)))
