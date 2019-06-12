#! /usr/bin/env python
# -*- coding: utf-8 -*-	
import requests
import time
import random
import os.path
import re
import threading
import json
import rsa
import base64
from lxml import etree
from io import BytesIO
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from fake_useragent import UserAgent
from urllib import parse
from config import *

AK = '1e3f2dd1c81f2075171a547893391274'

def getTime():
	return str(int(time.time() * 1000))

def getGID():
    def transform(char):
        if char == "4" or char == "-": return char
        number = random.randint(0, 15)
        if char != "x": number = 3 & number | 8
        return format(number, "x").upper()
    return "".join([transform(c) for c in "xxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"])

def getToken():
	tt = getTime()

	params = {
		'tpl': 'tb',
		'apiver': 'v3',
		'tt': tt,
		'class': 'login',
		'gid': gid,
	}

	r = s.get(f'https://passport.baidu.com/v2/api/?getapi', params = params,
					headers = {'User-Agent': ua}).text
	token = ''.join(re.findall(' "token" : "(.+?)"', r))
	return token

def saveCookiesForUser(cookie):
    ck_dict = requests.utils.dict_from_cookiejar(cookie)
    with open('.%s' % user, 'w') as f:
        ck_dict = str(ck_dict).replace("'", '"')
        f.write(ck_dict)
        f.close()

def loadCookiesForUser():
    with open('.%s' % user,'r') as fp1:
        load_cookies = json.load(fp1)
    return load_cookies

def loginCheck():
	tt = getTime()
	params = {
		'token': token,
		'tpl': 'tb',
		'apiver': 'v3',
		'tt': tt,
		'username': username,
	}
	r = s.get('https://passport.baidu.com/v2/api/?logincheck', params = params).json()
	codeString, vcodetype = r['data']['codeString'], r['data']['vcodetype']

	return codeString, vcodetype

def getKey():
	tt = getTime()

	params = {
		'token': token,
		'tpl': 'tb',
		'apiver': 'v3',
		'tt': tt,
		'gid': gid,
	}

	r = s.get('https://passport.baidu.com/v2/getpublickey', params = params, 
					headers = {'User-Agent': ua}).text
	resp = r.replace("'", '"')
	pubkey = json.loads(resp)['pubkey']
	key = json.loads(resp)['key']
	return pubkey, key

def getDSTK():
	r = s.get(f'https://passport.baidu.com/viewlog?ak={AK}').json()
	
	tk = r['data']['tk']
	ds = r['data']['ds']
	return tk, ds

def getPassword():
	pubkey, key = getKey()
	en_pwd = base64.b64encode(
		rsa.encrypt(
			(password).encode('utf-8'),
			rsa.PublicKey.load_pkcs1_openssl_pem(pubkey.encode())
		)
	)
	pwd = bytes.decode(en_pwd)
	return pwd, key

def  loginReq(data):
	r = s.post('https://passport.baidu.com/v2/api/?login', data = data, 
					headers = {'User-Agent': ua})
	resp = ''.join(re.findall('"err(.+?);', r.text))
	return resp

def getBDU(ltoken, lstr):
	tt = getTime()
	params = {
		'u': 'https://tieba.baidu.com/index.html',
		'tpl': 'tb',
		'ltoken': ltoken,
		'lstr': lstr,
		'actiontype': '3',
		'apiver': 'v3',
		'tt': tt,
	}
	r = s.get('https://passport.baidu.com/v2/?loginproxy', params = params)
	bdu = ''.join(re.findall('"hao123Param" : "(.+?)"', r.text))
	return bdu

def checkSMS(authtoken, lstr, ltoken, codeString, vcodetype):
	vcode = input('手机验证码：')
	params = {
		'authtoken': authtoken,
		'type': 'mobile',
		'jsonp': '1',
		'apiver': 'v3',
		'action': 'check',
		'vcode': vcode,
		'u': 'https://tieba.baidu.com/index.html',
		'lstr': lstr,
		'ltoken': ltoken,
		'tpl': 'tb',
	}
	r = s.get('https://passport.baidu.com/v2/sapi/authwidgetverify', params = params)
	rsp = r.text.replace("'", '"')
	json1 = json.loads(rsp)
	
	if json1['errno'] in ['110000']:
		bdu = getBDU(ltoken, lstr)
		tt = getTime()
		r1 = s.get(f'https://user.hao123.com/static/crossdomain.php?bdu={bdu}&t={tt}')
		r3 = s.get('http://tieba.baidu.com/f/like/mylike?pn=')
		saveCookiesForUser(s.cookies)
		s.cookies.clear()
		s.headers.clear()
	else:
		print(json1['msg'])
		checkSMS(authtoken, lstr, ltoken, codeString, vcodetype)

