# tieba_sign
百度贴吧多线程自动登录签到/自动打码<br>
经测试：在三个帐号，一共207个贴吧的情况下，全部签到完成速度为12s左右。(Cookies登录情况下)
## 效果
![效果](./view.png)

## 使用教程(Centos)
1、安装Chromium<br>
``` sh
yum install chromium
```
2、安装[Chromedriver](https://chromedriver.storage.googleapis.com/index.html?path=73.0.3683.68/)<br>
``` sh
wget https://chromedriver.storage.googleapis.com/73.0.3683.68/chromedriver_linux64.zip && unzip chromedriver_linux64.zip
mv chromedriver /usr/bin/ && chmod a+x /usr/bin/chromedriver
```
3、下载源码
``` sh
git clone https://github.com/MikuShare/tieba_sign/ && cd tieba_sign/
```
4、安装依赖
``` sh
pip install -r requirements.txt
```
5、修改配置文件(config.py)
``` python
users = ['用户名']
# 用户名,例如['用户1', '用户2', '用户3'] 一共3个用户

accounts = {
    '用户名': {
        'username': '帐号',
        'password': '密码'
    }
}

#用户名以及对应的帐号密码
#例如：
#accounts = {
#    '用户1': {
#        'username': '用户1的帐号',
#        'password': '用户1的密码.'
#    },
#    '用户2': {
#        'username': '用户2的帐号',
#        'password': '用户2的密码'
#    },
#    '用户3': {
#        'username': '用户3的帐号',
#        'password': '用户3的密码'
#    }
#}
# 一定要按照users里面的用户名顺序来填写accounts！！！
# 一定要按照users里面的用户名顺序来填写accounts！！！
# 一定要按照users里面的用户名顺序来填写accounts！！！
```
## 运行
``` sh
python tieba.py   # 开始登录并签到
```

## TODO
- [ ] ~~添加打码平台~~(已完成)
- [ ] ~~添加使用Cookies签到的脚本~~(已完成)
- [ ] ~~多线程签到~~(已完成)
- [ ] ~~多账号签到~~(已完成)
## 注意事项&已知BUG
1.脚本使用Python3.7.2编写，运行的时候请使用Python3<br>
2.Ubuntu安装Chromium的命令是：sudo apt-get install chromium-browser
``` sh
sudo apt-get install chromium-browser
```
3.测试在Ubuntu跟Centos都通过，Windows应该也可以，但是有些地方应该改动，后续会上传Windows的。<br>
4.签到100个吧之后需要验证码，~~后续会解决这个问题~~(已经添加打码功能)。<br>
5.登录时候如果验证码是中文的，也支持输入。<br>
6.支持多账号签到。<br>
7.使用自己训练的验证码接口。<br>
8.有时候登录会遇到验证码+二代验证的情况，这个验证码不用打码是因为可能会出现中文验证码，我并没有训练中文模型。<br>
9.如果遇到各种报Chrome的错，请运行：
``` sh
pkill chrome*
```
10.遇到任何问题，请提交Issues！<br>
## ChangeLog
2019年4月7日<br>
1.添加多线程签到，签到速度约为1秒20个贴吧。<br>
2.去除若快打码，使用自己训练的验证码识别接口，识别速度更快，准确率可以打到99.99%。<br>
3.增加多用户签到，自行按照config.py文件填写相应帐号密码即可。<br>
<br>
2019年3月25日<br>
1.修复不能正确判断验证类型的BUG(由于Centos安装的Chrome版本为71，Ubuntu为73，71版本的Chrome登录一定是验证码+二代验证，而73版本正常登录只有二代验证，所以这里判断策略出了点问题。)<br>
<br>
2019年3月20日<br>
1.由于签到一百个贴吧之后需要验证码，所以添加了打码功能，打码平台为[若快打码](https://www.ruokuai.com/)<br>
2.登录一次之后会自动保存cookies在本地，后续签到直接调用cookies。
## LICENSE
MIT
