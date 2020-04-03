#!/usr/bin/env python3
# coding=utf-8
import hashlib
import json
import os
import prettytable as pt
import pyzbar.pyzbar as pyzbar
import requests
import time
from io import BytesIO
from PIL import Image
from random import choice
from threading import Thread
import schedule


class Tieba(object):
    def __init__(self, users):
        self.users = users
        self.tb = pt.PrettyTable()
        self.s = requests.session()
        self.s.keep_alive = False

        self.MD5_KEY = 'tiebaclient!!!'
        self.CAPTCHA_API = 'http://222.187.238.211:10086/b'
        self.INDEX_URL = 'https://tieba.baidu.com/index.html'
        self.TBS_URL = 'http://tieba.baidu.com/dc/common/tbs'
        self.LIKES_URL = 'http://c.tieba.baidu.com/c/f/forum/like'
        self.SIGN_URL = 'http://c.tieba.baidu.com/c/c/forum/sign'
        self.GEN_IMG_URL = 'https://tieba.baidu.com/cgi-bin/genimg'
        self.QR_CODE_URL = 'https://passport.baidu.com/v2/api/getqrcode'
        self.UNICAST_URL = 'https://passport.baidu.com/channel/unicast'
        self.USER_INFO_URL = 'https://tieba.baidu.com/f/user/json_userinfo'
        self.QR_LOGIN_URL = 'https://passport.baidu.com/v3/login/main/qrbdusslogin'
        self.HAO123_URL = 'https://user.hao123.com/static/crossdomain.php'
        self.MY_LIKE_URL = 'http://tieba.baidu.com/f/like/mylike'

        self.ALL_TIEBA_LIST = []

        self.tb.field_names = ['贴吧', '状态']
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'c.tieba.baidu.com',
            'User-Agent': 'bdtb for Android 10.3.8.10',
            'Connection': 'close'
        }

    def get_time_stamp(self):
        return str(int(time.time() * 1000))

    def save_cookie(self, user):
        cookie_dict = self.s.cookies.get_dict()
        with open('.%s' % user, 'w') as f:
            json.dump(cookie_dict, f)
            f.close()

    def load_cookie(self, user):
        with open('.%s' % user, 'r') as f:
            cookie_dict = json.loads(f.read())
            f.close()
        for k, v in cookie_dict.items():
            self.s.cookies.set(k, v)

    def unicast(self, channel_id):
        tt = self.get_time_stamp()
        r = self.s.get(
            url=self.UNICAST_URL,
            params={
                'channel_id': channel_id,
                'tpl': 'tb',
                'apiver': 'v3',
                'callback': '',
                'tt': tt,
                '_': tt
            }
        )
        rsp = r.text.replace('(', '').replace(')', '')
        rsp_json = json.loads(rsp)
        try:
            channel_v = json.loads(rsp_json['channel_v'])
            return channel_v
        except:
            print('扫描超时')

    def qr_login_set_cookie(self, bduss):
        tt = self.get_time_stamp()
        r = self.s.get(
            url=self.QR_LOGIN_URL,
            params={
                'v': tt,
                'bduss': bduss,
                'u': self.INDEX_URL,
                'loginVersion': 'v4',
                'qrcode': '1',
                'tpl': 'tb',
                'apiver': 'v3',
                'tt': tt,
                'alg': 'v1',
                'time': tt[10:]
            }
        )
        rsp = json.loads(r.text.replace("'", '"'))
        bdu = rsp['data']['hao123Param']
        self.s.get(f'{self.HAO123_URL}?bdu={bdu}&t={tt}')
        self.s.get(self.MY_LIKE_URL)

    def down_qr_code(self, imgurl):
        r = self.s.get(f'https://{imgurl}')
        with open('qrcode.png', 'wb') as f:
            f.write(r.content)
            f.close()

    def read_qr_code(self, imgurl):
        self.down_qr_code(imgurl)
        img = Image.open('qrcode.png')
        barcodes = pyzbar.decode(img)
        for barcode in barcodes:
            barcodeData = barcode.data.decode("utf-8")
            return barcodeData

    def get_qr_code(self):
        tt = self.get_time_stamp()
        r = self.s.get(
            url=self.QR_CODE_URL,
            params={
                'lp': 'pc',
                'qrloginfrom': 'pc',
                'apiver': 'v3',
                'tt': tt,
                'tpl': 'tb',
                '_': tt
            }
        )
        app = input('有百度贴吧APP / 百度APP，请输入 1 ，没有请输入 2\n：')
        imgurl = r.json()['imgurl']
        while True:
            if app == '1':
                print(f'请使用浏览器打开二维码链接并使用百度贴吧APP / 百度APP扫描：https://{imgurl}')
                print('注意：请使用IE浏览器打开二维码链接！！！')
                break
            elif app == '2':
                qrurl = self.read_qr_code(imgurl)
                os.remove('./qrcode.png')
                print(f'请使用已经登录了百度贴吧网页端的浏览器打开链接并按照提示完成登陆：{qrurl}')
                break
        channel_id = r.json()['sign']
        return channel_id

    def qr_login(self, user):
        channel_id = self.get_qr_code()
        while True:
            rsp = self.unicast(channel_id)
            if rsp and rsp['status'] == 1: print('扫描成功,请在手机端确认登录!')
            if rsp and rsp['status'] == 0:
                print('确认登陆成功')
                bduss = rsp['v']
                self.qr_login_set_cookie(bduss)
                self.save_cookie(user)
                break

    def login(self, user):
        self.s.cookies.clear()
        self.qr_login(user)
        print('Login: True')
        tiebas = self.get_like_tiebas()
        self.ALL_TIEBA_LIST.extend(tiebas)
        self.start(tiebas)

    def check_login(self):
        r = self.s.get(self.TBS_URL)
        rsp = r.json()
        return True if rsp['is_login'] == 1 else False

    def calc_sign(self, str_dict):
        md5 = hashlib.md5()
        md5.update((
                           ''.join(
                               '%s=%s' % (k, v)
                               for k, v in str_dict.items()
                           ) + self.MD5_KEY).encode('utf-8')
                   )
        return md5.hexdigest().upper()

    def get_bduss_stoken(self):
        bduss = self.s.cookies.get_dict()['BDUSS']
        stoken = self.s.cookies.get_dict()['STOKEN']
        return bduss, stoken

    def get_like_tiebas(self):
        bduss, stoken = self.get_bduss_stoken()
        data = {
            'BDUSS': bduss,
            'stoken': stoken,
            'timestamp': self.get_time_stamp()
        }
        data['sign'] = self.calc_sign(data)
        for _ in range(5):
            try:
                r = requests.post(
                    url=self.LIKES_URL,
                    data=data,
                    cookies=self.s.cookies,
                    headers=self.headers,
                    timeout=3
                )
            except:
                continue
        return [tieba['name'] for tieba in r.json()['forum_list']]

    def get_tbs(self):
        r = self.s.get(self.TBS_URL).json()
        return r['tbs']

    def recognize_captcha(self, remote_url, rec_times=3):
        for _ in range(rec_times):
            while True:
                try:
                    response = requests.get(remote_url, timeout=6)
                    if response.text:
                        break
                    else:
                        print("retry, response.text is empty")
                except Exception as ee:
                    print(ee)

            files = {'image_file': ('captcha.jpg', BytesIO(response.content), 'application')}
            r = requests.post(self.CAPTCHA_API, files=files)
            try:
                predict_text = json.loads(r.text)["value"]
                return predict_text
            except:
                continue

    def sign_with_vcode(self, tieba, tbs, captcha_input_str, captcha_vcode_str):
        """
        由于暂时没碰见需要验证码的情况,
        故此处只是print
        """
        print(f'{tieba} 需要验证码')

    def sign(self, tieba):
        tbs = self.get_tbs()
        bduss, stoken = self.get_bduss_stoken()
        data = {
            'BDUSS': bduss,
            'kw': tieba,
            'stoken': stoken,
            'tbs': tbs,
            'timestamp': self.get_time_stamp()
        }
        sign = self.calc_sign(data)
        data['sign'] = sign
        for _ in range(5):
            try:
                r = requests.post(
                    url=self.SIGN_URL,
                    data=data,
                    cookies=self.s.cookies,
                    headers=self.headers,
                    timeout=5
                )
                rsp = r.json()
                break
            except:
                continue
        try:
            if rsp['user_info']['is_sign_in'] == 1:
                self.tb.add_row([tieba, '签到成功'])
        except:
            if rsp['error_msg'] == 'need vcode':  # 这里也不清楚手机端需不需要验证码
                captcha_vcode_str = rsp['data']['captcha_vcode_str']
                captcha_url = f'{self.GEN_IMG_URL}?{captcha_vcode_str}'
                captcha_input_str = self.recognize_captcha(captcha_url)
                self.sign_with_vcode(tieba, tbs, captcha_input_str, captcha_vcode_str)
            else:
                self.tb.add_row([tieba, rsp['error_msg']])

    def start(self, tiebas):
        threads = []
        for tieba in tiebas:
            t = Thread(target=self.sign, args=(tieba,))
            threads.append(t)

        for tieba in threads:
            tieba.start()

        for tieba in threads:
            tieba.join()

    def main(self):
        start_time = time.time()
        for user in self.users:
            print(f'当前登陆: {user}')
            if os.path.exists('.%s' % user):
                self.load_cookie(user)
                if self.check_login():
                    print('CookieLogin: True')
                    tiebas = self.get_like_tiebas()
                    self.ALL_TIEBA_LIST.extend(tiebas)
                    self.start(tiebas)
                else:
                    print('%sCookies失效...正在重新登录...' % user)
                    self.login(user)
            else:
                self.login(user)
            self.tb.align = 'l'
            print(self.tb)
            self.tb.clear_rows()
        else:
            end_time = time.time()
            print('总共签到{}个贴吧,耗时:{}秒'.format(
                len(self.ALL_TIEBA_LIST),
                int(end_time - start_time)
            )
            )


class Tool:
    def __init__(self):
        self.user_lists = []
        self.time_table = []

    def parse_config(self):
        with open('tieba_conf.json', 'r') as f:
            conf_dict = json.loads(f.read())
            f.close()
        self.user_lists = conf_dict['userNames']
        self.time_table = conf_dict['timeTable']
        print('当前用户列表：', self.user_lists)
        print('当前签到时间表: ', self.time_table)

    def get_user_lists(self):
        return self.user_lists

    def get_time_table(self):
        return self.time_table


if __name__ == "__main__":
    tool = Tool()
    tool.parse_config()

    tieba = Tieba(tool.get_user_lists())
    # 先执行一次，做登录以及cookies保存

    try:
        tieba.main()
        for moment in tool.get_time_table():
            schedule.every().day.at(moment).do(tieba.main)
    except Exception as e:
        print(e)

    try:
        while True:
            schedule.run_pending()
            time.sleep(5)
    except KeyboardInterrupt:
        print("close tieba sign task.")
