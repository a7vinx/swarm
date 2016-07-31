# swarm
v0.6.0

[English](https://github.com/Arvin-X/swarm/blob/master/README.md) | 中文

Swarm是一个开源的模块化分布式渗透测试工具，使用分布式任务队列实现主从模式系统间的通信，使用MongoDB做数据存储。Swarm由分布式框架及各功能模块组成，其中的功能模块既可以是对某些渗透功能的全新实现，也可以是对已经存在的渗透工具的简单封装以实现其分布式的功能。在模块化架构下很容易自定义模块或者为Swarm扩展新功能。

在现在的v0.6.0版本中，Swarm实现了五个模块：

 - 子域名扫描模块
 - 文件扫描模块
 - Nmap扩展模块
 - 站点地图爬虫模块
 - 入侵者模块

如果你想实现自己的模块，你可以阅读[这份文件](https://github.com/Arvin-X/swarm/blob/master/docs/modules.txt).

## 安装
可以在[这里](https://github.com/Arvin-X/swarm/archive/master.zip)下载swarm最新的压缩包。

你也可以使用git来获取swarm：

```
git clone git@github.com:Arvin-X/swarm.git
```

然后使用setup.py来安装：

```
python setup.py install
```

Swarm需要Python 2.6.x 或者2.7.x 环境。在master机器上，Swarm还需要MongoDB数据库支持。

如果你没有安装MongoDB，你可以使用apt-get来安装：

```
apt-get install mongodb
```


## 使用方法
在master主机上运行swarm来分发任务，在slave主机上使用“-p”参数运行swarm-s 接收并完成来自master的子任务。

```
swarm-s -p 9090
```

你也可以在slave主机的指定端口建立监听接收来自master对swarm-s的唤醒命令,这需要你使用swarm的“--waken”选项。如果你不需要唤醒swarm-s，将这一选项置为空。
你可以使用nc或者socat来建立监听：

```
nc -e /bin/sh -l 9090
```

然后使用唤醒命令例如:

```
swarm-s ARGS
```

你需要在命令中预留字符”ARGS”并保证它将会作为命令行参数传递给swarm-s，swarm将会在运行过程中使用类似“-p”等参数替换它。

Swarm的基本使用方法：

```
usage: swarm [-h] -m MODULE [-v] [-c] [-o PATH] [-t [TARGET [TARGET ...]]]
             [-T PATH] [-s [SWARM [SWARM ...]]] [-S PATH] [--waken CMD]
             [--timeout TIME] [--m-addr ADDR] [--m-port PORT] [--s-port PORT]
             [--authkey KEY] [--db-addr ADDR] [--db-port PORT] [--process NUM]
             [--thread NUM] [--taskg NUM] [--dom-compbrute] [--dom-dict PATH]
             [--dom-maxlevel NUM] [--dom-charset SET] [--dom-levellen LEN]
             [--dom-timeout TIME] [--dir-http-port PORT]
             [--dir-https-port PORT] [--dir-compbrute] [--dir-charset SET]
             [--dir-len LEN] [--dir-dict PATH] [--dir-maxdepth NUM]
             [--dir-timeout TIME] [--dir-not-exist FLAG] [--dir-quick-scan]
             [--nmap-ports PORTS] [--nmap-top-ports NUM] [--nmap-ops ...]
             [--int-target [URLS [URLS ...]]] [--int-method METHOD]
             [--int-headers JSON] [--int-cookies COOKIES] [--int-body BODY]
             [--int-payload PAYLOAD] [--int-flag FLAGS] [--int-timeout TIME]
             [--map-seed SEED] [--map-http-port PORT] [--map-https-port PORT]
             [--map-cookies COOKIES] [--map-interval TIME]
             [--map-timeout TIME]

optional arguments:
  -h, --help            show this help message and exit
  -m MODULE             Use module name in ./modules/ to enable it

Output:
  These option can be used to control output

  -v                    Output more verbose
  -c                    Disable colorful log output
  -o PATH               Record log in target file

Target:
  At least one of these options has to be provided to define target unless
  there is another special option for defining target in the module

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

Domain Scan:
  Thes option can be used to customize swarm action of subdomain name scan

  --dom-compbrute       Use complete brute force without dictionary on target
  --dom-dict PATH       Path to dictionary used for subdomain name scan
  --dom-maxlevel NUM    Max level of subdomain name to scan
  --dom-charset SET     Charset used for complete brute foce
  --dom-levellen LEN    Length interval of subdomain name each level
  --dom-timeout TIME    Timeout option for subdomain name scan

Directory Scan:
  These option can be used to customize swarm action of directory scan

  --dir-http-port PORT  Separated by comma if you need multiple ports
  --dir-https-port PORT
                        Separated by comma if you need multiple ports
  --dir-compbrute       Use complete brute force without dictionary on target
  --dir-charset SET     Charset used for complete brute foce
  --dir-len LEN         Length interval of directory name or file name
  --dir-dict PATH       Path to dictionary used for directory scan
  --dir-maxdepth NUM    Max depth in directory and file scan
  --dir-timeout TIME    Timeout option for directory scan
  --dir-not-exist FLAG  Separated by double comma if you need multiple flags
  --dir-quick-scan      Use HEAD method instead of GET in scan

Nmap Module:
  These options can be used customize nmap action on slave hosts

  --nmap-ports PORTS    Support format like '80,443,3306,1024-2048'
  --nmap-top-ports NUM  Scan <number> most common ports
  --nmap-ops ...        Nmap options list in nmap’s man pages, this should
                        be the last in cli args

Intruder:
  Use indicator symbol '@n@' where 'n' should be a number, like '@0@','@1@'
  etc to specify attack point in option 'int_target' and 'int_body'. Use
  'int_payload' option to specify payload used on these attack point to
  complete this attack.

  --int-target [URLS [URLS ...]]
                        Use this option instead of '-t' or '-T' options to
                        specify targets,separated by comma
  --int-method METHOD   Http method used in this attack
  --int-headers JSON    A JSON format data.(eg: {"User-
                        Agent":"Mozilla/5.0","Origin":"XXX"})
  --int-cookies COOKIES
                        Separated by comma. (eg: PHPSESSIONID:XX,token:XX)
  --int-body BODY       HTTP or HTTPS body. You can use indicator symbol in
                        this option
  --int-payload PAYLOAD
                        The format should follow '@0@:PATH,@1@:NUM-
                        NUM:CHARSET'
  --int-flag FLAGS      Separated by double comma if you have multiple flags
  --int-timeout TIME    Timeout option for intruder module

Sitemap Crawler:
  These options can be used to customize sitemap crawler, not support js
  parse yet

  --map-seed SEED       Separated by comma if you have multiple seeds
  --map-http-port PORT  Separated by comma if you need multiple ports
  --map-https-port PORT
                        Separated by comma if you need multiple ports
  --map-cookies COOKIES
                        Separated by comma if you have multiple cookies
  --map-interval TIME   Interval time between two request
  --map-timeout TIME    Timeout option for sitemap crawler

```

如果你有较多的需求，最好使用配置文件而不是命令行参数来定义它们。Swarm的配置文件在/etc/swarm/目录下。

## License ##
Swarm在[GPLv3](https://github.com/Arvin-X/swarm/blob/master/LICENSE)许可证下发布。
