#!/usr/bin/python

import commands
import json
import netifaces

class theIP:
    iface=""
    ipaddr=""
    netmask=""
    brdcast=""
    gateway=""
    dns=""
    macaddr=""
    
    def __init__(self, interfaceid):
        self.iface=interfaceid
        cmd = "ifconfig %s | grep 'inet addr:' |cut -d: -f2 | awk '{ print $1}'" % interfaceid
        self.ipaddr = commands.getoutput(cmd)
        if "error" in self.ipaddr: 
            self.ipaddr = ""
            return
        cmd = "ifconfig %s | grep 'inet addr:' |cut -d: -f3 | awk '{ print $1}'" % interfaceid
        self.brdcast = commands.getoutput(cmd)
        
        cmd = "ifconfig %s | grep 'inet addr:' |cut -d: -f4 | awk '{ print $1}'" % interfaceid
        self.netmask = commands.getoutput(cmd)
        
        cmd = r"route -n | grep 'UG[ \t]' | awk '{print $2}'"
        self.gateway = commands.getoutput(cmd)
    
    def __str__(self):
        d = {}
        d["interface"]=self.iface
        d["ipaddr"]=self.ipaddr
        d["netmask"]=self.netmask
        d["brdcast"]=self.brdcast
        return json.dumps(d)
        
def getipaddr(iface):
    if not iface:
        return ""
    try:
        ips = netifaces.ifaddresses(iface)[netifaces.AF_INET]
        ret = [];
        for i in ips:
            ret.append(i["addr"])
    except ValueError as e:
        print "bad value"

    return ret

def getifaces():
    return netifaces.interfaces()

def getipaddres():
    ret = {}
    for i in netifaces.interfaces():
        ret[i] = getipaddr(i)

    return ret


def main():
    i = theIP("eth0")
    print i.ipaddr
    print i.netmask
    print i.brdcast
    print i.dns
    print i.gateway
    print i.macaddr
    print i


if __name__ == "__main__":
    main()
