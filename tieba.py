#! /usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from selenium import webdriver
from lxml import etree
from PIL import Image
import time
import re
import os
import sys
import json
import threading
import random
from io import BytesIO
from config import *

def login(user, username, passwd, url = 'https://tieba.baidu.com/index.html'):

	option = webdriver.ChromeOptions()
	option.add_argument('--no-sandbox')
	option.add_argument('--disable-extensions')
	option.add_argument('--headless')
	option.add_argument('lang=zh_CN.UTF-8')
	option.add_argument('--disable-gpu')
	option.add_argument('--disable-dev-shm-usage')
	driver = webdriver.Chrome(executable_path='chromedriver', options=option)
	driver.get(url)
	time.sleep(0.16)
	print('正在登录:%s...' % user)
	driver.find_element_by_xpath('//*[@id="com_userbar"]/ul/li[4]/div/a').click() # 点击登录按钮
	time.sleep(1)
	driver.find_element_by_xpath('//*[@id="TANGRAM__PSP_10__footerULoginBtn"]').click() # 点击用户名登录
	driver.find_element_by_xpath('//*[@id="TANGRAM__PSP_10__userName"]').send_keys(username) # 帐号
	driver.find_element_by_xpath('//*[@id="TANGRAM__PSP_10__password"]').send_keys(passwd) # 帐号
	driver.find_element_by_xpath('//*[@id="TANGRAM__PSP_10__submit"]').click() # 点击登录按钮
	time.sleep(2.5)
	try:
		driver.find_element_by_xpath('//*[@id="TANGRAM__25__content_select_uname"]').click()
		verification = 1 # 单二代验证
	except:
		print('尝试验证码 + 二代验证中...')
		try:
		    element = driver.find_element_by_id('TANGRAM__PSP_10__verifyCodeImg')
		    verification = 2 # 验证码+二代验证
		except:
		    print('可能不需要验证码验证')
	
	if verification == 1:
		time.sleep(1)
		mode = input('需要二代验证,输入验证方式的序号\n1.手机验证\n2.密保邮箱验证\n请输入验证方式:')
		driver.find_element_by_xpath('//*[@id="TANGRAM__25__select_email"]').click()
		driver.find_element_by_xpath('//*[@id="TANGRAM__25__button_send_email"]').click()
		vcode = input('请输入验证码:')
		driver.find_element_by_xpath('//*[@id="TANGRAM__25__input_vcode"]').send_keys(vcode)
		driver.find_element_by_xpath('//*[@id="TANGRAM__25__button_submit"]').click()
		time.sleep(2.5)
		cookies = driver.get_cookies()
	elif verification == 2:
		driver.save_screenshot("/tmp/codingpy.png")
		time.sleep(3)
		size = driver.find_element_by_id('TANGRAM__PSP_10__verifyCodeImg').size
		left = int(element.location['x'])
		top = int(element.location['y'])
		right = int(element.location['x'] + element.size['width'])
		bottom = int(element.location['y'] + element.size['height'])
		im = Image.open('/tmp/codingpy.png')
		im = im.crop((left, top, right, bottom))
		im.save('code.png')
		ucode = input('请打开code.png查看验证码\n验证码:')
		driver.find_element_by_xpath('//*[@id="TANGRAM__PSP_10__verifyCode"]').send_keys(ucode) # 输入验证码
		driver.find_element_by_xpath('//*[@id="TANGRAM__PSP_10__submit"]').click() # 点击登录按钮
		time.sleep(3)
		driver.find_element_by_xpath('//*[@id="TANGRAM__25__content_select_uname"]').click()
		time.sleep(1)
		mode = input('需要二代验证,输入验证方式的序号\n1.手机验证\n2.密保邮箱验证\n请输入验证方式:')
		driver.find_element_by_xpath('//*[@id="TANGRAM__25__select_email"]').click()
		driver.find_element_by_xpath('//*[@id="TANGRAM__25__button_send_email"]').click()
		vcode = input('请输入验证码:')
		driver.find_element_by_xpath('//*[@id="TANGRAM__25__input_vcode"]').send_keys(vcode)
		driver.find_element_by_xpath('//*[@id="TANGRAM__25__button_submit"]').click()
		time.sleep(2.5)
		cookies = driver.get_cookies()
	else:
		print('未知错误！')
		os.system("pkill chrome*")
		sys.exit(0)


	print('登录成功!')
	os.system("pkill chrome*")
	return cookies

def gettbs(cookies, tieba):

	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'}
	r = requests.get('http://tieba.baidu.com/f?kw=%s' % tieba, headers = headers, cookies = cookies)
	tbslist = re.findall("'tbs':'(.+?)'", r.text)
	tbstr = "".join(tbslist)
	return tbstr

