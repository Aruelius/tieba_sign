# Tieba_Sign

[![](https://img.shields.io/github/license/Aruelius/tieba_sign.svg?color=ff69b4)](https://github.com/Aruelius/tieba_sign/blob/master/LICENSE)  [![](https://img.shields.io/badge/Python-3.7-ff69b4.svg)](hhttps://github.com/Aruelius/tieba_sign)  

百度贴吧多线程扫码登陆 / 自动签到 / 自动打码

经测试：在三个帐号，一共207个贴吧的情况下，全部签到完成速度为5s左右。(Cookies登录情况下)

**Use：Python3**

## 效果

![alt 效果图](./view.png)

## 使用教程

###### 1.安装依赖

```python
pip install -r requirements.txt
```
```shell
# Centos
yum install zbar -y

# Ubuntu
sudo apt-get install libzbar-dev -y
```
###### 2.增加用户配置 (tieba_sign.py)

```python
users = ['用户名']
# 用户名,例如['用户1', '用户2', '用户3'] 一共3个用户
# 请按照从前往后的顺序来依次进行登陆
```

### 运行

```shell
python tieba_sign.py # 开始登录并签到
```

------

请注意，在最新版本中，需要扫码登陆，程序运行的时候，会问你是否有百度贴吧 or 百度 APP，如果有，那就会出现一条二维码链接，使用 **IE浏览器** *(因为Chrome浏览器打开二维码链是黑底，百度贴吧APP不能有效的识别，所以建议使用IE浏览器)* 打开此链接，并使用APP扫码登陆；如果没有这两个APP，同样会给出一条链接，该链接是解析二维码得到的链接，使用任意**已经登陆了百度贴吧网页版**的浏览器打开该链接 —> 选择验证方式 —> 输入验证码 —> 点确认登录即可，脚本会自动完成登陆。

### TODO

- ~~手机号码登陆（Working）~~
- 扫码登陆~~，动态口令登陆~~（已完成）
- ~~自动获取QQ邮箱验证码，达到全自动登陆（Woking）~~
- 添加打码平台（已完成）
- 二次使用Cookie登陆（已完成）
- 多线程签到（已完成）
- 多账号签到（已完成）

### 优势

1. Python3
2. 支持Windows / Mac / Linux 全平台
3. 使用自建免费打码平台
4. 签到200个贴吧仅需5s左右
5. 扫码登陆更安全

### 注意事项

- 如果使用Crontab自动签到，请先将已经得到的Cookie文件放入/root/目录下

  > 如果不是root用户，把Cookie放入当前用户目录下即可
  >
  > Cookie文件格式为‘.User’，User为用户名，整体为隐藏文件
  >
  > 复制命令为cp，例子：```cp .User /root/```
  >
  > 查看隐藏文件命令为```ll -a```
  >
  > 建议设置自动签到时间为早四点和下午四点：04:00 16:00防止漏签
  >
  > 漏签只有一个原因，网络问题导致连接打码服务器出问题。

- 遇到任何问题，请提交Issues！

### ChangeLog

2019年10月12日

1. 登录块从账号密码登陆改成了扫码登陆，因为账号密码登陆需要拉动滑块验证
2. 验证码签到这块改善了代码，一般情况下不会再出现问题
3. 代码逻辑有改善

------

2019年06月12日

1. 重写登陆块，放弃selenium模拟登陆
2. 二次验证支持邮箱，手机验证码
3. 代码逻辑有改善

------

2019年04月07日

1. 添加多线程签到，签到速度约为1秒20个贴吧
2. 去除若快打码，使用自己训练的验证码识别接口，识别速度更快，准确率可以打到99.99%
3. 增加多用户签到，自行按照config.py文件填写相应帐号密码即可

------

2019年03月25日

1. 修复不能正确判断验证类型的BUG

   > 由于Centos安装的Chrome版本为71，Ubuntu为73，71版本的Chrome登录一定是验证码+二代验证，而73版本正常登录只有二代验证，所以这里判断策略出了点问题。

------

2019年03月20日

1. 由于签到一百个贴吧之后需要验证码，所以添加了打码功能，打码平台为若快打码
2. 登录一次之后会自动保存Cookie在本地，后续签到直接调用Cookie

------

### LICENSE

[MIT](https://github.com/Aruelius/tieba_sign/blob/master/LICENSE)
