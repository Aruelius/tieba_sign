# Tieba_sign_docker
功能：
1. 支持docker一键部署至服务器，并定时执行签到
2. 支持通过配置文件，修改用户列表、签到时间，并手动编译docker镜像

## 使用docker一键部署
### 1. cd到docker目录下

`cd docker`

### 2. 启动脚本

`./run_from_hub.sh 0`

> 脚本后面的参数可选0或者1

> 0表示使用最小化镜像，但功能上有缺失，只能支持通过百度贴吧或者百度APP扫码登录(推荐使用)；

> 1表示使用标准镜像，占用空间较大，但支持两种登录模式(见项目README.md)

> docker hub上编译好的镜像默认支持一个用户，定时签到时间为每天4：00和15:00，
如需要修改，可以用docker命令进入容器中修改tieba_conf.json后重启容器

## 手动build镜像
### 1. cd到_build目录

`cd docker/_build`

### 2. 修改配置文件(可选): 
如需要修改**用户列表**或者**定时签到**的时刻，
则修改对应文件夹下的`tieba_conf.json`。最小镜像在`minimize`下，标准镜像在`fullFunction`下。

例如：
````json
{
  "userNames": [
    "张三","李四"
  ],
  "timeTable": [
    "04:00","15:00","20:00"
  ]
}

````

### 3. 执行脚本编译并运行

`./build_and_run.sh 0`

> 脚本后面的参数可选0或者1，含义与上文一致