def getbar(cookies):

	url = 'http://tieba.baidu.com/f/like/mylike?pn='
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'}
	r_bar = requests.get(url + '1', headers = headers, cookies = cookies)
	webpage = etree.HTML(r_bar.text)

	pages = ['1']
	pns = webpage.xpath('//*[@id="j_pagebar"]/div/a') # 判断页数
	for pn in pns:
		if pn.text.isnumeric():
			pages.append(pn.text)

	tiebas = []
	for pageid in pages:
		r_bar_1 = requests.get(url + pageid, headers = headers, cookies = cookies)
		webpage = etree.HTML(r_bar_1.text)
		tag_a = webpage.xpath('//a[@title]') # 获取贴吧
		for a in tag_a:
			if a.text:
				tiebas.append(a.text)

	return tiebas

def recognize_captcha(remote_url, rec_times):

    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
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
	r = requests.post('http://tieba.baidu.com/sign/add', headers = headers, data = data, cookies = cookies)
	try:
		resp = r.json()
		if resp['data']['errmsg'] == 'success':
			print('贴吧:%s\t' % tieba, end = '')
			print('状态:打码签到成功!')

	except:
		resp = r.json()
		print('贴吧:%s\t' % tieba, end = '')
		print('状态:%s' % resp['error'])

def sign(cookies, tieba):

	tbs = gettbs(cookies, tieba)
	headers = {
		'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
		'Origin':'http://tieba.baidu.com',
		'Referer':'http://tieba.baidu.com',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
	}

	"""
	data = {
		'ie':'utf-8',
		'tbs':tbs, # 一键签到 只能签到规定数量的贴吧
	}
	"""

	data = {
		'ie':'utf-8',
		'kw':tieba,
		'tbs':tbs # 分开签到
	}
	r = requests.post('http://tieba.baidu.com/sign/add', headers = headers, data = data, cookies = cookies)
	try:
		resp = r.json()
		if resp['data']['errmsg'] == 'success':
			print('贴吧:%s\t' % tieba, end = '')
			print('状态:签到成功!')
	
	except:
		resp = r.json()
		if resp['error'] == 'need vcode': # 需要验证码
			captcha_vcode_str = resp['data']['captcha_vcode_str']
			captcha_url = 'https://tieba.baidu.com/cgi-bin/genimg?%s' % captcha_vcode_str
			captcha_input_str = recognize_captcha(captcha_url, 1)
			sign_vcode(tieba,tbs,captcha_input_str,captcha_vcode_str,cookies,headers)
		else:
			print('贴吧:%s\t' % tieba, end = '') # 黑名单或者别的情况
			print('状态:%s' % resp['error'])

def login_cookies(user, username, passwd):

	cookie = login(user, username, passwd)
	for item in cookie:
		s.cookies.set(item['name'],item['value'])
	cookies = requests.utils.dict_from_cookiejar(s.cookies)
	with open('.%s' % user,'w') as fp:
		json.dump(cookies,fp)
		fp.close()
	tiebas = getbar(cookies)
	list.extend(tiebas)

	threads=[]
	for i in range(len(tiebas)): # 多少个贴吧就分配多少个线程
		t=threading.Thread(target=sign,args=(cookies, tiebas[0+i]))
		threads.append(t)
	
	for i in threads:
		i.start()

	for i in threads:
		i.join()
	
	s.cookies.clear()
	os.system("pkill chrome*")

def main():
	for x in range(len(users)):
		user = users[x]
		username = accounts[user]['username']
		passwd = accounts[user]['password']
		if os.path.exists('.%s' % user):
			with open('.%s' % user,'r') as fp1:
				load_cookies = json.load(fp1)
			cookies = requests.utils.cookiejar_from_dict(load_cookies)
			print('正在使用Cookies登录:%s...' % user)
			r = requests.get('http://tieba.baidu.com/sysmsg/query/userunread', cookies = cookies)
			resp = r.json()
			if resp['errmsg'] == '成功':
				tiebas = getbar(cookies)
				list.extend(tiebas)

				threads=[] 
				for i in range(len(tiebas)):
					t=threading.Thread(target=sign,args=(cookies, tiebas[0+i]))
					threads.append(t)
				
				for i in threads:
					i.start()
				
				for i in threads:
					i.join()

				os.system("pkill chrome*")
			else:
				print('%sCookies失效...正在重新登录...' % user)
				login_cookies(user, username, passwd)
		else:
			login_cookies(user, username, passwd)

if __name__ == '__main__':
	list = []
	s = requests.session()
	start = time.time()
	main()
	end = time.time()
	print('总共签到{}个贴吧,耗时:{}秒'.format(len(list), int(end - start)))