def checkMail(authtoken, lstr, ltoken, codeString, vcodetype):
	vcode = input('邮件验证码:')
	print(vcode)
	params = {
		'authtoken': authtoken,
		'type': 'email',
		'jsonp': '1',
		'apiver': 'v3',
		'action': 'check',
		'vcode': vcode,
		'u': 'https://tieba.baidu.com/index.html',
		'lstr': lstr,
		'ltoken': ltoken,
		'tpl': 'tb',
	}

	r = s.get('https://passport.baidu.com/v2/sapi/authwidgetverify', params = params)
	rsp = r.text.replace("'", '"')
	json1 = json.loads(rsp)
	
	if json1['errno'] in ['110000']:
		bdu = getBDU(ltoken, lstr)
		tt = getTime()
		r1 = s.get(f'https://user.hao123.com/static/crossdomain.php?bdu={bdu}&t={tt}')
		r3 = s.get('http://tieba.baidu.com/f/like/mylike?pn=') # 不访问一下这个会出毛病。。。
		saveCookiesForUser(s.cookies)
		s.cookies.clear()
		s.headers.clear()
	else:
		print(json1['msg'])
		checkMail(authtoken, lstr, ltoken, codeString, vcodetype)

def SendSMS(authtoken, lstr, ltoken, codeString, vcodetype):
	params = {
		'authtoken': authtoken,
		'type': 'mobile',
		'jsonp': '1',
		'action': 'send',
		'u': 'https://tieba.baidu.com/index.html',
		'lstr': lstr,
		'ltoken': ltoken,
		'tpl': 'tb',
	}
	r = s.get('https://passport.baidu.com/v2/sapi/authwidgetverify', params = params)
	checkSMS(authtoken, lstr, ltoken, codeString, vcodetype)

def SendMail(authtoken, lstr, ltoken, codeString, vcodetype):
	params = {
		'authtoken': authtoken,
		'type': 'email',
		'jsonp': '1',
		'action': 'send',
		'u': 'https://tieba.baidu.com/index.html',
		'lstr': lstr,
		'ltoken': ltoken,
		'tpl': 'tb',
	}
	r = s.get('https://passport.baidu.com/v2/sapi/authwidgetverify', params = params)
	checkMail(authtoken, lstr, ltoken, codeString, vcodetype)

def TwoVerify(resp, codeString, vcodetype):
	Resp  = parse.unquote_plus(resp)
	authtoken = re.findall('authtoken=(.+?)&', Resp)[0]
	ltoken = re.findall('ltoken=(.+?)&', Resp)[0]
	lstr = re.findall('lstr=(.+?)&', Resp)[0]
	lstr = parse.unquote_plus(lstr)

	params = {
		'authtoken': authtoken,
		'jsonp': '1',
		'apiver': 'v3',
		'action': 'getapi',
		'u': 'https://tieba.baidu.com/index.html',
		'lstr': lstr,
		'ltoken': ltoken,
		'tpl': 'tb',
	}

	r = s.get('https://passport.baidu.com/v2/sapi/authwidgetverify', params = params,
					headers = {'User-Agent': ua}).text.replace("'", '"').replace('|| ""', '')
	json1 = json.loads(r)
	
	try:
		if json1['msg'] == '系统繁忙，请稍后再试':
			print(json1['msg'])
			os._exit(0)
		else:
			verification = input('1.邮箱验证  2.手机验证\n请选择登录验证方式：')
			if verification == '2':
				mobile = json1['data']['mobile']
				if mobile:
					print(f'已经发送验证码给：{mobile}')
					SendSMS(authtoken, lstr, ltoken, codeString, vcodetype)
				else:
					print('账户没有绑定手机号！')
					os._exit(0)
			elif verification == '1':
				mail = json1['data']['email']
				print(f'已经发送邮件给：{mail}')
				SendMail(authtoken, lstr, ltoken, codeString, vcodetype)
			else:
				print('选择错误,退出...')
				os._exit(0)
	
	except KeyboardInterrupt:
		print('\n用户退出！')
		os._exit(0)
	except:
		print('未知错误！') # 由于没遇到过没绑定邮箱跟手机号的账号，所以先未知错误
		os._exit(0)

def login():
	print(f'正在登陆：{user}')
	tt = getTime()
	pwd, rsakey = getPassword()
	tk, ds = getDSTK()
	codeString, vcodetype = loginCheck()

	data = {
		'token': token,
		'tpl': 'tb',
		'apiver': 'v3',
		'tt': tt,
		'u': 'https://tieba.baidu.com/index.html',
		'gid': gid,
		'username': username,
		'password': pwd,
		'rsakey': rsakey,
		'crypttype': '12',
		'ds': ds,
		'tk': tk
	}

	if codeString:
		print('需要验证码,请打开下方链接查看')
		print(f'https://passport.baidu.com/cgi-bin/genimage?{codeString}')
		
		verifycode = input('验证码：')
		data['codestring'] = codeString
		data['verifycode'] = verifycode
		data['vcodefrom'] = 'checkuname'
		resp = loginReq(data)
		
		TwoVerify(resp, codeString, vcodetype) # 二次验证
	else:
		resp = loginReq(data)
		TwoVerify(resp, codeString, vcodetype)

