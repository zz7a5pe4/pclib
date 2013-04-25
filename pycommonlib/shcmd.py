#!/usr/bin/python

import shlex, subprocess, sys
import pexpect
from logdec import prtwrapper

#bash treat return value 0 as success
class ShellResult:
    output = ""
    error = ""
    def __init__(self,v=127):
        self.ret = v

    def __str__(self):
        if self.ret == 0:
            return self.output
        else:
            return "Fail: {0}".format(self.error)

    def __nonzero__(self):
        if self.ret == 0:
            return True
        else:
            return False


def syncexec(shellcmds, logcmd=False, logrst=False, outputfile=sys.stdout):
    if not shellcmds:
        return None
    myprt = prtwrapper(file=outputfile)
    if logcmd: myprt(shellcmds)
    args = shlex.split(shellcmds)
    ret = ShellResult(0)
    p = subprocess.Popen(args,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret.output,ret.error = p.communicate()
    ret.ret = p.returncode

    if logrst:
        if ret:
            myprt(ret.output)
        else:
            myprt(ret.error)
    return ret

def syncexec_force(shellcmds, t=120, logcmd=False, logrst=False, outputfile=sys.stdout):
    if not shellcmds:
        return None
    myprt = prtwrapper(file=outputfile)
    if logcmd: myprt(shellcmds)
    ret = ShellResult(-1)
    child = None
    child_result_list = []
    try:
        child = pexpect.spawn('/bin/bash', ['-c', shellcmds], timeout=t)
        #index = p.expect ([pexpect.EOF, pexpect.TIMEOUT])
        while(1):
            i = child.expect ([pexpect.EOF, '.*(y/n).*$'])
            if i==0:
                child_result_list.append(child.before)
                break 
            elif i==1:
                child.sendline('y')             
    except pexpect.TIMEOUT as e:
        ret.error = "Timeout while running: {0}".format(shellcmds)
    except pexpect.ExceptionPexpect as e:
        ret.error = str(e)
    else:
        if child.isalive():
            child.wait()
        ret.ret = child.exitstatus if not child.exitstatus == None else -1
        ret.output = ''.join(child_result_list)
        ret.error = ret.output
    finally:
        if child:
            child.close()

    if logrst:
        if ret:
            myprt(ret.output)
        else:
            myprt(ret.error)
    return ret


def syncexec_timeout(shellcmds, t=600, logcmd=False, logrst=False, outputfile=sys.stdout):
    if not shellcmds:
        return None
    myprt = prtwrapper(file=outputfile)
    if logcmd: myprt(shellcmds)
    ret = ShellResult(-1)
    child = None
    try:
        child = pexpect.spawn('/bin/bash', ['-c', shellcmds], timeout=t)
        #index = p.expect ([pexpect.EOF, pexpect.TIMEOUT])
        while(1):
            i = child.readline()
            ret.output += i
            if not i:
                break
    except pexpect.TIMEOUT as e:
        ret.error = "Timeout while running: {0}".format(shellcmds)
    except pexpect.ExceptionPexpect as e:
        ret.error = str(e)
    else:
        if child.isalive():
            child.wait()
        ret.ret = child.exitstatus if not child.exitstatus == None else -1
        ret.output = ret.output.rstrip()
        ret.error = ret.output
    finally:
        if child:
            child.close()

    if logrst:
        if ret:
            myprt(ret.output)
        else:
            myprt(ret.error)
    return ret

def syncexec_generater(shellcmds, t=600, logcmd=False, logrst=False, outputfile=sys.stdout):
    if not shellcmds:
        return
    myprt = prtwrapper(file=outputfile)
    if logcmd: myprt(shellcmds)
    child = None
    try:
        child = pexpect.spawn('/bin/bash', ['-c', shellcmds], timeout=t)
        #index = p.expect ([pexpect.EOF, pexpect.TIMEOUT])
        while(1):
            i = child.readline()
            if i:
                if logrst:myprt(i.rstrip())
                yield i.rstrip()
            else:
                break
    except pexpect.TIMEOUT as e:
        yield "Timeout while running: {0}".format(shellcmds)
    except pexpect.ExceptionPexpect as e:
        yield str(e)
    #else:
        #yield str(child.exitstatus)
    finally:
        if child:
            child.close()
    return

def main():
    if len(sys.argv) < 2:
        cmd = r"ls -al ."
    else:
        cmd = sys.argv[1]
    
    #print "generator:"
    for i in syncexec_generater(cmd,t=10, logcmd=True):
        print i
    
    #print "normal:"
    r = syncexec(cmd,logcmd=True, logrst=True)
    #print r
    #print "success" if r else r.ret
    

if __name__ == '__main__':
    import sys
    main()
