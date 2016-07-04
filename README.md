# swarm
V0.1.0
Swarm is an open source distributed penetration testing Tool that use distributed task queue to implement communication in the master-slave mode system. It should have these features:

- Subdomain name scan
- Host info scan
- Directories and files scan
- Web vulnerabilities scan
- Host vulnerabilities scan
- Exploit module
- Result report

But now it only implement the feature of subdomain name scan with the distributed system in version 0.1.

## Install
Zipball can be download [here](https://github.com/Arvin-X/swarm/archive/master.zip).
You can also use git to get swarm:
```
git clone git@github.com:Arvin-X/swarm.git
```
Python 2.7.x is recommended. But it should also works fine on higher version with correct configuration.

## Usage
Run swarm.py on master host to distribute tasks and run swarm-s.py with '-p' option on slave host to finish the subtask from master.
```
python swarm-s.py -p 9090
```
You can also establish a listener on target port of slave host to receive command to waken swarm-s by specify '--waken' option. Otherwise you should leave '--waken' null.
To create a listener, you can use nc or socat like:
```
nc -e /bin/sh -l 9090
```
And use waken command like:
```
python /root/swarm/swarm-s.py ARGS
```
You should leave "ARGS" in your command for swarm to replace it with some necessary arguments like '-p'.

Basic usage of swarm:
```
usage: swarm.py [-h] [-v] [-c] [-o PATH] [-t [TARGET [TARGET ...]]] [-T PATH]
                [-s [SWARM [SWARM ...]]] [-S PATH] [--waken CMD]
                [--timeout TIME] [--m-addr ADDR] [--m-port PORT]
                [--s-port PORT] [--authkey KEY] [--process NUM] [--thread NUM]
                [-d] [--d-compbrute] [--d-dict PATH] [--d-maxlevel NUM]
                [--d-charset SET] [--d-levellen LEN] [--d-timeout TIME]

optional arguments:
  -h, --help            show this help message and exit

Output:
  These option can be used to control output

  -v                    Output more verbose
  -c                    Disable colorful log output
  -o PATH               Record log in target file

Target:
  At least one of these options has to be provided to define target

  -t [TARGET [TARGET ...]]
                        Target separated by blank (eg: github.com 127.0.0.0/24
                        192.168.1.5)
  -T PATH               File that contains target list, one target per line

Swarm:
  At least one of these options has to be provided to define slave host

  -s [SWARM [SWARM ...]]
                        Address of slave hosts with port if you need waken
                        them (eg: 192.168.1.2:9090 192.18.1.3:9191). No port
                        if swarm-s on slave host has already run and '--waken'
                        should be empty meanwhile
  -S PATH               File that contains slave list, one host per line
  --waken CMD           Command to waken up slave hosts, null if swarm-s on
                        slave host has already run
  --timeout TIME        Seconds to wait before request to swarm getting
                        response
  --m-addr ADDR         Master address which should be reachable by all slave
                        hosts
  --m-port PORT         Listen port on master host to distribute task
  --s-port PORT         Listen port on slave host to receive command from
                        master
  --authkey KEY         Auth key between master and slave hosts

Common:
  These option can be used to customize common configuration of slave host

  --process NUM         Number of process running on slave host
  --thread NUM          Number of threads running on slave host

Domain Scan:
  Thes option can be used to customize swarm action of subdomain name scan

  -d                    Do subdomain scan on target
  --d-compbrute         Use complete brute force without dictionary on target
  --d-dict PATH         Path to dictionary used for subdomain name scan
  --d-maxlevel NUM      Max level of subdomain name to scan
  --d-charset SET       Charset used for complete brute foce
  --d-levellen LEN      Length interval of subdomain name each level
  --d-timeout TIME      Timeout option for subdomain name scan
  ```
It is recommended that to use configuration file to configure swarm instead of using arguments if your requirement is high.

## License ##
Swarm is licensed under the GPLv3.