def getbar(cookies):
	url = 'http://tieba.baidu.com/f/like/mylike?pn='
	r_bar = requests.get(url + '1', cookies = cookies)
	webpage = etree.HTML(r_bar.text)

	pages = ['1']
	pns = webpage.xpath('//*[@id="j_pagebar"]/div/a') # 判断页数
	for pn in pns:
		if pn.text.isnumeric():
			pages.append(pn.text)

	tiebas = []
	for pageid in pages:
		r_bar_1 = requests.get(url + pageid, cookies = cookies)
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

	for index in range(rec_times):
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
	    url = "http://1i1.tw:10086/b"
	    files = {'image_file': ('captcha.jpg', BytesIO(response.content), 'application')}
	    r = requests.post(url=url, files=files)

	    # 识别结果
	    predict_text = json.loads(r.text)["value"]

	    return predict_text

def sign_vcode(tieba, tbs, captcha_input_str, captcha_vcode_str, cookies, headers):

	data = {
		'ie':'utf-8',
		'kw':tieba,
		'tbs':tbs,
		'captcha_input_str':captcha_input_str,
		'captcha_vcode_str':captcha_vcode_str
	}
	r = requests.post('http://tieba.baidu.com/sign/add', headers = headers, 
						data = data, cookies = cookies)
	try:
		resp = r.json()
		if resp['data']['errmsg'] == 'success':
			print('贴吧:%s\t' % tieba, end = '')
			print('状态:打码签到成功!')

	except:
		print('贴吧:%s\t' % tieba, end = '')
		print('状态:%s' % resp['error'])

def gettbs(cookies):
	r = requests.get('http://tieba.baidu.com/dc/common/tbs', cookies = cookies).json()
	return r['tbs']

def sign(cookies, tieba):
	tbs = gettbs(cookies)
	headers = {
		'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
		'Origin':'http://tieba.baidu.com',
		'Referer':'http://tieba.baidu.com',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWeb\
		Kit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
	}

	data = {
		'ie':'utf-8',
		'kw':tieba,
		'tbs':tbs
	}
	r = requests.post('http://tieba.baidu.com/sign/add', headers = headers, 
						data = data, cookies = cookies)
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
			sign_vcode(tieba,tbs,captcha_input_str,captcha_vcode_str,cookies,headers)
		else:
			print('贴吧:%s\t' % tieba, end = '') # 黑名单或者别的情况
			print('状态:%s' % resp['error'])

def Start(tiebas, cookies):
	threads=[] 
	for i in tiebas:
		t=threading.Thread(target=sign,args=(cookies, i))
		threads.append(t)
	
	for i in threads:
		i.start()
	
	for i in threads:
		i.join()

def main():
	global user, username, password, s, ua, gid, token, mailuser, mailpwd
	ua = UserAgent(verify_ssl=False).random
	for user in users:
		username = accounts[user]['username']
		password = accounts[user]['password']
		mailuser = accounts[user]['mailuser']
		mailpwd = accounts[user]['mailpwd']
		s = requests.session()
		r = s.get('https://tieba.baidu.com')
		if os.path.exists('.%s' % user):
			load_cookies = loadCookiesForUser()
			cookies = requests.utils.cookiejar_from_dict(load_cookies)

			print(f'正在使用Cookies登陆:{user}')
			r = s.get('http://tieba.baidu.com/sysmsg/query/userunread', 
						cookies = cookies).json()
			if r['errmsg'] == '成功':
				tiebas = getbar(cookies)
				list.extend(tiebas)
				Start(tiebas, cookies)
			else:
				print('%sCookies失效...正在重新登录...' % user)
				gid = getGID()
				token = getToken()
				login()
				load_cookies = loadCookiesForUser()
				cookies = requests.utils.cookiejar_from_dict(load_cookies)
				tiebas = getbar(cookies)
				list.extend(tiebas)
				Start(tiebas, cookies)
		else:
			gid = getGID()
			token = getToken()
			login()
			load_cookies = loadCookiesForUser()
			cookies = requests.utils.cookiejar_from_dict(load_cookies)
			tiebas = getbar(cookies)
			list.extend(tiebas)
			Start(tiebas, cookies)

if __name__ == '__main__':
	list = []
	start = time.time()
	main()
	end = time.time()
	print('总共签到{}个贴吧,耗时:{}秒'.format(len(list), int(end - start)))
