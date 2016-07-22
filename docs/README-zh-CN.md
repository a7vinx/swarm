# swarm
v0.3.0

[English](https://github.com/Arvin-X/swarm/blob/master/README.md) | 中文

Swarm是一个开源的模块化分布式渗透测试工具，使用分布式任务队列实现主从模式系统间的通信，使用MongoDB做数据存储。Swarm由分布式框架及各功能模块组成，其中的功能模块既可以是对某些渗透功能的全新实现，也可以是对已经存在的渗透工具的简单封装以实现其分布式的功能。在模块化架构下很容易自定义模块或者为Swarm扩展新功能。

在现在的v0.3.0版本中，Swarm只实现了两个模块：
- 子域名扫描模块
- 文件扫描模块

如果你想实现自己的模块，你可以阅读[这份文件](https://github.com/Arvin-X/swarm/blob/master/docs/modules.txt).

## 安装
可以在[这里](https://github.com/Arvin-X/swarm/archive/master.zip)下载swarm最新的压缩包。

你也可以使用git来获取swarm：

```
git clone git@github.com:Arvin-X/swarm.git
```
Swarm需要Python 2.6.x 或者2.7.x 环境。Swarm也需要MongoDB以及它的python支持库pymongo。

如果你没有安装MongoDB，你可以使用apt-get来安装：

```
apt-get install mongodb
```
要安装pymongo，可以使用：

```
pip install pymongo
```

## 使用方法
在master主机上运行swarm.py来分发任务，在slave主机上使用“-p”参数运行swarm-s.py 接收并完成来自master的子任务。
```
python swarm-s.py -p 9090
```
你也可以在slave主机的指定端口建立监听接收来自master对swarm-s的唤醒命令,这需要你使用swarm的“--waken”选项。如果你不需要唤醒swarm-s，将这一选项置为空。
你可以使用nc或者socat来建立监听：
```
nc -e /bin/sh -l 9090
```
然后使用唤醒命令例如:
```
python /root/swarm/swarm-s.py ARGS
```
你需要在命令中预留字符”ARGS”并保证它将会作为命令行参数传递给swarm-s，swarm将会在运行过程中使用类似“-p”等参数替换它。

Swarm的基本使用方法：

```
usage: swarm.py [-h] -m MODULE [-v] [-c] [-o PATH] [-t [TARGET [TARGET ...]]]
                [-T PATH] [-s [SWARM [SWARM ...]]] [-S PATH] [--waken CMD]
                [--timeout TIME] [--m-addr ADDR] [--m-port PORT]
                [--s-port PORT] [--authkey KEY] [--db-addr ADDR]
                [--db-port PORT] [--process NUM] [--thread NUM] [--taskg NUM]
                [--dir-http-port PORT] [--dir-https-port PORT]
                [--dir-compbrute] [--dir-charset SET] [--dir-len LEN]
                [--dir-dict PATH] [--dir-maxdepth NUM] [--dir-timeout TIME]
                [--dir-not-exist FLAG] [--dir-quick-scan] [--dom-compbrute]
                [--dom-dict PATH] [--dom-maxlevel NUM] [--dom-charset SET]
                [--dom-levellen LEN] [--dom-timeout TIME]

optional arguments:
  -h, --help            show this help message and exit
  -m MODULE             Use module name in ./modules/ to enable it

Output:
  These option can be used to control output

  -v                    Output more verbose
  -c                    Disable colorful log output
  -o PATH               Record log in target file

Target:
  At least one of these options has to be provided to define target

  -t [TARGET [TARGET ...]]
                        Separated by blank (eg: github.com 127.0.0.0/24
                        192.168.1.5)
  -T PATH               File that contains target list, one target per line

Swarm:
  Use these options to customize swarm connection. At least one of slave
  host has to be provided.

  -s [SWARM [SWARM ...]]
                        Address of slave hosts with port if you need waken
                        them (eg: 192.168.1.2:9090 192.18.1.3:9191). No port
                        if swarm-s on slave host has already run
  -S PATH               File that contains slave list, one host per line
  --waken CMD           Command to waken up slave hosts, null if swarm-s on
                        slave host has already run
  --timeout TIME        Seconds to wait before request to swarm getting
                        response
  --m-addr ADDR         Master address which is reachable by all slave hosts
  --m-port PORT         Listen port on master host to distribute task
  --s-port PORT         Listen port on slave host to receive command from
                        master
  --authkey KEY         Auth key between master and slave hosts

Database:
  These option can be used to access MongoDB server

  --db-addr ADDR        Address of MongoDB server
  --db-port PORT        Listening port of MongoDB server

Common:
  These option can be used to customize common configuration of slave host

  --process NUM         Max number of concurrent process on slave host
  --thread NUM          Max number of concurrent threads on slave host
  --taskg NUM           Granularity of subtasks from 1 to 3

Directory Scan:
  These option can be used to customize swarm action of directory scan

  --dir-http-port PORT  Separated by '|' if you need multiple ports
  --dir-https-port PORT
                        Separated by '|' if you need multiple ports
  --dir-compbrute       Use complete brute force without dictionary on target
  --dir-charset SET     Charset used for complete brute foce
  --dir-len LEN         Length interval of directory name or file name
  --dir-dict PATH       Path to dictionary used for directory scan
  --dir-maxdepth NUM    Max depth in directory and file scan
  --dir-timeout TIME    Timeout option for directory scan
  --dir-not-exist FLAG  Separated by '|' if you need multiple flags
  --dir-quick-scan      Use HEAD method instead of GET in scan

Domain Scan:
  Thes option can be used to customize swarm action of subdomain name scan

  --dom-compbrute       Use complete brute force without dictionary on target
  --dom-dict PATH       Path to dictionary used for subdomain name scan
  --dom-maxlevel NUM    Max level of subdomain name to scan
  --dom-charset SET     Charset used for complete brute foce
  --dom-levellen LEN    Length interval of subdomain name each level
  --dom-timeout TIME    Timeout option for subdomain name scan  
```
如果你有较多的需求，最好使用配置文件而不是命令行参数来定义它们。

## License ##
Swarm在[GPLv3](https://github.com/Arvin-X/swarm/blob/master/LICENSE)许可证下发布。
