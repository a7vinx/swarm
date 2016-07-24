# swarm
v0.4.0

English | [中文](https://github.com/Arvin-X/swarm/blob/master/docs/README-zh-CN.md).

Swarm is an open source modular distributed penetration testing Tool that use distributed task queue to implement communication in the master-slave mode system and use MongoDB for data storage. It consists of a distributed framework and function modules. The function module can be an entirely new implement of some penetration functions or it can be a simple wrap of an existing tool to implement distributed functionality. Because of the modularity architecture it is easy to customize and extend new features under the distributed framework.

Now in this version 0.4.0 it only has three modules:

- Subdomain name scan module
- Directories and files scan module
- Nmap extension module

If you want to write your own module, you can read [this](https://github.com/Arvin-X/swarm/blob/master/docs/modules.txt).


## Install
Zipball can be download [here](https://github.com/Arvin-X/swarm/archive/master.zip).
You can also use git to get swarm:

```
git clone git@github.com:Arvin-X/swarm.git
```

Swarm works with Python 2.6.x or 2.7.x. It need MongoDB and its python support *pymongo*. 

If you do not have MongoDB, you can use apt-get to install it:

```
apt-get install mongodb
```
To install pymongo, use:

```
pip install pymongo
```
If you want use Nmap extension module, you need python library *libnmap* on both master and slave host and *nmap* on slave host. To get *libnmap*, use pip:

```
pip install libnmap
```


## Usage
Run swarm.py on master host to distribute tasks and run swarm-s.py with '-p' option on slave host to finish the subtask from master.
```
python swarm-s.py -p 9090
```
You can also establish a listener on target port of slave host to receive command to waken swarm-s by specify '--waken' option when you run swarm.py. Otherwise you should leave '--waken' null.
To create a listener, you can use nc or socat like:
```
nc -e /bin/sh -l 9090
```
And use waken command like:
```
python /root/swarm/swarm-s.py ARGS
```
You need to leave "ARGS" in your command and ensure it will be cli args passed to swarm.py for swarm to replace it with some necessary arguments like '-p'.

Basic usage of swarm:

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
                [--dom-levellen LEN] [--dom-timeout TIME] [--nmap-ports PORTS]
                [--nmap-top-ports NUM] [--nmap-ops ...]

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

Domain Scan:
  Thes option can be used to customize swarm action of subdomain name scan

  --dom-compbrute       Use complete brute force without dictionary on target
  --dom-dict PATH       Path to dictionary used for subdomain name scan
  --dom-maxlevel NUM    Max level of subdomain name to scan
  --dom-charset SET     Charset used for complete brute foce
  --dom-levellen LEN    Length interval of subdomain name each level
  --dom-timeout TIME    Timeout option for subdomain name scan

Nmap Module:
  These options can be used customize nmap action on slave hosts

  --nmap-ports PORTS    Support format like '80,443,3306,1024-2048'
  --nmap-top-ports NUM  Scan <number> most common ports
  --nmap-ops ...        Nmap options list in nmap’s man pages, this should
                        be the last in cli args

```

It is recommended that to use configuration file to configure swarm instead of using cli arguments if your requirement is high.

## License ##
Swarm is licensed under the [GPLv3](https://github.com/Arvin-X/swarm/blob/master/LICENSE).
